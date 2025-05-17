import base64
import datetime
import json
import os
import threading
from time import sleep
import uuid

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
            # check if file expires
            for file, expiry in list(file_tracker.items()):
                file_path = os.path.join("data", file)
                if now > datetime.datetime.fromisoformat(expiry) and os.path.exists(file_path):
                    print(f"Removing {file}")
                    os.remove(file_path)
                    del file_tracker[file]
                    if_changed = True
            # save changes
            if if_changed:
                with open("temp_files.json", "w") as f:
                    json.dump(file_tracker, f)
                    if_changed = False
                # check hour later
                print("Temp_files removed")
            last_time = datetime.datetime.now() + datetime.timedelta(hours=24)

def create_file(content, file_type):
    pause_event.clear() # block data thread
    # create temporary file stored in data
    data = content.encode("utf8").split(b";base64,")[1]
    file_name = f"{uuid.uuid4()}.{file_type}"
    save_path = os.path.join("data", f"{file_name}")
    with open(save_path, "wb") as fp:
        fp.write(base64.decodebytes(data))
    # read temp_files.json
    with open("temp_files.json", "r") as f:
        file = json.load(f)
    # set cooldown for a temp file
    file[file_name] = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
    # write json
    print(f"Adding {file_name} to temp_files")
    with open("temp_files.json", "w") as f:
        json.dump(file, f)
    
    sleep(1) # ensure record has been written
    pause_event.set() # resume thread
    return save_path

