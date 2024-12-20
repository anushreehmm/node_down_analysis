# callbacks.py
import pandas as pd
from dash import Input, Output, State
import io
import base64
from app import app
from layout import success_message_style, error_message_style

# Global variables for processed data
file1_df = pd.DataFrame()
file2_df = pd.DataFrame()
merged_df = pd.DataFrame()

# File processing and decoding functions
def process_file(file_path, file_type):
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

        else:
            raise ValueError("Invalid file type specified.")
        
        return df
    except Exception as e:
        print(f"Error processing file: {e}")
        return pd.DataFrame()


def decode_file(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return io.BytesIO(decoded)
    except Exception as e:
        raise ValueError(f"Error decoding file: {e}")

def register_callbacks(app):

    # File upload callback for File1
    @app.callback(
        Output('file1-status', 'children'),
        Input('upload-file1', 'contents')
    )
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

    # File upload callback for File2
    @app.callback(
        Output('file2-status', 'children'),
        Input('upload-file2', 'contents')
    )
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

    # Callback to apply filters and update the table
    @app.callback(
        Output('filtered-table', 'data'),
        Input('filter-button', 'n_clicks'),
        State('date-range', 'start_date'),
        State('date-range', 'end_date'),
        State('downtime-dropdown', 'value')
    )
    def filter_data(n_clicks, start_date, end_date, downtime_value):
        if n_clicks is None or file1_df.empty or file2_df.empty:
            return []

        global merged_df
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
