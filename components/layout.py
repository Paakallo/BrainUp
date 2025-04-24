from dash import dcc, html

def create_viz_data_layout(mne_raw, bands_names):
    return html.Div([
        # Header with Logo
        html.Div(
            [
                html.Img(src="/assets/logo.png", alt="BrainUp Logo", style={"width": "100px", "margin-right": "20px"}),
                html.H1("EEG Data Visualization", style={"display": "inline-block", "vertical-align": "middle", "margin": "0"})
            ],
            style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "20px"}
        ),
        
        # Visualization Type Selection
        dcc.RadioItems(
            id="vis-type",
            options=[
                {"label": "Raw Signal", "value": "raw"},
                {"label": "PSD for Specific Band", "value": "specific_band"},
            ],
            value="raw",
            inline=True,
        ),

        # Upload file
        dcc.Upload(
            id="up-file",
            multiple=False,
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
        ),

        html.Br(),
        
        # Channel Selection
        html.Label("Select Channel:"),
        dcc.Dropdown(
            id="channel-dropdown",
            options=[{"label": "All Channels", "value": "all"}] + 
                    [{"label": ch, "value": ch} for ch in mne_raw.info["ch_names"]],
            value=None,
        ),
        html.Div([
            html.Button("All Channels", id="select-all-channels", n_clicks=0, style={"margin-right": "10px"}),
            html.Button("Clear Selected Channels", id="clear-channels", n_clicks=0)
        ], style={"margin-top": "10px"}),
        html.Br(),
        
        # Band Selection
        html.Div(
            [
                html.Label("Select Frequency Band:"),
                dcc.Dropdown(
                    id="band-dropdown",
                    options=[{"label": name, "value": name} for name in bands_names],
                    value=bands_names[0],
                ),
            ],
            id="band-dropdown-container",  
        ),
        html.Br(),
        
        # Filter Selection
        html.Div(
            [
                html.Label("Filter Frequency Range:"),
                dcc.RadioItems(
                    id="filter-frequency",
                    options=[
                        {"label": "No Filter", "value": "none"},
                        {"label": "Low Frequency (< 1 Hz)", "value": "low"},
                        {"label": "High Frequency (> 25 Hz)", "value": "high"},
                        {"label": "Custom Range", "value": "custom"}
                    ],
                    value="none",
                    inline=True,
                ),
                html.Div(
                    [
                        html.Label("Custom Frequency Range:"),
                        dcc.RangeSlider(
                            id="custom-frequency-slider",
                            min=0,
                            max=50,  # Scale updated to 0–50 Hz
                            step=0.5,
                            marks={i: f"{i} Hz" for i in range(0, 51, 5)},
                            value=[5, 10],  
                        ),
                    ],
                    id="custom-frequency-container",
                    style={"display": "none"},  
                ),
            ],
            id="filter-selection-container",  
        ),
        html.Br(),
        
        dcc.Graph(id="eeg-plot"),
    ])
