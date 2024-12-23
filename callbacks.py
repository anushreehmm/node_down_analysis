import pandas as pd
from dash.dependencies import Input, Output, State

# Import the functions from the process_data module
from process_data import filter_data

# Global data frames for processing
file1_df = pd.DataFrame()
file2_df = pd.DataFrame()
merged_df = pd.DataFrame()


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
    def filter_data_callback(n_clicks, start_date, end_date, downtime_value):
        if n_clicks is None or file1_df.empty or file2_df.empty:
            return []

        global merged_df
        merged_df = pd.merge(file1_df, file2_df, on="Node Alias", how="inner")

        # Apply filters to the merged data
        filtered_df = filter_data(
            merged_df,
            date_range=(start_date, end_date) if start_date and end_date else None,
            downtime_criteria=downtime_value
        )
        return filtered_df.to_dict('records')
