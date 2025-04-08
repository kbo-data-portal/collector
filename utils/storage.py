import os
import pandas as pd

from config import logger
from config import BASE_DIR

def read_scraped_data(filename):
    """
    Read data from a CSV or Parquet file and return it as a list of dictionaries.
    """
    try:
        file_extension = os.path.splitext(filename)[1].lower()

        file_path = filename
        if not os.path.exists(file_path):
            file_path = os.path.join(BASE_DIR, "output", filename)

        if file_extension == ".parquet":
            df = pd.read_parquet(file_path)
            logger.info(f"Successfully read Parquet file: {file_path}")
        elif file_extension == ".json":
            df = pd.read_json(file_path)
            logger.info(f"Successfully read JSON file: {file_path}")
        elif file_extension == ".csv":
            df = pd.read_csv(file_path)
            logger.info(f"Successfully read CSV file: {file_path}")
        else:
            logger.info(f"Unsupported file format: {file_extension}")
            return None
        
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return None
    
def save_scraped_data(data, data_type, filename, format="parquet"):
    """
    Save the scraped data in the specified format with a specific filename prefix.
    """
    try:
        if not data:
            logger.warning("No data to save.")
            return
        
        output_dir = os.path.join(BASE_DIR, "output", data_type)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if isinstance(data, dict):
            data = list(data.values()) 
        elif not isinstance(data, list):
            raise ValueError("Data must be a dictionary or a list.")

        df = pd.DataFrame(data)
        for column in df.select_dtypes(exclude=["number", "datetime"]).columns:
            df[column] = df[column].astype("string")

        if format == "parquet":
            file_path = os.path.join(output_dir, f"{filename}.parquet")
            df.to_parquet(file_path, engine="pyarrow", index=False)

            logger.info(f"Successfully save Parquet file: {file_path}")
        elif format == "json":
            file_path = os.path.join(output_dir, f"{filename}.json")
            json_data = df.to_json(orient="records", indent=4, force_ascii=False)

            json_data = json_data.replace(r"\/", "/")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_data)
            logger.info(f"Successfully save JSON file: {file_path}")
        elif format == "csv":
            file_path = os.path.join(output_dir, f"{filename}.csv")
            df.to_csv(file_path, index=False, encoding="utf-8") 

            logger.info(f"Successfully save CSV file: {file_path}")
        else:
            logger.warning(f"Unsupported file format: {format}")
    
    except Exception as e:
        logger.error(f"Error saving data: {e}")
