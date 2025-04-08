from datetime import datetime

from config import logger
from config import URLS, PAYLOADS
from config import Scraper, Player

from utils.convert import convert_row_data
from utils.request import initiate_session, parse_html_from_page
from utils.storage import save_scraped_data

def extract_data(soup, season):
    """
    Parses table headers and player rows from the given BeautifulSoup object.
    """
    if not soup:
        logger.error(f"Skipping season {season} due to parsing error.")
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

def scrape_player(url, payload, season, player_data):
    """
    Scrapes KBO player stats for a season across multiple pages.
    """
    logger.info(f"Scraping data from: {url}")
    session, viewstate, eventvalidation = initiate_session(url)
    if session is None:
        logger.error(f"Failed to initiate scraping session for URL: {url}. Skipping further processing.")
        return
    
    payload["__VIEWSTATE"] = viewstate
    payload["__EVENTVALIDATION"] = eventvalidation

    payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeason$ddlSeason"] = str(season)
    
    for page in range(1, season):
        logger.info(f"Scraping page {page} for season {season}...")
        payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfPage"] = str(page)
        
        try:
            soup = parse_html_from_page(session, url, payload)
            if soup is None:
                logger.warning(f"No content found for page {page}, season {season}.")
                continue
            
            headers, rows = extract_data(soup, season)
            if headers is None and rows is None:
                logger.warning(f"Data not found for page {page}, season {season}.")
                break
            if headers and not rows:
                logger.info(f"Reached the end of the pages for season {season}.")
                break  
            for row in rows:
                player_key = f"{season}{row[1]}{row[2]}"
                player_data.setdefault(player_key, {"SEASON_ID": season})
                player_data[player_key].update(convert_row_data(headers, row))
        except Exception as e:
            logger.error(f"Error during scraping page {page}, season {season}: {e}")
            continue
            
    session.close()

def run(season, format="parquet"):
    """
    Runs the player stats scraper for the given season(s).
    """
    logger.info("Starting to scrape Korean baseball player data...")

    urls = URLS[Scraper.PLAYER]
    payload = PAYLOADS[Scraper.PLAYER]

    start_season = 1982
    end_season = datetime.now().year
    if season:
        start_season = season
        end_season = season

    for player_type in Player:
        for target_season in range(start_season, end_season + 1):
            logger.info(f"Scraping {player_type} data for season {target_season}...")
            if player_type == Player.FIELDER or player_type == Player.RUNNER:
                if start_season < 2001:
                    continue

            player_data = {}
            for url in urls[player_type]:
                scrape_player(url, payload, season, player_data)
                
            if player_data:
                save_scraped_data(player_data, f"player/{target_season}", player_type.value, format)
            else:
                logger.warning(f"No {player_type} data found for season {target_season}.")
                return False
    
    return True
