from dash.dependencies import Input, Output, State
import pandas as pd
import io
import base64

def register_callbacks(app):
    @app.callback(
        Output('file1-status', 'children'),
        Input('upload-file1', 'contents')
    )
    def handle_file1_upload(contents):
        if contents:
            return "File 1 Uploaded Successfully"
        return "No file uploaded yet"

    @app.callback(
        Output('file2-status', 'children'),
        Input('upload-file2', 'contents')
    )
    def handle_file2_upload(contents):
        if contents:
            return "File 2 Uploaded Successfully"
        return "No file uploaded yet"

    @app.callback(
        Output('filtered-table', 'data'),
        Input('filter-button', 'n_clicks'),
        State('upload-file1', 'contents'),
        State('upload-file2', 'contents')
    )
    def filter_data(n_clicks, file1_contents, file2_contents):
        if not n_clicks or not file1_contents or not file2_contents:
            return []

        # Decode files
        file1 = decode_file(file1_contents)
        file2 = decode_file(file2_contents)

        # Example filter: Intersection of columns 'A' in both datasets
        filtered_data = pd.merge(file1, file2, on='A', how='inner')
        return filtered_data.to_dict('records')

def decode_file(contents):
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
