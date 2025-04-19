from datetime import datetime

from config import logger
from config import URLS, PAYLOADS
from config import Scraper, Player

from utils.convert import convert_row_data
from utils.request import initiate_scraping_session, fetch_html_soup
from utils.storage import save_scraped_data


def parse_player_data(soup) -> tuple[list[str], list[list]]:
    """Parses player stats table from the BeautifulSoup object."""
    if not soup:
        logger.error("Skipping player data due to empty or invalid soup object.")
        return None, None

    try:
        headers = [th.get_text(strip=True) for th in soup.select_one("thead tr").find_all("th")]
        row_data = [
            [td.get_text(strip=True) for td in tr.find_all("td")]
            for tr in soup.select("tbody tr")
        ]

        return headers, row_data
    except AttributeError as e:
        logger.error(f"Attribute error while parsing player data: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error during player extraction: {e}")
        return None, None


def scrape_player_data(
    url: str, 
    payload: dict, 
    season: int, 
    player_datas: dict
) -> None:
    """Scrapes player stats from a specific URL and season across paginated pages."""
    logger.info(f"Starting to fetch player stats from: {url}")
    session, viewstate, eventvalidation = initiate_scraping_session(url)

    if session is None:
        logger.error(f"Could not initiate session for URL: {url}")
        return

    payload["__VIEWSTATE"] = viewstate
    payload["__EVENTVALIDATION"] = eventvalidation
    payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeason$ddlSeason"] = str(season)

    for page_num in range(1, 9999): 
        logger.info(f"Fetching stats for page {page_num}...")

        payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfPage"] = str(page_num)
        
        try:
            soup = fetch_html_soup(url, payload, session)
            if soup is None:
                logger.warning(f"Page {page_num} returned no content.")
                continue

            headers, rows = parse_player_data(soup)
            if headers is None and rows is None:
                logger.warning(f"No table data on page {page_num}.")
                break

            if headers and not rows:
                logger.info(f"Last page reached at page {page_num}.")
                break

            for row in rows:
                player_id = f"{season}{row[1]}{row[2]}"
                player_datas.setdefault(player_id, {"LE_ID": 1, "SR_ID": 0, "SEASON_ID": season})
                player_datas[player_id].update(convert_row_data(headers, row))

        except Exception as e:
            logger.error(f"Error fetching stats for {page_num}: {e}")
            continue

    session.close()


def run(target_season: int = None, file_format: str = "parquet") -> None:
    """Main runner for scraping KBO game player stats."""
    logger.info("Starting KBO player stats scraping...")

    player_urls = URLS[Scraper.PLAYER]
    player_payload = PAYLOADS[Scraper.PLAYER]

    start_year = target_season or 1982
    end_year = target_season or datetime.now().year

    for player_type in Player:
        for year in range(start_year, end_year + 1):
            if player_type in (Player.FIELDER, Player.RUNNER) and year < 2001:
                continue

            logger.info(f"Processing player stats for {player_type.name}...")
            player_datas = {}

            for url in player_urls[player_type]:
                scrape_player_data(url, player_payload, year, player_datas)

            if player_datas:
                save_scraped_data(player_datas, f"player/{year}", player_type.value, file_format)
            else:
                logger.warning(f"No player stats found for {player_type.name}.")