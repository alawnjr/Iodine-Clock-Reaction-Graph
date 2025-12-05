import argparse
import math
import sys
import pandas as pd


def get_seconds_from_start(df):
    """
    Return integer second bins starting at 0 using either 't' (relative seconds)
    or 'Timestamp' (absolute time). Falls back to None if neither exists.
    """
    if 't' in df.columns:
        rel_seconds = df['t'].astype(float)
        start = rel_seconds.min()
        return rel_seconds.sub(start).apply(math.floor)
    if 'Timestamp' in df.columns:
        ts = pd.to_datetime(df['Timestamp'], errors='coerce')
        if ts.isnull().all():
            return None
        start = ts.min()
        rel_seconds = (ts - start).dt.total_seconds()
        return rel_seconds.apply(math.floor)
    return None


def extract_clear_values(csv_file, mode):
    """
    Extract Clear channel values from a CSV file and print as a list.
    Mode options:
      - raw: original values (default)
      - first-per-second: first sample in each second
      - median-per-second: median sample in each second
    """
    print(f"Reading: {csv_file}")
    print(f"Mode: {mode}")
    
    df = pd.read_csv(csv_file)
    
    if 'C' not in df.columns:
        print("Error: 'C' (Clear) column not found in CSV file!")
        print(f"Available columns: {', '.join(df.columns)}")
        return
    
    # Decide how to aggregate
    if mode == 'raw':
        clear_values = df['C'].tolist()
    else:
        seconds_from_start = get_seconds_from_start(df)
        if seconds_from_start is None:
            print("Error: No time column found ('t' or 'Timestamp') for per-second aggregation.")
            return
        
        grouped = df.groupby(seconds_from_start)['C']
        if mode == 'median-per-second':
            per_second = grouped.median().sort_index()
        elif mode == 'first-per-second':
            per_second = grouped.first().sort_index()
        else:
            print(f"Unknown mode: {mode}")
            return
        
        clear_values = per_second.tolist()
    
    print(f"\nFound {len(clear_values)} Clear values")
    print("\nClear values as Python list:")
    print(clear_values)
    
    print("\n\nClear values formatted for Arduino (20 per line):")
    for i in range(0, len(clear_values), 20):
        chunk = clear_values[i:i+20]
        line = "  " + ", ".join(map(str, chunk))
        if i + 20 < len(clear_values):
            line += ","
        print(line)
    
    print(f"\n\nTotal data points: {len(clear_values)}")
    print(f"Min value: {min(clear_values)}")
    print(f"Max value: {max(clear_values)}")


def main():
    parser = argparse.ArgumentParser(description="Extract Clear channel values from CSV.")
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument(
        "--mode",
        choices=["raw", "first-per-second", "median-per-second"],
        default="raw",
        help="Aggregation mode (default: raw)",
    )
    args = parser.parse_args()
    
    extract_clear_values(args.csv_file, args.mode)


if __name__ == "__main__":
    main()

