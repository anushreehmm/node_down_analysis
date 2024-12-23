# process_data.py

import pandas as pd

def process_file(file_path, file_type):
    """
    Processes the uploaded file based on its type.

    :param file_path: Path or buffer of the uploaded file.
    :param file_type: Type of file ('file1' or 'file2') for different structures.
    :return: Processed DataFrame.
    """
    try:
        df = pd.read_excel(file_path, skiprows=5)

        if file_type == "file1":
            df = df.rename(columns={
                'Unnamed: 0': 'Sl.no',
                'Unnamed: 1': 'IP Address',
                'Unnamed: 4': 'Event',
                'Unnamed: 6': 'Alarm Time',
                'Unnamed: 2': 'Node Alias'
            })
            df = df.drop(columns=['Sl.no', 'Clear Time', 'Duration', 'Description', 'Host Name'], errors='ignore')
            df = df.dropna(subset=['Node Alias', 'Alarm Time'])
            df['Alarm Time'] = pd.to_datetime(df['Alarm Time'], errors='coerce')
            df['Downtime Count'] = df.groupby('Node Alias')['Alarm Time'].transform('count')
        elif file_type == "file2":
            df = df.rename(columns={
                'Node Alias': 'Node Alias',
                'IP Address': 'IP Address',
                'Availability(%)': 'Availability',
                'Latency(msec)': 'Latency(msec)',
                'Packet Loss(%)': 'Packet Loss(%)'
            })
            df = df.drop(columns=['Host Name', 'Description'], errors='ignore')
            df['Packet Loss(%)'] = pd.to_numeric(df['Packet Loss(%)'], errors='coerce')
            df['Availability'] = pd.to_numeric(df['Availability'], errors='coerce')
            df['Latency(msec)'] = pd.to_numeric(df['Latency(msec)'], errors='coerce')
            df = df.dropna(subset=['Packet Loss(%)', 'Availability', 'Latency(msec)'])
        else:
            raise ValueError("Invalid file type specified.")

        return df
    except Exception as e:
        print(f"Error processing file: {e}")
        return pd.DataFrame()


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
            df = df[(df['Alarm Time'] >= pd.to_datetime(start_date)) & 
                    (df['Alarm Time'] <= pd.to_datetime(end_date))]

    if downtime_criteria:
        if '-' in downtime_criteria:
            low, high = map(int, downtime_criteria.split('-'))
            df = df[(df['Downtime Count'] >= low) & (df['Downtime Count'] <= high)]
        elif downtime_criteria.startswith('>'):
            threshold = int(downtime_criteria[1:])
            df = df[df['Downtime Count'] > threshold]

    return df
