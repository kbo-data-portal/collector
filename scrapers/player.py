
import re

from scrapers.base import KBOBaseScraper
from utils.convert import convert_row_data
from utils.request import initiate_session, fetch_html

class PlayerSeasonStatsScraper(KBOBaseScraper):
    def __init__(self, player_type, detail=False):
        super().__init__()

        if player_type == "hitter":
            self.urls = [
                "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=GAME_CN",
                "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic2.aspx?sort=GAME_CN",
                "https://www.koreabaseball.com/Record/Player/HitterBasic/Detail1.aspx?sort=GAME_CN"
            ]
        elif player_type == "pitcher":
            self.urls = [
                "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=GAME_CN",
                "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic2.aspx?sort=GAME_CN",
                "https://www.koreabaseball.com/Record/Player/PitcherBasic/Detail1.aspx?sort=GAME_CN",
                "https://www.koreabaseball.com/Record/Player/PitcherBasic/Detail2.aspx?sort=GAME_CN"
            ]
        elif player_type == "fielder":
            self.urls = [
                "https://www.koreabaseball.com/Record/Player/Defense/Basic.aspx?sort=GAME_CN"
            ]
        elif player_type == "runner":
            self.urls = [
                "https://www.koreabaseball.com/Record/Player/Runner/Basic.aspx?sort=GAME_CN"
            ]

        if detail:
            self.urls = [self.urls[0]]

        self.player_type = player_type
        self.payload = {
            "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$smData": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$udpContent|ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
            "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeries$ddlSeries": "0",
            "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderByCol": "GAME_CN",
            "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderBy": "DESC",
            "__EVENTTARGET": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
        }

    def _parse(self, response):
        thead_tr = response.select_one("thead tr")
        if not thead_tr:
            self.logger.warning("No header datas found in response.")
            return None, None
        
        headers = ["P_ID"] + [th.get_text(strip=True) for th in thead_tr.find_all("th")]
        rows = [
            [re.search(r'playerId=(\d+)', tr.find("a")["href"]).group(1)] +
            [td.get_text(strip=True) for td in tr.find_all("td")]
            for tr in response.select("tbody tr")
        ]

        return headers, rows
    
    def fetch(self, season, date):
        result = {}
        for i, url in enumerate(self.urls):
            session, viewstate, eventvalidation = initiate_session(url)
            if session is None:
                self.logger.error(f"Could not initiate session for URL: {url}")
                return
    
            self.logger.info(f"Fetching {self.player_type} stats for season {season}...")
            self.payload["__VIEWSTATE"] = viewstate
            self.payload["__EVENTVALIDATION"] = eventvalidation
            self.payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeason$ddlSeason"] = str(season)

            file_path = f"player/{season}/{self.player_type}/season_summary"
            for page_num in range(1, 9999): 
                self.payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfPage"] = str(page_num)
    
                try:
                    response = fetch_html(url, self.payload, session)
                    if response is None:
                        self.logger.warning(f"No valid response for page {page_num}.")
                        continue
                    
                    headers, rows = self.parse(response)
                    if headers is None and rows is None:
                        self.logger.info(f"No rows returned for page {page_num}.")
                        break
                    
                    if headers and not rows:
                        self.logger.info(f"Last page reached at page {page_num}.")
                        break
                    
                    self.backup(str(response), f"{file_path}_{i}_{page_num}", "html")

                    for row in rows:
                        result.setdefault(row[0], {"LE_ID": 1, "SR_ID": 0, "SEASON_ID": season})
                        result[row[0]].update(convert_row_data(headers, row))
                except Exception as e:
                    self.logger.error(f"Error fetching {self.player_type} stats for {page_num}: {e}")
                
            session.close()

        return {file_path: list(result.values())}
    
    
class PlayerDetailStatsScraper(KBOBaseScraper):
    def __init__(self, player_type, record_type):
        super().__init__()

        if player_type == "hitter":
            self.url = "https://www.koreabaseball.com/Record/Player/HitterDetail/{type}.aspx?playerId={id}"
        elif player_type == "pitcher":
            self.url = "https://www.koreabaseball.com/Record/Player/PitcherDetail/{type}.aspx?playerId={id}"

        self.player_type = player_type
        self.record_type = record_type
        self.payload = {
            "__EVENTTARGET": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeries"
        }

    def _parse(self, response):
        thead_tr = response.select_one("thead tr")
        if not thead_tr:
            self.logger.warning("No header datas found in response.")
            return None, None
        
        headers = [th.get_text(strip=True) for th in thead_tr.find_all("th")]
        rows = [
            [td.get_text(strip=True) for td in tr.find_all("td")]
            for tr in response.select("tbody tr")
        ]
        headers[0] = "MO" if self.record_type == "daily" else "SIT"
        
        return headers, rows
    
    def fetch(self, season, date):
        result = {}
        players = PlayerSeasonStatsScraper(self.player_type, True).fetch(season, date)
        for player in players[f"player/{season}/{self.player_type}/season_summary"]:
            player_id = player.get("P_ID", None)

            url = self.url.format(id=player_id, type=self.record_type)
            session, viewstate, eventvalidation = initiate_session(url)
            if session is None:
                self.logger.error(f"Could not initiate session for URL: {url}")
                return
            
            self.logger.info(f"Fetching {self.record_type} stats for player id {player_id}...")
            self.payload["__VIEWSTATE"] = viewstate
            self.payload["__EVENTVALIDATION"] = eventvalidation
            self.payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlYear"] = str(season)

            player_data = []
            file_path = f"player/{season}/{self.player_type}/{player_id}/{self.record_type}"
            for series in [0, 1, 3, 4, 5, 7]: 
                self.payload["ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeries"] = str(series)
                try:
                    response = fetch_html(url, self.payload, session)
                    if response is None:
                        self.logger.warning(f"No valid response for series {series}.")
                        continue
                    
                    headers, rows = self.parse(response)
                    if not rows or rows[0][0] == "기록이 없습니다.":
                        self.logger.info(f"No rows returned for series {series}.")
                        continue

                    self.backup(str(response), f"{file_path}_{series}", "html")
                    
                    for row in rows:
                        data = {
                            "LE_ID": 1, 
                            "SR_ID": series, 
                            "SEASON_ID": season, 
                            "P_ID": player_id, 
                            "P_NM": player.get("P_NM", None)
                        }
                        data.update(convert_row_data(headers, row))
                        player_data.append(data)

                except Exception as e:
                    self.logger.error(f"Error fetching {self.record_type} stats for series {series}: {e}")
                    continue
                
                result.setdefault(file_path, player_data)
                session.close()
            
        return result
    
    