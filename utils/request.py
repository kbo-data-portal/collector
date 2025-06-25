from requests import Session
from crawlquest import json, html
from bs4 import BeautifulSoup
from logger import get_logger

logger = get_logger()


def fetch_html(
    url: str,
    payload: dict,
    session: Session
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
    html_text = html(url, payload=payload, session=session)
    if html_text:
        return BeautifulSoup(html_text , "lxml")
    return None


def fetch_json(
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
    json_data = json(url, payload=payload)
    if json_data:
        return json_data 
    return None


def initiate_session(url: str) -> tuple[Session, str, str] | tuple[None, None, None]:
    """
    Initiates a session and retrieves the necessary form state tokens (__VIEWSTATE, __EVENTVALIDATION).

    Args:
        url (str): The URL to initiate the session with.

    Returns:
        tuple: (session, viewstate, eventvalidation) if successful,
               otherwise (None, None, None).
    """
    session = Session()

    try:
        html_text  = html(url, session=session)
        soup = BeautifulSoup(html_text, "lxml")

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

    except Exception as e:
        logger.error(f"Unexpected error during session initialization: {e}")

    return None, None, None

