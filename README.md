# KBO Data Collector
[![Test Scraper Status](https://github.com/leewr9/kbo-data-collector/actions/workflows/test_scraper.yml/badge.svg)](https://github.com/leewr9/kbo-data-collector/actions/workflows/test_scraper.yml)

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

---

### `player`: Scrapes KBO player data

This command allows you to scrape data for different types of players, including batters, pitchers, fielders, and base runners.
```bash
python run.py player --season <target_season>
```

#### Options:
- `-s, --season`: Specify the season year (e.g., `2011`) to scrape data for that year.

---

### `schedule`: Scrapes KBO schedule data

This command scrapes the schedule data for KBO games. You can fetch data for a specific season or scrape all data from the start of the KBO season in 2001 to today.
```bash
python run.py schedule --season <target_season>
```

#### Options:
- `-s, --season`: Specify the season year (e.g., `2024`) to scrape data for that year.

---

### `team`: Scrapes KBO team data

This command scrapes data related to KBO teams.
```bash
python run.py team
```

### Help

For more detailed information on any command, you can use the `--help` flag:

```bash
python run.py <command> --help
```

---

## Example Commands

1. **Scrape Game Data:**
    ```bash
    python run.py game --date 20111031
    ```

2. **Scrape Player Data for a 2011 Season:**
    ```bash
    python run.py player --season 2011
    ```

3. **Scrape KBO Schedule Data for a 2011 Season:**
    ```bash
    python run.py schedule --season 2011
    ```

## License  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.  
