import base64
import os
import plotly.express as px
from plotly.tools import mpl_to_plotly
from components.helpers import create_file, create_user_folder, initialize
# temporary workaround for deployment test
if not os.path.exists("data") or not os.path.exists("temp_files.json"):
        initialize()

from PIL import Image
import dash
from dash import Input, Output, State, html, dcc, ctx
import plotly.graph_objects as go
from components.data_acc import calculate_psd, construct_mne_object, extract_all_power_bands, get_file, bands_names, bands_freq, load_file, pd2mne, plot_raw_channels, plot_power_band, power_band2csv, create_top_map
from components.helpers import filter_data, cleanup_expired_files, start_data_thread
from components.layout import create_viz_data_layout
import threading

app = dash.Dash(__name__)
app.title = "BrainUp"  
app._favicon = "logo.png"
server = app.server

# Define global constants (in my opinion temporary solution)
mne_raw = construct_mne_object()
power_bands = []
spectrum = None
u_id = None  # User ID for file management

app.layout = create_viz_data_layout(mne_raw, bands_names)

# threading.Thread(target=cleanup_expired_files, daemon=True).start()
start_data_thread()

@app.callback(
    Output("user-id", "style"),
    Output("h4_id", "style"),
    Output("user-id", "value"),
    Output("select-file", "options"),
    Output("select-file", "style"),
    Input("show_u_id", "n_clicks"),
    Input("uid-input", "n_submit"),
    State("uid-input", "value"),
    prevent_initial_call=True
)
def update_user_id(n_clicks, n_submit, typed_value):
    """
    Update user ID display based on button click or Enter key press
    """
    
    global u_id

    triggered_id = ctx.triggered_id

    # Enter key pressed in uid-input
    if triggered_id == "uid-input":
        u_id = typed_value
        options = [{'label': f"{filename}", 'value': f"{filename}"} for filename in os.listdir(os.path.join("data", u_id))]
        return dash.no_update, dash.no_update, u_id, options, {"display": "inline-block"}

    # Button clicked to show/hide user ID
    if triggered_id == "show_u_id":
        if n_clicks % 2 != 0:
            # Show elements if we have a u_id
            if u_id is None:
                return dash.no_update
            return {"display": "inline-block"}, {"display": "inline-block"}, u_id, dash.no_update, {"display": "block"}
        else:
            return {"display": "none"}, {"display": "none"}, dash.no_update, dash.no_update, {"display": "none"}

# Callback for uploading file and nuking the whole page
@app.callback(
        Output("name-channels", "data"),
        Output("vis-type", "value"),
        Output("band-dropdown", "value"),
        Output("filter-frequency", "value"),
        Output("custom-frequency-slider", "value"),
        Input("upload-file-zone", "contents"),
        Input("upload-file-zone", "filename"),
        Input("select-file", "value"),
        prevent_initial_call=True,
        allow_duplicate=True
)
def upload_file(file, filename, sel_file):
    global mne_raw, spectrum, power_bands, u_id
    # quit if nothing is uploaded
    if filename is None:
        return dash.no_update

    triggered_id = ctx.triggered_id

    if triggered_id != "select-file":
        u_path, u_id = create_user_folder(u_id)

        raw_data = get_file(file, filename, u_id)
        print("File uploaded")
        
        mne_raw = pd2mne(raw_data)
        spectrum, channels_info = calculate_psd(raw_data)
        power_bands = extract_all_power_bands(spectrum)
        # Return reset values for all components
        return (
            channels_info,
            "raw",  # Default visualization type
            None,  # No band selected
            None,  # No filter selected
            None,  # No custom frequency
        )
    else:
        raw_data = load_file(sel_file, u_id)
        print("File loaded")
        
        mne_raw = pd2mne(raw_data)
        spectrum, channels_info = calculate_psd(raw_data)
        power_bands = extract_all_power_bands(spectrum)
        # Return reset values for all components
        return (
            channels_info,
            "raw",  # Default visualization type
            None,  # No band selected
            None,  # No filter selected
            None,  # No custom frequency
        )

# Callback for updating the layout to show/hide the band dropdown
@app.callback(
    Output("main-container", "style"),
    Input("name-channels", "data"), 
    prevent_initial_call=True
)
def toggle_band_dropdown_visibility(name_channels):
    if name_channels == None:
        return {"display": "none"}
    else:
        return {"display": "block"}

# Callback for updating channel dropdown options
@app.callback(
    Output("channel-dropdown", "options"),
    Input("vis-type", "value"),
    Input("name-channels", "data"),
    prevent_initial_call=True
)
def update_channel_dropdown_options(vis_type, name_channels):
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
    Output("eeg-plot", "style"),
    Output("topo-img", "src"),
    Output("topo-img", "style"),
    [Input("vis-type", "value"),
     Input("channel-dropdown", "value"),
     Input("band-dropdown", "value"),
     Input("filter-frequency", "value"),
     Input("custom-frequency-slider", "value")],
     prevent_initial_call=True
)
def update_plot(vis_type, selected_channels, selected_band, filter_frequency, custom_range):
    """
    Update plot or display image
    If vis_type == "topo", then eeg-plot element isn't updated and vice versa 
    """

    fig = go.Figure()
    img = go.Image()    
    if not selected_channels:
        return fig, {"display": "none"}, dash.no_update, dash.no_update  

    # Apply frequency filtering
    filtered_raw = mne_raw.copy()  
    if filter_frequency == "low":
        filtered_raw = filter_data(filtered_raw, high_freq=1)
    elif filter_frequency == "high":
        filtered_raw = filter_data(filtered_raw, low_freq=25)
    elif filter_frequency == "custom":
        if custom_range is None or len(custom_range) != 2:
            custom_range = [5, 10]
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

    # Display topographic map
    elif vis_type == "topo":
        mat_fig = create_top_map(spectrum)       
        img_path = create_file(mat_fig, ".png")
        image = Image.open(img_path)
        return dash.no_update, {"display": "none"}, image, {"display": "block"}
    return fig, {"display": "block"}, dash.no_update, {"display": "none"} 

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-button", "n_clicks"),
    State("name-channels", "data"),
    prevent_initial_call=True,
)
def download_power_band(n_clicks, name_channels):
    df = power_band2csv(power_bands, name_channels)
    return dcc.send_data_frame(df.to_csv, "power_bands.csv")


if __name__ == "__main__":
    app.run(debug=True)
