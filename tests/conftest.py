import pytest
from datetime import datetime

from config import URLS, PAYLOADS
from config import Scraper, Game, Player

@pytest.fixture
def urls():
    return URLS

@pytest.fixture
def payloads():
    payload = PAYLOADS
    payload[Scraper.GAME].update({
        "srId": "7",
        "seasonId": "2011",
        "gameId": "20111031SKSS0"
    })
    return payload

@pytest.fixture
def columns():
    return {
        Scraper.GAME: {
            Game.DETAIL: [
                "LE_ID", "SR_ID", "G_ID", "G_DT", "SEASON_ID", "HOME_NM", "HOME_ID", 
                "AWAY_NM", "AWAY_ID", "S_NM", "CROWD_CN", "H_W_CN", "H_L_CN", "H_D_CN", 
                "A_W_CN", "A_L_CN", "A_D_CN", "T_SCORE_CN", "B_SCORE_CN", "START_TM", 
                "END_TM", "USE_TM", "FULL_HOME_NM", "FULL_AWAY_NM", "H_INITIAL_LK", 
                "A_INITIAL_LK", "W_L", "W_L_T", "INN_1", "INN_2", "INN_3", "INN_4", 
                "INN_5", "INN_6", "INN_7", "INN_8", "INN_9", "INN_10", "INN_11", 
                "INN_12", "INN_13", "INN_14", "INN_15", "R", "H", "E", "B"
            ],
            Game.STAT: {
                Player.HITTER: [
                    "G_ID", "BAT", "POS", "P_NM", "INN_1", "INN_2", "INN_3", "INN_4", 
                    "INN_5", "INN_6", "INN_7", "INN_8", "INN_9", "AB", "H", "RBI", 
                    "R", "AVG"
                ],
                Player.PITCHER: [
                    "G_ID", "H_A", "P_NM", "POS", "W_L", "W", "L", "SV", "IP", "TBF", 
                    "NP", "AB", "H", "HR", "BB", "SO", "R", "ER", "ERA"
                ]
            }
        },
        Scraper.PLAYER: {
            Player.HITTER: [
                "SEASON_ID", "P_NM", "TEAM_NM", "AVG", "G", "PA", "AB", "R", "H", 
                "2B", "3B", "HR", "TB", "RBI", "SAC", "SF"
            ],
            Player.PITCHER: [
                "SEASON_ID", "P_NM", "TEAM_NM", "ERA", "G", "W", "L", "SV", "HLD", 
                "WPCT", "IP", "H", "HR", "BB", "HBP", "SO", "R", "ER", "WHIP"
            ],
            Player.FIELDER: [],
            Player.RUNNER: []
        },
        Scraper.SCHEDULE: [
            "LE_ID", "SR_ID", "SEASON_ID", "G_DT", "G_DT_TXT", "G_ID", "HEADER_NO", 
            "G_TM", "S_NM", "AWAY_ID", "HOME_ID", "AWAY_NM", "HOME_NM", "T_PIT_P_ID", 
            "T_PIT_P_NM", "B_PIT_P_ID", "B_PIT_P_NM", "W_PIT_P_ID", "W_PIT_P_NM", 
            "SV_PIT_P_ID", "SV_PIT_P_NM", "L_PIT_P_ID", "L_PIT_P_NM", "T_D_PIT_P_ID", 
            "T_D_PIT_P_NM", "B_D_PIT_P_ID", "B_D_PIT_P_NM", "GAME_STATE_SC", "CANCEL_SC_ID", 
            "CANCEL_SC_NM", "GAME_INN_NO", "GAME_TB_SC", "GAME_TB_SC_NM", "GAME_RESULT_CK", 
            "T_SCORE_CN", "B_SCORE_CN", "TV_IF", "VS_GAME_CN", "STRIKE_CN", "BALL_CN", 
            "OUT_CN", "B1_BAT_ORDER_NO", "B2_BAT_ORDER_NO", "B3_BAT_ORDER_NO", "T_P_ID", 
            "T_P_NM", "B_P_ID", "B_P_NM", "GAME_SC_ID", "GAME_SC_NM", "IE_ENTRY_CK", 
            "START_PIT_CK", "T_GROUP_SC", "T_RANK_NO", "B_GROUP_SC", "B_RANK_NO", 
            "ROUND_SC", "DETAIL_SC", "GAME_NO", "LINEUP_CK", "VOD_CK", "KBOT_SE", "SCORE_CK"
        ]
    }

@pytest.fixture
def date():
    return datetime.strptime("20111031", "%Y%m%d")
