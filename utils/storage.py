import os
import pandas as pd

def read_scraped_data(file_path):
    """
    Read data from a CSV or Parquet file and return it as a list of dictionaries.
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.parquet':
            df = pd.read_parquet(file_path)
            print(f"Successfully read Parquet file: {file_path}")
        elif file_extension == '.csv':
            df = pd.read_csv(file_path)
            print(f"Successfully read CSV file: {file_path}")
        else:
            print(f"Unsupported file format: {file_extension}")
            return None
        
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error reading Parquet file: {e}")
        return None
    
def save_scraped_data(data, filename, format="parquet"):
    """
    Save the scraped data to CSV and Parquet files with a specific filename prefix.
    """
    try:
        if not data:
            print("No data to save.")
            return
        
        if isinstance(data, dict):
            data = list(data.values()) 
        elif not isinstance(data, list):
            raise ValueError("Data must be a dictionary or a list.")

        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        df = pd.DataFrame(data)
        if "POS" in df:
            df["POS"] = df["POS"].astype(str)
                
        if format == 'parquet':
            file_path = os.path.join(output_dir, f"{filename}.parquet")
            df.to_parquet(file_path, engine="pyarrow", index=False)

            print(f"Successfully save Parquet file: {file_path}")
        elif format == 'json':
            file_path = os.path.join(output_dir, f"{filename}.json")
            json_data = df.to_json(orient="records", indent=4, force_ascii=False)

            json_data = json_data.replace(r'\/', '/')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            print(f"Successfully save JSON file: {file_path}")
        elif format == 'csv':
            file_path = os.path.join(output_dir, f"{filename}.csv")
            df.to_csv(file_path, index=False, encoding="utf-8") 

            print(f"Successfully save CSV file: {file_path}")
        else:
            print(f"Unsupported file format: {format}")
    
    except Exception as e:
        print(f"Error saving data: {e}")
