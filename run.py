import os
import argparse
import textwrap
from datetime import datetime

from config import logger
from config import Scraper, Player

from scrapers import game_scraper, player_scraper, schedule_scraper, team_scraper

def scrape_game_data_command(args):
    game_scraper.run(args.date, args.format)

def scrape_player_data_command(args):
    player_scraper.run(args.season, args.format)

def scrape_schedule_data_command(args):
    schedule_scraper.run(args.season, args.format)

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
    game_parser.add_argument("-d", "--date", type=str, help="Specify a date (YYYYMMDD) to fetch data for that day.")
    game_parser.set_defaults(func=scrape_game_data_command)

    # Player Parser
    player_parser = subparsers.add_parser("player",
        help="KBO Player Data Scraper",
        formatter_class=argparse.RawTextHelpFormatter
    )
    player_parser.add_argument("-s", "--season", type=int, default=None, help="Specify the season year (e.g., 2024).")
    player_parser.set_defaults(func=scrape_player_data_command)

    # Schedule Parser
    schedule_parser = subparsers.add_parser("schedule",
        help="KBO Schedule Data Scraper",
        formatter_class=argparse.RawTextHelpFormatter
    )
    schedule_parser.add_argument("-s", "--season", type=int, default=None, help="Specify the season year (e.g., 2024).")
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
