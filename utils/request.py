import requests
from bs4 import BeautifulSoup

from lxml import etree
from config import logger

def send_post_request(url, payload, session=None):
    """
    Sends a POST request to the provided URL and returns the response.
    Can be used for both HTML and JSON responses.
    Handles request and connection errors.
    """
    try:
        if session:
            response = session.post(url, data=payload)
        else:
            response = requests.post(url, data=payload)
        
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during request: {e}")
        return None

def parse_html_from_page(session, url, payload):
    """
    Send a POST request to the URL and return the parsed HTML.
    """
    response = send_post_request(url, payload, session)
    if response:
        return BeautifulSoup(response.text, "lxml")
    return None

def parse_json_from_url(url, payload):
    """
    Sends a POST request to the provided URL and returns the parsed JSON response.
    """
    response = send_post_request(url, payload)
    if response:
        return response.json()
    return None

def initiate_session(url):
    """
    Initializes a session for scraping the provided URL and retrieves the necessary form data (viewstate, eventvalidation).
    """
    session = requests.Session()
    
    try:
        response = session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "lxml")
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
        
        if not viewstate or not eventvalidation:
            logger.warning("Skipping due to missing form data.")
            return None, None, None
        
        return session, viewstate.strip(), eventvalidation.strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in scraping data: {e}")

    return None, None, None
