import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def change_mont(data_ch:list):
    # Form the 10-20 montage
    mont1020 = mne.channels.make_standard_montage('standard_1020')
    # Choose what chann`els you want to keep 
    # Make sure that these channels exist e.g. T1 does not exist in the standard 10-20 EEG system!
    kept_channels = data_ch 
    ind = [i for (i, channel) in enumerate(mont1020.ch_names) if channel in kept_channels]
    mont1020_new = mont1020.copy()
    # Keep only the desired channels
    mont1020_new.ch_names = [mont1020.ch_names[x] for x in ind]
    kept_channel_info = [mont1020.dig[x+3] for x in ind]
    # Keep the first three rows as they are the fiducial points information
    mont1020_new.dig = mont1020.dig[0:3]+kept_channel_info
    # mont1020.plot()
    # mont1020_new.plot()
    return mont1020_new

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
# Standard montage
mont = change_mont(channel_names)

# Create MNE Raw object and calculate PSD
info = mne.create_info(channel_names, 256, ch_types="eeg")
mne_raw = mne.io.RawArray(raw_data.T, info)
print(mne_raw.get_montage())
mne_raw.set_montage(mont)

psd = mne_raw.compute_psd()

psd.plot_topomap(ch_type='eeg')

