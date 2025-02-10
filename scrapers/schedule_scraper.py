from datetime import timedelta

from config import logger
from config import URLS, FILENAMES, PAYLOADS
from config import Scraper

from utils.convert import convert_row_data
from utils.request import parse_json_from_url
from utils.storage import save_scraped_data

def extract_data(json):
    """
    Extract headers and schedule data store it in a dictionary.
    """
    if not json:
        logger.error("Skipping schedule due to parsing error.")
        return None, None
    
    try:
        games = json.get("game", [])
        if not games:
            logger.info("Skipping schedule due to parsing.")
            return None, None

        headers = [header.strip() for header in games[0].keys()]
        rows = [
            [row for row in game.values()] 
            for game in games
        ]
        return headers, rows
    except AttributeError as e:
        logger.error(f"Error parsing schedule data: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error while extracting data: {e}")
        return None, None
    
def scrape_schedule(url, payload, start_date, end_date, schedule_data):
    """
    Scrapes Korean baseball game data for the specified date range.
    """
    logger.info(f"Scraping data from: {url}")

    current_date = start_date.replace()
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        
        logger.info(f"Scraping data for {date_str}...")
        payload["date"] = date_str

        try:
            json_data = parse_json_from_url(url, payload)
            if not json_data or int(json_data.get("code", 0)) != 100:
                logger.warning(f"No valid data found for {date_str}. Skipping...")
                current_date += timedelta(days=1)
                continue
            
            headers, rows = extract_data(json_data)
            if not rows:
                logger.info(f"Reached the end of data for {date_str}.")
                current_date += timedelta(days=1)
                continue  

            for row in rows:
                schedule_data.append(convert_row_data(headers, row))
        except Exception as e:
            logger.error(f"Error occurred while scraping data for {date_str}: {e}")
        
        current_date += timedelta(days=1)

def run(start_date, end_date, season=None, format="parquet"):
    """ 
    Scrapes schedule data for the given date range.
    """
    logger.info(f"Starting to scrape Korean baseball schedule data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    url = URLS[Scraper.SCHEDULE]
    filename = FILENAMES[Scraper.SCHEDULE]
    payload = PAYLOADS[Scraper.SCHEDULE]

    schedule_data = []
    scrape_schedule(url, payload, start_date, end_date, schedule_data)

    if schedule_data:
        save_scraped_data(schedule_data, filename, season, format)
        return True
    
    return False
