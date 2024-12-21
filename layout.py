from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container(
        fluid=True,
        style={"backgroundColor": "#f5f5f5", "minHeight": "100vh", "padding": "20px"},
        children=[
            dbc.Row(
                dbc.Col(
                    html.H1(
                        "Node Availability Report",
                        className="text-center text-light bg-primary p-4 mb-4 rounded",
                        style={"fontSize": "36px", "font-family": "Roboto, sans-serif"}
                    )
                )
            ),
            dbc.Row([
                dbc.Col([
                    html.Label("Upload Node File:", style={"color": "#000", "fontWeight": "bold"}),
                    dcc.Upload(
                        id='upload-file1',
                        children=html.Button('Upload Node File'),
                        multiple=False
                    ),
                    html.Div(id='file1-status', style={"color": "#666"})
                ], width=6),
                dbc.Col([
                    html.Label("Upload Second File:", style={"color": "#000", "fontWeight": "bold"}),
                    dcc.Upload(
                        id='upload-file2',
                        children=html.Button('Upload File 2'),
                        multiple=False
                    ),
                    html.Div(id='file2-status', style={"color": "#666"})
                ], width=6),
            ], className="mb-4"),
            dbc.Row(
                dbc.Col(
                    html.Button("Filter Data", id='filter-button', className="btn btn-primary")
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Loading(
                        id="loading-icon",
                        type="circle",
                        children=dash_table.DataTable(id='filtered-table')
                    )
                )
            )
        ]
    )
