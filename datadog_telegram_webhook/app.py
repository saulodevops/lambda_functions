from flask import Flask, request, jsonify
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
EXPECTED_HEADER_KEY = os.getenv('EXPECTED_HEADER_KEY')
EXPECTED_HEADER_VALUE = os.getenv('EXPECTED_HEADER_VALUE')

# Debug prints to verify environment variables
print(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
print(f"TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
print(f"EXPECTED_HEADER_KEY: {EXPECTED_HEADER_KEY}")
print(f"EXPECTED_HEADER_VALUE: {EXPECTED_HEADER_VALUE}")

@app.route('/webhook', methods=['POST'])
def webhook():
    # Check for the custom header
    custom_header_value = request.headers.get(EXPECTED_HEADER_KEY)
    if not custom_header_value:
        return jsonify({"status": "error", "message": "Unauthorized1"}), 401

    # Check if the custom header matches the expected value
    if custom_header_value not in [EXPECTED_HEADER_VALUE, f'"{EXPECTED_HEADER_VALUE}"', f"'{EXPECTED_HEADER_VALUE}'"]:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.json
    print("Received data:", json.dumps(data, indent=2))

    # Extract the title and description
    title = data['event']['body']['embeds'][0]['title']
    description = data['event']['body']['embeds'][0]['description']

    # Remove '%%%' from the description
    description = description.replace('%%%', '')

    # Find the start of the message with [ALERT], [WARN], or [RECOVERED]
    keywords = ["[ALERT]", "[WARN]", "[RECOVERED]"]
    start_index = -1
    for keyword in keywords:
        start_index = description.find(keyword)
        if start_index != -1:
            break

    # Extract the message starting from the keyword and ending at the first newline
    if start_index != -1:
        end_index = description.find('\n', start_index)
        if end_index != -1:
            description = description[start_index:end_index]
        else:
            description = description[start_index:]
    else:
        description = "No alert message found."

    # Format the message
    message = f"Title: {title}\nDescription: {description}"

    # Send alert to Telegram
    send_telegram_message(message)

    return jsonify({"status": "success"}), 200

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)