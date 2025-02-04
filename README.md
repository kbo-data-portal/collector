# KBO Data Collector
This repository is dedicated to collecting and scraping KBO (Korea Baseball Organization) data. It includes scripts and processes for gathering player statistics, team data, game results, and other related information.

## Overview
This project provides two Python scripts to scrape Korean Baseball Organization (KBO) data:
1. **Player Data Scraper** - Fetches player statistics (hitters or pitchers).
2. **Schedule Data Scraper** - Retrieves game schedules from 2001-04-05 to today or for a specific date.

## Requirements
- Python 3.10+

Install dependencies using:
```sh
pip install -r requirements.txt
```

## Player Data Scraper
### Usage
```sh
python scrape_player_data.py [-p {hitter,pitcher}] [-a]
```
### Arguments
- `-p, --player` : Choose player type (`hitter` for batters, `pitcher` for pitchers).
- `-a, --all` : Scrape data for all players.

### Examples
- Scrape hitter data:
  ```sh
  python scrape_player_data.py -p hitter
  ```
- Scrape pitcher data:
  ```sh
  python scrape_player_data.py -p pitcher
  ```
- Scrape all player data:
  ```sh
  python scrape_player_data.py -a
  ```

## Schedule Data Scraper
### Usage
```sh
python scrape_schedule_data.py [-d YYYYMMDD] [-f]
```
### Arguments
- `-d, --date` : Fetch schedule data for a specific date (format: `YYYYMMDD`).
- `-f, --full` : Scrape all schedule data from 2001-04-05 to today.

### Examples
- Scrape schedule for a specific date:
  ```sh
  python scrape_schedule_data.py -d 20240501
  ```
- Scrape all schedules from 2001-04-05 to today:
  ```sh
  python scrape_schedule_data.py -f
  ```
  
## Output
The scraped data is saved in:
- **CSV Format:** `output/baseball_schedule.csv` / `{player_type}_player_stats.csv`
- **Parquet Format:** `output/baseball_schedule.parquet` / `{player_type}_player_stats.parquet`

## License  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.  
