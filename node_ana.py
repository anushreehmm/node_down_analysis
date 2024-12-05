#!/usr/bin/env python
# coding: utf-8

import os
import configparser
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc
import re
import webview  # Import PyWebview
import threading  # Import threading for running the app in a separate thread
import io
import base64

# Define patterns for file identification
file1_pattern = r"iBUS-Node-EVENT-TAJ_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"
file2_pattern = r"iBUS-Taj_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"

# Function to clean data
def data_clean(file_path, pattern_key):
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
        df = df.dropna(subset=['Alarm Time'])  
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
    return pd.DataFrame()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Remaining code structure remains unchanged...


# Layout
custom_label_style = {
    "color": "#000000",  
    "fontWeight": "bold",
    "marginBottom": "5px"
}

custom_dropdown_style = {
    "backgroundColor": "#ffffff",  
    "color": "#000000",  
    "border": "1px solid #007bff",  
    "borderRadius": "5px",  
    "padding": "8px 12px",  
    "fontSize": "14px",  
    "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"  
}

app.layout = dbc.Container(
    fluid=True,
    style={
        "backgroundColor": "#f5f5f5",
        "minHeight": "100vh",
        "padding": "20px"
    },
    children=[
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Node Availability Report",
                    className="text-center text-light bg-primary p-4 mb-4 rounded",
                    style={"fontSize": "36px", "font-family": "Roboto, sans-serif"}
                ),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Upload File:", style=custom_label_style),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Button('Upload File'),
                            multiple=False
                        )
                    ],
                    width=4
                ),
                dbc.Col(
                    [
                        html.Label("Select Downtime Count:", style=custom_label_style),
                        dcc.Dropdown(
                            id='downtime-dropdown',
                            options=[
                                {'label': '1-3', 'value': '1-3'},
                                {'label': '4-5', 'value': '4-5'},
                                {'label': '>5', 'value': '>5'},
                                {'label': '>10', 'value': '>10'}
                            ],
                            value='1-3',
                            placeholder='Select downtime count criteria',
                            style=custom_dropdown_style
                        )
                    ],
                    width=4
                ),
                dbc.Col(
                    [
                        html.Br(),
                        dbc.Button(
                            "Apply Filters",
                            id='filter-button',
                            color="success"
                        )
                    ],
                    width=4
                )
            ],
            className="mb-4"
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("Filtered Node Availability")),
                        dbc.CardBody(
                            dash_table.DataTable(
                                id='filtered-table',
                                columns=[
                                    {'name': 'Node Alias', 'id': 'Node Alias'},
                                    {'name': 'Availability', 'id': 'Availability'},
                                    {'name': 'Downtime Count', 'id': 'Downtime Count'}
                                ],
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '10px',
                                    'backgroundColor': '#2c2c2c',
                                    'color': 'white'
                                },
                                style_header={
                                    'backgroundColor': '#1a1a1a',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'filter_query': '{Availability} > 99.5',
                                            'column_id': 'Availability'
                                        },
                                        'backgroundColor': '#28a745',
                                        'color': 'white'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Availability} <= 99.5 && {Availability} > 98.5',
                                            'column_id': 'Availability'
                                        },
                                        'backgroundColor': '#ffc107',
                                        'color': 'black'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Availability} <= 98.5',
                                            'column_id': 'Availability'
                                        },
                                        'backgroundColor': '#dc3545',
                                        'color': 'white'
                                    }
                                ]
                            )
                        )
                    ],
                    color="dark",
                    outline=True
                ),
                width=12
            )
        ),
        html.Div(id='filtered-data', style={'display': 'none'})
    ]
)

# Helper function to decode uploaded file data
def decode_file(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return io.BytesIO(decoded)

# Callback for file upload
@app.callback(
    Output('filtered-table', 'data'),
    Output('filtered-data', 'children'),
    Input('filter-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('downtime-dropdown', 'value')
)
def filter_data(n_clicks, contents, downtime_value):
    if n_clicks is None or contents is None:
        return [], ""

    # Decode and read the uploaded file
    file = decode_file(contents)
    df = pd.read_excel(file)

    # Clean the data
    pattern_key = "file1_pattern"  # You can determine the pattern here based on your logic
    cleaned_df = data_clean(file, pattern_key)

    # Downtime Count Filtering
    if downtime_value:
        if downtime_value == '1-3':
            cleaned_df = cleaned_df[cleaned_df['Downtime Count'] <= 3]
        elif downtime_value == '4-5':
            cleaned_df = cleaned_df[(cleaned_df['Downtime Count'] >= 4) & (cleaned_df['Downtime Count'] <= 5)]
        elif downtime_value == '>5':
            cleaned_df = cleaned_df[cleaned_df['Downtime Count'] > 5]
        elif downtime_value == '>10':
            cleaned_df = cleaned_df[cleaned_df['Downtime Count'] > 10]

    # Return the filtered data for the table
    table_data = cleaned_df.to_dict('records')
    return table_data, ""

def run_dash():
    app.run_server(debug=True, use_reloader=False)

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(host="0.0.0.0", port=port, debug=True)
