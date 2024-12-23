# process_data.py

import pandas as pd

def filter_data(df, date_range=None, downtime_criteria=None):
    """
    Filters the data based on the given date range and downtime criteria.
    
    :param df: DataFrame containing node data.
    :param date_range: Tuple (start_date, end_date) for filtering by date.
    :param downtime_criteria: Downtime count range as a string, e.g., '1-3'.
    :return: Filtered DataFrame.
    """
    if date_range:
        start_date, end_date = date_range
        if start_date and end_date:
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if downtime_criteria:
        if '-' in downtime_criteria:
            low, high = map(int, downtime_criteria.split('-'))
            df = df[(df['Downtime Count'] >= low) & (df['Downtime Count'] <= high)]
        elif downtime_criteria.startswith('>'):
            threshold = int(downtime_criteria[1:])
            df = df[df['Downtime Count'] > threshold]
            
    return df
