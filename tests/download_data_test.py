import mne
import numpy as np
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
raw_data = pd.read_csv(os.path.join(data_folder, "s00.csv"), names=channel_names)


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
print("Brain waves count:", len(power_bands))
print("pow and freq:", len(power_bands[0]))

print("pow for 19 channels:", len(power_bands[0][0]))
print("pow for 1 channel list:", len(power_bands[0][0][0]))
print("pow for 1 channel val:", (power_bands[0][0][0][0]))

print()

print("freq range for 19 channels:", len(power_bands[0][1]))
print("freq range for 19 channel val:", power_bands[0][1])
print("freq value for 19 channel:", power_bands[0][1][0])