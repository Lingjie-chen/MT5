import os
import csv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataCleaner")

def clean_csv_duplicates(file_path, key_columns=None):
    """
    Remove duplicates from a CSV file based on key columns using standard csv module
    to avoid memory overhead of pandas.
    """
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return

    try:
        # Read all rows
        rows = []
        header = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
                rows = list(reader)
            except StopIteration:
                return # Empty file
                
        original_count = len(rows)
        if original_count == 0:
            return

        # Deduplicate
        # Use a dictionary to keep the LAST occurrence of each key
        # key -> row_data
        
        # Identify key indices
        key_indices = []
        if key_columns:
            for k in key_columns:
                if k in header:
                    key_indices.append(header.index(k))
        
        unique_rows = {} # key_tuple -> row
        
        # If no valid key columns found, use whole row as key (tuple)
        use_whole_row = not key_indices
        
        for row in rows:
            if use_whole_row:
                key = tuple(row)
            else:
                key = tuple(row[i] for i in key_indices)
            
            # This overwrites previous entry, effectively keeping the LAST one
            unique_rows[key] = row
            
        cleaned_rows = list(unique_rows.values())
        cleaned_count = len(cleaned_rows)
        removed_count = original_count - cleaned_count
        
        if removed_count > 0:
            logger.info(f"Cleaning {os.path.basename(file_path)}: Removed {removed_count} duplicates ({original_count} -> {cleaned_count})")
            # Save back
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(cleaned_rows)
        else:
            logger.info(f"Cleaning {os.path.basename(file_path)}: No duplicates found.")
            
    except Exception as e:
        logger.error(f"Failed to clean {file_path}: {e}")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    backup_dir = os.path.join(project_root, "scripts", "postgres_backup")

    logger.info(f"Starting backup data cleanup in: {backup_dir}")

    # 1. Trades: key = ticket
    clean_csv_duplicates(os.path.join(backup_dir, "trades_backup.csv"), key_columns=["ticket"])
    # 2. Signals: key = symbol,timeframe,timestamp
    clean_csv_duplicates(os.path.join(backup_dir, "signals_backup.csv"), key_columns=["symbol", "timeframe", "timestamp"])
    # 3. Account Metrics: key = timestamp
    clean_csv_duplicates(os.path.join(backup_dir, "account_metrics_backup.csv"), key_columns=["timestamp"])

    logger.info("Backup data cleanup completed.")

if __name__ == "__main__":
    main()
