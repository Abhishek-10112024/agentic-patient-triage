import os
import json
import shutil


RECORDINGS_DIR = "data/recordings"
RESPONSES_DIR = "data/responses"


def get_next_index(folder_path):
    files = os.listdir(folder_path)
    return len(files) + 1


def save_recording(file_path):
    os.makedirs(RECORDINGS_DIR, exist_ok=True)

    idx = get_next_index(RECORDINGS_DIR)
    new_path = os.path.join(RECORDINGS_DIR, f"recording_{idx}.wav")

    shutil.move(file_path, new_path)

    return new_path, idx


def save_response(response: dict, idx: int):
    os.makedirs(RESPONSES_DIR, exist_ok=True)

    file_path = os.path.join(RESPONSES_DIR, f"response_{idx}.json")

    with open(file_path, "w") as f:
        json.dump(response, f, indent=4)

    return file_path
