# data_processing/file_processing.py

import pandas as pd
import io
import base64

def process_file(file_path, file_type):
    """
    Processes the uploaded file based on its type.
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

def decode_file(contents):
    """
    Decodes the uploaded file data.
    """
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return io.BytesIO(decoded)
    except Exception as e:
        raise ValueError(f"Error decoding file: {e}")
