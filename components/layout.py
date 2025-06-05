from dash import dcc, html

number_of_channels = 0  

def create_header():
    return html.Div(
        [
            html.Img(src="/assets/logo.png", alt="BrainUp Logo", id="header-logo"),
            html.H1("EEG Data Visualization", id="header-label"),
        ],
        id="header-container",
    )

def create_uid_section():
    return html.Div([
            html.Button("Show UID", id="show_u_id"),
            html.H4("User ID:", id="h4_id", style={"display": "none"}),
            dcc.Textarea(
                value='',  # Default value
                id='user-id',
                style={"display": "none"},
                readOnly=True  # Optional: prevent editing
            ),
            dcc.Input(
                id='uid-input',
                type='text',
                placeholder='Enter your user ID',
                n_submit=0  # Tracks Enter key presses
            ),
            dcc.Dropdown(
                id='select-file',
                options=[
                    {'label': 'Option 1', 'value': 'opt1'},
                    {'label': 'Option 2', 'value': 'opt2'},
                    {'label': 'Option 3', 'value': 'opt3'}
                ],
                value='opt1',  # default value
                clearable=False,
                style={"display": "none"}  # Initially hidden
                )
        ], style={
        'display': 'flex',
        # 'alignItems': 'center',
        # 'gap': '10px',  # optional: for consistent spacing
        }) 

def create_upload_section():
    return dcc.Upload(
        id="upload-file-zone",
        multiple=False,
        children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
    )

def create_channel_assignment_row(channel_number, channels_names, value=None):
    return html.Div(
        [
            html.H3(f"Channel {channel_number + 1}", id=f"channel-assignment-label-{channel_number}"),
            dcc.Dropdown(
                id=f"channel-assignment-dropdown-{channel_number}",
                options=[{"label": ch, "value": ch} for ch in channels_names],
                placeholder=f"Assign name to Channel {channel_number + 1}",
                value=value
            )
        ]
    )

def create_electrode_navigation():
    """Create the electrode navigation component with left/right arrows."""
    return html.Div(
        className="electrode-navigation-container",
        children=[
            # Left arrow
            html.Button(
                "←",
                id="prev-electrode-view",
                className="electrode-nav-button prev-electrode-button",
            ),
            
            # Electrode image
            html.Img(
                id="electrode-image",
                src="/assets/21_electrodes.svg", 
                alt="Electrodes", 
                className="electrode-image",
            ),
            
            # Right arrow
            html.Button(
                "→",
                id="next-electrode-view",
                className="electrode-nav-button next-electrode-button",
            ),
        ]
    )

def create_channel_name_assignment():
    return html.Div(
        [
            html.Div(
                [
                    create_electrode_navigation(),
                ],
                id="channels-image-container"
            ),
            html.Div(
                [
                    html.H2("Assign Channel Names", id="assign-channel-label"),
                    html.Div(
                        [
                            html.Button(
                                "Assign Automatically",
                                id="assign-channels-automaticlly-button",
                                n_clicks=0,
                                className="assign-button"
                            ),
                            html.Button(
                                "Assign Manually",
                                id="assign-channels-manually-button",
                                n_clicks=0,
                                className="assign-button"
                            ),
                        ],
                        className="assign-button-container"
                    ),
                    html.Div(
                        id="channel-assignment-container",
                        children=[],  # Placeholder for dynamic rows
                        style={"display": "none"},
                    ),
                    html.Button(
                        "Confirm Assignments",
                        id="assign-channels-confirm-button",
                        n_clicks=0,
                        className="assign-button",
                        style={"display": "none"},
                    ),
                ],
                id="channels-all-rows-assignment-container",
            ),
        ],
        id="channels-name-assignment-container",
        style={"display": "none"},
    )

def create_main_visualization_container(mne_raw, bands_names):
    from app import assigned_channels_names  # Import the global list
    return html.Div(
        [
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
            html.Label("Select Channel:"),
            dcc.Dropdown(
                id="channel-dropdown",
                options=[{"label": "All Channels", "value": "all"}] +
                        [{"label": ch, "value": ch} for ch in assigned_channels_names],
                value=None,
            ),
            html.Div(
                [
                    html.Button("All Channels", id="select-all-channels", n_clicks=0, style={"margin-right": "10px"}),
                    html.Button("Clear Selected Channels", id="clear-channels", n_clicks=0)
                ],
                id="channel-buttons-container",
            ),
            html.Br(),
            html.Div(
                [
                    html.Label("Select Frequency Band:"),
                    dcc.Dropdown(
                        id="band-dropdown",
                        options=[{"label": name, "value": name} for name in bands_names],
                        value='Delta',
                    ),
                ],
                id="band-dropdown-container",
                style={"display": "none"},
            ),
            html.Br(),
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
                                max=50,
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
            dcc.Graph(id="eeg-plot"),
            html.Button("Download Power Band", id="download-button"),
            dcc.Download(id="download-dataframe-csv"),

            html.Img(id="topo-img", style={"display": "none"})
        ],
        id="main-container",
        style={"display": "none"},
    )

def create_viz_data_layout(mne_raw, bands_names, number_of_channels):
    return html.Div([
        dcc.Store(id="name-channels", data=False),
        dcc.Store(id="number-of-channels", data=number_of_channels),
        dcc.Store(id="electrode-view-store", data={"type": "21_electrodes"}),  
        dcc.Store(id="channels-names-store", data=[]),  # <-- Add this line
        create_header(),
        create_uid_section(),
        create_upload_section(),
        html.Br(),
        html.Br(),
        create_channel_name_assignment(),
        create_main_visualization_container(mne_raw, bands_names),
    ])
