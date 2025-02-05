import requests
from bs4 import BeautifulSoup

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
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during request: {e}")
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
