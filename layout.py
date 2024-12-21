from dash import dcc, html
import dash_table
import dash_bootstrap_components as dbc

# Custom styles
custom_label_style = {"color": "#000", "fontWeight": "bold"}
custom_dropdown_style = {"width": "100%"}
success_message_style = {"color": "green", "fontWeight": "bold"}

# App layout
layout = dbc.Container(
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
                html.Label("Upload Node File:", style=custom_label_style),
                dcc.Upload(id='upload-file1', children=html.Button('Upload Node File'), multiple=False),
                html.Div(id='file1-status', style=success_message_style)
            ], width=6),
            dbc.Col([
                html.Label("Upload Second File:", style=custom_label_style),
                dcc.Upload(id='upload-file2', children=html.Button('Upload File 2'), multiple=False),
                html.Div(id='file2-status', style=success_message_style)
            ], width=6),
        ], className="mb-4"),
        # Filters Section
        dbc.Row([
            dbc.Col([
                html.Label("Select Date Range:", style=custom_label_style),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=None,
                    end_date=None,
                    display_format='YYYY-MM-DD',
                    style=custom_dropdown_style
                )
            ], width=4),
            dbc.Col([
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
            ], width=4),
            dbc.Col([
                html.Br(),
                dbc.Button("Apply Filters", id='filter-button', color="success")
            ], width=4)
        ], className="mb-4"),
        # Data Table Section
        dbc.Row(
            dbc.Col(
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
                            'if': {'filter_query': '{Availability} >= 97', 'column_id': 'Availability'},
                            'backgroundColor': '#28a745',
                            'color': 'white'
                        },
                        {
                            'if': {'filter_query': '{Availability} >= 90 && {Availability} < 97', 'column_id': 'Availability'},
                            'backgroundColor': '#ffc107',
                            'color': 'black'
                        },
                        {
                            'if': {'filter_query': '{Availability} < 90', 'column_id': 'Availability'},
                            'backgroundColor': '#dc3545',
                            'color': 'white'
                        }
                    ]
                ),
                width=12
            )
        ),
    ]
)
