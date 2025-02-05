from datetime import timedelta
from utils.request import parse_json_from_url
from utils.storage import save_scraped_data

def scrape_game_schedule(url, start_date, end_date, schedule_datas):
    """
    Scrapes Korean baseball game data for the specified date range.
    """
    payload = {
        "leId": "1",
        "srId": "0,1,3,4,5,6,7,8,9"
    }

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        
        print(f"Scraping data for {date_str}...")
        payload["date"] = date_str

        json_data = parse_json_from_url(url, payload)
        if not json_data or int(json_data.get("code", 0)) != 100:
            continue

        schedule_datas.extend(json_data["game"])
        current_date += timedelta(days=1)

def run(start_date, end_date):
    """ 
    Scrapes schedule data for the given date range.
    """
    print(f"Starting to scrape Korean baseball schedule data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    url = "https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList"

    schedule_datas = []
    print(f"Scraping data from: {url}")
    scrape_game_schedule(url, start_date, end_date, schedule_datas)

    save_scraped_data(schedule_datas, "game_schedule")
