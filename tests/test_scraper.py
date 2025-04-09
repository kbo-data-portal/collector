from config import HOME
from config import Scraper, Game, Player

from scrapers.game import scrape_game_summary, scrape_player_statistics
from scrapers.player import scrape_player_data
from scrapers.schedule import scrape_schedule_data
from scrapers.team import scrape_team


def test_game(urls, payloads, columns, test_date):
    """
    Test the game scraping functions by verifying the extracted column headers.
    
    This test checks:
    1. Game details: Ensures the scraped data from the game detail endpoint matches expected columns.
    2. Game statistics: Verifies that both hitter and pitcher statistics contain the correct columns.
    """
    # Test game details scraping
    game_details = scrape_game_summary(
        url=urls[Scraper.GAME][Game.DETAIL], 
        payload=payloads[Scraper.GAME]
    )
    assert list(game_details[0].keys()) == columns[Scraper.GAME][Game.DETAIL]
    
    # Test game statistics scraping
    hitter_columns, pitcher_columns = scrape_player_statistics(
        url=urls[Scraper.GAME][Game.STAT], 
        payload=payloads[Scraper.GAME]
    )

    # Check hitter statistics columns
    assert list(hitter_columns[0].keys()) == columns[Scraper.GAME][Game.STAT][Player.HITTER]

    # Check pitcher statistics columns
    assert list(pitcher_columns[0].keys()) == columns[Scraper.GAME][Game.STAT][Player.PITCHER]


def test_player(urls, payloads, columns, test_date):
    """
    Test the player scraping functions by verifying the extracted column headers for both hitters and pitchers.
    
    This test checks:
    1. Hitter statistics: Ensures the scraped player data for hitters matches the expected columns.
    2. Pitcher statistics: Verifies that the player data for pitchers also contains the correct columns.
    """
    # Test hitter data scraping
    hitter_data = {}
    scrape_player_data(
        url=urls[Scraper.PLAYER][Player.HITTER][0], 
        payload=payloads[Scraper.PLAYER], 
        season=test_date.year, 
        player_datas=hitter_data
    )

    hitter_columns = list(hitter_data.values())[0]
    assert list(hitter_columns.keys()) == columns[Scraper.PLAYER][Player.HITTER]

    # Test pitcher data scraping
    pitcher_data = {}
    scrape_player_data(
        url=urls[Scraper.PLAYER][Player.PITCHER][0], 
        payload=payloads[Scraper.PLAYER], 
        season=test_date.year, 
        player_datas=pitcher_data
    )

    pitcher_columns = list(pitcher_data.values())[0]
    assert list(pitcher_columns.keys()) == columns[Scraper.PLAYER][Player.PITCHER]


def test_schedule(urls, payloads, columns, test_date):
    """
    Test the schedule scraping function by verifying the extracted column headers for the schedule data.
    
    This test ensures:
    1. The scraped schedule data matches the expected columns for the given date.
    """
    schedule_data = scrape_schedule_data(
        url=urls[Scraper.SCHEDULE], 
        payload=payloads[Scraper.SCHEDULE], 
        start_date=test_date, 
        end_date=test_date
    )
    assert list(schedule_data[0].keys()) == columns[Scraper.SCHEDULE]


def test_team():
    assert True
