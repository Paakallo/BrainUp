import os
import shutil
import glob
import kagglehub


def prepare_dataset():
    os.makedirs("data", exist_ok=True)
    path = kagglehub.dataset_download("amananandrai/complete-eeg-dataset")
    for file in glob.glob(os.path.join(path, '*.csv')):
        shutil.move(file, "data")
