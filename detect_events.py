"""
Event Detection Script for Iodine Clock Reaction Data

This script analyzes CSV files containing color sensor data to detect:
1. Pour-in event: When reactants were poured in (sudden change in readings)
2. Clock stop event: When the reaction completes (sigmoid transition from light to dark)

Dependencies:
    pandas, numpy, matplotlib, scipy

Usage:
    python detect_events.py <csv_file> [--plot]
    
Example:
    python detect_events.py color_data_20250101_120000.csv --plot
"""

import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime, timedelta

def calculate_relative_time(df):
    """Calculate relative time in seconds from the first timestamp"""
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    start_time = df['Timestamp'].iloc[0]
    df['Time_s'] = (df['Timestamp'] - start_time).dt.total_seconds()
    return df

def detect_pour_in(df, channel='C', window_size=10, threshold_factor=3.0):
    """
    Detect when reactants were poured in by looking for sudden changes in color readings.
    
    Args:
        df: DataFrame with color data
        channel: Channel to analyze ('R', 'G', 'B', or 'C')
        window_size: Size of rolling window for smoothing
        threshold_factor: Multiplier for standard deviation to set threshold
    
    Returns:
        Tuple of (pour_in_time_s, pour_in_timestamp, confidence)
    """
    if channel not in df.columns:
        print(f"Warning: Channel '{channel}' not found. Using 'C' instead.")
        channel = 'C'
    
    # Smooth the data to reduce noise
    values = df[channel].values
    smoothed = pd.Series(values).rolling(window=window_size, center=True).mean().fillna(values)
    
    # Calculate first derivative (rate of change)
    derivative = np.gradient(smoothed)
    
    # Calculate rolling statistics for adaptive threshold
    rolling_mean = pd.Series(derivative).rolling(window=window_size*2, center=True).mean()
    rolling_std = pd.Series(derivative).rolling(window=window_size*2, center=True).std()
    
    # Find points where derivative exceeds threshold
    threshold = rolling_mean + threshold_factor * rolling_std
    
    # Find the first significant change (pour-in should happen early)
    # Look in the first 30% of the data
    search_end = int(len(df) * 0.3)
    significant_changes = np.where(np.abs(derivative[:search_end]) > np.abs(threshold[:search_end]))[0]
    
    if len(significant_changes) > 0:
        # Take the first significant change
        pour_in_idx = significant_changes[0]
        pour_in_time_s = df.iloc[pour_in_idx]['Time_s']
        pour_in_timestamp = df.iloc[pour_in_idx]['Timestamp']
        
        # Calculate confidence based on magnitude of change
        change_magnitude = np.abs(derivative[pour_in_idx])
        avg_change = np.abs(derivative[:search_end]).mean()
        confidence = min(100, (change_magnitude / (avg_change + 1e-6)) * 20)
        
        return pour_in_time_s, pour_in_timestamp, confidence
    
    return None, None, 0

def sigmoid(x, L, k, x0):
    """
    Sigmoid function: L / (1 + exp(-k * (x - x0)))
    L: maximum value
    k: steepness
    x0: inflection point (midpoint)
    """
    return L / (1 + np.exp(-k * (x - x0)))

def detect_clock_stop(df, channel='C', min_points=50):
    """
    Detect when the clock should stop by fitting a sigmoid curve to the transition.
    The reaction changes from light to dark, following a sigmoid curve.
    
    Args:
        df: DataFrame with color data
        channel: Channel to analyze ('R', 'G', 'B', or 'C')
        min_points: Minimum number of points required for sigmoid fitting
    
    Returns:
        Tuple of (clock_stop_time_s, clock_stop_timestamp, inflection_point_time_s)
    """
    if channel not in df.columns:
        print(f"Warning: Channel '{channel}' not found. Using 'C' instead.")
        channel = 'C'
    
    if len(df) < min_points:
        print(f"Warning: Not enough data points ({len(df)}) for sigmoid fitting. Need at least {min_points}.")
        return None, None, None
    
    # Get time and values
    time_s = df['Time_s'].values
    values = df[channel].values
    
    # Determine if values are increasing or decreasing (reaction goes light to dark)
    # If initial values are higher, reaction is decreasing (light to dark)
    # If initial values are lower, reaction is increasing (dark to light)
    initial_avg = np.mean(values[:min(20, len(values)//10)])
    final_avg = np.mean(values[-min(20, len(values)//10):])
    
    is_decreasing = initial_avg > final_avg
    
    # Normalize values to 0-1 range for better sigmoid fitting
    if is_decreasing:
        # Invert so we're fitting an increasing sigmoid
        normalized = (values.max() - values) / (values.max() - values.min() + 1e-6)
    else:
        normalized = (values - values.min()) / (values.max() - values.min() + 1e-6)
    
    # Initial guess for sigmoid parameters
    L_guess = 1.0  # Maximum normalized value
    k_guess = 0.1  # Steepness (adjust based on time scale)
    x0_guess = time_s[len(time_s) // 2]  # Midpoint guess
    
    try:
        # Fit sigmoid curve
        popt, _ = curve_fit(sigmoid, time_s, normalized,
                           p0=[L_guess, k_guess, x0_guess],
                           maxfev=5000,
                           bounds=([0.5, 0.01, time_s[0]], [1.5, 10.0, time_s[-1]]))
        
        L, k, x0 = popt
        
        # The inflection point (x0) is where the reaction is halfway through
        # For clock stop, we might want a point slightly after inflection
        # Use 90% of the transition as the "stop" point
        # Calculate time when sigmoid reaches 0.9
        # 0.9 = L / (1 + exp(-k * (t - x0)))
        # Solving: t = x0 + (1/k) * ln(0.9 / (L - 0.9))
        if L > 0.9:
            stop_time_s = x0 + (1/k) * np.log(0.9 / (L - 0.9))
        else:
            stop_time_s = x0
        
        # Ensure stop time is within data range
        stop_time_s = max(time_s[0], min(time_s[-1], stop_time_s))
        
        # Find closest timestamp
        stop_idx = np.argmin(np.abs(time_s - stop_time_s))
        clock_stop_timestamp = df.iloc[stop_idx]['Timestamp']
        
        return stop_time_s, clock_stop_timestamp, x0
        
    except Exception as e:
        print(f"Error fitting sigmoid: {e}")
        # Fallback: find point of maximum rate of change
        derivative = np.gradient(values)
        max_change_idx = np.argmax(np.abs(derivative))
        stop_time_s = time_s[max_change_idx]
        clock_stop_timestamp = df.iloc[max_change_idx]['Timestamp']
        return stop_time_s, clock_stop_timestamp, stop_time_s

def analyze_csv_file(csv_file, plot=False):
    """
    Analyze a CSV file to detect pour-in and clock stop events.
    
    Args:
        csv_file: Path to CSV file
        plot: Whether to create a visualization plot
    """
    print(f"\n{'='*60}")
    print(f"Analyzing: {csv_file}")
    print(f"{'='*60}")
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    if len(df) == 0:
        print("Error: CSV file is empty")
        return
    
    print(f"Found {len(df)} data points")
    
    # Calculate relative time
    df = calculate_relative_time(df)
    
    # Detect pour-in event
    print("\n--- Pour-In Detection ---")
    pour_in_time_s, pour_in_timestamp, confidence = detect_pour_in(df, channel='C')
    
    if pour_in_time_s is not None:
        print(f"Pour-in detected at:")
        print(f"  Relative time: {pour_in_time_s:.2f} seconds")
        print(f"  Timestamp: {pour_in_timestamp}")
        print(f"  Confidence: {confidence:.1f}%")
    else:
        print("Could not detect pour-in event")
    
    # Detect clock stop event
    print("\n--- Clock Stop Detection ---")
    clock_stop_time_s, clock_stop_timestamp, inflection_time_s = detect_clock_stop(df, channel='C')
    
    if clock_stop_time_s is not None:
        print(f"Clock stop detected at:")
        print(f"  Relative time: {clock_stop_time_s:.2f} seconds")
        print(f"  Timestamp: {clock_stop_timestamp}")
        if inflection_time_s is not None and inflection_time_s != clock_stop_time_s:
            print(f"  Inflection point (50% transition): {inflection_time_s:.2f} seconds")
        
        if pour_in_time_s is not None:
            reaction_time = clock_stop_time_s - pour_in_time_s
            print(f"\nReaction time (pour-in to clock stop): {reaction_time:.2f} seconds ({reaction_time/60:.2f} minutes)")
    else:
        print("Could not detect clock stop event")
    
    # Create visualization if requested
    if plot:
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(f'Event Detection: {csv_file}', fontsize=14, fontweight='bold')
        
        # Plot 1: Clear channel with events marked
        ax1 = axes[0]
        ax1.plot(df['Time_s'], df['C'], 'b-', alpha=0.7, linewidth=1, label='Clear Channel')
        
        if pour_in_time_s is not None:
            ax1.axvline(pour_in_time_s, color='g', linestyle='--', linewidth=2, 
                       label=f'Pour-in ({pour_in_time_s:.2f}s)')
        
        if clock_stop_time_s is not None:
            ax1.axvline(clock_stop_time_s, color='r', linestyle='--', linewidth=2,
                       label=f'Clock Stop ({clock_stop_time_s:.2f}s)')
            if inflection_time_s is not None and inflection_time_s != clock_stop_time_s:
                ax1.axvline(inflection_time_s, color='orange', linestyle=':', linewidth=1.5,
                           label=f'Inflection ({inflection_time_s:.2f}s)')
        
        ax1.set_xlabel('Time (seconds)', fontsize=11)
        ax1.set_ylabel('Clear Channel Value', fontsize=11)
        ax1.set_title('Clear Channel with Detected Events', fontsize=12, fontweight='bold')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: All channels
        ax2 = axes[1]
        for channel, color in [('R', 'red'), ('G', 'green'), ('B', 'blue'), ('C', 'purple')]:
            if channel in df.columns:
                ax2.plot(df['Time_s'], df[channel], color=color, alpha=0.7, linewidth=1, label=channel)
        
        if pour_in_time_s is not None:
            ax2.axvline(pour_in_time_s, color='g', linestyle='--', linewidth=2)
        
        if clock_stop_time_s is not None:
            ax2.axvline(clock_stop_time_s, color='r', linestyle='--', linewidth=2)
        
        ax2.set_xlabel('Time (seconds)', fontsize=11)
        ax2.set_ylabel('Color Channel Value', fontsize=11)
        ax2.set_title('All Color Channels', fontsize=12, fontweight='bold')
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = csv_file.replace('.csv', '_events.png')
        plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
        print(f"\nPlot saved to: {plot_filename}")
        
        plt.show()
    
    return {
        'pour_in_time_s': pour_in_time_s,
        'pour_in_timestamp': pour_in_timestamp,
        'clock_stop_time_s': clock_stop_time_s,
        'clock_stop_timestamp': clock_stop_timestamp,
        'reaction_time_s': clock_stop_time_s - pour_in_time_s if (pour_in_time_s and clock_stop_time_s) else None
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_events.py <csv_file> [--plot]")
        print("\nExample:")
        print("  python detect_events.py color_data_20250101_120000.csv")
        print("  python detect_events.py color_data_20250101_120000.csv --plot")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    plot = '--plot' in sys.argv
    
    results = analyze_csv_file(csv_file, plot=plot)
    
    if results:
        print(f"\n{'='*60}")
        print("Summary:")
        print(f"{'='*60}")
        if results['pour_in_time_s']:
            print(f"Pour-in: {results['pour_in_time_s']:.2f}s")
        if results['clock_stop_time_s']:
            print(f"Clock stop: {results['clock_stop_time_s']:.2f}s")
        if results['reaction_time_s']:
            print(f"Reaction time: {results['reaction_time_s']:.2f}s ({results['reaction_time_s']/60:.2f} min)")

if __name__ == "__main__":
    main()

