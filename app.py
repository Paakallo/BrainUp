import os
import mne
import numpy as np
from components.helpers import prepare_dataset
import dash
from dash import Input, Output, State, html, dcc
import plotly.graph_objects as go
from components.data_acc import calculate_psd, construct_mne_object, extract_all_power_bands, get_file, bands_names, bands_freq, pd2mne, plot_raw_channels, plot_power_band, power_band2csv, channels_names_21, channels_names_70
from components.helpers import filter_data
from components.layout import create_viz_data_layout

if not os.path.exists("data"):
        prepare_dataset()

app = dash.Dash(__name__)
app.title = "BrainUp"  
app._favicon = "logo.png"
server = app.server


# Define global constants (in my opinion temporary solution)
mne_raw = construct_mne_object()
power_bands = []
number_of_channels = 0
channels_names = channels_names_21 # Default channel names for 21 electrodes

app.layout = html.Div([
    create_viz_data_layout(mne_raw, bands_names, number_of_channels),
    dcc.Store(id="channels-names-store", data=channels_names),  # Add this line
])

# Callback for uploading the file
@app.callback(
    Output("name-channels", "data"),
    Output("number-of-channels", "data"),
    Output("vis-type", "value"),
    Output("band-dropdown", "value"),
    Output("filter-frequency", "value"),
    Output("custom-frequency-slider", "value"),
    Input("upload-file-zone", "contents"),
    Input("upload-file-zone", "filename"),
    prevent_initial_call=True
)
def upload_file(file, filename):
    if filename is None:
        print("No file uploaded")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    raw_data, channels_info = get_file(file, filename)
    print(f"File uploaded: {filename}")
    
    global mne_raw, power_bands
    mne_raw = pd2mne(raw_data)
    power_bands = extract_all_power_bands(calculate_psd(raw_data))
    number_of_channels = len(channels_info)
    
    return (
        channels_info,
        number_of_channels,
        "raw",
        None,
        None,
        None,
    )

# Callback for updating the layout to show channel name asigment container when file is uploaded
@app.callback(
        Output("channels-name-assignment-container", "style"),
        Input("number-of-channels", "data")
)
def channel_assigment_visibility(number_of_channels):
    if number_of_channels > 0:
        return {"display": "block"}
    else:
        return {"display": "none"}

# Callback to handle electrode view navigation
@app.callback(
    Output("electrode-view-store", "data"),
    Output("electrode-image", "src"),
    Output("channel-assignment-container", "style", allow_duplicate=True),
    Output("channels-names-store", "data"),
    Input("prev-electrode-view", "n_clicks"),
    Input("next-electrode-view", "n_clicks"),
    State("electrode-view-store", "data"),
    prevent_initial_call=True
)
def update_electrode_view(prev_clicks, next_clicks, current_view):
    global channels_names

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Get current view type or default to 21_electrodes
    view_type = current_view.get("type", "21_electrodes") if current_view else "21_electrodes"
    
    # Toggle between views
    if button_id == "prev-electrode-view" or button_id == "next-electrode-view":
        if view_type == "21_electrodes":
            new_view = "70_electrodes"
            channels_names = channels_names_70  # Update channel names for 70 electrodes
        else:
            new_view = "21_electrodes"
            channels_names = channels_names_21
            
        # Return the new state and image source
        return {"type": new_view}, f"assets/{new_view}.svg", {"display": "none"}, channels_names
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback for updating channel assignment rows based on the number of channels and channel names
@app.callback(
    Output("channel-assignment-container", "children", allow_duplicate=True),
    Input("number-of-channels", "data"),
    Input("channels-names-store", "data"),  # Add this input
    prevent_initial_call=True,
)
def update_channel_assigment_children(callback_number_of_channels, current_channels_names):
    global number_of_channels, channels_names
    number_of_channels = callback_number_of_channels
    channels_names = current_channels_names  # Update global for consistency
    print(f"Updating channel assignment for {number_of_channels} channels. Names: {'21' if channels_names == channels_names_21 else '70'}")
    from components.layout import create_channel_assignment_row
    return [
        create_channel_assignment_row(i, channels_names) for i in range(number_of_channels)
    ]

# Callback for updating channel dropdown options
@app.callback(
    Output("channel-dropdown", "options"),
    Input("vis-type", "value"),
    Input("name-channels", "data"),
    Input("channels-names-store", "data"),  # Add this input
    prevent_initial_call=True
)
def update_channel_dropdown_options(vis_type, name_channels, current_channels_names):
    # prevent updating channels without uploaded file
    if not name_channels:
        return dash.no_update
    # Use the current channel names from the store
    return [{"label": ch, "value": ch} for ch in current_channels_names]

# Reset channel-dropdown value when channel names change
@app.callback(
    Output("channel-dropdown", "value", allow_duplicate=True),
    Input("channels-names-store", "data"),
    prevent_initial_call=True
)
def reset_channel_dropdown_value(current_channels_names):
    return []  # or None if you want no selection

# Callback for updating the layout to allow multiple channel selection
@app.callback(
    Output("channel-dropdown", "multi"),
    Input("vis-type", "value"),
    prevent_initial_call=True
)
def toggle_channel_multi_select(vis_type):
    return True  

# Callback to handle "All Channels" and "Clear Selected Channels" buttons
@app.callback(
    Output("channel-dropdown", "value"),
    [Input("select-all-channels", "n_clicks"),
     Input("clear-channels", "n_clicks")],
    prevent_initial_call=True
)
def handle_channel_buttons(select_all_clicks, clear_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "select-all-channels":
        return [ch for ch in mne_raw.info["ch_names"]]  
    elif triggered_id == "clear-channels":
        return [] 
    return dash.no_update

# Callback for showing/hiding the filter selection container
@app.callback(
    Output("filter-selection-container", "style"),
    Input("vis-type", "value")
)
def toggle_filter_selection_container(vis_type):
    if vis_type == "specific_band":
        return {"display": "none"}  
    return {"display": "block"}  

# Callback for showing/hiding the custom frequency slider
@app.callback(
    Output("custom-frequency-container", "style"),
    [Input("filter-frequency", "value"),
     Input("vis-type", "value")],
     prevent_initial_call=True
)
def toggle_custom_frequency_slider(filter_frequency, vis_type):
    if vis_type == "specific_band":
        return {"display": "none"}  
    elif filter_frequency == "custom":
        return {"display": "block"}  
    return {"display": "none"}  

# Callback for updating the layout to show/hide the band dropdown
@app.callback(
    Output("band-dropdown-container", "style"),
    Input("vis-type", "value"),
    prevent_initial_call=True
)
def toggle_band_dropdown_visibility(vis_type):
    if vis_type == "specific_band":
        return {"display": "block"} 
    else:
        return {"display": "none"} 

# Callback for updating the plot
@app.callback(
    Output("eeg-plot", "figure"),
    [Input("vis-type", "value"),
     Input("channel-dropdown", "value"),
     Input("band-dropdown", "value"),
     Input("filter-frequency", "value"),
     Input("custom-frequency-slider", "value")],
     prevent_initial_call=True
)
def update_plot(vis_type, selected_channels, selected_band, filter_frequency, custom_range):
    fig = go.Figure()
    
    # Prevent error if selected_channels is empty or None
    if not selected_channels:
        return fig  

    # Ensure selected_channels are present in mne_raw.info["ch_names"]
    valid_channels = [ch for ch in selected_channels if ch in mne_raw.info["ch_names"]]
    if not valid_channels:
        return fig

    # Apply frequency filtering
    filtered_raw = mne_raw.copy()  
    if filter_frequency == "low":
        filtered_raw = filter_data(filtered_raw, high_freq=1)
    elif filter_frequency == "high":
        filtered_raw = filter_data(filtered_raw, low_freq=25)
    elif filter_frequency == "custom":
        filtered_raw = filter_data(filtered_raw, low_freq=custom_range[0], high_freq=custom_range[1])

    # PSD visualization for specific band
    if vis_type == "specific_band":
        if selected_band is None:
            return dash.no_update
        band_data = plot_power_band(power_bands, selected_band, mne_raw, "all")
        for ch_name, freqs, power in band_data:
            if ch_name in valid_channels:
                fig.add_trace(go.Scatter(x=freqs, y=power, mode="lines", name=ch_name))
        for i, name in enumerate(bands_names):
            if selected_band.lower() == name.lower():
                band_index = i
                break    
        fig.update_layout(
            title=f"PSD for {selected_band} Band ({bands_freq[band_index][0]} - {bands_freq[band_index][1]} Hz) - Selected Channels", 
            xaxis_title="Frequency (Hz)", 
            yaxis_title="Power Spectral Density",
            yaxis=dict(autorange=True)  
        )
        
    # Raw signal visualization for selected channels  
    elif vis_type == "raw":
        times, data = plot_raw_channels(filtered_raw, valid_channels)
        for i, channel_name in enumerate(valid_channels):
            fig.add_trace(go.Scatter(x=times, y=data[i], mode="lines", name=channel_name))
        fig.update_layout(
            title="Raw Signal - Selected Channels", 
            xaxis_title="Time (s)", 
            yaxis_title="Amplitude (uV)",
            xaxis=dict(autorange=True),  
            yaxis=dict(range=[-100, 100]) 
        )
    
    return fig

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-button", "n_clicks"),
    State("name-channels", "data"),
    prevent_initial_call=True,
)
def download_power_band(n_clicks, name_channels):
    df = power_band2csv(power_bands, name_channels)
    return dcc.send_data_frame(df.to_csv, "power_bands.csv")

# Callback for updating the layout to show/hide manually assigned channels
@app.callback(
    Output("channel-assignment-container", "style"),
    Output("channel-dropdown", "value", allow_duplicate=True),
    Output("channel-assignment-container", "children", allow_duplicate=True),
    Input("assign-channels-manually-button", "n_clicks"),
    State("number-of-channels", "data"),
    State("channels-names-store", "data"),
    prevent_initial_call=True
)
def channel_assigment_rows_visibility(n_clicks, number_of_channels, channels_names):
    if n_clicks is not None and n_clicks > 0:
        from components.layout import create_channel_assignment_row
        children = []
        preselected = []
        for i in range(number_of_channels):
            value = None  # <-- Make every selection empty
            preselected.append(value)
            children.append(create_channel_assignment_row(i, channels_names, value))
        return {"display": "block"}, preselected, children
    return dash.no_update, dash.no_update, dash.no_update

# Callback for "Assign Automatically" button
@app.callback(
    Output("channel-assignment-container", "style", allow_duplicate=True),
    Output("channel-dropdown", "value", allow_duplicate=True),
    Output("channel-assignment-container", "children", allow_duplicate=True),
    Input("assign-channels-automaticlly-button", "n_clicks"),
    State("number-of-channels", "data"),
    State("channels-names-store", "data"),
    prevent_initial_call=True
)
def channel_assigment_auto_rows_visibility(n_clicks, number_of_channels, channels_names):
    if n_clicks is not None and n_clicks > 0:
        from components.layout import create_channel_assignment_row
        children = []
        preselected = []
        for i in range(number_of_channels):
            value = channels_names[i] if i < len(channels_names) else None
            preselected.append(value)
            children.append(create_channel_assignment_row(i, channels_names, value))
        return {"display": "block"}, preselected, children
    return dash.no_update, dash.no_update, dash.no_update

if __name__ == "__main__":
    app.run(debug=True)
