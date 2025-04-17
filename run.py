import argparse

from scrapers import game, player, schedule, spectator, team


def scrape_all_data(args: argparse.Namespace) -> None:
    """Handle scraping all data."""
    player.run(args.season, args.format)
    schedule.run(args.season, args.format)
    spectator.run(args.season, args.format)
    game.run(
        target_season=args.season, 
        file_format=args.format
    )


def scrape_game_data(args: argparse.Namespace) -> None:
    """Handle scraping game data."""
    game.run(
        target_season=args.season, 
        target_date=args.date, 
        file_format=args.format
    )


def scrape_player_data(args: argparse.Namespace) -> None:
    """Handle scraping player data."""
    player.run(args.season, args.format)


def scrape_schedule_data(args: argparse.Namespace) -> None:
    """Handle scraping schedule data."""
    schedule.run(args.season, args.format)


def scrape_spectator_data(args: argparse.Namespace) -> None:
    """Handle scraping spectator data."""
    spectator.run(args.season, args.format)


def scrape_team_data(args: argparse.Namespace) -> None:
    """Handle scraping team data."""
    team.run()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the KBO data scraping CLI."""
    parser = argparse.ArgumentParser(
        description="KBO Data Scraping Tool",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Choose a scraping target")

    # Common format argument function
    def add_format_argument(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-s", "--season", type=int, help="Season year (e.g., 2011)")
        parser.add_argument(
            "-f", "--format",
            type=str,
            choices=["parquet", "json", "csv"],
            default="parquet",
            help="Output format: 'parquet', 'json', or 'csv' (default: parquet)."
        )

    # Game data
    game_parser = subparsers.add_parser("game", help="Scrape game data")
    game_parser.add_argument("-d", "--date", type=str, help="Specify date (YYYYMMDD)")
    add_format_argument(game_parser)
    game_parser.set_defaults(func=scrape_game_data)

    # Player data
    player_parser = subparsers.add_parser("player", help="Scrape player data")
    add_format_argument(player_parser)
    player_parser.set_defaults(func=scrape_player_data)

    # Schedule data
    schedule_parser = subparsers.add_parser("schedule", help="Scrape schedule data")
    add_format_argument(schedule_parser)
    schedule_parser.set_defaults(func=scrape_schedule_data)

    # Spectator data
    spectator_parser = subparsers.add_parser("spectator", help="Scrape spectator data")
    add_format_argument(spectator_parser)
    spectator_parser.set_defaults(func=scrape_spectator_data)

    # Team data
    team_parser = subparsers.add_parser("team", help="Scrape team data")
    team_parser.set_defaults(func=scrape_team_data)

    add_format_argument(parser)
    parser.set_defaults(func=scrape_all_data)

    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
