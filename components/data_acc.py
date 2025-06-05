import base64
import io
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
import pyxdf

from components.helpers import create_file
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for thread-safe plotting

# Define constants
data_folder = os.path.join(os.getcwd(), "data")
channels_names_21 = [
    # Frontal Pole
    "Fp1", "Fp2",
    # Frontal
    "F3", "F4", "F7", "F8", "Fz",
    # Temporal
    "T3", "T4", "T5", "T6",
    # Central
    "C3", "C4", "Cz",
    # Parietal
    "P3", "P4", "Pz",
    # Occipital
    "O1", "O2",
]

channels_names_68 = [
    # Frontal Pole
    "Fp1", "Fp2", "AF7", "AF3", "AF4", "AF8", "F9", "F10",
    # Frontal
    "Fz", "F7", "F3", "F1", "F2", "F4", "F8", "F5", "F6",
    # Frontotemporal
    "FT9", "FT7", "FT8", "FT10",
    # Central
    "Cz", "C3", "C1", "C2", "C4", "C5", "C6",
    # Temporal
    "T9", "T7", "T8", "T10",
    # Central-Parietal
    "CPZ", "CP1", "CP3", "CP5", "CP2", "CP4", "CP6",
    # Temporal-Parietal
    "TP9", "TP7", "TP8", "TP10",
    # Parietal
    "Pz", "P3", "P1", "P2", "P4", "P5", "P6", "P7", "P8", "P9", "P10",
    # Occipital
    "OZ", "O1", "O2", "PO7", "PO3", "POZ", "PO4", "PO8",
] # 68 channels

delta = [0.5,4] # Delta:   0.5 – 4   Hz   → Deep sleep, unconscious states
theta = [4,8] # Theta:   4   – 8   Hz   → Drowsiness, meditation, creativity
alpha = [8,13] # Alpha:   8   – 13  Hz   → Relaxed wakefulness, calm focus
beta = [13,30] # Beta:    13  – 30  Hz   → Active thinking, alertness, problem-solving
gamma = [30,100] # Gamma:   30  – 100 Hz   → Higher cognitive functions, memory, consciousness
bands_freq = [delta, theta, alpha, beta, gamma]
bands_names = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']


def construct_mne_object():
    # Create an empty Raw object with specified channels
    n_channels = 1  
    # Create empty data (0 samples)
    data = np.zeros((n_channels, 0))
    # Create minimal info
    info = mne.create_info(["None"], 256, ch_types="eeg")
    # Create Raw object
    mne_raw = mne.io.RawArray(data, info)
    return mne_raw

def get_file(contents, file_name: str):
    # Returns pandas DataFrame and column names from decoded contents
    # contents are decoded from uploaded file
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if file_name.endswith(".csv"):
            raw_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            raw_data, channels_info = check_columns(raw_data)
        elif file_name.endswith(".xls"):  # Test needed
            raw_data = pd.read_excel(io.BytesIO(decoded))
            raw_data, channels_info = check_columns(raw_data)
        elif file_name.endswith(".edf"):
            raw_data = mne.io.read_raw_edf(create_file(contents, "edf"), preload=True)
            channels_info = raw_data.ch_names
        elif file_name.endswith(".xdf"):
            raw_data, channels_info = read_raw_xdf(create_file(contents, "xdf"))
        else:
            raise TypeError("Unsupported file type.")
    except Exception as e:
        print(f"Error processing file: {e}")
        raise ValueError("Error reading file. Please check the file format and content.")
    
    return raw_data

def read_raw_xdf(fname:str):
    streams, header = pyxdf.load_xdf(fname)
    # find the stream with EEG data
    eeg_stream = None
    for stream in streams:
        print(stream['info']['type'][0].lower())
        if stream['info']['type'][0].lower() == 'eeg':
            eeg_stream = stream
            break
    if eeg_stream is None:
        raise RuntimeError("No EEG stream found in the XDF file.")
    # prepare data and frequency
    data = np.array(eeg_stream["time_series"]).T # shape (n_channels, n_times)
    sfreq = float(streams[0]["info"]["nominal_srate"][0])
    # channel names
    if eeg_stream['info']['desc'][0] != None:
        ch_names = [ch['label'][0] for ch in eeg_stream['info']['desc'][0]['channels'][0]['channel']]
    else:
        n_channels = int(eeg_stream['info']['channel_count'][0])
        ch_names = [f"CH{i+1}" for i in range(n_channels)]
    ch_types = ['eeg'] * len(ch_names)
    # create mne object
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw_data = mne.io.RawArray(data, info)
    return raw_data, ch_names

# def create_file(content, file_type):
#     # create temporary file stored in data
#     data = content.encode("utf8").split(b";base64,")[1]
#     save_path = os.path.join("data", f"{uuid.uuid4()}.{file_type}")
#     with open(save_path, "wb") as fp:
#         fp.write(base64.decodebytes(data))
#     return save_path

def check_columns(import_data:pd.DataFrame):
    # filter data and choose appropriate column names
    df = import_data.select_dtypes(include=['number']) # select onlu numeric values
    columns = list(df.columns)
    channels_info = [] # output

    is_string = False # check if there is a string
    for i,col in enumerate(columns):
        if any(char.isalpha() for char in str(col)): # check if there is a letter
            channels_info.append(col)
            is_string = True
        else:
            channels_info.append(str(i)) # electrode number

    if not is_string: # move numeric columns to a row 
        column_names_row = pd.DataFrame([df.columns.tolist()], columns=df.columns)
        df = pd.concat([column_names_row, df], ignore_index=True)

    df.columns = channels_info
    return df, channels_info

def pd2mne(raw_data:pd.DataFrame):
    # Convert DataFrame to mne object
    print(type(raw_data))
    if not isinstance(raw_data, pd.DataFrame):
        return raw_data
    print(type(raw_data))
    info = mne.create_info(list(raw_data.columns), 256, ch_types="eeg")
    mne_raw = mne.io.RawArray(raw_data.T, info)
    print(type(mne_raw))
    return mne_raw

def calculate_psd(mne_raw:mne.io.RawArray):
    """ Calculate Power Spectral Density (PSD) for the given MNE Raw object.
    """
    psd = mne_raw.compute_psd()
    return psd

def get_power_band(spectrum:mne.time_frequency.Spectrum, band:list):
    fmin, fmax = band
    power, freqs = spectrum.get_data(return_freqs=True, fmin=fmin, fmax=fmax)
    return power, freqs

def extract_all_power_bands(spectrum:mne.time_frequency.Spectrum):
    power_bands = []
    for band in bands_freq:
        power_bands.append(get_power_band(spectrum, band))
    return power_bands

def power_band2csv(power_bands:list, channels:list):
    pw_dic = {}
    for i, band in enumerate(bands_names):
        sel_band = power_bands[i]
        freq = sel_band[1]
        pw_dic[f"{band}_freq"] = freq
        all_pow = sel_band[0]
        # iterate channels
        for j, chan in enumerate(channels):
            pow = all_pow[j]
            pw_dic[f"{chan}({band})_power"] = pow
    # Find the maximum length
    max_len = max(len(v) for v in pw_dic.values())
    # Pad shorter lists with np.nan
    for key, value in pw_dic.items():
        if len(value) < max_len:
            pw_dic[key] = np.pad(value, (0, max_len - len(value)), constant_values=np.nan)
    df = pd.DataFrame(pw_dic)
    return df

def set_mont(data_ch:list):
    """
    Change montage if mne_object doesn't have one
    Standard montage is 10-20
    """
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

def create_top_map(mne_raw, psd_data:mne.time_frequency.spectrum.Spectrum):
    
    print("setting montage")
    if mne_raw.get_montage() is None:
        new_mon = set_mont(mne_raw.ch_names)
        mne_raw.set_montage(new_mon)
    
    # temporary fix for montage
    print("Calculating PSD")
    psd_data = calculate_psd(mne_raw)
    print("Plotting topomap")
    topo_fig = psd_data.plot_topomap(ch_type='eeg', show=False)
    #TODO: adjust to monitor resolution
    screen_width_px = 1620 
    screen_height_px = 1080 
    dpi = 100  

    width_in = screen_width_px / dpi
    height_in = screen_height_px / dpi

    topo_fig.set_size_inches(width_in, height_in)
    print("Topomap created")
    return topo_fig

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

