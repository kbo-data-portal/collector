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
Where `<command>` is a required command that must be selected, and `[options]` are optional and apply to all commands, providing additional configuration or functionality.

### Options
- `-y, --year`: Specify the year for which to collect game data (e.g., `2014`).
- `-d, --date`: Specify a specific date (in `YYYYMMDD` format) to scrape data for.
- `-f, --format`: Specify the output format. Supported formats are `parquet`, `json`, and `csv`.
- `-s, --series`: Specify the Series ID to indicate the type of league or competition stage [See Series ID](#series-id).

### Commands

#### `game`
Used to scrape game-related data.

##### Example
Scrape game data for the 2014 season in CSV format
```bash
python run.py game -y 2014 -f csv
```

Scrape game data for a specific date (2014-11-11) in JSON format
```bash
python run.py game -d 20141111 -f json
```

#### `schedule`
Used to scrape the schedule of games for a season.

##### Example
Scrape schedule data for the 2014 season in Parquet format
```bash
python run.py schedule -y 2014 -f parquet
```

#### `player`
Used to scrape player statistics data.

##### Example
Scrape player data for the 2014 season in CSV format
```bash
python run.py player -y 2014 -f csv
```

### Help
To get more detailed information about any command, you can use the `--help` flag. This will display the available options and arguments for that specific command.

```bash
python run.py <command> --help
```


## Data Description

### Series ID
Each game record includes a `SR_ID` field that indicates the type of league or stage of the season.

| SR_ID | Description                  |
|-------|------------------------------|
| 0     | Regular Season               |
| 1     | Preseason Game               |
| 3     | Semi-Playoffs                |
| 4     | Wild Card Round              |
| 5     | Playoffs                     |
| 7     | Korean Series                |
| 8     | International Competitions   |
| 9     | All-ytar Game                |

You can use this field to filter or categorize games based on the competition stage.


## License  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.  
