import os
import argparse
import textwrap
from datetime import datetime

from config import logger
from config import FILENAMES
from config import Scraper, Player

from scrapers import (
    game_scraper,
    player_scraper,
    schedule_scraper,
    team_scraper
)

def scrape_game_data_command(args):
    if args.path:
        game_scraper.run(args.path, args.format)
    else:
        scrape_schedule_data_command(args)
        filename = f"{FILENAMES[Scraper.SCHEDULE]}.{args.format}"
        game_scraper.run(filename, args.format)

def scrape_player_data_command(args):
    if args.player:
        player_scraper.run(Player(args.player), args.season, args.format)
    else:
        player_scraper.run(Player.HITTER, args.season, args.format)
        player_scraper.run(Player.PITCHER, args.season, args.format)

def scrape_schedule_data_command(args):
    if args.full:
        schedule_scraper.run(
            start_date=datetime.strptime("20010405", "%Y%m%d"), 
            end_date=datetime.now(),
            format=args.format
        )
    else:
        if args.date:
            try:
                target_date = datetime.strptime(args.date, "%Y%m%d")
            except ValueError:
                logger.error("Invalid date format. Please use YYYYMMDD.")
                exit(1)
        else:
            target_date = datetime.now()
        schedule_scraper.run(
            start_date=target_date, 
            end_date=target_date,
            format=args.format
        )

def scrape_team_data_command(args):
    team_scraper.run()

def main():
    parser = argparse.ArgumentParser(
        description="KBO Data Scraping Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Select a command")

    parser.add_argument(
        "-f", "--format", 
        type=str, choices=["parquet", "json", "csv"], 
        default="parquet", 
        help="Output file format. Choose from 'parquet', 'json', or 'csv'. Default is 'parquet'."
    )

    # Game Parser
    game_parser = subparsers.add_parser("game", 
        help="KBO Game Data Scraper",
        formatter_class=argparse.RawTextHelpFormatter
    )
    game_parser.add_argument("-p", "--path", type=str, help="Path to the schedule file to be parsed.")
    game_parser.add_argument("-d", "--date", type=str, help="Specify a date (YYYYMMDD) to fetch data for that day.")
    game_parser.add_argument("-f", "--full", action="store_true", help="Scrape all data from 2001-04-05 to today.")
    game_parser.set_defaults(func=scrape_game_data_command)

    # Player Parser
    player_parser = subparsers.add_parser("player",
        help="KBO Player Data Scraper",
        formatter_class=argparse.RawTextHelpFormatter
    )
    player_parser.add_argument(
        "-p", "--player", 
        type=str, choices=[Player.HITTER.value, Player.PITCHER.value, 
                           Player.FIELDER.value, Player.RUNNER.value], 
        help=textwrap.dedent("""\
            Specify the player type to scrape:
              'hitter'  - Batting statistics
              'pitcher' - Pitching statistics
              'fielder' - Fielding statistics
              'runner'  - Base running statistics
        """)
    )
    player_parser.add_argument("-a", "--all", action="store_true", help="Scrape data for all players.")
    player_parser.add_argument("-s", "--season", type=int, default=None, help="Specify the season year (e.g., 2024).")
    player_parser.set_defaults(func=scrape_player_data_command)

    # Schedule Parser
    schedule_parser = subparsers.add_parser("schedule",
        help="KBO Schedule Data Scraper",
        formatter_class=argparse.RawTextHelpFormatter
    )
    schedule_parser.add_argument("-d", "--date", type=str, help="Specify a date (YYYYMMDD) to fetch data for that day.")
    schedule_parser.add_argument("-f", "--full", action="store_true", help="Scrape all data from 2001-04-05 to today.")
    schedule_parser.set_defaults(func=scrape_schedule_data_command)

    # Team Parser
    team_parser = subparsers.add_parser("team",
        help="KBO Team Data Scraper",
        formatter_class=argparse.RawTextHelpFormatter
    )
    team_parser.set_defaults(func=scrape_team_data_command)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
