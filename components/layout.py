from dash import dcc, html

def create_viz_data_layout(mne_raw, bands_names):
    return html.Div([
        html.H1("EEG Data Visualization"),
        dcc.RadioItems(
            id="vis-type",
            options=[
                {"label": "Raw Signal", "value": "raw"},
                {"label": "PSD for Specific Band", "value": "specific_band"},
            ],
            value="raw",
            inline=True,
        ),
        html.Br(),
        html.Label("Select Channel:"),
        dcc.Dropdown(
            id="channel-dropdown",
            options=[{"label": "All Channels", "value": "all"}] + 
                    [{"label": ch, "value": ch} for ch in mne_raw.info["ch_names"]],
            value=None,
        ),
        html.Div([
            html.Button("All Channels", id="select-all-channels", n_clicks=0),
            html.Button("Clear Selected Channels", id="clear-channels", n_clicks=0)
        ], style={"margin-top": "10px"}),
        html.Br(),
        html.Div(
            [
                html.Label("Select Frequency Band:"),
                dcc.Dropdown(
                    id="band-dropdown",
                    options=[{"label": name, "value": name} for name in bands_names],
                    value=bands_names[0],
                ),
            ],
            id="band-dropdown-container",  # Add an ID for dynamic visibility
        ),
        html.Br(),
        dcc.Graph(id="eeg-plot"),
    ])
