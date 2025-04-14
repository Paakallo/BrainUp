import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from components.data_acc import mne_raw, power_bands, bands_names, bands_freq, plot_raw_channel, plot_channel_bands, plot_power_band

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("EEG Data Visualization"),
    dcc.RadioItems(
        id="vis-type",
        options=[
            {"label": "PSD for Specific Band", "value": "specific_band"}
        ],
        value="raw",
        inline=True,
    ),
    html.Br(),  # Add a break line here
    html.Label("Select Channel:"),
    dcc.Dropdown(
        id="channel-dropdown",
        options=[{"label": "All Channels", "value": "all"}] +  # Add "All Channels" option
                [{"label": ch, "value": ch} for ch in mne_raw.info["ch_names"]],
        value="all",  # Default to "All Channels"
    ),
    html.Br(),  # Add another break line here
    html.Label("Select Frequency Band (if applicable):"),
    dcc.Dropdown(
        id="band-dropdown",
        options=[{"label": name, "value": name} for name in bands_names],
        value=bands_names[0],
    ),
    html.Br(),  # Add another break line here
    dcc.Graph(id="eeg-plot"),
])

# Callback for enabling/disabling band dropdown
@app.callback(
    Output("band-dropdown", "disabled"),
    Input("vis-type", "value")
)
def toggle_band_dropdown(vis_type):
    return vis_type == "raw"

# Callback for updating the plot
@app.callback(
    Output("eeg-plot", "figure"),
    [Input("vis-type", "value"),
     Input("channel-dropdown", "value"),
     Input("band-dropdown", "value")]
)
def update_plot(vis_type, selected_channel, selected_band):
    if vis_type == "specific_band":
        # Plot PSD for a specific band
        band_data = plot_power_band(power_bands, selected_band, mne_raw, selected_channel)
        fig = go.Figure()
        for ch_name, freqs, power in band_data:
            fig.add_trace(go.Scatter(x=freqs, y=power, mode="lines", name=ch_name))
        fig.update_layout(title=f"PSD for {selected_band} Band - {selected_channel if selected_channel != 'all' else 'All Channels'}",
                          xaxis_title="Frequency (Hz)", yaxis_title="Power Spectral Density")
    return fig

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
