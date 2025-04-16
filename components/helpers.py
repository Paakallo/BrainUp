import os
import shutil
import glob
import kagglehub

def filter_data(raw, low_freq=None, high_freq=None):
    filtered_raw = raw.copy().filter(l_freq=low_freq, h_freq=high_freq)
    return filtered_raw
  
def prepare_dataset():
    os.makedirs("data", exist_ok=True)
    path = kagglehub.dataset_download("amananandrai/complete-eeg-dataset")
    for file in glob.glob(os.path.join(path, '*.csv')):
        shutil.move(file, "data")
