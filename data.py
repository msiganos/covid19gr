import pandas as pd
import numpy as np
import requests
import bs4
import re
import json


df_daily_stats = None
df_three_days_stats = None
df_weekly_stats = None
df_total_stats = None

# Load data from csv files
def load_data_from_csv():
    return dict(
        df_daily_stats = pd.read_csv('data/daily_stats.csv'),
        df_three_days_stats = pd.read_csv('data/three_days_stats.csv'),
        df_weekly_stats = pd.read_csv('data/weekly_stats.csv'),
        df_total_stats = pd.read_csv('data/total_stats.csv')
    )


# Extract new raw data from webpage
def get_raw_data(save=False):

    URL = 'https://covid19.innews.gr/'

    try:
        r = requests.get(URL)
    
        if r.status_code != 200:
            return None
    
        # Load response to BeautifulSoup
        soup = bs4.BeautifulSoup(r.text, 'html.parser')  

        # Find script tag that contains the required data      
        script_tag = soup.find_all('script')[2]

        # Extract daily_stats
        m = re.search("var daily_stats = (\[.*\])", script_tag.string)
        daily_stats = json.loads(m.group(1))
        df_daily_stats = pd.DataFrame.from_records(daily_stats)

        # Extract weekly_stats
        m = re.search("var weekly_stats = (\[.*\])", script_tag.string)
        weekly_stats = json.loads(m.group(1))
        df_weekly_stats = pd.DataFrame.from_records(weekly_stats)

        # Extract three_days_stats
        m = re.search("var three_days_stats = (\[.*\])", script_tag.string)
        three_days_stats = json.loads(m.group(1))
        df_three_days_stats = pd.DataFrame.from_records(three_days_stats)

        # Extract last_stats
        # m = re.search("var last_stats = (\{.*\})", script_tag.string)
        # last_stats = json.loads(m.group(1))
        # series_last_stats = pd.Series(last_stats)

        # Extract total_stats
        m = re.search("var total_stats = (\{.*\})", script_tag.string)
        total_stats = json.loads(m.group(1))
        series_total_stats = pd.Series(total_stats)

        if save:
            df_daily_stats.to_csv('data/daily_stats-raw.csv', index=False)
            df_three_days_stats.to_csv('data/three_days_stats-raw.csv', index=False)
            df_weekly_stats.to_csv('data/weekly_stats-raw.csv', index=False)
            series_total_stats.to_csv('data/total_stats-raw.csv', index=False)

        return dict(
            df_daily_stats = df_daily_stats,
            df_three_days_stats = df_three_days_stats,
            df_weekly_stats = df_weekly_stats,
            df_total_stats = series_total_stats
        )
    
    except Exception as err:
        print(f'Error occurred: {err}')
        return None


# Process daily stats
def process_daily_stats(df, save=False):
    df_daily_stats = df.copy()
    
    # Cummulative sums for daily stats
    df_daily_stats['calculated_cases_cumsum'] = df_daily_stats['cases'].cumsum()
    df_daily_stats['calculated_deceased_cumsum'] = df_daily_stats['deceased'].cumsum()

    # Daily PCR tests
    series_tests_pcr = df_daily_stats['total_tests'].diff()
    series_tests_pcr[0] = df_daily_stats['total_tests'].iloc[0]
    series_tests_pcr = series_tests_pcr.astype(int)
    # Set daily PCR tests value equal to the previous day where there are negative differences
    series_tests_pcr[series_tests_pcr<0] = np.nan
    series_tests_pcr.ffill(inplace=True)
    
    # Daily rapid tests
    series_tests_rapid = df_daily_stats['total_rapid_tests'].diff()
    series_tests_rapid[0] = df_daily_stats['total_rapid_tests'].iloc[0]
    series_tests_rapid = series_tests_rapid.astype(int)
    # Set daily rapid tests value equal to the previous day where there are negative differences
    series_tests_rapid[series_tests_rapid<0] = np.nan
    series_tests_rapid.ffill(inplace=True)

    # Add calculated daily tests (PCR, rapid, total) to df_daily_stats
    df_daily_stats['calculated_tests_pcr'] = series_tests_pcr.astype(int)
    df_daily_stats['calculated_tests_rapid'] = series_tests_rapid.astype(int)
    df_daily_stats['calculated_tests_total'] = df_daily_stats['calculated_tests_pcr'] + df_daily_stats['calculated_tests_rapid']

    # Daily positivity rate
    df_daily_stats['calculated_positivity'] = df_daily_stats['cases'] / df_daily_stats['calculated_tests_total'] * 100

    # Fatality rate (data up to current day)
    df_daily_stats['calculated_fatality'] = df_daily_stats['calculated_deceased_cumsum'] / df_daily_stats['calculated_cases_cumsum'] * 100

    if save:
        df_daily_stats.to_csv('data/daily_stats.csv', index=False)

    return df_daily_stats


# Process total stats
def process_total_stats(series, save=False):
    # Create total stats dataframe from series
    df_total_stats = pd.DataFrame(series)
    df_total_stats.rename(columns={0: 'value'}, inplace=True)
    df_total_stats.drop(['id','date','created_at', 'updated_at'], inplace=True)
    df_total_stats.reset_index(inplace=True)
    df_total_stats['category'] = df_total_stats.apply(lambda row: row['index'].split('_')[0], axis=1)
    df_total_stats['age'] = df_total_stats.apply(lambda row: '_'.join(row['index'].split('_')[1:-1]), axis=1)
    df_total_stats['gender'] = df_total_stats.apply(lambda row: row['index'].split('_')[-1], axis=1)
    df_total_stats.set_index('index', inplace=True)
    df_total_stats['value'] = df_total_stats['value'].astype(int)

    if save:
        df_total_stats.to_csv('data/total_stats.csv', index=False)

    return df_total_stats


# Process three days stats
def process_three_days_stats(df, save=False):
    df_three_days_stats = df.copy()
    
    if save:
        df_three_days_stats.to_csv('data/three_days_stats.csv', index=False)

    return df_three_days_stats


# Process weekly stats
def process_weekly_stats(df, save=False):
    df_weekly_stats = df.copy()

    if save:
        df_weekly_stats.to_csv('data/weekly_stats.csv', index=False)

    return df_weekly_stats


def load_new_data(save=False):
    print('Getting new data...')

    global df_daily_stats
    global df_three_days_stats
    global df_weekly_stats
    global df_total_stats

    # Get raw data
    dfs_raw = get_raw_data()

    # If getting new raw data failed, read data from saved csv files
    if dfs_raw is None:
        print('Getting new raw data failed.')
        dfs = load_data_from_csv()
        df_daily_stats = dfs['df_daily_stats']
        df_total_stats = dfs['df_total_stats']
        df_three_days_stats = dfs['df_three_days_stats']
        df_weekly_stats = dfs['df_weekly_stats']
    else:
        # Process data
        df_daily_stats = process_daily_stats(dfs_raw['df_daily_stats'], save=save)
        df_total_stats = process_total_stats(dfs_raw['df_total_stats'], save=save)
        df_three_days_stats = process_three_days_stats(dfs_raw['df_three_days_stats'], save=save)
        df_weekly_stats = process_weekly_stats(dfs_raw['df_weekly_stats'], save=save)

# Initial call of load_new_data
load_new_data(save=True)