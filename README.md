# KBO Data Collector
[![Test Scraper Status](https://github.com/leewr9/kbo-data-collector/actions/workflows/test_scraper.yml/badge.svg)](https://github.com/leewr9/kbo-data-collector/actions/workflows/test_scraper.yml)

This repository is dedicated to collecting and scraping KBO (Korea Baseball Organization) data. It includes scripts and processes for gathering player statistics, team data, game results, and other related information.

## Installation
### Requirements
- Python 3.12+ is required.

### Steps to Install
1. **Clone the repository**
    ```bash
    git clone https://github.com/leewr9/kbo-data-collector.git
    cd kbo-data-collector
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Usage
This project provides a tool for scraping KBO data in various formats. You can specify the target data and output format using commands.

### Command Syntax
```bash
python run.py <command> [options]
```
Where `<command>` is one of the available commands, and `[options]` are the command-specific options.
If no `<command>` is specified, it will collect data for the entire season.

### Example
Scrape all data for the 2011 season in Parquet format
```bash
python run.py -s 2011 -f parquet
```

### Available Commands

#### `game`
Used to scrape game-related data.

##### Options
- `-s, --season`: Specify the season for which to collect game data (e.g., `2011`).
- `-d, --date`: Specify a specific date (in `YYYYMMDD` format) to scrape data for.
- `-f, --format`: Specify the output format. Supported formats are `parquet`, `json`, and `csv`.

##### Example
Scrape game data for the 2011 season in CSV format
```bash
python run.py game -s 2011 -f csv
```

Scrape game data for a specific date (2011-10-31) in JSON format
```bash
python run.py game -d 20111031 -f json
```

#### `schedule`
Used to scrape the schedule of games for a season.

##### Options
- `-s, --season`: Specify the season for which to collect schedule data.
- `-f, --format`: Specify the output format. Supported formats are `parquet`, `json`, and `csv`.

##### Example
Scrape schedule data for the 2011 season in Parquet format
```bash
python run.py schedule -s 2011 -f parquet
```

#### `player`
Used to scrape player statistics data.

##### Options
- `-s, --season`: Specify the season for which to collect player data.
- `-f, --format`: Specify the output format. Supported formats are `parquet`, `json`, and cs`v.

##### Example
Scrape player data for the 2011 season in CSV format
```bash
python run.py player -s 2011 -f csv
```

### Help
To get more detailed information about any command, you can use the `--help` flag. This will display the available options and arguments for that specific command.

```bash
python run.py <command> --help
```

## License  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.  
