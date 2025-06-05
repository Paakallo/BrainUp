import base64
import datetime
import json
import os
import threading
from time import sleep
import uuid

import mne
import pandas as pd

from components.data_acc import check_columns, read_raw_xdf

pause_event = threading.Event() # define pause event


def filter_data(raw, low_freq=None, high_freq=None):
    filtered_raw = raw.copy().filter(l_freq=low_freq, h_freq=high_freq)
    return filtered_raw
  
def initialize():
    os.makedirs("data", exist_ok=True)
    with open("temp_files.json", "w") as f:
        json.dump({}, f, indent=4)
   
def start_data_thread():
    threading.Thread(target=cleanup_expired_files, daemon=True).start()

def cleanup_expired_files():
    last_time = datetime.datetime.min # intialize last_time
    if_changed = False
    pause_event.wait() # instruct to wait until the flag is set

    while True:
        now = datetime.datetime.now()
        if now > last_time:
            with open("temp_files.json", "r") as f:
                file_tracker = json.load(f)
            print("Checking temp_files...")
            # iterate through all users
            for user in file_tracker.keys():
                # iterate through all files of the user
                for file, expiry in file_tracker[user].items():
                    file_path = os.path.join("data", user, file)
                    if now > datetime.datetime.fromisoformat(expiry) and os.path.exists(file_path):
                        print(f"Removing {file}")
                        os.remove(file_path)
                        del file_tracker[user][file]
                        if_changed = True
            # save changes
            if if_changed:
                with open("temp_files.json", "w") as f:
                    json.dump(file_tracker, f)
                    if_changed = False
                # check hour later
                print("Temp_files removed")
            last_time = datetime.datetime.now() + datetime.timedelta(days=7)  # check every week

def create_user_folder(u_id:str=None):
    if u_id is not None:
        return os.path.join(os.getcwd(), "data", u_id), u_id
    u_id = str(uuid.uuid4())
    user_folder = os.path.join(os.getcwd(), "data", u_id)
    os.makedirs(user_folder, exist_ok=True)

    with open("temp_files.json", "r") as f:
        file_tracker = json.load(f)

    # add user folder to temp_files.json
    file_tracker[u_id] = {}
    with open("temp_files.json", "w") as f:
        json.dump(file_tracker, f, indent=4)
    
    return user_folder, u_id

def create_file(content, file_name:str, u_id:str=None):
    """
    Create a file from the given content and save it.
    If u_id is provided, the file is saved in the user's folder.
    If u_id is None, the file is saved in the root of the data folder.
    """
    pause_event.clear() # block data thread
    # save data inside user folder
    if not file_name.endswith(".png"):
        data = content.encode("utf8").split(b";base64,")[1]
        save_path = os.path.join("data", u_id, file_name)
        with open(save_path, "wb") as fp:
            fp.write(base64.decodebytes(data))
        add_file_record(file_name, u_id)
    # save figure as png
    elif file_name.endswith(".png"):
        save_path = os.path.join("data", file_name)
        content.savefig(save_path, bbox_inches="tight")
        add_file_record(file_name)
    else:
        raise TypeError
    sleep(1) # ensure record has been written
    pause_event.set() # resume thread
    return save_path

def add_file_record(file_name:str, u_id:str=None):
    """ Adds a file record to the temp_files.json file.
    If u_id is None, the file is added to the root of temp_files.json.
    If u_id is provided, the file is added to the user's folder in temp_files.json.
    """
    # add file record to temp_files.json
    with open("temp_files.json", "r") as f:
        file_tracker = json.load(f)

    if u_id is None: 
        file_tracker[file_name] = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
    else:
        file_tracker[u_id][file_name] = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
    
    with open("temp_files.json", "w") as f:
        json.dump(file_tracker, f, indent=4)

def load_file(file_name:str, u_id:str):
    """ Loads a file from the user's folder or the root of the data folder.
    """
    file_path = os.path.join("data", u_id, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_name} not found in {file_path}")

    if file_name.endswith(".csv"):
        raw_data = pd.read_csv(file_path)
        raw_data = check_columns(raw_data)
    elif file_name.endswith(".xls"): # Test needed
        raw_data = pd.read_excel(file_path)
        raw_data = check_columns(raw_data)
    elif file_name.endswith(".edf"):
        raw_data = mne.io.read_raw_edf(file_path, preload=True) # temporarily hardcoded
    elif file_name.endswith(".xdf"):
        raw_data = read_raw_xdf(create_file(contents, file_name, u_id))
    else:
        raise TypeError


    return file_path