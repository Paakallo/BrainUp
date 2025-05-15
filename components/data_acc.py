import base64
import io
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
import pyxdf

# Define constants
data_folder = os.path.join(os.getcwd(), "data")
channels_names = ['Fp1', 'Fp2', 'F3', 'F4', 'F7', 'F8', 'T3', 'T4', 'C3', 'C4', 'T5', 'T6', 'P3', 'P4', 'O1', 'O2', 'Fz', 'Cz', 'Pz'] # 19 channels
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
    
    return raw_data, channels_info

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

def create_file(content, file_type):
    # create temporary file stored in data
    data = content.encode("utf8").split(b";base64,")[1]
    save_path = os.path.join("data", f"{uuid.uuid4()}.{file_type}")
    with open(save_path, "wb") as fp:
        fp.write(base64.decodebytes(data))
    return save_path

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
    if not isinstance(raw_data, pd.DataFrame):
        return raw_data
    info = mne.create_info(list(raw_data.columns), 256, ch_types="eeg")
    mne_raw = mne.io.RawArray(raw_data.T, info)
    return mne_raw

def calculate_psd(raw_data:pd.DataFrame):
    # Create MNE Raw object and calculate PSD
    mne_raw = pd2mne(raw_data)
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


###
### Specific Vizaulization Functions
###

# Function to plot the raw signal for one or more channels
def plot_raw_channels(raw, channel_names):
    channel_indices = [raw.info['ch_names'].index(ch) for ch in channel_names if ch in raw.info['ch_names']]
    if not channel_indices:
        raise ValueError(f"None of the selected channels were found in the data.")
    
    data, times = raw[channel_indices]
    print(data)
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

