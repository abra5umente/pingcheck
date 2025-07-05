import requests
import datetime
import time
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# grab vars from .env file
couchdb_user = os.environ.get("COUCHDB_USER")
couchdb_pass = os.environ.get("COUCHDB_PASS")
couchdb_host = os.environ.get("COUCHDB_HOST")
couchdb_port = os.environ.get("COUCHDB_PORT")

## USER-DEFINED VARIABLES ##

# define quiet hours in 24H time
sleep_hours = range (1, 7) # sleeping hours from 1am to 7am

## SERVICE URLS ##
jellyfin_url = "https://jellyfin.skink-broadnose.ts.net"
jellyseerr_url = "https://jellyseerr.skink-broadnose.ts.net"
unraid_url = "https://unraid.skink-broadnose.ts.net:8600"
hass_url = "http://homeassistant.local:8123/"
couchdb_url = f"http://{couchdb_user}:{couchdb_pass}@{couchdb_host}:{couchdb_port}/_up"
tdarr_url = "http://192.168.86.232:8265/"
pihole_url ="http://192.168.86.58/admin/login"
# example_service = "http://example.com/status" 

## END USER-DEFINED VARIABLES ##

# Pushover API credentials
pushover_api_token = os.environ.get("PUSHOVER_API_TOKEN")
pushover_user_key = os.environ.get("PUSHOVER_USER_KEY")
pushover_url = "https://api.pushover.net/1/messages.json"

# set up logging
log_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
log_handler = TimedRotatingFileHandler(
    "service_monitor.log", when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.INFO)

if sys.stdout.isatty():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

# define functions
def check_service_status(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking {url}: {e}")
        return False
    
def send_pushover_notification(message):
    payload = {
        "token": pushover_api_token,
        "user": pushover_user_key,
        "message": message
    }
    try:
        response = requests.post(pushover_url, data=payload)
        if response.status_code != 200:
            logging.error(f"Failed to send pushover notification: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending pushover notification: {e}")
        return False
    
# track the last known status for each service
last_status = {}

# main loop
while True:
    # check the status of each service
    services = {
        "Jellyfin": jellyfin_url,
        "Jellyseerr": jellyseerr_url,
        "Unraid": unraid_url,
        "Home Assistant": hass_url,
        "Obsidian Livesync": couchdb_url,
        "Tdarr": tdarr_url,
        "Pi-hole": pihole_url
        # "Example Service": example_service  # Uncomment and replace with actual service if needed
    }
    current_hour = datetime.datetime.now().hour

    for service_name, service_url in services.items():
        is_up = check_service_status(service_url)
        was_up = last_status.get(service_name, True) # assumes services are up by default if not previously checked
        if not is_up:
            if was_up:
                if current_hour not in sleep_hours:
                    logging.info(f"{service_name} is down, sending notification...")
                    send_pushover_notification(f"{service_name} is down")
                else:
                    logging.info(f"{service_name} is down, but it's during sleep hours, not sending notification")
            else:
                logging.info(f"{service_name} is still down, no notification sent")
        else:
            if not was_up:
                logging.info(f"{service_name} is back up")
                if current_hour not in sleep_hours:
                    send_pushover_notification(f"{service_name} is back up")
            else:
                logging.info(f"{service_name} is up and running")
        last_status[service_name] = is_up # update the last known status
    logging.info("Service check complete, sleeping for 5 minutes") 
    time.sleep(300)
