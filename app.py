import os

import mne
import numpy as np
from components.helpers import prepare_dataset
# temporary workaround for deployment test
if not os.path.exists("data"):
        prepare_dataset()

import dash
from dash import Input, Output, html
import plotly.graph_objects as go
from components.data_acc import calculate_psd, construct_mne_object, extract_all_power_bands, get_file, bands_names, bands_freq, pd2mne, plot_raw_channels, plot_power_band
from components.helpers import filter_data
from components.layout import create_viz_data_layout


app = dash.Dash(__name__)
app.title = "BrainUp"  
app._favicon = "logo.png"
server = app.server

# Define global constants (in my opinion temporary solution)
mne_raw = construct_mne_object()
power_bands = []

app.layout = create_viz_data_layout(mne_raw, bands_names)

# Callback for uploading file and nuking the whole page
@app.callback(
        # Output("flag-store", "data"),
        Output("name-channels", "data"),
        # Output("channel-dropdown", "options"),
        Output("vis-type", "value"),
        # Output("channel-dropdown", "value"),
        Output("band-dropdown", "value"),
        Output("filter-frequency", "value"),
        Output("custom-frequency-slider", "value"),
        # Output("eeg-plot", "figure"),
        Input("up-file", "contents"),
        Input("up-file", "filename"),
        prevent_initial_call=True
)
def upload_file(file, filename):
    global mne_raw, power_bands
    # quit if nothing is uploaded
    if filename is None:
        return dash.no_update
    
    raw_data, channels_info = get_file(file, filename)
    print("File uploaded")
    
    mne_raw = pd2mne(raw_data)
    spectrum = calculate_psd(raw_data)
    power_bands = extract_all_power_bands(spectrum)

    # Create empty figure
    fig = go.Figure()
    
    # Return reset values for all components
    return (
        # True, # initializes upload
        channels_info,
        # [{"label": "All Channels", "value": "all"}] + [{"label": ch, "value": ch} for ch in channels],
        "raw",  # Default visualization type
        # [],  # Empty channel selection
        None,  # No band selected
        None,  # No filter selected
        None,  # No custom frequency
        # fig  # Empty figure
    )
       
# Callback for updating channel dropdown options
@app.callback(
    Output("channel-dropdown", "options"),
    Input("vis-type", "value"),
    Input("name-channels", "data"),
    prevent_initial_call=True
)
def update_channel_dropdown_options(vis_type,name_channels):
    # prevent updating channels without uploaded file
    if not name_channels:
        return dash.no_update
    return [{"label": ch, "value": ch} for ch in name_channels]

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
    
    if not selected_channels:
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
            if ch_name in selected_channels:
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
        times, data = plot_raw_channels(filtered_raw, selected_channels)
        for i, channel_name in enumerate(selected_channels):
            fig.add_trace(go.Scatter(x=times, y=data[i], mode="lines", name=channel_name))
        fig.update_layout(
            title="Raw Signal - Selected Channels", 
            xaxis_title="Time (s)", 
            yaxis_title="Amplitude (uV)",
            xaxis=dict(autorange=True),  
            yaxis=dict(range=[-100, 100]) 
        )
    
    return fig


if __name__ == "__main__":
    app.run(debug=True)
