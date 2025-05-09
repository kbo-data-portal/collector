from datetime import datetime, timedelta
import json

from scrapers.base import KBOBaseScraper
from utils.convert import convert_row_data
from utils.request import fetch_json


class GameScheduleScraper(KBOBaseScraper):
    def __init__(self, format, series):
        super().__init__(format, series)

        self.url = "https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList"
        self.payload = {
            "leId": "1",
            "srId": ",".join(map(str, self.series))
        }

    def _parse(self, response):
        games = response.get("game", [])
        if not games:
            self.logger.warning("No game entries found in response.")
            return None, None
        
        headers = [key.strip() for key in games[0].keys()]
        rows = [[value for value in game.values()] for game in games]

        return headers, rows
    
    def fetch(self, season, date):
        start_date = datetime.strptime(date, "%Y%m%d") if date else datetime(season, 1, 1)
        end_date = datetime.strptime(date, "%Y%m%d") if date else datetime(season, 12, 31)

        result = {}
        while start_date <= end_date:
            date_str = start_date.strftime("%Y%m%d")

            self.logger.info(f"Fetching schedule for date {date_str}...")
            self.payload["date"] = date_str

            try:
                response = fetch_json(self.url, self.payload)
                if not response or int(response.get("code", 0)) != 100:
                    self.logger.warning(f"No valid response for date {date_str}.")
                    continue

                headers, rows = self.parse(response)
                if not rows:
                    self.logger.info(f"No rows returned for date {date_str}.")
                    continue
                    
                file_path = f"game/schedule/{season}/{date_str}"
                self.backup(response, file_path, "json")

                for row in rows:
                    result.setdefault(file_path, [])
                    result[file_path].append(convert_row_data(headers, row))
            except Exception as e:
                self.logger.error(f"Error fetching schedule for date {date_str}: {e}")
            finally:
                start_date += timedelta(days=1)

        return result


class GameResultScraper(KBOBaseScraper):
    def __init__(self, format, series):
        super().__init__(format, series)
        
        self.url = "https://www.koreabaseball.com/ws/Schedule.asmx/GetScoreBoardScroll"
        self.payload = {
            "leId": "1"
        }

        self.games = GameScheduleScraper(format, series)

    def _parse(self, response):
        maxInnings = response.get("maxInning", None)
        if not maxInnings:
            self.logger.warning("No inning datas found in response.")
            return None, None
        
        headers, rows = ["IS_HOME"], [[False],[True]]
        for key, value in response.items():
            if key == "maxInning":
                break
            if not key.startswith("table"):
                headers.append(key)
                rows[0].append(value)
                rows[1].append(value)

        headers += [f"INN_{i}" for i in range(1, maxInnings + 1)] + ["R", "H", "E", "B"]

        tables = [
            json.loads(response.get("table2", "[]")),
            json.loads(response.get("table3", "[]"))
        ]
        for table in tables:
            rows[0].extend([cell["Text"] for cell in table["rows"][0]["row"]])
            rows[1].extend([cell["Text"] for cell in table["rows"][1]["row"]])

        return headers, rows
    
    def fetch(self, season, date):
        result = {}

        fetch_data = self.games.fetch(season, date)
        for path, schedules in fetch_data.items():
            self.save(schedules, path)
            for schedule in schedules:
                game_id = schedule.get("G_ID", None)

                self.logger.info(f"Fetching result for game id {game_id}...")
                self.payload["srId"] = schedule.get("SR_ID", None)
                self.payload["seasonId"] = schedule.get("SEASON_ID", None)
                self.payload["gameId"] = game_id

                try:
                    response = fetch_json(self.url, self.payload)
                    if not response or int(response.get("code", 0)) != 100:
                        self.logger.warning(f"No valid response for game id {game_id}.")
                        continue

                    headers, rows = self.parse(response)
                    if not rows:
                        self.logger.info(f"No rows returned for game id {game_id}.")
                        continue

                    file_path = f"game/result/{season}/{game_id[:8]}"
                    self.backup(response, file_path, "json")
                    
                    for row in rows:
                        result.setdefault(file_path, [])
                        result[file_path].append(convert_row_data(headers, row))
                except Exception as e:
                    self.logger.error(f"Error fetching result for game id {game_id}: {e}")

        return result
    
    