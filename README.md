# KBO Data Collector
This repository is dedicated to collecting and scraping KBO (Korea Baseball Organization) data. It includes scripts and processes for gathering player statistics, team data, game results, and other related information.

## Installation
- Python 3.12+

1. **Clone the repository**:
    ```bash
    git clone https://github.com/leewr9/kbo-data-collector.git
    cd kbo-data-collector
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    
## Usage

### Main Command

The tool can be run via the command line and offers four main commands: `game`, `player`, `schedule`, and `team`.
```bash
python run.py <command> [options]
```

### Commands

### `game`: Scrapes KBO game data

This command scrapes data related to specific KBO games. It will internally fetch schedule data as well.

```bash
python run.py game --date <target_date>
```

#### Options:
- `-d, --date`: Specify a date (in `YYYYMMDD` format) to fetch data for that day.
- `-f, --full`: Scrape all available data from April 5, 2001, to today.

> **Note**: Since the `game` command internally fetches the schedule data, the options `-d` and `-f` are the same as those for the `schedule` command and will also apply when scraping game data.

#### `player`: Scrapes KBO player data

This command allows you to scrape data for different types of players, including batters, pitchers, fielders, and base runners.
```bash
python run.py player --player <player_type> --season <target_season>
```

##### Options:
- `-p, --player`: Specify the type of player data to scrape. Valid options are:
  - `hitter` for batting statistics
  - `pitcher` for pitching statistics
  - `fielder` for fielding statistics
  - `runner` for base running statistics
- `-a, --all`: Scrape data for all players.
- `-s, --season`: Specify the season year (e.g., `2024`) to scrape data for that year.

#### `schedule`: Scrapes KBO schedule data

This command scrapes the schedule data for KBO games. You can fetch data for a specific date or scrape all data from the start of the KBO season in 2001 to today.
```bash
python run.py schedule --date <target_date>
```

##### Options:
- `-d, --date`: Specify a date (in `YYYYMMDD` format) to fetch data for that day.
- `-f, --full`: Scrape all available data from April 5, 2001, to today.


#### `team`: Scrapes KBO team data

This command scrapes data related to KBO teams.
```bash
python run.py team
```

### Help

For more detailed information on any command, you can use the `--help` flag:

```bash
python run.py <command> --help
```

## Functions

Each command is mapped to a corresponding function in the code:

- `scrape_game_data_command`: Handles scraping of game data.
- `scrape_player_data_command`: Handles scraping of player data.
- `scrape_schedule_data_command`: Handles scraping of schedule data.
- `scrape_team_data_command`: Handles scraping of team data.

These functions take care of the web scraping and data processing based on the command-line arguments passed.

---

## Example Commands

1. **Scrape Game Data:**
    ```bash
    python run.py game --date 20240205
    ```

2. **Scrape Player Data for Batters in 2024 Season:**
    ```bash
    python run.py player --player hitter --season 2024
    ```

3. **Scrape KBO Schedule Data for a Specific Date:**
    ```bash
    python run.py schedule --date 20240205
    ```

## License  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.  
