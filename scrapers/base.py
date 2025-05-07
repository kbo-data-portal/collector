from abc import ABC, abstractmethod
from config import logger
from datetime import datetime
import pandas as pd
import os

class KBOBaseScraper(ABC):
    """Base class for scraping KBO data (player, game, schedule, team)."""

    def __init__(self): 
        self.save_name = None
        self.save_dir = None
        self.start_year = 1982
        self.current_year = datetime.now().year

    @abstractmethod
    def fetch(self, season):
        """Fetch raw data (must be implemented by subclass)."""
        pass

    @abstractmethod
    def _parse(self, response):
        """Parse raw response into structured data (must be implemented by subclass)."""
        pass

    def parse(self, response):
        """Wrapper for parse logic with error handling."""
        if not response:
            logger.error("Skipping data due to empty or invalid response.")
            return None, None

        try:
            return self._parse(response)
        except (AttributeError, KeyError, TypeError) as e:
            logger.error(f"Known parsing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
        return None, None

    def save(self, data: list[dict] | dict, format: str):
        """
        Save the scraped data to a file.

        Args:
            data (list[dict] | dict): Data to save.
            format (str, optional): Format of output file ('parquet', 'json', 'csv').
        """
        if not isinstance(data, list):
            raise ValueError("Data must be a dictionary or a list of dictionaries.")
        
        try:
            base_dir = os.getcwd()
            output_path = os.path.join(base_dir, "output", self.save_dir)
            os.makedirs(output_path, exist_ok=True)

            full_path = os.path.join(output_path, f"{self.save_name}.{format}")

            df = pd.DataFrame(data)

            for column in df.select_dtypes(exclude=["number", "datetime"]).columns:
                df[column] = df[column].astype("string")

            if format == "parquet":
                df.to_parquet(full_path, engine="pyarrow", index=False)
            elif format == "json":
                json_str = df.to_json(orient="records", indent=4, force_ascii=False).replace(r"\/", "/")
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
            elif format == "csv":
                df.to_csv(full_path, index=False, encoding="utf-8")
            else:
                logger.warning(f"Unsupported file format: {format}")

            logger.info(f"Saved file: {full_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")

    def run(self, year: int = None, file_format: str = "parquet"):
        """
        Run scraping job over a target year or full range.

        Args:
            year (int, optional): Target season. If not given, run from start_year to current_year.
            file_format (str): File format to save data.
        """
        start = year or self.start_year
        end = year or self.current_year

        for season in range(start, end + 1):
            data = self.fetch(season)
            if data:
                self.save(data, file_format)
            else:
                logger.warning(f"No data found for season {season}.")
