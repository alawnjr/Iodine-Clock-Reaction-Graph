import pandas as pd
import sys
from datetime import datetime, timedelta

def convert_csv_format(input_file, output_file):
    """
    Convert CSV format from 'Timestamp,t,R,G,B,C' to 'Timestamp,R,G,B,C'
    where the new Timestamp includes the relative time 't' added as seconds/milliseconds
    """
    print(f"Reading: {input_file}")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Check if the file has the expected columns
    if 't' not in df.columns:
        print("Error: Input file doesn't have 't' column. Already in correct format?")
        return False
    
    print(f"Found {len(df)} rows to convert")
    
    # Parse the base timestamp (assuming format like "11/17/25 18:52")
    # Convert to full datetime
    base_timestamp_str = df['Timestamp'].iloc[0]
    
    # Try different date formats
    try:
        # Try format: "11/17/25 18:52"
        base_timestamp = datetime.strptime(base_timestamp_str, "%m/%d/%y %H:%M")
    except ValueError:
        try:
            # Try format: "2025-11-17 18:52"
            base_timestamp = datetime.strptime(base_timestamp_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error: Unable to parse timestamp format: {base_timestamp_str}")
            return False
    
    print(f"Base timestamp: {base_timestamp}")
    
    # Create new timestamp column by adding 't' seconds to base timestamp
    new_timestamps = []
    for idx, row in df.iterrows():
        # Add the relative time (in seconds) to the base timestamp
        new_time = base_timestamp + timedelta(seconds=float(row['t']))
        # Format as "YYYY-MM-DD HH:MM:SS.mmm"
        new_timestamps.append(new_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    
    # Create new dataframe with converted format
    df_converted = pd.DataFrame({
        'Timestamp': new_timestamps,
        'R': df['R'],
        'G': df['G'],
        'B': df['B'],
        'C': df['C']
    })
    
    # Save to output file
    df_converted.to_csv(output_file, index=False)
    print(f"Converted file saved to: {output_file}")
    print(f"Successfully converted {len(df_converted)} rows")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_format.py <input_file> [output_file]")
        print("Example: python convert_format.py color_data_11_21.csv color_data_11_21_converted.csv")
        return
    
    input_file = sys.argv[1]
    
    # Generate output filename if not provided
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Default: add "_converted" before the file extension
        if input_file.endswith('.csv'):
            output_file = input_file[:-4] + '_converted.csv'
        else:
            output_file = input_file + '_converted.csv'
    
    print("=" * 60)
    print("CSV Format Converter")
    print("=" * 60)
    
    success = convert_csv_format(input_file, output_file)
    
    if success:
        print("\nConversion completed successfully!")
    else:
        print("\nConversion failed.")


if __name__ == "__main__":
    main()

