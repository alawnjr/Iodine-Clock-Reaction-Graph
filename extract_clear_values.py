import pandas as pd
import sys

def extract_clear_values(csv_file):
    """
    Extract Clear channel values from a CSV file and print as a list
    """
    print(f"Reading: {csv_file}")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Check if 'C' column exists
    if 'C' not in df.columns:
        print("Error: 'C' (Clear) column not found in CSV file!")
        print(f"Available columns: {', '.join(df.columns)}")
        return
    
    # Extract Clear values
    clear_values = df['C'].tolist()
    
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
    if len(sys.argv) < 2:
        print("Usage: python extract_clear_values.py <csv_file>")
        print("Example: python extract_clear_values.py color_data_11_14Trial1.csv")
        return
    
    csv_file = sys.argv[1]
    extract_clear_values(csv_file)


if __name__ == "__main__":
    main()

