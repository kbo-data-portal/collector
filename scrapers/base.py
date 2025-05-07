from abc import ABC, abstractmethod
from config import logger
from datetime import datetime
import pandas as pd
import os

class KBOBaseScraper(ABC):
    """Base class for scraping KBO data (player, game, schedule, team)."""

    def __init__(self): 
        self.save_dir = "output"
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

    def save(
        data: list[dict] | dict,
        category: str,
        filename: str,
        file_format: str = "parquet"
    ) -> None:
        """
        Save the scraped data to a file.

        Args:
            data (list[dict] | dict): Data to save.
            category (str): Type of data (e.g., 'schedule', 'player').
            filename (str): Name of the output file (without extension).
            file_format (str, optional): Format of output file ('parquet', 'json', 'csv').
        """
        try:
            if not data:
                logger.warning(f"No data to save: {category}/{filename}.{file_format}")
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(base_dir, "output", category)
            os.makedirs(output_path, exist_ok=True)

            full_path = os.path.join(output_path, f"{filename}.{file_format}")

            if isinstance(data, dict):
                data = list(data.values())
            elif not isinstance(data, list):
                raise ValueError("Data must be a dictionary or a list of dictionaries.")

            df = pd.DataFrame(data)

            for column in df.select_dtypes(exclude=["number", "datetime"]).columns:
                df[column] = df[column].astype("string")

            if file_format == "parquet":
                df.to_parquet(full_path, engine="pyarrow", index=False)
            elif file_format == "json":
                json_str = df.to_json(orient="records", indent=4, force_ascii=False).replace(r"\/", "/")
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
            elif file_format == "csv":
                df.to_csv(full_path, index=False, encoding="utf-8")
            else:
                logger.warning(f"Unsupported file format: {file_format}")

            logger.info(f"Saved file: {full_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")

    def run(self, year: int = None, file_format: str = "parquet") -> None:
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
                self.save(data, "schedule", f"{season}", file_format)
            else:
                logger.warning(f"No data found for season {season}.")
