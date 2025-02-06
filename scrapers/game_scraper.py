import json
from requests.exceptions import RequestException

from config import logger
from config import URLS, PAYLOADS, FILENAMES, HOME, AWAY
from config import Scraper, Game, Player

from utils.convert import convert_row_data
from utils.request import parse_json_from_url
from utils.storage import read_scraped_data, save_scraped_data

def extract_data(tables):
    """
    Extracts and combines statistics from multiple tables.
    """
    combined_data = []
    
    try:
        table_rows = [
            [[cell["Text"] for cell in row["row"]] for row in table["rows"]]
            for table in tables
        ]
    except (KeyError, TypeError) as e:
        logger.error(f"Error extracting table data: {e}")
        return []

    for row_set in zip(*table_rows):
        combined_data.append(sum(row_set, []))
    
    return combined_data

def extract_hitter_stats(data, game_id, player_datas):
    """
    Extracts hitter statistics for a specific Korean baseball game.
    """
    innings = data.get("realMaxInning", 0)

    headers = ["G_ID", "BAT", "POS", "선수명"]
    headers += [f"INN_{inn}" for inn in range(1, innings + 1)]
    headers += ["타수", "안타", "타점", "득점", "타율"]

    try:
        home = extract_data([
            json.loads(data.get("arrHitter", [{}])[1].get("table1", "[]")),
            json.loads(data.get("arrHitter", [{}])[1].get("table2", "[]")),
            json.loads(data.get("arrHitter", [{}])[1].get("table3", "[]"))
        ])
        away = extract_data([
            json.loads(data.get("arrHitter", [{}])[0].get("table1", "[]")),
            json.loads(data.get("arrHitter", [{}])[0].get("table2", "[]")),
            json.loads(data.get("arrHitter", [{}])[0].get("table3", "[]"))
        ])
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding hitter data for game {game_id}: {e}")
        return

    player_datas[HOME][Player.HITTER].extend(
        [convert_row_data(headers, [game_id, "H"] + player) 
         for player in home]
    )
    player_datas[AWAY][Player.HITTER].extend(
        [convert_row_data(headers, [game_id, "A"] + player) 
         for player in away]
    )

def extract_pitcher_stats(data, game_id, player_datas):
    """
    Extracts pitcher statistics for a specific Korean baseball game.
    """
    headers = ["G_ID", "H/A", "선수명", "등판", "결과", "승", "패", "세", 
               "이닝", "타자", "투구수", "타수", "피안타", "홈런", "4사구", 
               "삼진", "실점", "자책", "평균자책점"]

    try:
        home = extract_data([json.loads(data.get("arrPitcher", [{}])[1].get("table", "[]"))])
        away = extract_data([json.loads(data.get("arrPitcher", [{}])[0].get("table", "[]"))])
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding pitcher data for game {game_id}: {e}")
        return

    player_datas[HOME][Player.PITCHER].extend(
        [convert_row_data(headers, [game_id, "H"] + player) 
         for player in home]
    )
    player_datas[AWAY][Player.PITCHER].extend(
        [convert_row_data(headers, [game_id, "A"] + player) 
         for player in away]
    )

def scrape_game_stats(url, payload, player_datas):
    """
    Scrapes hitter and pitcher statistics for a specific Korean baseball game.
    Extracts both home and away team data.
    """
    logger.info(f"Scraping data from: {url}")

    game_id = payload["gameId"]
    logger.info(f"Scraping game detail for {game_id}...")

    player_datas.setdefault(HOME, {Player.HITTER: [], Player.PITCHER: []})
    player_datas.setdefault(AWAY, {Player.HITTER: [], Player.PITCHER: []})

    try:
        json_data = parse_json_from_url(url, payload)
        if not json_data or int(json_data.get("code", 0)) != 100:
            logger.warning(f"No valid data found for player stats in game {game_id}. Skipping...")
            return
    except RequestException as e:
        logger.error(f"Error fetching player data for {game_id}: {e}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON for player stats in game {game_id}: {e}")
        return
    
    extract_hitter_stats(json_data, game_id, player_datas)
    extract_pitcher_stats(json_data, game_id, player_datas)

def scrape_game_details(url, payload, game_datas):
    """
    Scrapes Korean baseball game detail for the specified game.
    """
    logger.info(f"Scraping data from: {url}")

    game_id = payload["gameId"]
    logger.info(f"Scraping game detail for {game_id}...")
    
    game_datas.setdefault(HOME, [])
    game_datas.setdefault(AWAY, [])

    try:
        json_data = parse_json_from_url(url, payload)
        if not json_data or int(json_data.get("code", 0)) != 100:
            logger.warning(f"No valid data found for game {game_id}. Skipping...")
            return
    except RequestException as e:
        logger.error(f"Error fetching game data for {game_id}: {e}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON for game {game_id}: {e}")
        return

    innings = json_data.get("maxInning", 0)

    headers, rows = [], {HOME: [], AWAY: []}
    for header, row in json_data.items():
        if header == "maxInning":
            break
        if not header.startswith("table"):
            headers.append(header)
            rows[HOME].append(row)
            rows[AWAY].append(row)

    try:
        data = extract_data([
            json.loads(json_data.get("table1", "[]")),
            json.loads(json_data.get("table2", "[]")),
            json.loads(json_data.get("table3", "[]"))
        ])
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding table data for game {game_id}: {e}")
        return

    headers += ["W/L", "W/L/T"] + [f"INN_{inn}" for inn in range(1, innings + 1)] + ["R", "H", "E", "B"]

    game_datas[HOME].append(convert_row_data(headers, rows[HOME] + data[1]))
    game_datas[AWAY].append(convert_row_data(headers, rows[AWAY] + data[0]))

def run(filename, format):
    """ 
    Scrapes detailed game data, including schedule and player statistics.
    """
    schedule_datas = read_scraped_data(filename)

    urls = URLS[Scraper.GAME]
    filenames = FILENAMES[Scraper.GAME]
    payload = PAYLOADS[Scraper.GAME]

    game_datas, player_datas = {}, {}
    for schedule in schedule_datas:
        if not "G_ID" in schedule:
            logger.error(f"Invalid date format. Please check the {filename}")
            exit(1)
        payload["srId"] = str(schedule["SR_ID"]),
        payload["seasonId"] = str(schedule["SEASON_ID"])
        payload["gameId"] = str(schedule["G_ID"])
        
        logger.info(f"Starting to scrape Korean baseball schedule data from {payload["gameId"]}...")

        scrape_game_details(urls[Game.DETAIL], payload, game_datas)
        scrape_game_stats(urls[Game.STAT], payload, player_datas)
    
    game_datas[Game.DETAIL] = game_datas[HOME] + game_datas[AWAY]
    save_scraped_data(game_datas[Game.DETAIL], filenames[Game.DETAIL], format)
    
    player_datas.setdefault(Player.HITTER, [])
    player_datas[Player.HITTER].extend(player_datas[HOME][Player.HITTER])
    player_datas[Player.HITTER].extend(player_datas[AWAY][Player.HITTER])
    save_scraped_data(player_datas[Player.HITTER], 
                      filenames[Game.STAT][Player.HITTER], format)
    
    player_datas.setdefault(Player.PITCHER, [])
    player_datas[Player.PITCHER].extend(player_datas[HOME][Player.PITCHER])
    player_datas[Player.PITCHER].extend(player_datas[AWAY][Player.PITCHER])
    save_scraped_data(player_datas[Player.PITCHER], 
                      filenames[Game.STAT][Player.PITCHER], format)

