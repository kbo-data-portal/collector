import os
import pandas as pd

from config import logger
from config import BASE_DIR


def load_scraped_data(file_name: str) -> list[dict] | None:
    """
    Loads scraped data from a file (CSV, JSON, or Parquet) and returns it as a list of dictionaries.

    Args:
        file_name (str): Name or relative path of the file to load.

    Returns:
        list[dict] | None: List of records from the file as dictionaries, or None if an error occurs.
    """
    try:
        ext = os.path.splitext(file_name)[1].lower()
        file_path = file_name

        if not os.path.exists(file_path):
            file_path = os.path.join(BASE_DIR, "output", file_name)

        if ext == ".parquet":
            df = pd.read_parquet(file_path)
            logger.info(f"Loaded Parquet file: {file_path}")
        elif ext == ".json":
            df = pd.read_json(file_path)
            logger.info(f"Loaded JSON file: {file_path}")
        elif ext == ".csv":
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV file: {file_path}")
        else:
            logger.warning(f"Unsupported file extension: {ext}")
            return None

        return df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Failed to load file: {e}")
        return None


def save_scraped_data(
    data: list[dict] | dict,
    data_type: str,
    file_name: str,
    format: str = "parquet"
) -> None:
    """
    Saves scraped data to a file in the specified format (Parquet, JSON, or CSV).

    Args:
        data (list[dict] | dict): The scraped data to save.
        data_type (str): Type/category of the data (used to determine subdirectory).
        file_name (str): The base filename (without extension).
        format (str, optional): File format to save in ('parquet', 'json', or 'csv'). Defaults to 'parquet'.

    Returns:
        None
    """
    try:
        if not data:
            logger.warning("No data to save.")
            return

        output_dir = os.path.join(BASE_DIR, "output", data_type)
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{file_name}.{format}")

        if isinstance(data, dict):
            data = list(data.values())
        elif not isinstance(data, list):
            raise ValueError("Data must be a dictionary or a list of dictionaries.")

        df = pd.DataFrame(data)

        # Convert all non-numeric/non-datetime columns to string type
        for column in df.select_dtypes(exclude=["number", "datetime"]).columns:
            df[column] = df[column].astype("string")

        if format == "parquet":
            df.to_parquet(output_path, engine="pyarrow", index=False)
            logger.info(f"Saved Parquet file: {output_path}")

        elif format == "json":
            json_data = df.to_json(orient="records", indent=4, force_ascii=False)
            json_data = json_data.replace(r"\/", "/")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_data)
            logger.info(f"Saved JSON file: {output_path}")

        elif format == "csv":
            df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Saved CSV file: {output_path}")

        else:
            logger.warning(f"Unsupported file format: {format}")

    except Exception as e:
        logger.error(f"Failed to save file: {e}")
