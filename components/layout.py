from dash import dcc, html

def create_viz_data_layout(mne_raw, bands_names):
    return html.Div([
        # upload name channels
        dcc.Store(id='name-channels', data=False),  

        # Header with Logo
        html.Div(
            [
                html.Img(src="/assets/logo.png", alt="BrainUp Logo", style={"width": "100px", "margin-right": "20px"}),
                html.H1("EEG Data Visualization", style={"display": "inline-block", "vertical-align": "middle", "margin": "0"})
            ],
            style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "20px"}
        ),

        # Upload file
        dcc.Upload(
            id="upload-file-zone",
            multiple=False,
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
        ),

        html.Br(),
        html.Br(),

        
        html.Div([
            html.Button("Show UID", id="show_u_id"),
            html.H4("User ID:", id="h4_id", style={"display": "none"}),
            dcc.Textarea(
                value='',  # Default value
                id='user-id',
                style={'flex': '1', "display": "none"},
                readOnly=True  # Optional: prevent editing
            ),
            dcc.Input(
                id='uid-input',
                type='text',
                placeholder='Type something and press Enter',
                n_submit=0  # Tracks Enter key presses
            )
        ], style={
        'display': 'flex',
        'alignItems': 'center',
        'gap': '10px',  # optional: for consistent spacing
        }),

        # Main Visualization a data manipulation container
        # This container will be hidden until a file is uploaded
        html.Div(
            [    
                # Visualization Type Selection
                dcc.RadioItems(
                    id="vis-type",
                    options=[
                        {"label": "Raw Signal", "value": "raw"},
                        {"label": "PSD for Specific Band", "value": "specific_band"},
                        {"label": "Topo", "value":"topo"},
                    ],
                    value="raw",
                    inline=True,
                ),
                
                # Channel Selection
                html.Label("Select Channel:"),
                dcc.Dropdown(
                    id="channel-dropdown",
                    options=[{"label": "All Channels", "value": "all"}] + 
                            [{"label": ch, "value": ch} for ch in mne_raw.info["ch_names"]],
                    value=None,
                ),
                
                # Channel Selection Buttons
                html.Div(
                    [
                        html.Button("All Channels", id="select-all-channels", n_clicks=0, style={"margin-right": "10px"}),
                        html.Button("Clear Selected Channels", id="clear-channels", n_clicks=0)
                    ], 
                    id="channel-buttons-container",
                ),
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
                    style={"display": "none"},  
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
                
                dcc.Graph(id="eeg-plot", style={"display": "none"}),

                # Download file
                html.Button("Download Power Band", id="download-button"),
                dcc.Download(id="download-dataframe-csv"),
            
                html.Img(id="topo-img", style={"display": "none"}),
            ],
            id="main-container",
            style={"display": "none"},  
        ),
    ])
