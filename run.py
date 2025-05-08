import argparse

from scrapers.game import GameScheduleScraper, GameResultScraper
from scrapers.player import PlayerSeasonStatsScraper, PlayerDetailStatsScraper


def get_scrapers(args: argparse.Namespace) -> list:
    """Return a list of scraper instances based on the selected command."""
    if args.command == "schedule":
        return [GameScheduleScraper()]
    elif args.command == "game":
        return [GameResultScraper()]
    elif args.command == "player":
        scrapers = []
        for pt in ["hitter", "pitcher", "fielder", "runner"]:
            scrapers.append(PlayerSeasonStatsScraper(pt))
        for pt in ["hitter", "pitcher"]:
            scrapers.append(PlayerDetailStatsScraper(pt, "daily"))
            scrapers.append(PlayerDetailStatsScraper(pt, "situation"))
        return scrapers
    else:
        return []


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the KBO data scraping CLI."""
    parser = argparse.ArgumentParser(
        description="KBO Data Scraping Tool",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Choose a scraping target", required=True)

    # Common format argument function
    def add_format_argument(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-s", "--season", type=int, help="Season year (e.g., 2011)")
        parser.add_argument("-d", "--date", type=str, help="Specify date (YYYYMMDD)")
        parser.add_argument(
            "-f", "--format",
            type=str,
            choices=["parquet", "json", "csv"],
            default="csv",
            help="Output format: 'parquet', 'json', or 'csv' (default: csv)."
        )

    # Schedule data
    schedule_parser = subparsers.add_parser("schedule", help="Scrape schedule data")
    add_format_argument(schedule_parser)

    # Game data
    game_parser = subparsers.add_parser("game", help="Scrape game data")
    add_format_argument(game_parser)
    game_parser.set_defaults(func=GameResultScraper())

    # Player data
    player_parser = subparsers.add_parser("player", help="Scrape player data")
    add_format_argument(player_parser)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    scrapers = get_scrapers(args)
    if not scrapers:
        parser.print_help()
        return

    for scraper in scrapers:
        scraper.run(args.season, args.date, args.format)


if __name__ == "__main__":
    main()
