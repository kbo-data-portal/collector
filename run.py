import argparse

from scrapers.base import KBOBaseScraper
from scrapers.game import GameScheduleScraper, GameResultScraper
from scrapers.player import PlayerSeasonStatsScraper, PlayerDetailStatsScraper


def get_scrapers(command, format, series) -> list[KBOBaseScraper]:
    """Return a list of scraper instances based on the selected command."""
    if command == "schedule":
        return [GameScheduleScraper(format, series)]
    elif command == "game":
        return [GameResultScraper(format, series)]
    elif command == "player":
        scrapers = []
        for pt in ["hitter", "pitcher", "fielder", "runner"]:
            scrapers.append(PlayerSeasonStatsScraper(format, series, pt))
        for pt in ["hitter", "pitcher"]:
            scrapers.append(PlayerDetailStatsScraper(format, series, pt, "daily"))
            scrapers.append(PlayerDetailStatsScraper(format, series, pt, "situation"))
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
        parser.add_argument("-y", "--year", type=int, help="Season year (e.g., 2011)")
        parser.add_argument("-d", "--date", type=str, help="Specify date (YYYYMMDD)")
        parser.add_argument(
            "-f", "--format",
            type=str,
            choices=["parquet", "json", "csv"],
            default="csv",
            help="Output format: 'parquet', 'json', or 'csv' (default: csv)."
        )
        parser.add_argument(
            "-s", "--series",
            type=int,
            choices=[0,1,3,4,5,7,8,9],
            default=0,
            help="Series ID (default: 0) - 0: Regular Season, 1: Preseason, 3: Semi-PO, 4: Wildcard, 5: Playoff, 7: Korean Series, 8: International, 9: All-Star)"
        )

    # Schedule data
    schedule_parser = subparsers.add_parser("schedule", help="Scrape schedule data")
    add_format_argument(schedule_parser)

    # Game data
    game_parser = subparsers.add_parser("game", help="Scrape game data")
    add_format_argument(game_parser)

    # Player data
    player_parser = subparsers.add_parser("player", help="Scrape player data")
    add_format_argument(player_parser)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    scrapers = get_scrapers(args.command, args.format, [args.series])
    if not scrapers:
        parser.print_help()
        return

    for scraper in scrapers:
        scraper.run(args.year, args.date)


if __name__ == "__main__":
    main()
