import os
import requests
import json
import time

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

# Function to get current SMS messages
def get_sms_messages():
    try:
        sms_list = os.popen('termux-sms-list').read().strip()
        sms_json = json.loads(sms_list)
        sms_messages = {}
        for sms in sms_json:
            # Use the unique ID of the SMS to track new messages
            sms_id = sms['id']
            address = sms.get('address', 'Unknown').replace('_', '\\_')  # Escape for Markdown
            body = sms.get('body', 'No message').replace('_', '\\_')
            sms_messages[sms_id] = f"From: `{address}`\nMessage: {body}"
        return sms_messages
    except Exception as e:
        print(f"Error getting SMS messages: {str(e)}")
        return {}

# Function to monitor and send new SMS messages
def monitor_sms():
    # Get the initial list of SMS messages
    previous_sms = get_sms_messages()

    while True:
        # Continuously monitor SMS inbox
        try:
            current_sms = get_sms_messages()

            # Check if there are any new messages
            for sms_id, message in current_sms.items():
                if sms_id not in previous_sms:
                    # New SMS found, send it to Telegram
                    send_to_telegram(message)
                    print(f"New SMS detected and sent: {message}")

            # Update previous SMS list
            previous_sms = current_sms

            # Sleep for a few seconds before checking again (adjust as needed)
            time.sleep(5)

        except KeyboardInterrupt:
            print("Stopped SMS monitoring.")
            break
        except Exception as e:
            print(f"Error in SMS monitoring: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_sms()
