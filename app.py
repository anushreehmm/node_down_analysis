# app.py
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
from callbacks import register_callbacks  # Callback registration

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Set app layout
app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": "#f5f5f5", "minHeight": "100vh", "padding": "20px"},
    children=[
        html.H1("Node Availability Report", className="text-center text-light bg-primary p-4 mb-4 rounded"),
        # Add file upload and filtering UI components
        # Same layout code as before
    ]
)

# Register callbacks to the app
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
