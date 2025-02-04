import os
import requests
import pandas as pd
import argparse
from bs4 import BeautifulSoup
from datetime import datetime

def convert_column_name(column_str):
    """
    Convert column names to a standardized format.
    """
    if column_str == "순위":
        return None
    elif column_str == "선수명":
        return "P_NM"
    elif column_str == "팀명":
        return "TEAM_NM"
    else:
        return column_str.upper()

    
def convert_to_data(fraction_str):
    """
    Convert a fraction string to a decimal number. If the input is not in fraction format, 
    convert it to float or string as needed.
    """
    try:
        if fraction_str == "-":
            return float(0)
        
        if ' ' in fraction_str and '/' in fraction_str:
            whole, fraction = fraction_str.split(' ')
            numerator, denominator = map(int, fraction.split('/'))
            decimal_value = int(whole) + (numerator / denominator)
            return round(decimal_value, 2)
        elif '/' in fraction_str:
            numerator, denominator = map(int, fraction_str.split('/'))
            decimal_value = numerator / denominator
            return round(decimal_value, 2)
        
        try:
            return float(fraction_str)
        except ValueError:
            return str(fraction_str)
    
    except Exception:
        return fraction_str
    
def fetch_page_data(session, url, payload):
    """
    Send a POST request to the URL and return the parsed HTML.
    Handles request and connection errors.
    """
    try:
        response = session.post(url, data=payload)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in fetching page data: {e}")
        return None

def extract_viewstate_and_eventvalidation(soup):
    """
    Extract the __VIEWSTATE and __EVENTVALIDATION values from the page.
    """
    try:
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
        return viewstate, eventvalidation
    except AttributeError as e:
        print(f"Error extracting viewstate and eventvalidation: {e}")
        return None, None

def parse_table_data(soup, season):
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

def scrape_korean_baseball_data(url, player_data):
    """
    Main function to scrape Korean baseball stats for a range of seasons and pages.
    """
    session = requests.Session()
    
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        viewstate, eventvalidation = extract_viewstate_and_eventvalidation(soup)
        if not viewstate or not eventvalidation:
            print("Skipping due to missing form data.")
            return
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error in scraping data: {e}")
        return

    base_payload = {
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$smData": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$udpContent|ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeries$ddlSeries": "0",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderByCol": "GAME_CN",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderBy": "DESC",
        "__EVENTTARGET": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
        "__VIEWSTATE": viewstate.strip(),
        "__EVENTVALIDATION": eventvalidation.strip()
    }
    
    for season in range(datetime.now().year, 1981, -1):
        base_payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeason$ddlSeason"] = str(season)
        
        for page in range(1, 9999):
            print(f"Scraping page {page} for season {season}...")
            base_payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfPage"] = str(page)
            
            soup = fetch_page_data(session, url, base_payload)
            if soup is None:
                continue
            
            headers, rows = parse_table_data(soup, season)
            if not rows:
                print(f"Reached the end of the pages for season {season}. No more data found.")
                break  

            for row in rows:
                if len(row) < len(headers):
                    print(f"Skipping incomplete row: {row}")
                    continue
                
                player_key = f"{season}{row[1]}{row[2]}"
                player_data.setdefault(player_key, {"SEASON_ID": season})
                print(season, row[1])

                for header, data in zip(headers, row):
                    column = convert_column_name(header)
                    if column:
                        player_data[player_key][column] = convert_to_data(data)

def save_scraped_data(player_data, filename_prefix):
    """
    Save the scraped data to CSV and Parquet files with a specific filename prefix.
    """
    try:
        if not player_data:
            print("No data to save.")
            return
        
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        df = pd.DataFrame(list(player_data.values()))
        if "era" in df:
            df = df.sort_values(by=['SEASON_ID', 'TEAM_NM', 'ERA'], ascending=[True, True, True])
        elif "avg" in df:
            df = df.sort_values(by=['SEASON_ID', 'TEAM_NM', 'AVG'], ascending=[True, True, False])
        

        df.to_csv(os.path.join(output_dir, f"{filename_prefix}_player_stat.csv"), index=False, encoding="utf-8-sig")
        df.to_parquet(os.path.join(output_dir, f"{filename_prefix}_player_stat.parquet"), engine="pyarrow", index=False)
        print(f"Data saved as {filename_prefix}_player_stat CSV and Parquet.")
    except Exception as e:
        print(f"Error saving data: {e}")

def scrape_player_data(player_type):
    """
    Scrapes data for the given player type (hitter or pitcher).
    """
    print(f"Starting to scrape Korean baseball {player_type} data...")
    player_data = {}
    
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
        ]
    }
    
    for url in urls[player_type]:
        print(f"Scraping data from: {url}")
        scrape_korean_baseball_data(url, player_data)
    
    save_scraped_data(player_data, player_type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KBO Player Data Scraper")
    parser.add_argument("-p", "--player", type=str, choices=["hitter", "pitcher"], help="Choose the player type to scrape: 'hitter' for batters, 'pitcher' for pitchers.")
    parser.add_argument("-a", "--all", action="store_true", help="Scrape data for all players.")

    args = parser.parse_args()

    if args.player:
        scrape_player_data(args.player)
    else:
        scrape_player_data("hitter")
        scrape_player_data("pitcher")

