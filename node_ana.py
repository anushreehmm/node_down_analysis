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

# Define patterns for file identification
file1_pattern = r"iBUS-Node-EVENT-TAJ_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"
file2_pattern = r"iBUS-Taj_\d{1,2}(st|nd|rd|th) [A-Za-z]{3} \d{4} \d{2}_\d{2}_\d{2}\.xlsx"

# Define global variables for date limits
min_date = pd.Timestamp("2022-01-01")  # Replace with your data's minimum date
max_date = pd.Timestamp.now()          # Replace with your data's maximum date

# Custom styles
custom_label_style = {"color": "#000", "fontWeight": "bold"}
custom_dropdown_style = {"width": "100%"}

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
        # Title Section
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
        # Filters Section
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Date Range:", style=custom_label_style),
                        dcc.DatePickerRange(
                            id='date-range',
                            start_date=None,
                            end_date=None,
                            min_date_allowed=min_date.date(),
                            max_date_allowed=max_date.date(),
                            display_format='YYYY-MM-DD',
                            style=custom_dropdown_style
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
                        dbc.Button("Apply Filters", id='filter-button', color="success")
                    ],
                    width=4
                )
            ],
            className="mb-4"
        ),
        # Data Table Section
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
                                }
                            )
                        )
                    ],
                    color="dark",
                    outline=True
                ),
                width=12
            )
        ),
        # Hidden Div for Storing Data
        html.Div(id='filtered-data', style={'display': 'none'})
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

# Callback for filtering
@app.callback(
    Output('filtered-table', 'data'),
    Output('filtered-data', 'children'),
    Input('filter-button', 'n_clicks'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('downtime-dropdown', 'value')
)
def filter_data(n_clicks, start_date, end_date, downtime_value):
    if n_clicks is None:
        return [], ""

    filtered_df = merged_df.copy()

    # Date filtering
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['Alarm Time'] >= pd.to_datetime(start_date)) & 
            (filtered_df['Alarm Time'] <= pd.to_datetime(end_date))
        ]

    # Downtime Count Filtering
    if downtime_value:
        if downtime_value == '1-3':
            filtered_df = filtered_df[filtered_df['Downtime Count'] <= 3]
        elif downtime_value == '4-5':
            filtered_df = filtered_df[(filtered_df['Downtime Count'] >= 4) & (filtered_df['Downtime Count'] <= 5)]
        elif downtime_value == '>5':
            filtered_df = filtered_df[filtered_df['Downtime Count'] > 5]
        elif downtime_value == '>10':
            filtered_df = filtered_df[filtered_df['Downtime Count'] > 10]

    table_data = filtered_df.to_dict('records')
    return table_data, ""

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
