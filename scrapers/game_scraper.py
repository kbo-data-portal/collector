import json
from datetime import datetime
from requests.exceptions import RequestException

from config import logger
from config import URLS, PAYLOADS, HOME, AWAY
from config import Scraper, Game, Player

from scrapers.schedule_scraper import scrape_schedule

from utils.convert import convert_row_data
from utils.request import parse_json_from_url
from utils.storage import save_scraped_data

def extract_data(tables):
    """
    Extracts and merges data from multiple nested table structures.
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

def extract_hitter_stats(data, game_id, player_data):
    """
    Extracts hitter statistics from a game and appends them to the player_data dictionary.
    """
    innings = data.get("realMaxInning", 0)

    headers = ["G_ID", "H/A", "BAT", "POS", "선수명"]
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

    player_data[HOME][Player.HITTER].extend(
        [convert_row_data(headers, [game_id, "H"] + player) 
         for player in home]
    )
    player_data[AWAY][Player.HITTER].extend(
        [convert_row_data(headers, [game_id, "A"] + player) 
         for player in away]
    )

def extract_pitcher_stats(data, game_id, player_data):
    """
    Extracts pitcher statistics from a game and appends them to the player_data dictionary.
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

    player_data[HOME][Player.PITCHER].extend(
        [convert_row_data(headers, [game_id, "H"] + player) 
         for player in home]
    )
    player_data[AWAY][Player.PITCHER].extend(
        [convert_row_data(headers, [game_id, "A"] + player) 
         for player in away]
    )

def scrape_game_stats(url, payload):
    """
    Scrapes the hitter and pitcher statistics for a specific game.
    """
    logger.info(f"Scraping data from: {url}")

    player_data = {}

    game_id = payload["gameId"]
    logger.info(f"Scraping game detail for {game_id}...")

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

    player_data.setdefault(HOME, {Player.HITTER: [], Player.PITCHER: []})
    player_data.setdefault(AWAY, {Player.HITTER: [], Player.PITCHER: []})
    
    extract_hitter_stats(json_data, game_id, player_data)
    extract_pitcher_stats(json_data, game_id, player_data)

    hitter_data = player_data[HOME][Player.HITTER] + player_data[AWAY][Player.HITTER]
    pitcher_data = player_data[HOME][Player.PITCHER] + player_data[AWAY][Player.PITCHER]

    return hitter_data, pitcher_data

def scrape_game_details(url, payload):
    """
    Scrapes summary data (runs, hits, errors, innings) for a specific game.
    """
    logger.info(f"Scraping data from: {url}")

    game_id = payload["gameId"]
    logger.info(f"Scraping game detail for {game_id}...")

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
    home_data = convert_row_data(headers, rows[HOME] + data[1])
    away_data = convert_row_data(headers, rows[AWAY] + data[0])

    return [home_data, away_data]

def run(date, format="parquet"):
    """
    Runs the data scraping pipeline for KBO game details and player statistics.
    """
    logger.info("Starting to scrape Korean baseball game data...")

    start_date=datetime(2001, 4, 5)
    end_date = datetime.now()
    if date:
        start_date = datetime.strptime(date, "%Y%m%d")
        end_date = datetime.strptime(date, "%Y%m%d")

    url = URLS[Scraper.SCHEDULE]
    payload = PAYLOADS[Scraper.SCHEDULE]

    schedule_data = scrape_schedule(url, payload, start_date, end_date)
    if not schedule_data:
        logger.warning("No schedule data found for the specified date range.")
        return False

    urls = URLS[Scraper.GAME]
    payload = PAYLOADS[Scraper.GAME]

    game_data = {}
    for schedule in schedule_data:
        game_id = schedule.get("G_ID")
        game_date = str(schedule.get("G_DT"))

        if not game_id:
            logger.warning("No game ID found in schedule data. Skipping...")
            continue

        game_data.setdefault(game_date, {
            Scraper.GAME: [],
            Player.HITTER: [],
            Player.PITCHER: []
        })

        payload["srId"] = str(schedule.get("SR_ID")),
        payload["seasonId"] = str(schedule.get("SEASON_ID"))
        payload["gameId"] = str(game_id)
        
        logger.info(f"Scraping game data for ID {payload['gameId']}...")

        summary_data = scrape_game_details(urls[Game.DETAIL], payload)
        hitter_data, pitcher_data = scrape_game_stats(urls[Game.STAT], payload)

        if summary_data and hitter_data and pitcher_data:
            game_data[game_date][Scraper.GAME].extend(summary_data)
            game_data[game_date][Player.HITTER].extend(hitter_data)
            game_data[game_date][Player.PITCHER].extend(pitcher_data)
        else:
            logger.warning(f"No data found for game {schedule["G_ID"]}. Skipping...")
            return False

    for target_date, target_data in game_data.items():
        data_type = f"game/{target_date[:4]}/{target_date}"
        save_scraped_data(target_data[Scraper.GAME], data_type, "summary", format)
        save_scraped_data(target_data[Player.HITTER], data_type, "hitters", format)
        save_scraped_data(target_data[Player.PITCHER], data_type, "pitchers", format)

    return True
