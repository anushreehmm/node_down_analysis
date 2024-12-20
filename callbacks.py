# callbacks.py
from dash.dependencies import Input, Output, State
from data_processing import process_file, decode_file  # Import from data_processing.py
import pandas as pd

# Global data variables
file1_df = None
file2_df = None
merged_df = None

def register_callbacks(app):

    @app.callback(
        Output('file1-status', 'children'),
        Input('upload-file1', 'contents')
    )
    def handle_file1_upload(contents):
        if contents is None:
            return ""
        try:
            file1 = decode_file(contents)
            global file1_df
            file1_df = process_file(file1, "file1")
            return "File 1 uploaded and processed successfully!"
        except Exception as e:
            return f"Error: {e}"

    @app.callback(
        Output('file2-status', 'children'),
        Input('upload-file2', 'contents')
    )
    def handle_file2_upload(contents):
        if contents is None:
            return ""
        try:
            file2 = decode_file(contents)
            global file2_df
            file2_df = process_file(file2, "file2")
            return "File 2 uploaded and processed successfully!"
        except Exception as e:
            return f"Error: {e}"

    @app.callback(
        Output('filtered-table', 'data'),
        Input('filter-button', 'n_clicks'),
        State('date-range', 'start_date'),
        State('date-range', 'end_date'),
        State('downtime-dropdown', 'value')
    )
    def filter_data(n_clicks, start_date, end_date, downtime_value):
        if n_clicks is None or file1_df.empty or file2_df.empty:
            return []

        global merged_df
        merged_df = pd.merge(file1_df, file2_df, on="Node Alias", how="inner")

        filtered_df = merged_df.copy()

        if start_date and end_date:
            filtered_df = filtered_df[
                (filtered_df['Alarm Time'] >= pd.to_datetime(start_date)) & 
                (filtered_df['Alarm Time'] <= pd.to_datetime(end_date))
            ]

        if downtime_value:
            # Add filtering logic based on downtime
            pass

        return filtered_df.to_dict('records')
