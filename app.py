# app.py
import dash
import dash_bootstrap_components as dbc
from dash import html
import os

# Import the layout and callbacks
from layout import layout
from callbacks import register_callbacks

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Set the app layout
app.layout = layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
