from scrapers.game import GameScheduleScraper, GameResultScraper
from scrapers.player import PlayerSeasonStatsScraper


def _test_scraper(scraper, test_season, test_date, column):
    """
    Helper function to test a scraper by verifying the extracted column headers.
    
    This function checks that the scraped data for each fetched entry has the expected column structure.
    """
    fetch_data = scraper.fetch(test_season, test_date)
    for value in fetch_data.values():
        assert list(value[0].keys()) == column


def test_schedule(test_season, test_date):
    """
    Test the schedule scraping function by verifying the extracted column headers for the schedule data.
    
    This test ensures:
    1. The scraped schedule data matches the expected columns for the given date.
    """
    column = ["LE_ID", "SR_ID", "SEASON_ID", "G_DT", "G_DT_TXT", "G_ID", "HEADER_NO", "G_TM", "S_NM", "AWAY_ID", "HOME_ID", "AWAY_NM", "HOME_NM", "T_PIT_P_ID", "T_PIT_P_NM", "B_PIT_P_ID", "B_PIT_P_NM", "W_PIT_P_ID", "W_PIT_P_NM", "SV_PIT_P_ID", "SV_PIT_P_NM", "L_PIT_P_ID", "L_PIT_P_NM", "T_D_PIT_P_ID", "T_D_PIT_P_NM", "B_D_PIT_P_ID", "B_D_PIT_P_NM", "GAME_STATE_SC", "CANCEL_SC_ID", "CANCEL_SC_NM", "GAME_INN_NO", "GAME_TB_SC", "GAME_TB_SC_NM", "GAME_RESULT_CK", "T_SCORE_CN", "B_SCORE_CN", "TV_IF", "VS_GAME_CN", "STRIKE_CN", "BALL_CN", "OUT_CN", "B1_BAT_ORDER_NO", "B2_BAT_ORDER_NO", "B3_BAT_ORDER_NO", "T_P_ID", "T_P_NM", "B_P_ID", "B_P_NM", "GAME_SC_ID", "GAME_SC_NM", "IE_ENTRY_CK", "START_PIT_CK", "T_GROUP_SC", "T_RANK_NO", "B_GROUP_SC", "B_RANK_NO", "ROUND_SC", "DETAIL_SC", "GAME_NO", "LINEUP_CK", "VOD_CK", "KBOT_SE", "SCORE_CK", "CHECK_SWING_CK"]
    _test_scraper(GameScheduleScraper(), test_season, test_date, column)


def test_game(test_season, test_date):
    """
    Test the game scraping functions by verifying the extracted column headers.
    
    This test checks:
    1. Game details: Ensures the scraped data from the game detail endpoint matches expected columns.
    2. Game statistics: Verifies that both hitter and pitcher statistics contain the correct columns.
    """
    column = ["IS_HOME", "LE_ID", "SR_ID", "G_ID", "G_DT", "SEASON_ID", "HOME_NM", "HOME_ID", "AWAY_NM", "AWAY_ID", "S_NM", "CROWD_CN", "H_W_CN", "H_L_CN", "H_D_CN", "A_W_CN", "A_L_CN", "A_D_CN", "T_SCORE_CN", "B_SCORE_CN", "START_TM", "END_TM", "USE_TM", "FULL_HOME_NM", "FULL_AWAY_NM", "INN_1", "INN_2", "INN_3", "INN_4", "INN_5", "INN_6", "INN_7", "INN_8", "INN_9", "INN_10", "INN_11", "INN_12", "INN_13", "INN_14", "INN_15", "R", "H", "E", "B"]
    _test_scraper(GameResultScraper(), test_season, test_date, column)


def test_player(test_season, test_date):
    """
    Test the player scraping functions by verifying the extracted column headers for both hitters and pitchers.
    
    This test checks:
    1. Hitter statistics: Ensures the scraped player data for hitters matches the expected columns.
    2. Pitcher statistics: Verifies that the player data for pitchers also contains the correct columns.
    """
    columns = [
        ["LE_ID", "SR_ID", "SEASON_ID", "P_ID", "P_NM", "TEAM_NM", "AVG", "G", "PA", "AB", "R", "H", "2B", "3B", "HR", "TB", "RBI", "SAC", "SF"],
        ["LE_ID", "SR_ID", "SEASON_ID", "P_ID", "P_NM", "TEAM_NM", "ERA", "G", "W", "L", "SV", "HLD", "WPCT", "IP", "H", "HR", "BB", "HBP", "SO", "R", "ER", "WHIP"],
        ["LE_ID", "SR_ID", "SEASON_ID", "P_ID", "P_NM", "TEAM_NM", "G", "SBA", "SB", "CS", "SB%", "OOB", "PKO"],
        ["LE_ID", "SR_ID", "SEASON_ID", "P_ID", "P_NM", "TEAM_NM", "POS", "G", "GS", "IP", "E", "PKO", "PO", "A", "DP", "FPCT", "PB", "SB", "CS", "CS%"]
    ]
    player_types = ["hitter", "pitcher", "runner", "fielder"]
    for col, pt in zip(columns, player_types):
        _test_scraper(PlayerSeasonStatsScraper(pt, True), test_season, test_date, col)

