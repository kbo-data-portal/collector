from datetime import datetime, timedelta

from .base import KBOBaseScraper
from config import logger

from utils.convert import convert_row_data
from utils.request import fetch_json

class ScheduleScraper(KBOBaseScraper):
    def __init__(self):
        super().__init__()
        self.url = "https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList"
        self.payload = {
            "leId": "1",
            "srId": "0,1,3,4,5,6,7,8,9",
        }

    def _parse(self, response):
        games = response.get("game", [])
        if not games:
            logger.warning("No game entries found in response.")
            return None, None
        
        headers = [key.strip() for key in games[0].keys()]
        rows = [[value for value in game.values()] for game in games]

        return headers, rows
    
    def fetch(self, season):
        self.save_dir = f"schedule"
        self.save_name = season

        start_date = datetime(season, 1, 1)
        end_date = datetime(season, 12, 31)

        result = []
        while start_date <= end_date:
            date_str = start_date.strftime("%Y%m%d")

            logger.info(f"Fetching schedule for date {date_str}...")
            self.payload["date"] = date_str

            try:
                response = fetch_json(self.url, self.payload)
                if not response or int(response.get("code", 0)) != 100:
                    logger.warning(f"No valid response for date {date_str}.")
                    continue

                headers, rows = self.parse(response)
                if not rows:
                    logger.info(f"No rows returned for date {date_str}.")
                    continue

                for row in rows:
                    result.append(convert_row_data(headers, row))
            except Exception as e:
                logger.error(f"Error fetching schedule for date {date_str}: {e}")
            finally:
                start_date += timedelta(days=1)

        return result
