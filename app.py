from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time
import json
import os
import requests
import threading

app = Flask(__name__)

# UltraMsg API Configuration
ULTRA_API_URL = os.environ.get('ULTRA_API_URL')
ULTRA_API_TOKEN = os.environ.get('ULTRA_API_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')


# Full documenation here `https://blog.ultramsg.com/make-whatsapp-chatbot-using-python-ultramsg/`

class UltraChatBot:
    def __init__(self):
        self.ultraAPIUrl = ULTRA_API_URL
        self.token = ULTRA_API_TOKEN

    def send_requests(self, endpoint, data):
        url = f"{self.ultraAPIUrl}{endpoint}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.json()

    def send_message(self, chatID, text):
        data = {"to": chatID, "body": text}
        return self.send_requests('messages/chat', data)


chatbot = UltraChatBot()

# List of websites to monitor
websites = [
    {
        'url': 'https://example.com/login',
        'username_field': 'name=username',
        'password_field': 'name=password',
        'username': 'your_username',
        'password': 'your_password',
        'submit_button': '//button[@type="submit"]'
    },
    # If you have more than website you want to monitor
]


def check_website(website):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        driver.get(website['url'])
        time.sleep(2)

        username_field = driver.find_element(
            By.NAME, website['email_field'].split('=')[1])
        password_field = driver.find_element(
            By.NAME, website['password_field'].split('=')[1])

        username_field.send_keys(website['email'])
        password_field.send_keys(website['password'])

        submit_button = driver.find_element(By.XPATH, website['submit_button'])
        submit_button.click()

        time.sleep(3)

        if 'dashboard' not in driver.current_url:
            raise Exception('Login failed')

        chatbot.send_message(
            CHAT_ID, f"✅ Login successful for {website['url']}. Everything is working fine.")
    except Exception as e:
        chatbot.send_message(
            CHAT_ID, f"⚠️ Login failed for {website['url']}: {str(e)}")
    finally:
        driver.quit()


def monitor_websites():
    for website in websites:
        check_website(website)

# Flask endpoint to trigger monitoring manually


# @app.route('/run-monitor', methods=['GET'])
# def run_monitor():
#     threading.Thread(target=monitor_websites).start()
#     return jsonify({"message": "Website monitoring started."})


# Schedule the task to run every day at 'specific time you want the script to run e.g 09.00
schedule.every().day.at("08:30").do(monitor_websites)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Run scheduler in a separate thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
