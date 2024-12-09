#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc
import io
import base64

# Define patterns for file identification
file1_pattern = r"iBUS-Node-EVENT-TAJ_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"
file2_pattern = r"iBUS-Taj_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"

# Function to clean data
def data_clean(file_path, pattern_key):
    try:
        if pattern_key == "file1_pattern":
            df = pd.read_excel(file_path, skiprows=5)
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
            return df
        elif pattern_key == "file2_pattern":
            df = pd.read_excel(file_path)
            df = df.drop([0, 1, 2, 3, 4], axis=0).reset_index(drop=True)
            df = df.drop(columns=['Unnamed: 2', 'Unnamed: 3'], errors='ignore')
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
                html.Label("Upload File:", style={"color": "#000", "fontWeight": "bold"}),
                dcc.Upload(id='upload-data', children=html.Button('Upload File'), multiple=False)
            ], width=4),
            dbc.Col([
                html.Label("Select Downtime Count:", style={"color": "#000", "fontWeight": "bold"}),
                dcc.Dropdown(
                    id='downtime-dropdown',
                    options=[
                        {'label': '1-3', 'value': '1-3'},
                        {'label': '4-5', 'value': '4-5'},
                        {'label': '>5', 'value': '>5'}
                    ],
                    placeholder='Select downtime count criteria',
                )
            ], width=4),
            dbc.Col(
                dbc.Button("Apply Filters", id='filter-button', color="success"), width=4
            )
        ]),
        dbc.Row(
            dbc.Col(dash_table.DataTable(id='filtered-table', style_table={'overflowX': 'auto'}), width=12)
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
        print(f"Error decoding file: {e}")
        return None

# Callback for file upload
@app.callback(
    [Output('filtered-table', 'data')],
    [Input('filter-button', 'n_clicks')],
    [State('upload-data', 'contents'), State('downtime-dropdown', 'value')]
)
def filter_data(n_clicks, contents, downtime_value):
    if not n_clicks or not contents:
        return [[]]

    file = decode_file(contents)
    if file is None:
        return [[]]

    # Determine pattern key
    pattern_key = "file1_pattern" if re.search(file1_pattern, contents) else "file2_pattern"
    cleaned_df = data_clean(file, pattern_key)

    # Apply filters
    if downtime_value:
        if downtime_value == '1-3':
            cleaned_df = cleaned_df[cleaned_df['Downtime Count'] <= 3]
        elif downtime_value == '4-5':
            cleaned_df = cleaned_df[(cleaned_df['Downtime Count'] >= 4) & (cleaned_df['Downtime Count'] <= 5)]
        elif downtime_value == '>5':
            cleaned_df = cleaned_df[cleaned_df['Downtime Count'] > 5]

    return [cleaned_df.to_dict('records')]

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8050))  # Use PORT environment variable or default to 8050
    app.run_server(debug=False, host="0.0.0.0", port=port)
