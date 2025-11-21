import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta

def interpolate_color_data(input_file, output_file, interval=1.0):
    """
    Calculate median color sensor data over regular time intervals
    
    Args:
        input_file: Input CSV file path
        output_file: Output CSV file path
        interval: Time interval in seconds (default: 1.0)
    """
    print(f"Reading: {input_file}")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print(f"Found {len(df)} data points")
    
    # Parse timestamps and calculate relative time
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    start_time = df['Timestamp'].iloc[0]
    df['Time_s'] = (df['Timestamp'] - start_time).dt.total_seconds()
    
    # Get the time range
    time_start = 0
    time_end = df['Time_s'].iloc[-1]
    
    print(f"Original time range: {time_start:.2f}s to {time_end:.2f}s")
    print(f"Calculating median for data points every {interval} second(s)")
    
    # Assign each data point to a time bin
    df['Time_bin'] = np.floor(df['Time_s'] / interval) * interval
    
    # Group by time bin and calculate median for each channel
    grouped = df.groupby('Time_bin').agg({
        'R': 'median',
        'G': 'median',
        'B': 'median',
        'C': 'median'
    }).reset_index()
    
    print(f"Created {len(grouped)} median points")
    
    # Round values to integers
    grouped['R'] = np.round(grouped['R']).astype(int)
    grouped['G'] = np.round(grouped['G']).astype(int)
    grouped['B'] = np.round(grouped['B']).astype(int)
    grouped['C'] = np.round(grouped['C']).astype(int)
    
    # Ensure values are non-negative
    grouped['R'] = np.maximum(grouped['R'], 0)
    grouped['G'] = np.maximum(grouped['G'], 0)
    grouped['B'] = np.maximum(grouped['B'], 0)
    grouped['C'] = np.maximum(grouped['C'], 0)
    
    # Enforce monotonically increasing values (each value >= previous value)
    print("Enforcing monotonically increasing constraint...")
    for channel in ['R', 'G', 'B', 'C']:
        for i in range(1, len(grouped)):
            if grouped.loc[i, channel] < grouped.loc[i-1, channel]:
                grouped.loc[i, channel] = grouped.loc[i-1, channel]
    
    # Create new timestamps starting from time 0
    # Use a base timestamp of 2025-01-01 00:00:00
    base_time = datetime(2025, 1, 1, 0, 0, 0)
    new_timestamps = [base_time + timedelta(seconds=float(t)) for t in grouped['Time_bin']]
    new_timestamps_str = [ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] for ts in new_timestamps]
    
    new_times = grouped['Time_bin']
    new_r = grouped['R']
    new_g = grouped['G']
    new_b = grouped['B']
    new_c = grouped['C']
    
    # Create output dataframe
    df_interpolated = pd.DataFrame({
        'Timestamp': new_timestamps_str,
        'R': new_r,
        'G': new_g,
        'B': new_b,
        'C': new_c
    })
    
    # Save to file
    df_interpolated.to_csv(output_file, index=False)
    print(f"\nMedian data saved to: {output_file}")
    print(f"Successfully created {len(df_interpolated)} median points")
    
    # Show some statistics
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Original data points: {len(df)}")
    print(f"Median data points: {len(df_interpolated)}")
    print(f"Time interval: {interval} second(s)")
    print(f"Average points per interval: {len(df) / len(df_interpolated):.1f}")
    print(f"Duration: {time_end:.2f} seconds ({time_end/60:.2f} minutes)")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python interpolate_data.py <input_file> [output_file] [interval]")
        print("Example: python interpolate_data.py color_data_11_21.csv output.csv 1.0")
        print("\nArguments:")
        print("  input_file  - Input CSV file with color data")
        print("  output_file - Output CSV file (default: adds '_interpolated' to input)")
        print("  interval    - Time interval in seconds for median calculation (default: 1.0)")
        print("\nNote: This tool calculates the median of all data points within each time interval.")
        return
    
    input_file = sys.argv[1]
    
    # Generate output filename if not provided
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        if input_file.endswith('.csv'):
            output_file = input_file[:-4] + '_interpolated.csv'
        else:
            output_file = input_file + '_interpolated.csv'
    
    # Get interval if provided
    interval = 1.0
    if len(sys.argv) >= 4:
        try:
            interval = float(sys.argv[3])
        except ValueError:
            print(f"Warning: Invalid interval '{sys.argv[3]}', using default 1.0 second")
    
    print("=" * 60)
    print("Color Data Median Tool")
    print("=" * 60)
    
    try:
        success = interpolate_color_data(input_file, output_file, interval)
        
        if success:
            print("\nMedian calculation completed successfully!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

