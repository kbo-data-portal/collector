import argparse
from datetime import datetime
from scrapers import (
    game_scraper,
    player_scraper,
    schedule_scraper,
    team_scraper
)

def scrape_game_data_command(args):
    scrape_schedule_data_command(args)
    game_scraper.run("output/game_schedule.parquet")

def scrape_player_data_command(args):
    if args.all:
        player_scraper.run("hitter", args.season)
        player_scraper.run("pitcher", args.season)
    elif args.player:
        player_scraper.run(args.player, args.season)
    else:
        player_scraper.run("hitter", args.season)
        player_scraper.run("pitcher", args.season)

def scrape_schedule_data_command(args):
    if args.full:
        schedule_scraper.run(
            start_date=datetime.strptime("20010405", "%Y%m%d"), 
            end_date=datetime.now()
        )
    else:
        if args.date:
            try:
                target_date = datetime.strptime(args.date, "%Y%m%d")
            except ValueError:
                print("Invalid date format. Please use YYYYMMDD.")
                exit(1)
        else:
            target_date = datetime.now()
        schedule_scraper.run(
            start_date=target_date, 
            end_date=target_date
        )

def scrape_team_data_command(args):
    team_scraper.run()

def main():
    parser = argparse.ArgumentParser(description='KBO Data Scraping Tool')
    subparsers = parser.add_subparsers(dest='command', help='Select a command')

    game_parser = subparsers.add_parser('game', help="KBO Game Data Scraper")
    game_parser.add_argument("-d", "--date", type=str, 
                                 help="Specify a date (YYYYMMDD) to fetch data for that day.")
    game_parser.add_argument("-f", "--full", action="store_true", 
                                 help="Scrape all data from 2001-04-05 to today.")
    game_parser.set_defaults(func=scrape_game_data_command)

    player_parser = subparsers.add_parser('player', help="KBO Player Data Scraper")
    player_parser.add_argument("-p", "--player", type=str, choices=["hitter", "pitcher", "fielder", "runner"], 
                           help="Specify the player type to scrape. Options are:\n"
                                "'hitter' for batting statistics,\n"
                                "'pitcher' for pitching statistics,\n"
                                "'fielder' for fielding statistics,\n"
                                "'runner' for base running statistics.")
    player_parser.add_argument("-a", "--all", action="store_true", 
                               help="Scrape data for all players.")
    player_parser.add_argument("-s", "--season", type=int, default=None, 
                               help="Specify the season year to scrape data for (e.g., 2024).")
    player_parser.set_defaults(func=scrape_player_data_command)

    schedule_parser = subparsers.add_parser('schedule', help="KBO Schedule Data Scraper")
    schedule_parser.add_argument("-d", "--date", type=str, 
                                 help="Specify a date (YYYYMMDD) to fetch data for that day.")
    schedule_parser.add_argument("-f", "--full", action="store_true", 
                                 help="Scrape all data from 2001-04-05 to today.")
    schedule_parser.set_defaults(func=scrape_schedule_data_command)

    team_parser = subparsers.add_parser('team', help="KBO Team Data Scraper")
    team_parser.set_defaults(func=scrape_team_data_command)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
