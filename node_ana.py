#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import re
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc
import io
import base64

# Define patterns for file identification (optional use, e.g., for testing)
file1_pattern = r"iBUS-Node-EVENT-TAJ_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"
file2_pattern = r"iBUS-Taj_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"

# Function to clean data
def data_clean(file_path, pattern_key):
    try:
        df = pd.read_excel(file_path)
        if pattern_key == "file1_pattern":
            required_columns = ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4', 'Unnamed: 6', 'Unnamed: 2']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Column {col} not found in File 1.")

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
        elif pattern_key == "file2_pattern":
            required_columns = ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Column {col} not found in File 2.")

            df = df.drop([0, 1, 2, 3, 4], axis=0).reset_index(drop=True)
            df = df.rename(columns={
                'Unnamed: 0': 'Node Alias',
                'Unnamed: 1': 'IP Address',
                'Unnamed: 4': 'Availability',
                'Unnamed: 5': 'Latency(msec)',
                'Unnamed: 6': 'Packet Loss(%)'
            })
            df['Packet Loss(%)'] = pd.to_numeric(df['Packet Loss(%)'], errors='coerce')
            df['Availability'] = pd.to_numeric(df['Availability'], errors='coerce')
            df['Latency(msec)'] = pd.to_numeric(df['Latency(msec)'], errors='coerce')
            df = df.dropna(subset=['Packet Loss(%)', 'Availability', 'Latency(msec)'])
        else:
            raise ValueError("Invalid pattern key specified.")
        return df
    except Exception as e:
        print(f"Error during data cleaning: {e}")
        return pd.DataFrame()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Layout
app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": "#f5f5f5", "minHeight": "100vh", "padding": "20px"},
    children=[
        dbc.Row(
            dbc.Col(html.H1("Node Availability Report", className="text-center text-light bg-primary p-4 mb-4 rounded"), width=12)
        ),
        dbc.Row([
            dbc.Col([
                html.Label("Upload File 1:", style={"color": "#000", "fontWeight": "bold"}),
                dcc.Upload(id='upload-file1', children=html.Button('Upload File 1'), multiple=False)
            ], width=6),
            dbc.Col([
                html.Label("Upload File 2:", style={"color": "#000", "fontWeight": "bold"}),
                dcc.Upload(id='upload-file2', children=html.Button('Upload File 2'), multiple=False)
            ], width=6),
        ]),
        dbc.Row(
            dbc.Col(
                dbc.Button("Merge and Display Data", id='merge-button', color="success"), width=12, className="mt-3"
            )
        ),
        dbc.Row(
            dbc.Col(dash_table.DataTable(id='merged-table', style_table={'overflowX': 'auto'}), width=12)
        )
    ]
)

# Helper function to decode uploaded file data
def decode_file(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return io.BytesIO(decoded)
    except Exception as e:
        raise ValueError(f"Error decoding file: {e}")

# Callback to handle file upload and merging
@app.callback(
    Output('merged-table', 'data'),
    [Input('merge-button', 'n_clicks')],
    [State('upload-file1', 'contents'), State('upload-file2', 'contents')]
)
def merge_files(n_clicks, file1_contents, file2_contents):
    if not n_clicks or not file1_contents or not file2_contents:
        return []

    try:
        # Decode and process File 1
        file1 = decode_file(file1_contents)
        df1 = data_clean(file1, "file1_pattern")
        if df1.empty:
            raise ValueError("File 1 processing returned an empty DataFrame.")

        # Decode and process File 2
        file2 = decode_file(file2_contents)
        df2 = data_clean(file2, "file2_pattern")
        if df2.empty:
            raise ValueError("File 2 processing returned an empty DataFrame.")

        # Merge datasets on 'Node Alias'
        if 'Node Alias' not in df1.columns or 'Node Alias' not in df2.columns:
            raise ValueError("Missing 'Node Alias' column in one of the files.")
        merged_df = pd.merge(df1, df2, on='Node Alias', how='inner')

        return merged_df.to_dict('records')
    except Exception as e:
        print(f"Error during file merge: {e}")
        return []

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
