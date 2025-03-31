from flask import Flask
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

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
# Get the server's local time zone

# Creating  a scheduler instance
scheduler = BackgroundScheduler(daemon=True)


# @app.route("/send_email")


# Replace with your website login URL
WEBSITE_URL = ''
EMAIL = ''  # Replace with your username
PASSWORD = ''  # Replace with your password
# Replace with the username field's name or ID
LOGIN_EMAIL_FIELD = 'name=email'
# Replace with the password field's name or ID
LOGIN_PASSWORD_FIELD = 'name=password'
LOGIN_BUTTON_SELECTOR = '//button[@type="submit"]'


def check_login():
    try:
        # Set up Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode (no GUI)
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)

        # Open the website
        driver.get(WEBSITE_URL)
        time.sleep(2)  # Wait for the page to load

        # Find the username and password fields and fill them
        email_field = driver.find_element(
            By.NAME, LOGIN_EMAIL_FIELD.split('=')[1])
        password_field = driver.find_element(
            By.NAME, LOGIN_PASSWORD_FIELD.split('=')[1])
        email_field.send_keys(EMAIL)
        password_field.send_keys(PASSWORD)

        # Click the login button
        login_button = driver.find_element(By.XPATH, LOGIN_BUTTON_SELECTOR)
        login_button.click()
        time.sleep(3)  # Wait for the login process to complete

        # Check if login was successful
        # Replace 'dashboard' with a URL or element that indicates successful login
        if '' in driver.current_url:
            print(driver.current_url)
            logging.info("Login successful.")
            return True
        else:
            logging.error("Login failed.")
            return False
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return False
    finally:
        driver.quit()


def index():
    with app.app_context():
        msg = Message(subject='Hello from the other side!',
                      sender='charlesbiegon973@gmail.com', recipients=['charleskibet101@gmail.com'])
        msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works."
        mail.send(msg)
        return "Message sent!"


def send_email(subject, body):
    try:
        with app.app_context():
            msg = Message(subject,  sender='charlesbiegon973@gmail.com',
                          recipients=['charleskibet101@gmail.com'],)
            msg.body = body
            mail.send(msg)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


def monitor_login():
    if index():
        subject = "✅ Hey charles"
        body = f"Today is gonna be a good"
    else:
        subject = "✅ Hey charles"
        body = f"Today is gonna be a good"

    send_email(subject, body)


scheduler.add_job(
    monitor_login,
    'cron',
    hour=9,
    minute=26,

)

scheduler.start()


if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=5000)
