import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.convert import convert_row_data
from utils.request import parse_html_from_page
from utils.storage import save_scraped_data

def extract_data(soup, season):
    """
    Extract table headers and player data from the page and store it in a dictionary.
    """
    if not soup:
        print(f"Skipping season {season} due to parsing error.")
        return
    
    try:
        headers = [th.get_text(strip=True) for th in soup.find("thead").find("tr").find_all("th")]
        rows = [
            [td.get_text(strip=True) for td in tr.find_all("td")] 
            for tr in soup.find("tbody").find_all("tr")
        ]
        
        return headers, rows
    except AttributeError as e:
        print(f"Error parsing table data for season {season}: {e}")
        return None, None

def scrape_player(url, target_season, player_datas):
    """
    Main function to scrape Korean baseball stats for a range of seasons and pages.
    """
    session = requests.Session()
    
    try:
        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
        
        if not viewstate or not eventvalidation:
            print("Skipping due to missing form data.")
            return
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error in scraping data: {e}")
        return

    payload = {
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$smData": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$udpContent|ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeries$ddlSeries": "0",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderByCol": "GAME_CN",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderBy": "DESC",
        "__EVENTTARGET": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
        "__VIEWSTATE": viewstate.strip(),
        "__EVENTVALIDATION": eventvalidation.strip()
    }
    
    start_season = datetime.now().year
    if target_season:
        start_season = target_season

    for season in range(start_season, 1981, -1):
        payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeason$ddlSeason"] = str(season)
        
        for page in range(1, 9999):
            print(f"Scraping page {page} for season {season}...")
            payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfPage"] = str(page)
            
            soup = parse_html_from_page(session, url, payload)
            if soup is None:
                continue
            
            headers, rows = extract_data(soup, season)
            if not rows:
                print(f"Reached the end of the pages for season {season}.")
                break  

            for row in rows:
                if len(row) < len(headers):
                    print(f"Skipping incomplete row: {row}")
                    continue
                
                player_key = f"{season}{row[1]}{row[2]}"
                player_datas.setdefault(player_key, {"SEASON_ID": season})
                player_datas[player_key].update(convert_row_data(headers, row))

        if target_season and target_season == season:
            break

def run(player_type, season, format):
    """
    Scrapes data for the given player type (hitter or pitcher).
    """
    print(f"Starting to scrape Korean baseball {player_type} data...")

    urls = {
        "hitter": [
            "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic2.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/HitterBasic/Detail1.aspx?sort=GAME_CN"
        ],
        "pitcher": [
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic2.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Detail1.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Detail2.aspx?sort=GAME_CN"
        ],
        "fielder": [],
        "runner": []
    }
    
    player_datas = {}
    for url in urls[player_type]:
        print(f"Scraping data from: {url}")
        scrape_player(url, season, player_datas)
    
    filenames = {
        "hitter": "batting_stats_player",
        "pitcher": "pitching_stats_player",
        "fielder": "fielding_stats_player",
        "runner": "running_stats_player"
    }

    save_scraped_data(player_datas, filenames[player_type], format)
