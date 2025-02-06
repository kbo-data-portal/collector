import os
import logging
import time
from enum import Enum

# Enum Definitions
class Scraper(Enum):
    GAME = "game"
    PLAYER = "player"
    SCHEDULE = "schedule"
    TEAM = "team"

class Game(Enum):
    DETAIL = "detail"
    STAT = "stat"

class Player(Enum):
    HITTER = "hitter"
    PITCHER = "pitcher"
    FIELDER = "fielder"
    RUNNER = "runner"

# Constants
NOW = time.strftime("%Y-%m-%d_%H-%M-%S")
HOME = "home"
AWAY = "away"

# Directories and Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", NOW)
LOG_DIR = os.path.join(BASE_DIR, "logs", NOW)

# URL and Payload Configuration
URLS = {
    Scraper.GAME: {
        Game.DETAIL: "https://www.koreabaseball.com/ws/Schedule.asmx/GetScoreBoardScroll",
        Game.STAT: "https://www.koreabaseball.com/ws/Schedule.asmx/GetBoxScoreScroll"
    },
    Scraper.PLAYER: {
        Player.HITTER: [
            "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic2.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/HitterBasic/Detail1.aspx?sort=GAME_CN"
        ],
        Player.PITCHER: [
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic2.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Detail1.aspx?sort=GAME_CN",
            "https://www.koreabaseball.com/Record/Player/PitcherBasic/Detail2.aspx?sort=GAME_CN"
        ]
    },
    Scraper.SCHEDULE: "https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList"
}

PAYLOADS = {
    Scraper.GAME: {
        "leId": "1",
        "srId": None,
        "seasonId": None,
        "gameId": None
    },
    Scraper.PLAYER: {
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$smData": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$udpContent|ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$ddlSeries$ddlSeries": "0",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderByCol": "GAME_CN",
        "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$hfOrderBy": "DESC",
        "__EVENTTARGET": "ctl00$ctl00$ctl00$cphContents$cphContents$cphContents$lbtnOrderBy",
        "__VIEWSTATE": None,
        "__EVENTVALIDATION": None
    },
    Scraper.SCHEDULE: {
        "leId": "1",
        "srId": "0,1,3,4,5,6,7,8,9",
        "date": None
    }
}

FILENAMES = {
    Scraper.GAME: {
        Game.DETAIL: "game_details",
        Game.STAT: {
            Player.HITTER: "batting_stats_game",
            Player.PITCHER: "pitching_stats_game"
        }
    },
    Scraper.PLAYER: {
        Player.HITTER: "batting_stats_player",
        Player.PITCHER: "pitching_stats_player",
        Player.FIELDER: "fielding_stats_player",
        Player.RUNNER: "running_stats_player"
    },
    Scraper.SCHEDULE: "game_schedules"
}

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

create_directory(OUTPUT_DIR)
create_directory(LOG_DIR)

# Logger Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO) 
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

file_handler = logging.FileHandler(os.path.join(LOG_DIR, "run.log"))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
