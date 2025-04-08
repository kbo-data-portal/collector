from datetime import datetime, timedelta

from config import logger
from config import URLS, PAYLOADS
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
    
def scrape_schedule(url, payload, start_date, end_date):
    """
    Scrapes KBO schedule data for the given date range.
    """
    logger.info(f"Scraping data from: {url}")

    schedule_data = []

    while start_date <= end_date:
        date_str = start_date.strftime("%Y%m%d")
        
        logger.info(f"Scraping data for {date_str}...")
        payload["date"] = date_str

        try:
            json_data = parse_json_from_url(url, payload)
            if not json_data or int(json_data.get("code", 0)) != 100:
                logger.warning(f"No valid data found for {date_str}. Skipping...")
                start_date += timedelta(days=1)
                continue
            
            headers, rows = extract_data(json_data)
            if not rows:
                logger.info(f"Reached the end of data for {date_str}.")
                start_date += timedelta(days=1)
                continue  

            for row in rows:
                schedule_data.append(convert_row_data(headers, row))
        except Exception as e:
            logger.error(f"Error occurred while scraping data for {date_str}: {e}")
        
        start_date += timedelta(days=1)

    return schedule_data

def run(season, format="parquet"):
    """
    Runs the schedule scraper for the given season(s).
    """
    logger.info("Starting to scrape Korean baseball schedule data...")
    
    url = URLS[Scraper.SCHEDULE]
    payload = PAYLOADS[Scraper.SCHEDULE]

    start_season = 2001
    end_season = datetime.now().year
    if season:
        start_season = season
        end_season = season
    
    for target_season in range(start_season, end_season + 1):
        logger.info(f"Scraping schedule data for season {target_season}...")
        
        start_date = datetime(target_season, 1, 1)
        end_date = datetime(target_season, 12, 31)

        schedule_data = scrape_schedule(url, payload, start_date, end_date)
        if schedule_data:
            save_scraped_data(schedule_data, "schedule", f"{target_season}", format)
        else:
            logger.warning(f"No schedule data found for season {target_season}.")
            return False
    
    return True
