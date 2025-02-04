import os
import requests
import pandas as pd
import argparse
from datetime import datetime, timedelta

def fetch_data_from_url(url, payload):
    """
    Sends a POST request to the provided URL and returns the parsed JSON response.
    Handles request and connection errors gracefully.
    """
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error with request: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while fetching data: {e}")
        return None

def scrape_baseball_schedule(url, schedule_data, start_date, end_date):
    """
    Scrapes Korean baseball game data for the specified date range.
    """
    payload = {
        "leId": "1",
        "srId": "0,1,2,3,4,5,6,7,8,9"
    }

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        print(f"Scraping data for {date_str}...")
        payload["date"] = date_str

        json_data = fetch_data_from_url(url, payload)
        if json_data and json_data.get("game"):
            schedule_data.extend(json_data["game"])

        current_date += timedelta(days=1)

def save_schedule_data_to_file(schedule_data):
    """
    Saves the scraped schedule data into CSV and Parquet files.
    """
    try:
        if not schedule_data:
            print("No data to save.")
            return
        
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        df = pd.DataFrame(schedule_data)
        df = df.sort_values(by=['SEASON_ID', 'G_TM'], ascending=[True, True])
        df.to_csv(os.path.join(output_dir, "baseball_schedule.csv"), index=False, encoding="utf-8-sig")
        df.to_parquet(os.path.join(output_dir, "baseball_schedule.parquet"), engine="pyarrow", index=False)

        print("Data successfully saved.")
    except Exception as e:
        print(f"Error saving data to file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KBO Baseball Schedule Scraper")
    parser.add_argument("-d", "--date", type=str, help="Specify a date (YYYYMMDD) to fetch data for that day.")
    parser.add_argument("-f", "--full", action="store_true", help="Scrape all data from 2001-04-05 to today.")

    args = parser.parse_args()

    url = "https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList"
    schedule_data = []

    if args.full:
        start_date = datetime.strptime("20010405", "%Y%m%d")
        end_date = datetime.now()
    elif args.date:
        try:
            start_date = datetime.strptime(args.date, "%Y%m%d")
            end_date = start_date
        except ValueError:
            print("Invalid date format. Please use YYYYMMDD.")
            exit(1)
    else:
        start_date = datetime.now()
        end_date = start_date

    print(f"Starting to scrape KBO schedule data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    scrape_baseball_schedule(url, schedule_data, start_date, end_date)
    save_schedule_data_to_file(schedule_data)
