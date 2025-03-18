from flask import Flask
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import schedule
import time
import os
import threading

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Creating  a scheduler instance
scheduler = BackgroundScheduler(daemon=True)

@app.route("/send_email")
def index():
    msg = Message(subject='Hello from the other side!', sender='charlesbiegon973@gmail.com', recipients=['charleskibet101@gmail.com'])
    msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works."
    mail.send(msg)
    return "Message sent!"

def greeting():
    with app.app_context():
        msg = Message(subject='Hello from the other side!',
                      sender='charlesbiegon973@gmail.com', recipients=['charleskibet101@gmail.com'])
        msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works."
        mail.send(msg)
        print('sending message')
        return "Message sent!"


# Schedule the task to run every day at 'specific time you want the script to run e.g 09.00
scheduler.add_job(
    greeting,
   
   'interval',
    seconds=120
)

scheduler.start()

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
        with app.app_context():
            msg = Message(
                subject=f"✅ Login successful for {website['url']}",
                sender='charlesbiegon973@gmail.com',
                recipients=['charleskibet101@gmail.com'],
                body=f"Login to {website['url']} was successful.")
            mail.send(msg)
    except Exception as e:
        with app.app_context():
            msg = Message(
                subject=f"⚠️ Login failed for {website['url']}",
                sender='charlesbiegon973@gmail.com',
                recipients=['charleskibet101@gmail.com'],
                body=f"Error: {str(e)}"
            )
            mail.send(msg)
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


# while True:
#         time.sleep(1)

# def run_scheduler():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# Run scheduler in a separate thread
# threading.Thread(target=run_scheduler, daemon=True).start()
if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=5000)
