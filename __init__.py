# app/__init__.py

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_table
from app.callbacks import handle_file1_upload, handle_file2_upload, filter_data

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Layout
app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": "#f5f5f5", "minHeight": "100vh", "padding": "20px"},
    children=[
        # Title Section and other layout components here as you currently have it
    ]
)

# Callbacks
app.callback(
    Output('file1-status', 'children'),
    Input('upload-file1', 'contents')
)(handle_file1_upload)

app.callback(
    Output('file2-status', 'children'),
    Input('upload-file2', 'contents')
)(handle_file2_upload)

app.callback(
    Output('filtered-table', 'data'),
    Input('filter-button', 'n_clicks'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('downtime-dropdown', 'value')
)(filter_data)

