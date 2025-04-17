from datetime import datetime

from config import logger
from config import URLS, PAYLOADS
from config import Scraper

from utils.convert import convert_row_data
from utils.request import initiate_scraping_session, fetch_html_soup
from utils.storage import save_scraped_data


def parse_spectator_data(soup) -> tuple[list[str], list[list]]:
    """Parses spectator data table from the BeautifulSoup object."""
    if not soup:
        logger.error("Skipping spectator data due to empty or invalid soup object.")
        return None, None

    try:
        headers = [th.get_text(strip=True) for th in soup.select_one("thead tr").find_all("th")]
        row_data = [
            [td.get_text(strip=True) for td in tr.find_all("td")]
            for tr in soup.select("tbody tr")
        ]

        return headers, row_data
    except AttributeError as e:
        logger.error(f"Attribute error while parsing spectator data: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error during spectator extraction: {e}")
        return None, None


def scrape_spectator_data(
    url: str, 
    payload: dict, 
    season: int
) -> list[dict]:
    """Scrapes spectator data from a specific URL across a season."""
    logger.info(f"Starting to fetch spectator data from: {url}")
    collected_spectators = []

    session, viewstate, eventvalidation = initiate_scraping_session(url)

    if session is None:
        logger.error(f"Could not initiate session for URL: {url}")
        return

    payload["__VIEWSTATE"] = viewstate
    payload["__EVENTVALIDATION"] = eventvalidation
    payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeason"] = str(season)

    try:
        soup = fetch_html_soup(url, payload, session)
        if soup is None:
            logger.warning(f"Season {season} returned no content.")
            return

        headers, rows = parse_spectator_data(soup)
        if headers is None and rows is None:
            logger.warning(f"No table data on season {season}.")
            return

        for row in rows:
            collected_spectators.append(convert_row_data(headers, row))
    except Exception as e:
        logger.error(f"Error fetching spectator for {season}: {e}")

    session.close()
    return collected_spectators


def run(target_season: int = None, file_format: str = "parquet") -> None:
    """Main runner for scraping KBO game spectator."""
    logger.info("Starting KBO spectator scraping...")

    spectator_url = URLS[Scraper.SPECTATOR]
    spectator_payload = PAYLOADS[Scraper.SPECTATOR]

    start_season = target_season or 2023
    end_season = target_season or datetime.now().year

    for target_year in range(start_season, end_season + 1):
        logger.info(f"Processing spectator for season {target_year}...")

        spectator_records = scrape_spectator_data(spectator_url, spectator_payload, target_year)

        if spectator_records:
            save_scraped_data(spectator_records, "spectator", f"{target_year}", file_format)
        else:
            logger.warning(f"No spectator data found for season {target_year}.")
            