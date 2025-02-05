import json
from utils.convert import convert_row_data
from utils.request import parse_json_from_url
from utils.storage import read_scraped_data, save_scraped_data

def extract_data(tables):
    """
    Extracts and combines statistics from multiple tables.
    """
    combined_data = []
    
    table_rows = [
        [[cell["Text"] for cell in row["row"]] for row in table["rows"]]
        for table in tables
    ]
    
    for row_set in zip(*table_rows):
        combined_data.append(sum(row_set, []))
    
    return combined_data

def scrape_game_details(url, series_id, season_id, game_id, game_datas):
    """
    Scrapes Korean baseball game detail for the specified game.
    """
    print(f"Scraping game detail for {game_id}...")
    payload = {
        "leId": "1",
        "srId": str(series_id),
        "seasonId": str(season_id), 
        "gameId": str(game_id)

    }

    game_datas.setdefault("HOME", [])
    game_datas.setdefault("AWAY", [])

    json_data = parse_json_from_url(url, payload)
    if not json_data or int(json_data.get("code", 0)) != 100:
        return

    innings = json_data["maxInning"]

    headers, rows = [], {"HOME": [], "AWAY": []}
    for header, row in json_data.items():
        if header == "maxInning":
            break
        if not header.startswith("table"):
            headers.append(header)
            rows["HOME"].append(row)
            rows["AWAY"].append(row)

    data = extract_data([
        json.loads(json_data["table1"]),
        json.loads(json_data["table2"]),
        json.loads(json_data["table3"])
    ])
    headers += ["W/L", "W/L/T"] + [f"INN_{inn}" for inn in range(1, innings + 1)] + ["R", "H", "E", "B"]

    game_datas["HOME"].append(convert_row_data(headers, rows["HOME"] + data[1]))
    game_datas["AWAY"].append(convert_row_data(headers, rows["AWAY"] + data[0]))

def scrape_player_stats(url, series_id, season_id, game_id, player_datas):
    """
    Scrapes hitter and pitcher statistics for a specific Korean baseball game.
    Extracts both home and away team data.
    """
    print(f"Scraping player stats for {game_id}...")
    payload = {
        "leId": "1",
        "srId": str(series_id),
        "seasonId": str(season_id), 
        "gameId": str(game_id)

    }

    player_datas.setdefault("HOME", {"hitter": [], "pitcher": []})
    player_datas.setdefault("AWAY", {"hitter": [], "pitcher": []})
    
    json_data = parse_json_from_url(url, payload)
    if not json_data or int(json_data.get("code", 0)) != 100:
        return

    innings = json_data["realMaxInning"]

    hitter_headers = ["G_ID", "BAT", "POS", "선수명"]
    hitter_headers += [f"INN_{inn}" for inn in range(1, innings + 1)]
    hitter_headers += ["타수", "안타", "타점", "득점", "타율"]

    home_hitters = extract_data([
        json.loads(json_data["arrHitter"][1]["table1"]),
        json.loads(json_data["arrHitter"][1]["table2"]),
        json.loads(json_data["arrHitter"][1]["table3"])
    ])
    away_hitters = extract_data([
        json.loads(json_data["arrHitter"][0]["table1"]),
        json.loads(json_data["arrHitter"][0]["table2"]),
        json.loads(json_data["arrHitter"][0]["table3"])
    ])
    
    player_datas["HOME"]["hitter"].extend(
        [convert_row_data(hitter_headers, [game_id, "HOME"] + player) for player in home_hitters]
    )
    player_datas["AWAY"]["hitter"].extend(
        [convert_row_data(hitter_headers, [game_id, "AWAY"] + player) for player in away_hitters]
    )

    pitcher_headers = ["G_ID", "H/A", "선수명", "등판", "결과", "승", "패", "세", "이닝", "타자", "투구수", 
                       "타수", "피안타", "홈런", "4사구", "삼진", "실점", "자책", "평균자책점"]

    home_pitchers = extract_data([json.loads(json_data["arrPitcher"][1]["table"])])
    away_pitchers = extract_data([json.loads(json_data["arrPitcher"][0]["table"])])

    player_datas["HOME"]["pitcher"].extend(
        [convert_row_data(pitcher_headers, [game_id, "HOME"] + player) for player in home_pitchers]
    )
    player_datas["AWAY"]["pitcher"].extend(
        [convert_row_data(pitcher_headers, [game_id, "AWAY"] + player) for player in away_pitchers]
    )

def run(schedule_path):
    """ 
    Scrapes detailed game data, including schedule and player statistics.
    """
    schedule_datas = read_scraped_data(schedule_path)
    game_datas, player_datas = {}, {}
    for schedule in schedule_datas:
        series_id, season_id, game_id = schedule["SR_ID"], schedule["SEASON_ID"], schedule["G_ID"]
        print(f"Starting to scrape Korean baseball schedule data from {game_id}...")

        url = "https://www.koreabaseball.com/ws/Schedule.asmx/GetScoreBoardScroll"

        print(f"Scraping data from: {url}")
        scrape_game_details(url, series_id, season_id, game_id, game_datas)

        url = "https://www.koreabaseball.com/ws/Schedule.asmx/GetBoxScoreScroll"

        print(f"Scraping data from: {url}")
        scrape_player_stats(url, series_id, season_id, game_id, player_datas)

    save_scraped_data(game_datas["HOME"] + game_datas["AWAY"], "game_details")
    save_scraped_data(player_datas["HOME"]["hitter"] + player_datas["AWAY"]["hitter"], "batting_stats_game")
    save_scraped_data(player_datas["HOME"]["pitcher"] + player_datas["AWAY"]["pitcher"], "pitching_stats_game")

