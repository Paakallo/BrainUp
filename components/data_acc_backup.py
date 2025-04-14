import mne
import pandas as pd
import matplotlib.pyplot as plt
import os

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

def plot_raw_channel(raw, channel_name):
    """
    Plot the raw EEG signal for a specific channel.
    """
    
    # Ensure the channel exists
    if channel_name not in raw.info['ch_names']:
        print(f"Channel '{channel_name}' not found.")
        return

    # Find the channel index
    channel_idx = raw.info['ch_names'].index(channel_name)

    # Extract the data and times
    data, times = raw[channel_idx]

    # Plot the raw EEG data
    plt.figure(figsize=(10, 5))
    plt.plot(times, data.T, label=channel_name, color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (uV)')
    plt.title(f'Raw EEG Signal for Channel: {channel_name}')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()

def plot_channel_bands(raw, spectrum, channel_name, all_bands, band_names):
    """
    Plot the power spectrum for a specific channel across different frequency bands.
    """
    
    # Ensure the channel exists
    if channel_name not in raw.info['ch_names']:
        raise ValueError(f"Channel '{channel_name}' not found in the data.")
    
    # Get the channel index
    channel_index = raw.info['ch_names'].index(channel_name)
    
    # Initialize the plot
    plt.figure(figsize=(10, 6))
    
    # Loop through all bands
    for band, band_name in zip(all_bands, band_names):
        # Extract power and frequency for the current band
        power, freqs = get_power_band(spectrum, band)
        # Get power for the selected channel
        channel_power = power[channel_index]
        # Plot the power spectrum for this band
        plt.plot(freqs, channel_power, label=f'{band_name} ({band[0]}-{band[1]} Hz)')
    
    # Customize the plot
    plt.title(f'Power Spectrum by Frequency Band for Channel: {channel_name}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density (uV^2/Hz)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_power_band(power_bands, band_name, raw, channel_name="all"):
    """
    Plot the PSD for a specific band across all channels.
    """
    
    for i in range(len(bands_names)):
        if band_name.lower() == bands_names[i].lower():
            band_index = i
            break
    
    selected_power_band = power_bands[band_index]
    pow1, freq1 = selected_power_band

    if channel_name != "all" and channel_name not in raw.info['ch_names']:
        raise ValueError(f"Channel '{channel_name}' not found in the data.")
    elif channel_name.lower() == "all":
        for i, ch_name in enumerate(raw.info['ch_names']):
            plt.plot(freq1, pow1[i], label=ch_name)
    else:
        channel_index = raw.info['ch_names'].index(channel_name)
        plt.plot(freq1, pow1[channel_index], label=channel_name)

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density') # uV^2/Hz
    plt.title(f'PSD - {bands_names[band_index]} ({bands_freq[band_index][0]} - {bands_freq[band_index][1]} Hz)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # Example usage
    plot_raw_channel(mne_raw, 'Fp1')
    plot_channel_bands(mne_raw, psd, 'Fp1', bands_freq, bands_names)
    plot_power_band(power_bands, "delta", mne_raw, "all")
    plot_power_band(power_bands, "delta", mne_raw, "Fp1")
    