import mne
import pandas as pd
import matplotlib.pyplot as plt


raw_d = pd.read_csv('data/s00.csv', names=['Fp1', 'Fp2', 'F3', 'F4', 'F7', 'F8', 'T3', 'T4', 'C3', 'C4', 'T5', 'T6', 'P3', 'P4', 'O1', 'O2', 'Fz', 'Cz', 'Pz'])
channel_names = ['Fp1', 'Fp2', 'F3', 'F4', 'F7', 'F8', 'T3', 'T4', 'C3', 'C4', 'T5', 'T6', 'P3', 'P4', 'O1', 'O2', 'Fz', 'Cz', 'Pz']

# Preprocessing
# TODO:

# Feature Extraction

info = mne.create_info(channel_names, 256, ch_types="eeg")
raw = mne.io.RawArray(raw_d.T, info)

spec = raw.compute_psd()

# EEG Frequency Bands:
# Delta:   0.5 – 4   Hz   → Deep sleep, unconscious states
# Theta:   4   – 8   Hz   → Drowsiness, meditation, creativity
# Alpha:   8   – 13  Hz   → Relaxed wakefulness, calm focus
# Beta:    13  – 30  Hz   → Active thinking, alertness, problem-solving
# Gamma:   30  – 100 Hz   → Higher cognitive functions, memory, consciousness

delta = [0.5,4]
theta = [4,8]
alpha = [8,13]
beta = [13,30]
gamma = [30,100]

def get_power_band(spectrum:mne.time_frequency.Spectrum, band:list):
    fmin, fmax = band
    power, freqs = spectrum.get_data(return_freqs=True, fmin=fmin, fmax=fmax)
    return power, freqs

def get_all(spectrum):
    return_l = []
    all_bands = [delta, theta, alpha, beta, gamma]
    for band in all_bands:
        return_l.append(get_power_band(spectrum, band))
    return return_l

bands = get_all(spec)

band = bands[4] # for tests only gamma
pow1, freq1 = band

for i, ch_name in enumerate(raw.info['ch_names']):

    plt.plot(freq1, pow1[i], label=ch_name)

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density (uV^2/Hz)')
    plt.title('PSD from RawArray')
    plt.legend()
    plt.show()
