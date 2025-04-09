import requests
from bs4 import BeautifulSoup
from config import logger


def send_post_request(
    url: str,
    payload: dict,
    session: requests.Session | None = None
) -> requests.Response | None:
    """
    Sends a POST request to the specified URL with the given payload.

    Args:
        url (str): Target URL.
        payload (dict): Form data or payload to include in the POST request.
        session (requests.Session | None): Optional session for persistent connection.

    Returns:
        requests.Response | None: Response object if successful, otherwise None.
    """
    try:
        response = session.post(url, data=payload) if session else requests.post(url, data=payload)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during request: {e}")
    return None


def fetch_html_soup(
    url: str,
    payload: dict,
    session: requests.Session
) -> BeautifulSoup | None:
    """
    Sends a POST request and returns the parsed HTML content as a BeautifulSoup object.

    Args:
        url (str): The target URL.
        payload (dict): The form data for the POST request.
        session (requests.Session): The session to use for the request.

    Returns:
        BeautifulSoup | None: Parsed HTML document, or None on failure.
    """
    response = send_post_request(url, payload, session)
    if response:
        return BeautifulSoup(response.text, "lxml")
    return None


def fetch_json_response(
    url: str,
    payload: dict
) -> dict | list | None:
    """
    Sends a POST request and parses the JSON response.

    Args:
        url (str): The target URL.
        payload (dict): The form data for the POST request.

    Returns:
        dict | list | None: Parsed JSON object or list, or None on failure.
    """
    response = send_post_request(url, payload)
    if response:
        try:
            return response.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
    return None


def initiate_scraping_session(url: str) -> tuple[requests.Session, str, str] | tuple[None, None, None]:
    """
    Initiates a session and retrieves the necessary form state tokens (__VIEWSTATE, __EVENTVALIDATION).

    Args:
        url (str): The URL to initiate the session with.

    Returns:
        tuple: (session, viewstate, eventvalidation) if successful,
               otherwise (None, None, None).
    """
    session = requests.Session()

    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        viewstate_tag = soup.find("input", {"id": "__VIEWSTATE"})
        eventvalidation_tag = soup.find("input", {"id": "__EVENTVALIDATION"})

        if not viewstate_tag or not eventvalidation_tag:
            logger.warning("Missing VIEWSTATE or EVENTVALIDATION tokens.")
            return None, None, None

        viewstate = viewstate_tag.get("value", "").strip()
        eventvalidation = eventvalidation_tag.get("value", "").strip()

        if not viewstate or not eventvalidation:
            logger.warning("VIEWSTATE or EVENTVALIDATION value is empty.")
            return None, None, None

        return session, viewstate, eventvalidation

    except requests.exceptions.RequestException as e:
        logger.error(f"Session initiation failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during session initialization: {e}")

    return None, None, None
