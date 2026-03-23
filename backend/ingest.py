import os
import pandas as pd
import sqlite3
from pathlib import Path

# Path to the dataset and database
DATASET_DIR = Path(r"C:\Users\INDRAKUMAR\Desktop\FDE Task\sap-order-to-cash-dataset\sap-o2c-data")
DB_PATH = Path(r"C:\Users\INDRAKUMAR\Desktop\FDE Task\backend\o2c_graph.db")

def ingest_data():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    if not DATASET_DIR.exists():
        print(f"Error: Dataset directory {DATASET_DIR} does not exist.")
        return
        
    for entity_folder in DATASET_DIR.iterdir():
        if entity_folder.is_dir():
            table_name = entity_folder.name
            print(f"Processing entity: {table_name}")
            
            # Find all JSONL files in the folder (usually there is one per entity or partitioned)
            df_list = []
            for file_path in entity_folder.glob("*.jsonl"):
                print(f"  Reading {file_path.name}")
                try:
                    df = pd.read_json(file_path, lines=True)
                    df_list.append(df)
                except Exception as e:
                    print(f"  Failed to read {file_path.name}: {e}")
            
            if df_list:
                # Combine partitions if multiple
                combined_df = pd.concat(df_list, ignore_index=True)
                
                # Write to SQLite
                print(f"  Writing {len(combined_df)} rows to table '{table_name}'")
                try:
                    combined_df.to_sql(table_name, conn, if_exists='replace', index=False)
                except Exception as e:
                    print(f"  Failed to write to DB: {e}")
            else:
                print(f"  No JSONL files found in {table_name}")

    conn.close()
    print("Data ingestion complete!")

if __name__ == "__main__":
    ingest_data()
