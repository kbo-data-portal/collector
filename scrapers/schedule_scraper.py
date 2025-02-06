from datetime import timedelta

from config import logger
from config import URLS, FILENAMES, PAYLOADS
from config import Scraper

from utils.request import parse_json_from_url
from utils.storage import save_scraped_data

def scrape_schedule(url, payload, start_date, end_date, schedule_data):
    """
    Scrapes Korean baseball game data for the specified date range.
    """
    logger.info(f"Scraping data from: {url}")

    current_date = start_date
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

            schedule_data.extend(json_data["game"])
        except Exception as e:
            logger.error(f"Error occurred while scraping data for {date_str}: {e}")
        
        current_date += timedelta(days=1)
    
    if not schedule_data:
        schedule_data.append({"status": "No games available for this date"})

def run(start_date, end_date, format):
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
        save_scraped_data(schedule_data, filename, format)
