from dash import dcc, html
from components.data_acc import channels_names  # Import channels_names

number_of_channels = 0  # Default value; will be updated dynamically

def create_header():
    return html.Div(
        [
            html.Img(src="/assets/logo.png", alt="BrainUp Logo", id="header-logo"),
            html.H1("EEG Data Visualization", id="header-label"),
        ],
        id="header-container",
    )

def create_upload_section():
    return dcc.Upload(
        id="upload-file-zone",
        multiple=False,
        children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
    )

def create_channel_assignment_row(channel_number):
    return html.Div(
        [
            html.H3(f"Channel {channel_number + 1}", id=f"channel-assignment-label-{channel_number}"),
            dcc.Dropdown(
                id=f"channel-assignment-dropdown-{channel_number}",
                options=[{"label": ch, "value": ch} for ch in channels_names],  # Populate dropdown with channels_names
                placeholder=f"Assign name to Channel {channel_number + 1}",
            )
        ],
        id=f"channel-assignment-row-container-{channel_number}",
    )

def create_channel_name_assignment():
    return html.Div(
        [
            html.Div(
                [
                    html.Img(src="/assets/21_electrodes.svg", alt="21 Electrodes (10/20)", id="channels-image"),
                ],
                id="channels-image-container",
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
                ],
            ),
        ],
        id="channels-name-assignment-container",
    )

def create_main_visualization_container(mne_raw, bands_names):
    return html.Div(
        [
            dcc.RadioItems(
                id="vis-type",
                options=[
                    {"label": "Raw Signal", "value": "raw"},
                    {"label": "PSD for Specific Band", "value": "specific_band"},
                ],
                value="raw",
                inline=True,
            ),
            html.Label("Select Channel:"),
            dcc.Dropdown(
                id="channel-dropdown",
                options=[{"label": "All Channels", "value": "all"}] +
                        [{"label": ch, "value": ch} for ch in mne_raw.info["ch_names"]],
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
                        value=bands_names[0],
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
        ],
        id="main-container",
        style={"display": "none"},
    )

def create_viz_data_layout(mne_raw, bands_names, number_of_channels):
    return html.Div([
        dcc.Store(id="name-channels", data=False),
        dcc.Store(id="number-of-channels", data=number_of_channels),
        create_header(),
        create_upload_section(),
        html.Br(),
        html.Br(),
        create_channel_name_assignment(),
        create_main_visualization_container(mne_raw, bands_names),
    ])
