from datetime import datetime

from config import logger
from config import URLS, PAYLOADS, FILENAMES
from config import Scraper

from utils.convert import convert_row_data
from utils.request import initiate_session, parse_html_from_page
from utils.storage import save_scraped_data

def extract_data(soup, season):
    """
    Extract table headers and player data from the page and store it in a dictionary.
    """
    if not soup:
        logger.info(f"Skipping season {season} due to parsing error.")
        return None, None
    
    try:
        headers = [th.get_text(strip=True) for th in soup.find("thead").find("tr").find_all("th")]
        rows = [
            [td.get_text(strip=True) for td in tr.find_all("td")] 
            for tr in soup.find("tbody").find_all("tr")
        ]
        return headers, rows
    except AttributeError as e:
        logger.error(f"Error parsing table data for season {season}: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error while extracting data for season {season}: {e}")
        return None, None

def scrape_player(url, payload, target_season, player_data):
    """
    Main function to scrape Korean baseball stats for a range of seasons and pages.
    """
    logger.info(f"Scraping data from: {url}")
    session, viewstate, eventvalidation = initiate_session(url)
    if session is None:
        logger.error(f"Failed to initiate scraping session for URL: {url}. Skipping further processing.")
        return
    
    payload["__VIEWSTATE"] = viewstate
    payload["__EVENTVALIDATION"] = eventvalidation
    
    start_season = datetime.now().year
    if target_season:
        start_season = target_season

    for season in range(start_season, 1981, -1):
        payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeason$ddlSeason"] = str(season)
        
        for page in range(1, 9999):
            logger.info(f"Scraping page {page} for season {season}...")
            payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfPage"] = str(page)
            
            try:
                soup = parse_html_from_page(session, url, payload)
                if soup is None:
                    logger.warning(f"No content found for page {page}, season {season}.")
                    continue
                
                headers, rows = extract_data(soup, season)
                if not rows:
                    logger.info(f"Reached the end of the pages for season {season}.")
                    break  

                for row in rows:
                    player_key = f"{season}{row[1]}{row[2]}"
                    player_data.setdefault(player_key, {"SEASON_ID": season})
                    player_data[player_key].update(convert_row_data(headers, row))
            except Exception as e:
                logger.error(f"Error during scraping page {page}, season {season}: {e}")
                continue

        if target_season and target_season == season:
            break
    session.close()

def run(player_type, season, format):
    """
    Scrapes data for the given player type (hitter or pitcher).
    """
    logger.info(f"Starting to scrape Korean baseball {player_type} data...")

    urls = URLS[Scraper.PLAYER]
    filenames = FILENAMES[Scraper.PLAYER]
    payload = PAYLOADS[Scraper.PLAYER]

    player_data = {}
    for url in urls[player_type]:
        scrape_player(url, payload, season, player_data)

    save_scraped_data(player_data, filenames[player_type], format)
