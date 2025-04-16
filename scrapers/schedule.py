from datetime import datetime, timedelta

from config import logger
from config import URLS, PAYLOADS
from config import Scraper

from utils.convert import convert_row_data
from utils.request import fetch_json_response
from utils.storage import save_scraped_data


def parse_schedule_data(json_response: dict) -> tuple[list[str], list[list]]:
    """Parses headers and schedule data from the given JSON response."""
    if not json_response:
        logger.error("Skipping schedule due to empty or invalid JSON response.")
        return None, None

    try:
        games = json_response.get("game", [])
        if not games:
            logger.warning("No game entries found in JSON response.")
            return None, None

        headers = [key.strip() for key in games[0].keys()]
        row_data = [[value for value in game.values()] for game in games]

        return headers, row_data
    except AttributeError as e:
        logger.error(f"Attribute error while parsing schedule data: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error during schedule extraction: {e}")
        return None, None


def scrape_schedule_data(
    url: str,
    payload: dict,
    start_date: datetime,
    end_date: datetime
) -> list[dict]:
    """Scrapes schedule data from the given URL across a date range."""
    logger.info(f"Starting to fetch schedule data from: {url}")
    collected_schedules = []

    while start_date <= end_date:
        date_str = start_date.strftime("%Y%m%d")
        logger.info(f"Fetching schedule for date {date_str}...")

        payload["date"] = date_str

        try:
            json_response = fetch_json_response(url, payload)
            if not json_response or int(json_response.get("code", 0)) != 100:
                logger.warning(f"No valid response for {date_str}.")
                start_date += timedelta(days=1)
                continue

            headers, rows = parse_schedule_data(json_response)
            if not rows:
                logger.info(f"No rows returned for {date_str}.")
                start_date += timedelta(days=1)
                continue

            for row in rows:
                collected_schedules.append(convert_row_data(headers, row))
        except Exception as e:
            logger.error(f"Error fetching schedule for {date_str}: {e}")
        finally:
            start_date += timedelta(days=1)

    return collected_schedules


def run(target_season: int = None, file_format: str = "parquet") -> bool:
    """Main runner for scraping KBO game schedule."""
    logger.info("Starting KBO schedule scraping...")

    schedule_url = URLS[Scraper.SCHEDULE]
    schedule_payload = PAYLOADS[Scraper.SCHEDULE]

    start_season = target_season or 2001
    end_season = target_season or datetime.now().year

    for target_year in range(start_season, end_season + 1):
        logger.info(f"Processing schedule for season {target_year}...")

        start_date = datetime(target_year, 1, 1)
        end_date = datetime(target_year, 12, 31)

        schedule_records = scrape_schedule_data(schedule_url, schedule_payload, start_date, end_date)

        if schedule_records:
            save_scraped_data(schedule_records, "schedule", f"{target_year}", file_format)
        else:
            logger.warning(f"No schedule data found for season {target_year}.")
            return False

    return True
