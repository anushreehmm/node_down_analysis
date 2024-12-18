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

# Global variables for processed data
merged_df = pd.DataFrame()

# Custom styles
custom_label_style = {"color": "#000", "fontWeight": "bold"}
custom_dropdown_style = {"width": "100%"}
success_message_style = {"color": "green", "fontWeight": "bold"}
error_message_style = {"color": "red", "fontWeight": "bold"}

# Function to clean and process data based on structure
def data_clean_auto(file_path):
    """
    Automatically detects the type of file based on its columns and processes it.
    """
    try:
        df = pd.read_excel(file_path)

        # Check the structure and process the file accordingly
        if 'Event' in df.columns and 'Alarm Time' in df.columns:  # File 1 (Node Events)
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
            file_type = "file1"
        elif 'Availability' in df.columns and 'Latency(msec)' in df.columns:  # File 2 (Taj Data)
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
            file_type = "file2"
        else:
            raise ValueError("Unrecognized file structure. Please check the file.")

        return df, file_type

    except Exception as e:
        print(f"Error during data cleaning: {e}")
        return pd.DataFrame(), None


# Helper function to decode uploaded file data
def decode_file(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return io.BytesIO(decoded)
    except Exception as e:
        raise ValueError(f"Error decoding file: {e}")


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
        # File Upload Section
        dbc.Row([
            dbc.Col([
                html.Label("Upload File:", style=custom_label_style),
                dcc.Upload(id='upload-file', children=html.Button('Upload File'), multiple=True),
                html.Div(id='file-status', style=success_message_style)
            ], width=12)
        ], className="mb-4"),
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
                            value=None,
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
                dash_table.DataTable(
                    id='filtered-table',
                    columns=[],
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
                ),
                width=12
            )
        )
    ]
)


# Callbacks
@app.callback(
    Output('file-status', 'children'),
    Output('filtered-table', 'columns'),
    Input('upload-file', 'contents'),
    State('upload-file', 'filename')
)
def handle_file_upload(contents, filenames):
    if contents is None:
        return "", []

    global merged_df
    columns = []
    messages = []
    try:
        for content, filename in zip(contents, filenames):
            file_data = decode_file(content)
            df, file_type = data_clean_auto(file_data)

            if file_type == "file1":
                merged_df = df if merged_df.empty else pd.concat([merged_df, df], ignore_index=True)
                columns = [{'name': col, 'id': col} for col in df.columns]
                messages.append(f"File '{filename}' uploaded successfully (Node Events).")
            elif file_type == "file2":
                merged_df = df if merged_df.empty else pd.merge(merged_df, df, on="Node Alias", how="inner")
                columns = [{'name': col, 'id': col} for col in df.columns]
                messages.append(f"File '{filename}' uploaded successfully (Taj Data).")

        return " | ".join(messages), columns
    except Exception as e:
        return f"Error: {e}", []


@app.callback(
    Output('filtered-table', 'data'),
    Input('filter-button', 'n_clicks'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('downtime-dropdown', 'value')
)
def filter_data(n_clicks, start_date, end_date, downtime_value):
    if n_clicks is None or merged_df.empty:
        return []

    filtered_df = merged_df.copy()

    # Apply filters
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


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
