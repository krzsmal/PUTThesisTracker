from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from lxml import html
import requests
import schedule
import smtplib
import random
import logging
import json
import time
import os

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
load_dotenv()
ELOGIN_LOGIN = os.getenv("ELOGIN_LOGIN")
ELOGIN_PASSWORD = os.getenv("ELOGIN_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
TOPICS_FILE = "topics.json"
SEND_INITIAL_EMAILS = False  # Set to True to send emails with topics on startup

# User-Agent header for HTTP requests
USER_AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}


# Loads the list of topics from a file
def load_topics():
    if os.path.exists(TOPICS_FILE):
        with open(TOPICS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


# Saves the list of topics to a file
def save_topics(new_topics):
    existing_topics = load_topics()
    existing_topics_set = {topic["topic"] for topic in existing_topics}
    
    for topic in new_topics:
        if topic["topic"] not in existing_topics_set:
            existing_topics.append(topic)
    
    with open(TOPICS_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_topics, file, indent=4, ensure_ascii=False)


# Sends an email notification
def send_email(subject: str, body: str) -> None:
    if not SENDER_EMAIL or not APP_PASSWORD or not RECEIVER_EMAIL:
        logging.error("Missing email credentials! Check the .env file.")
        return

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        logging.info("Email notification sent regarding topics change.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


# Fetches the list of available topics
def get_topics(session: requests.Session) -> list:

    # Fetch topics page
    url = "https://usosapd.put.poznan.pl/topics/browse/"
    response = session.get(url, headers=USER_AGENT)
    
    if response.status_code != 200:
        raise ConnectionError("Failed to fetch topics")
    
    if "Wymagane zalogowanie" in response.text:
        raise ValueError("Session expired, re-login required")

    topics_page = html.fromstring(response.content)
    csrf_elements = topics_page.xpath("//input[@name='csrfmiddlewaretoken']")
    if not csrf_elements:
        raise ValueError("CSRF token not found on the topics page")
    csrf_token = csrf_elements[0].value

    # Send request to filter topics
    url = "https://usosapd.put.poznan.pl/topics/browse/filter/set/"
    payload = {
        "csrfmiddlewaretoken": csrf_token,
        "department": "",
        "query": "",
        "type": "ing",
        "study_field_code": "Inf",
        "study_field_query": "Informatyka",
        "status": "AVAILABLE"
    }
    headers = {
        'origin': 'https://usosapd.put.poznan.pl',
        'referer': 'https://usosapd.put.poznan.pl/topics/browse/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
    }

    response = session.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        raise ConnectionError("Failed to set filters for topics")

    # Fetch the topics list again after applying filters
    url = "https://usosapd.put.poznan.pl/topics/browse/"
    response = session.get(url, headers=USER_AGENT)
    
    if response.status_code != 200:
        raise ConnectionError("Failed to fetch topics")
    
    if "Wymagane zalogowanie" in response.text:
        raise ValueError("Session expired, re-login required")

    # Parse the fetched data
    topics_page = html.fromstring(response.content)
    topics_table = topics_page.xpath("//tbody")[0]
    topics = []
    for row in topics_table.xpath("./tr"):
        topic = row.xpath(".//a/span")[0].text.strip()
        topic_link = f'https://usosapd.put.poznan.pl{row.xpath(".//a")[0].attrib["href"]}'
        topic_provider = row.xpath("./td/a")[0].text.strip()
        topics.append({"topic": topic, "link": topic_link, "provider": topic_provider})
    
    return topics


# Logs in to the elogin system
def login(session: requests.Session, login: str, password: str) -> None:
    url = "https://elogin.put.poznan.pl/app/login"

    response = session.get(url, headers=USER_AGENT)
    if response.status_code != 200:
        raise ConnectionError("Failed to connect to the login server")

    login_page = html.fromstring(response.content)
    csrf_elements = login_page.xpath("//input[@name='csrf_token']")
    if not csrf_elements:
        raise ValueError("CSRF token not found on the login page")
    csrf_token = csrf_elements[0].value

    payload = {
        "csrf_token": csrf_token,
        "login": login,
        "password": password,
        "send": ""
    }
    
    response = session.post(url, headers=USER_AGENT, data=payload)
    if "Podano nieprawidłowe hasło" in response.text:
        raise ValueError("Login failed, check your credentials")
    
    logging.info("Successfully logged in")


# Checks for new topics and sends an email notification if any are found
def check_topics() -> None:
    global session
    attempt = 0
    
    logging.info("Checking for new topics.")
    last_topics = load_topics()

    while attempt < 2:
        try:
            logging.info("Atempt number: " + str(attempt + 1))
            topics = get_topics(session)
            new_topics = [topic for topic in topics if topic not in last_topics]

            if new_topics:
                logging.info("New topics found!")
                save_topics(new_topics)
                for topic in new_topics:
                    send_email(f"{topic['topic']}", f"<b>Temat:</b> {topic['topic']}<br><b>Osoba zgłaszająca temat:</b> {topic['provider']}<br><b>Link:</b> {topic['link']}")
                    
            return

        except ValueError as e:
            if "Session expired" in str(e):
                logging.warning("Session expired, re-logging in.")
                session = requests.Session()
                login(session, ELOGIN_LOGIN, ELOGIN_PASSWORD)
                attempt += 1
            else:
                logging.error(f"Error: {e}")
                return


# Checks for new topics with a random delay
def check_topics_with_delay():
    delay = random.randint(0, 15*60)
    time.sleep(delay)
    check_topics()


if __name__ == "__main__":
    if not ELOGIN_LOGIN or not ELOGIN_PASSWORD:
        logging.critical("Missing eLogin login or password in .env file! Check configuration.")
        exit(1)

    session = requests.Session()
    login(session, ELOGIN_LOGIN, ELOGIN_PASSWORD)

    if not SEND_INITIAL_EMAILS:
        topics = get_topics(session)
        save_topics(topics)

    for hour in ["09:00", "12:00", "15:00", "18:00", "21:00", "00:00"]:
        schedule.every().day.at(hour).do(check_topics)

    while True:
        schedule.run_pending()
        time.sleep(60)