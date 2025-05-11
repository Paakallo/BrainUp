from data_acc import check_columns, pd2mne 
import pandas as pd
import mne

# raw_data = pd.read_csv("data/przyklad.csv")
# print(raw_data)
# cos, cols = check_columns(raw_data)
# print(cos.head())



# Load the EDF file
raw = mne.io.read_raw_edf('data/ex.edf', preload=True)

# Access data and metadata
data, times = raw[:]
print(raw.info)              # Metadata
print(raw.ch_names)          # Channel names
print(raw)            # (n_channels, n_times)

# Plot signals (optional)
# raw.plot()

# raw_data = pd.read_csv("data/przyklad.csv")
# cols = list(raw_data.columns)
# mne_raw = pd2mne(raw_data)

# print(mne_raw)