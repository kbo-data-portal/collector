from config import HOME
from config import Scraper, Game, Player

from scrapers.game_scraper import scrape_game_details, scrape_game_stats
from scrapers.player_scraper import scrape_player
from scrapers.schedule_scraper import scrape_schedule
from scrapers.team_scraper import scrape_team

def test_game(urls, payloads, columns):
    """
    Test the game scraping functions by verifying the extracted column headers.
    
    This test checks:
    1. Game details: Ensures the scraped data from the game detail endpoint matches expected columns.
    2. Game statistics: Verifies that both hitter and pitcher statistics contain the correct columns.
    """
    # Test game details scraping
    test_data = scrape_game_details(
        url=urls[Scraper.GAME][Game.DETAIL], 
        payload=payloads[Scraper.GAME]
    )
    assert list(test_data[0].keys()) == columns[Scraper.GAME][Game.DETAIL]
    
    # Test game statistics scraping
    test_hitter, test_pitcher = scrape_game_stats(
        url=urls[Scraper.GAME][Game.STAT], 
        payload=payloads[Scraper.GAME]
    )

    # Check hitter statistics columns
    assert list(test_hitter[0].keys()) == columns[Scraper.GAME][Game.STAT][Player.HITTER]

    # Check pitcher statistics columns
    assert list(test_pitcher[0].keys()) == columns[Scraper.GAME][Game.STAT][Player.PITCHER]

def test_player(urls, payloads, columns):
    """
    Test the player scraping functions by verifying the extracted column headers for both hitters and pitchers.
    
    This test checks:
    1. Hitter statistics: Ensures the scraped player data for hitters matches the expected columns.
    2. Pitcher statistics: Verifies that the player data for pitchers also contains the correct columns.
    """
    # Test hitter data scraping
    test_data = {}
    scrape_player(
        url=urls[Scraper.PLAYER][Player.HITTER][0], 
        payload=payloads[Scraper.PLAYER], 
        season=2011, 
        player_data=test_data
    )

    test_hitter = list(test_data.values())[0]
    assert list(test_hitter.keys()) == columns[Scraper.PLAYER][Player.HITTER]

    # Test pitcher data scraping
    test_data = {}
    scrape_player(
        url=urls[Scraper.PLAYER][Player.PITCHER][0], 
        payload=payloads[Scraper.PLAYER], 
        season=2011, 
        player_data=test_data
    )

    test_pitcher = list(test_data.values())[0]
    assert list(test_pitcher.keys()) == columns[Scraper.PLAYER][Player.PITCHER]

def test_schedule(urls, payloads, columns, date):
    """
    Test the schedule scraping function by verifying the extracted column headers for the schedule data.
    
    This test ensures:
    1. The scraped schedule data matches the expected columns for the given date.
    """
    test_data = scrape_schedule(
        url=urls[Scraper.SCHEDULE], 
        payload=payloads[Scraper.SCHEDULE], 
        start_date=date, 
        end_date=date
    )
    assert list(test_data[0].keys()) == columns[Scraper.SCHEDULE]

def test_team():
    assert True
