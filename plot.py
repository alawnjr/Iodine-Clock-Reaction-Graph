import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime

def plot_color_data(csv_files):
    """
    Plot R, G, B, C values from multiple CSV files
    """
    if not csv_files:
        print("No color data CSV files found!")
        return
    
    print(f"Found {len(csv_files)} CSV file(s) to plot")
    
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Color Sensor Data Over Time', fontsize=16, fontweight='bold')
    
    # Flatten axes for easier iteration
    axes_flat = axes.flatten()
    
    colors_to_plot = ['R', 'G', 'B', 'C']
    color_map = {'R': 'red', 'G': 'green', 'B': 'blue', 'C': 'purple'}
    
    # Plot each CSV file
    for csv_file in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Convert timestamp to datetime
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            
            # Create a relative time in seconds from start
            df['Time (s)'] = (df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds()
            
            # Extract filename for legend
            filename = os.path.basename(csv_file)
            
            # Plot each color channel in its own subplot
            for idx, color_channel in enumerate(colors_to_plot):
                if color_channel in df.columns:
                    axes_flat[idx].plot(df['Time (s)'], df[color_channel], 
                                       label=filename, 
                                       marker='o' if len(df) < 50 else '',
                                       markersize=3,
                                       linewidth=1.5,
                                       alpha=0.7)
            
            print(f"Plotted: {filename} ({len(df)} data points)")
            
        except Exception as e:
            print(f"Error plotting {csv_file}: {e}")
    
    # Configure each subplot
    for idx, color_channel in enumerate(colors_to_plot):
        axes_flat[idx].set_xlabel('Time (seconds)', fontsize=10)
        axes_flat[idx].set_ylabel(f'{color_channel} Value', fontsize=10)
        axes_flat[idx].set_title(f'{color_channel} Channel', fontsize=12, fontweight='bold')
        axes_flat[idx].grid(True, alpha=0.3)
        axes_flat[idx].legend(fontsize=8)
    
    plt.tight_layout()
    
    # Save the plot
    output_filename = f"color_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as: {output_filename}")
    
    # Show the plot
    plt.show()


def plot_combined_rgb(csv_files):
    """
    Create an additional plot showing all RGB values on the same graph
    """
    if not csv_files:
        return
    
    fig, ax = plt.subplots(figsize=(15, 6))
    fig.suptitle('RGB Values Combined', fontsize=16, fontweight='bold')
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df['Time (s)'] = (df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds()
            
            filename = os.path.basename(csv_file)
            
            # Plot R, G, B on same axis
            ax.plot(df['Time (s)'], df['R'], 'r-', label=f'{filename} - Red', alpha=0.7, linewidth=1.5)
            ax.plot(df['Time (s)'], df['G'], 'g-', label=f'{filename} - Green', alpha=0.7, linewidth=1.5)
            ax.plot(df['Time (s)'], df['B'], 'b-', label=f'{filename} - Blue', alpha=0.7, linewidth=1.5)
            
        except Exception as e:
            print(f"Error in combined plot for {csv_file}: {e}")
    
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Color Value', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    
    plt.tight_layout()
    
    # Save the combined plot
    output_filename = f"rgb_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Combined RGB plot saved as: {output_filename}")
    
    plt.show()


def read_files_to_plot(filelist_path="files_to_plot.txt"):
    """
    Read list of CSV files to plot from a text file
    Returns list of valid file paths
    """
    csv_files = []
    
    if not os.path.exists(filelist_path):
        print(f"File list not found: {filelist_path}")
        print(f"Creating example file: {filelist_path}")
        
        # Create an example file with all available CSV files
        all_csv_files = glob.glob("color_data_*.csv")
        if all_csv_files:
            with open(filelist_path, 'w') as f:
                f.write("# List the CSV files you want to plot (one per line)\n")
                f.write("# Lines starting with # are comments and will be ignored\n")
                f.write("# Example:\n")
                for csv_file in all_csv_files[:3]:  # Show first 3 as examples
                    f.write(f"# {csv_file}\n")
                f.write("\n")
                f.write("# Uncomment the files you want to plot:\n")
                for csv_file in all_csv_files:
                    f.write(f"{csv_file}\n")
            print(f"Created {filelist_path} with all available CSV files.")
            print(f"Edit this file to select which files to plot, then run again.")
        else:
            with open(filelist_path, 'w') as f:
                f.write("# List the CSV files you want to plot (one per line)\n")
                f.write("# Lines starting with # are comments and will be ignored\n")
                f.write("# Example:\n")
                f.write("# color_data_20251010_153420.csv\n")
            print(f"No CSV files found. Created empty {filelist_path}")
            print("Add your CSV filenames to this file, then run again.")
        return []
    
    # Read the file list
    print(f"Reading file list from: {filelist_path}")
    with open(filelist_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                if os.path.exists(line):
                    csv_files.append(line)
                    print(f"  ✓ Found: {line}")
                else:
                    print(f"  ✗ Not found: {line}")
    
    return csv_files


def main():
    print("=" * 60)
    print("Color Sensor Data Plotter")
    print("=" * 60)
    
    # Read list of files to plot from text file
    csv_files = read_files_to_plot("files_to_plot.txt")
    
    if not csv_files:
        print("\nNo valid CSV files to plot.")
        print("Please edit 'files_to_plot.txt' and add the files you want to plot.")
        return
    
    print(f"\nPlotting {len(csv_files)} file(s)...\n")
    
    # Create the main plot with all channels
    plot_color_data(csv_files)
    
    # Create combined RGB plot
    print("\nCreating combined RGB plot...")
    plot_combined_rgb(csv_files)
    
    print("\nDone!")


if __name__ == "__main__":
    main()

