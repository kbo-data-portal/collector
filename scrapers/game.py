import sys
import json
from datetime import datetime
from requests.exceptions import RequestException

from config import logger
from config import URLS, PAYLOADS, HOME, AWAY
from config import Scraper, Game, Player

from scrapers import schedule

from utils.convert import convert_row_data
from utils.request import fetch_json_response
from utils.storage import save_scraped_data


def parse_player_stats(tables: list[dict]) -> list[list[str]]:
    """Parses nested table structures to extract player statistics."""
    combined_data = []

    try:
        parsed_tables = [
            [[cell["Text"] for cell in row["row"]] for row in table["rows"]]
            for table in tables
        ]
    except (KeyError, TypeError) as e:
        logger.error(f"Failed to parse table rows: {e}")
        return []

    for rows in zip(*parsed_tables):
        combined_data.append(sum(rows, []))
    
    return combined_data


def parse_hitter_stats(game_json: dict, game_id: str, player_stats: dict) -> None:
    """Parses hitter statistics from JSON and updates the player_stats dictionary."""
    innings = game_json.get("realMaxInning", 0)

    headers = ["G_ID", "H/A", "BAT", "POS", "선수명"]
    headers += [f"INN_{i}" for i in range(1, innings + 1)]
    headers += ["타수", "안타", "타점", "득점", "타율"]

    try:
        home_hitters = parse_player_stats([
            json.loads(game_json.get("arrHitter", [{}])[1].get("table1", "[]")),
            json.loads(game_json.get("arrHitter", [{}])[1].get("table2", "[]")),
            json.loads(game_json.get("arrHitter", [{}])[1].get("table3", "[]"))
        ])
        away_hitters = parse_player_stats([
            json.loads(game_json.get("arrHitter", [{}])[0].get("table1", "[]")),
            json.loads(game_json.get("arrHitter", [{}])[0].get("table2", "[]")),
            json.loads(game_json.get("arrHitter", [{}])[0].get("table3", "[]"))
        ])
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed for hitter stats: {e}")
        return

    player_stats[HOME][Player.HITTER].extend(
        [convert_row_data(headers, [game_id, "H"] + row) for row in home_hitters]
    )
    player_stats[AWAY][Player.HITTER].extend(
        [convert_row_data(headers, [game_id, "A"] + row) for row in away_hitters]
    )


def parse_pitcher_stats(game_json: dict, game_id: str, player_stats: dict) -> None:
    """Parses pitcher statistics from JSON and updates the player_stats dictionary."""
    headers = [
        "G_ID", "H/A", "선수명", "등판", "결과", "승", "패", "세", "이닝", "타자",
        "투구수", "타수", "피안타", "홈런", "4사구", "삼진", "실점", "자책", "평균자책점"
    ]

    try:
        home_pitchers = parse_player_stats([
            json.loads(game_json.get("arrPitcher", [{}])[1].get("table", "[]"))
        ])
        away_pitchers = parse_player_stats([
            json.loads(game_json.get("arrPitcher", [{}])[0].get("table", "[]"))
        ])
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed for pitcher stats: {e}")
        return

    player_stats[HOME][Player.PITCHER].extend(
        [convert_row_data(headers, [game_id, "H"] + row) for row in home_pitchers]
    )
    player_stats[AWAY][Player.PITCHER].extend(
        [convert_row_data(headers, [game_id, "A"] + row) for row in away_pitchers]
    )


def scrape_player_statistics(url: str, payload: dict) -> tuple | None:
    """Scrapes both hitter and pitcher stats from game stat endpoint."""
    logger.info(f"Starting to fetch player stats from: {url}")

    game_id = payload["gameId"]
    logger.info(f"Fetching stats for game ID {game_id}...")

    try:
        game_json = fetch_json_response(url, payload)
        print(f"Game JSON: {game_json}")
        if not game_json or int(game_json.get("code", 0)) != 100:
            logger.warning(f"No valid player data found for game {game_id}.")
            return
    except RequestException as e:
        logger.error(f"Failed request for player stats: {e}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format for player stats: {e}")
        return

    player_stats = {
        HOME: {Player.HITTER: [], Player.PITCHER: []},
        AWAY: {Player.HITTER: [], Player.PITCHER: []}
    }

    parse_hitter_stats(game_json, game_id, player_stats)
    parse_pitcher_stats(game_json, game_id, player_stats)

    return (
        player_stats[HOME][Player.HITTER] + player_stats[AWAY][Player.HITTER],
        player_stats[HOME][Player.PITCHER] + player_stats[AWAY][Player.PITCHER]
    )


def scrape_game_summary(url: str, payload: dict) -> list | None:
    """Scrapes the overall summary (runs/hits/errors/innings) for a game."""
    logger.info(f"Starting to fetch game summary from: {url}")

    game_id = payload["gameId"]
    logger.info(f"Fetching summary for game ID {game_id}...")

    try:
        game_json = fetch_json_response(url, payload)
        if not game_json or int(game_json.get("code", 0)) != 100:
            logger.warning(f"No valid summary data for game {game_id}.")
            return
    except RequestException as e:
        logger.error(f"Failed request for summary data: {e}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format for summary: {e}")
        return

    innings = game_json.get("maxInning", 0)

    headers = []
    rows = {HOME: [], AWAY: []}
    for key, value in game_json.items():
        if key == "maxInning":
            break
        if not key.startswith("table"):
            headers.append(key)
            rows[HOME].append(value)
            rows[AWAY].append(value)

    try:
        table_rows = parse_player_stats([
            json.loads(game_json.get("table1", "[]")),
            json.loads(game_json.get("table2", "[]")),
            json.loads(game_json.get("table3", "[]"))
        ])
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode summary tables: {e}")
        return

    full_headers = headers + ["H/A", "W/L", "W/L/T"] + \
        [f"INN_{i}" for i in range(1, innings + 1)] + ["R", "H", "E", "B"]
    
    return [
        convert_row_data(full_headers, rows[HOME] + ["H"] + table_rows[1]),
        convert_row_data(full_headers, rows[AWAY] + ["A"] + table_rows[0])
    ]


def run(
    target_season: int = None, 
    target_date: str | None = None, 
    file_format: str = "parquet"
) -> None:
    """Main runner for scraping KBO game summary and player data."""
    logger.info("Starting KBO game data scraping...")

    if target_season:
        start_date = datetime(target_season, 1, 1)
        end_date = datetime(target_season, 12, 31)
    else:
        start_date = datetime.strptime(target_date, "%Y%m%d") if target_date else datetime(2001, 4, 5)
        end_date = datetime.strptime(target_date, "%Y%m%d") if target_date else datetime.now()

    schedule_url = URLS[Scraper.SCHEDULE]
    schedule_payload = PAYLOADS[Scraper.SCHEDULE]
    schedule_data = schedule.scrape_schedule_data(schedule_url, schedule_payload, start_date, end_date)

    if not schedule_data:
        logger.warning("No schedule found. Exiting pipeline.")
        sys.exit(1)

    game_url = URLS[Scraper.GAME]
    game_payload = PAYLOADS[Scraper.GAME]
    daily_game_data = {}

    for game in schedule_data:
        game_id = game.get("G_ID")
        game_date = str(game.get("G_DT"))

        if not game_id:
            logger.warning("Missing game ID in schedule entry.")
            continue

        daily_game_data.setdefault(game_date, {
            Scraper.GAME: [],
            Player.HITTER: [],
            Player.PITCHER: []
        })
        
        game_payload["srId"] = str(game.get("SR_ID"))
        game_payload["seasonId"] = str(game.get("SEASON_ID"))
        game_payload["gameId"] = str(game_id)

        logger.info(f"Processing game for ID {game_id}...")

        summary = scrape_game_summary(game_url[Game.SUMMARY], game_payload)
        stats = scrape_player_statistics(game_url[Game.STAT], game_payload)

        if summary and stats:
            hitter_data, pitcher_data = stats
            daily_game_data[game_date][Scraper.GAME].extend(summary)
            daily_game_data[game_date][Player.HITTER].extend(hitter_data)
            daily_game_data[game_date][Player.PITCHER].extend(pitcher_data)
        else:
            logger.warning(f"No game data for game {game_id}.")

    for date_key, data_by_type in daily_game_data.items():
        path_prefix = f"game/{date_key[:4]}/{date_key}"
        save_scraped_data(data_by_type[Scraper.GAME], path_prefix, "summary", file_format)
        save_scraped_data(data_by_type[Player.HITTER], path_prefix, "hitter", file_format)
        save_scraped_data(data_by_type[Player.PITCHER], path_prefix, "pitcher", file_format)
