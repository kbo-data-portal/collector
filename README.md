# KBO Data Portal - Collector

[![build-test](https://github.com/KBO-Data-Portal/collector/actions/workflows/build-test.yml/badge.svg)](https://github.com/KBO-Data-Portal/collector/actions/workflows/build-test.yml)

This repository is dedicated to collecting and scraping KBO (Korea Baseball Organization) data.
It includes scripts and processes for gathering player statistics, team data, game results, and other related information.

## Feature

- Scrape KBO data including game results, schedules, and player statistics
- Supports various output formats: `Parquet`, `JSON`, `CSV`
- Flexible command-line interface with multiple scraping commands
- Filter by year, specific date, and series ID (league/stage type)

## Installation

### Requirements

- Python 3.12+ is required.

### Steps to Install

1. **Clone the repository**

   ```bash
   git clone https://github.com/kbo-data-portal/collector.git
   cd collector
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

This project provides a command-line tool for scraping KBO data.
You can specify the target data and output format using commands.

### Command Syntax

```bash
python run.py <command> [options]
```

- `<command>` — The target data type (game, schedule, player)
- `[options]` — Additional filters and configurations

### Options

| Option         | Description                                             |
| -------------- | ------------------------------------------------------- |
| `-y, --year`   | Specify the year (e.g., 2014)                           |
| `-d, --date`   | Specific date in YYYYMMDD format                        |
| `-f, --format` | Output format: parquet, json, csv                       |
| `-s, --series` | Series ID to indicate league/stage type (see Series ID) |

### Commands

`game`
Scrape game-related data.

```bash
python run.py game -y 2014 -f csv  # Season data
python run.py game -d 20141111 -f json  # Specific date data
```

`schedule`
Scrape schedule of games.

```bash
python run.py schedule -y 2014 -f parquet
```

`player`
Scrape player statistics.

```bash
python run.py player -y 2014 -f csv
```

### Help

For detailed command usage, run:

```bash
python run.py <command> --help
```

## Data Description

### Series ID

Each game record includes a `SR_ID` field representing the league/stage type:

| SR_ID | Description                |
| ----- | -------------------------- |
| 0     | Regular Season             |
| 1     | Preseason Game             |
| 3     | Semi-Playoffs              |
| 4     | Wild Card Round            |
| 5     | Playoffs                   |
| 7     | Korean Series              |
| 8     | International Competitions |
| 9     | All-star Game              |

You can use this field to filter games based on the competition stage.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
