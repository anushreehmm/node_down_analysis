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
file1_df = pd.DataFrame()  # For File 1 (Node Events)
file2_df = pd.DataFrame()  # For File 2 (Taj Data)
merged_df = pd.DataFrame()  # Combined dataframe

# Function to clean and process data based on structure
def data_clean_auto(file_path):
    """
    Automatically detects the type of file based on its columns and processes it.
    """
    try:
        df = pd.read_excel(file_path, skiprows=5)

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
        elif 'Availability(%)' in df.columns and 'Latency(msec)' in df.columns:  # File 2 (Taj Data)
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
                html.Label("Upload Node Events File (File 1):", style={"fontWeight": "bold"}),
                dcc.Upload(id='upload-file1', children=html.Button('Upload File 1'), multiple=False),
                html.Div(id='file1-status', style={"color": "green", "fontWeight": "bold"})
            ], width=6),
            dbc.Col([
                html.Label("Upload Taj Data File (File 2):", style={"fontWeight": "bold"}),
                dcc.Upload(id='upload-file2', children=html.Button('Upload File 2'), multiple=False),
                html.Div(id='file2-status', style={"color": "green", "fontWeight": "bold"})
            ], width=6)
        ], className="mb-4"),
        # Data Table Section
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='merged-table',
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
    Output('file1-status', 'children'),
    Input('upload-file1', 'contents'),
    State('upload-file1', 'filename')
)
def handle_file1_upload(contents, filename):
    global file1_df
    if contents is None:
        return ""

    try:
        file_data = decode_file(contents)
        df, file_type = data_clean_auto(file_data)

        if file_type != "file1":
            return f"Error: Uploaded file is not Node Events data."
        
        file1_df = df
        return f"File 1 '{filename}' uploaded successfully."
    except Exception as e:
        return f"Error: {e}"


@app.callback(
    Output('file2-status', 'children'),
    Input('upload-file2', 'contents'),
    State('upload-file2', 'filename')
)
def handle_file2_upload(contents, filename):
    global file2_df
    if contents is None:
        return ""

    try:
        file_data = decode_file(contents)
        df, file_type = data_clean_auto(file_data)

        if file_type != "file2":
            return f"Error: Uploaded file is not Taj Data."
        
        file2_df = df
        return f"File 2 '{filename}' uploaded successfully."
    except Exception as e:
        return f"Error: {e}"


@app.callback(
    Output('merged-table', 'columns'),
    Output('merged-table', 'data'),
    Input('file1-status', 'children'),
    Input('file2-status', 'children')
)
def update_merged_table(file1_status, file2_status):
    global file1_df, file2_df, merged_df
    if file1_df.empty or file2_df.empty:
        return [], []

    # Merge based on Node Alias
    try:
        merged_df = pd.merge(file1_df, file2_df, on="Node Alias", how="inner")
        columns = [{"name": col, "id": col} for col in merged_df.columns]
        data = merged_df.to_dict("records")
        return columns, data
    except Exception as e:
        return [], []


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
