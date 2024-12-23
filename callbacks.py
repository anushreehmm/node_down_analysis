# callbacks.py

from dash import Input, Output, State, callback, ctx
from process_data import filter_data
import pandas as pd

# Placeholder DataFrame
df_placeholder = pd.DataFrame({
    "Node Alias": ["Node1", "Node2", "Node3"],
    "Availability": [98, 92, 88],
    "Downtime Count": [2, 5, 12],
    "Date": pd.to_datetime(["2024-12-01", "2024-12-05", "2024-12-10"])
})

def register_callbacks(app):
    @app.callback(
        Output('filtered-table', 'data'),
        [
            Input('filter-button', 'n_clicks')
        ],
        [
            State('date-range', 'start_date'),
            State('date-range', 'end_date'),
            State('downtime-dropdown', 'value')
        ]
    )
    def update_table(n_clicks, start_date, end_date, downtime_value):
        if not ctx.triggered_id == "filter-button":
            # No filtering applied yet
            return df_placeholder.to_dict('records')
        
        # Process filters
        date_range = (start_date, end_date) if start_date and end_date else None
        filtered_data = filter_data(df_placeholder, date_range=date_range, downtime_criteria=downtime_value)
        return filtered_data.to_dict('records')
