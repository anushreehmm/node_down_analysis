# app/callbacks.py

from dash import Input, Output, State
import pandas as pd
from data_processing.file_processing import process_file, decode_file

# Callback for file upload
def handle_file1_upload(contents):
    if contents is None:
        return ""
    try:
        file1 = decode_file(contents)
        global file1_df
        file1_df = process_file(file1, "file1")
        return "File 1 uploaded and processed successfully!"
    except Exception as e:
        return f"Error: {e}"

def handle_file2_upload(contents):
    if contents is None:
        return ""
    try:
        file2 = decode_file(contents)
        global file2_df
        file2_df = process_file(file2, "file2")
        return "File 2 uploaded and processed successfully!"
    except Exception as e:
        return f"Error: {e}"

# Callback to filter the data
def filter_data(n_clicks, start_date, end_date, downtime_value):
    if n_clicks is None or file1_df.empty or file2_df.empty:
        return []

    merged_df = pd.merge(file1_df, file2_df, on="Node Alias", how="inner")
    filtered_df = merged_df.copy()

    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['Alarm Time'] >= pd.to_datetime(start_date)) & 
            (filtered_df['Alarm Time'] <= pd.to_datetime(end_date))
        ]

    if downtime_value:
        if downtime_value == '1-3':
            filtered_df = filtered_df[filtered_df['Downtime Count'] <= 3]
        elif downtime_value == '4-5':
            filtered_df = filtered_df[(filtered_df['Downtime Count'] >= 4) & (filtered_df['Downtime Count'] <= 5)]
        elif downtime_value == '>5':
            filtered_df = filtered_df[filtered_df['Downtime Count'] > 5]
        elif downtime_value == '>10':
            filtered_df = filtered_df[filtered_df['Downtime Count'] > 10]

    return filtered_df.to_dict('records')
