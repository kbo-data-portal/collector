from abc import ABC, abstractmethod
from datetime import datetime
import os
import json

import pandas as pd

from logger import get_logger

class KBOBaseScraper(ABC):
    """Base class for scraping KBO data (player, game, schedule, team)."""

    def __init__(self): 
        self.logger = get_logger()
        self.start_year = 1982
        self.current_year = datetime.now().year

        base_dir = os.getcwd()
        self.backup_path = os.path.join(base_dir, "output", "raw")
        self.save_path = os.path.join(base_dir, "output", "processed")

    @abstractmethod
    def _parse(self, response) -> tuple[list, list]:
        """Parse raw response into structured data (must be implemented by subclass)."""
        pass

    @abstractmethod
    def fetch(self, season: int, date: str) -> dict[str, list]:
        """Fetch raw data (must be implemented by subclass)."""
        pass

    def parse(self, response):
        """Wrapper for parse logic with error handling."""
        if not response:
            self.logger.error("Skipping data due to empty or invalid response.")
            return None, None

        try:
            return self._parse(response)
        except (AttributeError, KeyError, TypeError, json.JSONDecodeError) as e:
            self.logger.error(f"Known parsing error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during parsing: {e}")
        return None, None

    def backup(self, data: str | dict, file_path: str, format: str):
        """
        Backed up the scraped data to a file.

        Args:
            data (str | dict): Data to save.
            file_path (str): Path of the output file (without extension).
            format (str): Format of output file ('html', 'json').
        """
        try:
            full_path = os.path.join(self.backup_path, f"{file_path}.{format}")
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            if format == "html":
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(data)
            elif format == "json":
                with open(full_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                self.logger.warning(f"Unsupported file format: {format}")

            self.logger.info(f"Backed up file: {full_path}")
        except Exception as e:
            self.logger.error(f"Failed to backup file: {e}")

    def save(self, data: list, file_path: str):
        """
        Save the processed data to a file.

        Args:
            data (list): Data to save.
            file_path (str): Path of the output file (without extension).
            format (str): Format of output file ('parquet', 'json', 'csv').
        """
        if not isinstance(data, list):
            raise ValueError("Data must be a dictionary or a list of dictionaries.")
        
        try:
            full_path = os.path.join(self.save_path, f"{file_path}.{self.format}")
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            df = pd.DataFrame(data)

            for column in df.select_dtypes(exclude=["number", "datetime"]).columns:
                df[column] = df[column].astype("string")

            if self.format == "parquet":
                df.to_parquet(full_path, engine="pyarrow", index=False)
            elif self.format == "json":
                json_str = df.to_json(orient="records", indent=4, force_ascii=False).replace(r"\/", "/")
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
            elif self.format == "csv":
                df.to_csv(full_path, index=False, encoding="utf-8")
            else:
                self.logger.warning(f"Unsupported file format: {self.format}")

            self.logger.info(f"Saved file: {full_path}")
        except Exception as e:
            self.logger.error(f"Failed to save file: {e}")

    def run(self, year: int, date: str, format: str):
        """
        Run scraping job over a target year/date or full range.

        Args:
            year (int): Target season year.
            date (str): Target date in 'YYYYMMDD' format to run the job for a specific day.
            format (str): File format to save the scraped data (e.g., 'parquet', 'csv').
        """
        start = year if year else int(date[:4]) if date else self.start_year
        end = year if year else int(date[:4]) if date else self.current_year
        self.format = format if format else "parquet"

        for season in range(start, end + 1):
            fetch_data = self.fetch(season, date)
            if fetch_data:
                for filename, data in fetch_data.items():
                    self.save(data, filename)
            else:
                self.logger.warning(f"No data found for season {season}.")
            if date:
                break
