import dash
from dash import Input, Output, html
import plotly.graph_objects as go
from components.data_acc import mne_raw, power_bands, bands_names, bands_freq, plot_raw_channels, plot_power_band
from components.layout import create_viz_data_layout  

app = dash.Dash(__name__)

app.layout = create_viz_data_layout(mne_raw, bands_names)

# Callback for enabling/disabling band dropdown
@app.callback(
    Output("band-dropdown", "disabled"),
    Input("vis-type", "value")
)
def toggle_band_dropdown(vis_type):
    return vis_type == "raw"

# Callback for updating channel dropdown options
@app.callback(
    Output("channel-dropdown", "options"),
    Input("vis-type", "value")
)
def update_channel_dropdown_options(vis_type):
    return [{"label": ch, "value": ch} for ch in mne_raw.info["ch_names"]]

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
        return [ch for ch in mne_raw.info["ch_names"]]  # Select all channels
    elif triggered_id == "clear-channels":
        return []  # Clear selection
    return dash.no_update

# Callback for updating the layout to allow multiple channel selection
@app.callback(
    Output("channel-dropdown", "multi"),
    Input("vis-type", "value")
)
def toggle_channel_multi_select(vis_type):
    return True  # Always allow multiple selection

# Callback for updating the layout to show/hide the band dropdown
@app.callback(
    Output("band-dropdown-container", "style"),
    Input("vis-type", "value")
)
def toggle_band_dropdown_visibility(vis_type):
    if vis_type == "specific_band":
        return {"display": "block"}  # Show the dropdown
    else:
        return {"display": "none"}  # Hide the dropdown

# Callback for updating the plot
@app.callback(
    Output("eeg-plot", "figure"),
    [Input("vis-type", "value"),
     Input("channel-dropdown", "value"),
     Input("band-dropdown", "value")]
)
def update_plot(vis_type, selected_channels, selected_band):
    fig = go.Figure()
    
    if not selected_channels:
        return fig  # Return empty figure if no channels are selected

    if vis_type == "specific_band":
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
            yaxis_title="Power Spectral Density")
        
    elif vis_type == "raw":
        times, data = plot_raw_channels(mne_raw, selected_channels)
        for i, channel_name in enumerate(selected_channels):
            fig.add_trace(go.Scatter(x=times, y=data[i], mode="lines", name=channel_name))
        fig.update_layout(
            title="Raw Signal - Selected Channels", 
            xaxis_title="Time (s)", 
            yaxis_title="Amplitude (uV)",
        )
    
    return fig

if __name__ == "__main__":
    app.run(debug=True)
