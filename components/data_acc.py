import mne
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
import io

# Define constants
data_folder = os.path.join(os.getcwd(), "data")
channel_names = ['Fp1', 'Fp2', 'F3', 'F4', 'F7', 'F8', 'T3', 'T4', 'C3', 'C4', 'T5', 'T6', 'P3', 'P4', 'O1', 'O2', 'Fz', 'Cz', 'Pz'] # 19 channels
delta = [0.5,4] # Delta:   0.5 – 4   Hz   → Deep sleep, unconscious states
theta = [4,8] # Theta:   4   – 8   Hz   → Drowsiness, meditation, creativity
alpha = [8,13] # Alpha:   8   – 13  Hz   → Relaxed wakefulness, calm focus
beta = [13,30] # Beta:    13  – 30  Hz   → Active thinking, alertness, problem-solving
gamma = [30,100] # Gamma:   30  – 100 Hz   → Higher cognitive functions, memory, consciousness
bands_freq = [delta, theta, alpha, beta, gamma]
bands_names = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']

# Load data
csv_files = []
used_csv_file_index: int = 0
if os.path.isdir(data_folder):
    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    if files:
        for i in range(len(files)):
            csv_files.append(os.path.join(data_folder, files[i]))
        print(f"Opening file: {csv_files[used_csv_file_index]}")
    else:
        raise FileNotFoundError("No CSV file found in the dataset directory.")
else:
    raise NotADirectoryError(f"The path '{data_folder}' is not a directory.")

try:
    raw_data = pd.read_csv(csv_files[used_csv_file_index], names=channel_names)
except ValueError:
    print(f"Entered path: \"{data_folder}\" is not a valid CSV file.")
    print("Error reading CSV file. Please check the file format and content.")

# Create MNE Raw object and calculate PSD
info = mne.create_info(channel_names, 256, ch_types="eeg")
mne_raw = mne.io.RawArray(raw_data.T, info)
psd = mne_raw.compute_psd()

def get_power_band(spectrum:mne.time_frequency.Spectrum, band:list):
    fmin, fmax = band
    power, freqs = spectrum.get_data(return_freqs=True, fmin=fmin, fmax=fmax)
    return power, freqs

def extract_all_power_bands(spectrum):
    power_bands = []
    for band in bands_freq:
        power_bands.append(get_power_band(spectrum, band))
    return power_bands

power_bands = extract_all_power_bands(psd)

###
### Specific Vizaulization Functions
###

# Function to plot the raw signal for one or more channels
def plot_raw_channels(raw, channel_names):
    channel_indices = [raw.info['ch_names'].index(ch) for ch in channel_names if ch in raw.info['ch_names']]
    if not channel_indices:
        raise ValueError(f"None of the selected channels were found in the data.")
    
    data, times = raw[channel_indices]
    return times, data

# Function to plot PSD for a channel across all bands
def plot_channel_bands(raw, spectrum, channel_name, all_bands, band_names):
    if channel_name not in raw.info['ch_names']:
        raise ValueError(f"Channel '{channel_name}' not found in the data.")
    
    channel_index = raw.info['ch_names'].index(channel_name)
    
    bands_plot_data = []
    for band, band_name in zip(all_bands, band_names):
        power, freqs = get_power_band(spectrum, band)
        channel_power = power[channel_index]
        bands_plot_data.append((band_name, freqs, channel_power))
        
    return bands_plot_data

# Function to plot the PSD for all channels in a specific band
def plot_power_band(power_bands, band_name, raw, channel_name="all"):
    for i, name in enumerate(bands_names):
        if band_name.lower() == name.lower():
            band_index = i
            break
        
    selected_power_band = power_bands[band_index]
    pow1, freq1 = selected_power_band
    
    band_plot_data = []
    if channel_name.lower() == "all":
        for i, ch_name in enumerate(raw.info['ch_names']):
            band_plot_data.append((ch_name, freq1, pow1[i]))
    else:
        channel_index = raw.info['ch_names'].index(channel_name)
        band_plot_data.append((channel_name, freq1, pow1[channel_index]))
        
    return band_plot_data

