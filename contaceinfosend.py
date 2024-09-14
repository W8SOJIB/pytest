import os
import requests
import json
import time
from queue import Queue
import threading

# Replace with your bot token and chat ID
TOKEN = '7409833692:AAEHa57FWspcNNFqPlPlvVwrZDcikh2bQmw'
CHAT_ID = '6285177516'

# Queue to hold new messages to be sent to Telegram
sms_queue = Queue()

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

# Function to get current SMS messages
def get_sms_messages():
    try:
        sms_list = os.popen('termux-sms-list').read().strip()
        sms_json = json.loads(sms_list)
        sms_messages = {}
        for sms in sms_json:
            sms_id = sms['id']
            address = sms.get('address', 'Unknown').replace('_', '\\_')  # Escape for Markdown
            body = sms.get('body', 'No message').replace('_', '\\_')
            sms_messages[sms_id] = f"From: `{address}`\nMessage: {body}"
        return sms_messages
    except Exception as e:
        print(f"Error getting SMS messages: {str(e)}")
        return {}

# Function to monitor and queue new SMS messages
def monitor_sms():
    # Get the initial list of SMS messages
    previous_sms = get_sms_messages()

    while True:
        try:
            # Get the latest list of SMS messages
            current_sms = get_sms_messages()

            # Check for new messages
            for sms_id, message in current_sms.items():
                if sms_id not in previous_sms:
                    # Add new SMS to the queue
                    sms_queue.put(message)
                    print(f"New SMS detected: {message}")

            # Update the previous SMS list
            previous_sms = current_sms

            # Sleep for a short interval before checking again
            time.sleep(2)  # Reduced check interval for faster response

        except Exception as e:
            print(f"Error in SMS monitoring: {str(e)}")
            time.sleep(2)

# Worker function to send queued messages to Telegram
def send_sms_worker():
    while True:
        try:
            # Check if there is any message in the queue
            if not sms_queue.empty():
                message = sms_queue.get()
                send_to_telegram(message)
                sms_queue.task_done()

        except Exception as e:
            print(f"Error in sending SMS worker: {str(e)}")
            time.sleep(2)

if __name__ == "__main__":
    # Start the SMS monitoring thread
    monitor_thread = threading.Thread(target=monitor_sms, daemon=True)
    monitor_thread.start()

    # Start the SMS sending worker thread
    worker_thread = threading.Thread(target=send_sms_worker, daemon=True)
    worker_thread.start()

    # Keep the script running
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Script stopped.")
            break
