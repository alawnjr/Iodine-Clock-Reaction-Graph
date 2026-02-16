import serial
import csv
import datetime
import time
import os
import matplotlib.pyplot as plt

# Configuration
SERIAL_PORT = 'COM3'  # Change this to your Arduino's port (e.g., COM3, COM4, /dev/ttyUSB0, etc.)
BAUD_RATE = 115200      # Make sure this matches your Arduino's baud rate
TIMEOUT = 1           # Serial timeout in seconds
UPDATE_INTERVAL = 5   # Update graph every N data points
ENABLE_LIVE_GRAPH = True  # Set to False to disable live plotting (faster data logging)

def generate_unique_filename():
    """Generate a unique CSV filename using timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"color_data_{timestamp}.csv"
    return filename

def parse_color_data(line):
    """
    Parse color data from serial line.
    Expected format from Arduino: "R G B C" (space-separated values)
    Example: "150 200 180 600"
    """
    try:
        # Remove any whitespace
        line = line.strip()
        
        # Skip the header line if present
        if line == "Red Green Blue Clear":
            return None
        
        # Parse space-separated format like "150 200 180 600"
        parts = line.split()
        if len(parts) >= 4:
            r = int(parts[0])
            g = int(parts[1])
            b = int(parts[2])
            c = int(parts[3])
            return r, g, b, c
        
        return None
    except (ValueError, IndexError) as e:
        print(f"Error parsing line: {line} - {e}")
        return None

def main():
    # Generate unique filename for this run
    csv_filename = generate_unique_filename()
    print(f"Starting color sensor data logging...")
    print(f"Data will be saved to: {csv_filename}")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    
    ser = None
    csvfile = None
    fig = None
    axes_flat = None
    lines = None
    
    try:
        # Initialize data storage (using lists to keep all data points)
        time_data = []
        r_data = []
        g_data = []
        b_data = []
        c_data = []
        
        start_time = None
        data_counter = 0
        
        # Set up real-time plotting if enabled
        if ENABLE_LIVE_GRAPH:
            plt.ion()  # Turn on interactive mode
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle('Real-Time Color Sensor Data', fontsize=14, fontweight='bold')
            axes_flat = axes.flatten()
            
            # Initialize line plots
            colors_list = ['R', 'G', 'B', 'C']
            color_map = {'R': 'red', 'G': 'green', 'B': 'blue', 'C': 'purple'}
            data_map = {'R': r_data, 'G': g_data, 'B': b_data, 'C': c_data}
            lines = {}
            
            for idx, channel in enumerate(colors_list):
                lines[channel], = axes_flat[idx].plot([], [], 'o-', color=color_map[channel], 
                                                       markersize=4, linewidth=1.5, alpha=0.7)
                axes_flat[idx].set_xlabel('Time (s)', fontsize=9)
                axes_flat[idx].set_ylabel(f'{channel} Value', fontsize=9)
                axes_flat[idx].set_title(f'{channel} Channel', fontsize=11, fontweight='bold')
                axes_flat[idx].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.001)
            print("Live graph enabled.")
        else:
            print("Live graph disabled (faster data logging).")
        
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)  # Wait for Arduino to reset after serial connection
        ser.reset_input_buffer()  # Clear any accumulated data in the buffer
        print("Connected! Reading data... (Press Ctrl+C to stop)")
        
        # Open CSV file for writing with line buffering
        csvfile = open(csv_filename, 'w', newline='', buffering=1)
        csv_writer = csv.writer(csvfile)
        
        # Write header
        csv_writer.writerow(['Timestamp', 'R', 'G', 'B', 'C'])
        csvfile.flush()  # Flush header immediately
        
        # Read and log data
        colors_list = ['R', 'G', 'B', 'C']
        color_map = {'R': 'red', 'G': 'green', 'B': 'blue', 'C': 'purple'}
        data_map = {'R': r_data, 'G': g_data, 'B': b_data, 'C': c_data}
        
        while True:
            # Read all available lines to avoid backlog
            if ser.in_waiting > 0:
                while ser.in_waiting > 0:
                    # Read line from serial
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        print(f"Received: {line}")
                        
                        # Parse the color data
                        color_data = parse_color_data(line)
                        
                        if color_data:
                            r, g, b, c = color_data
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                            
                            # Set start time on first data point
                            if start_time is None:
                                start_time = time.time()
                            
                            # Calculate relative time in seconds
                            current_time = time.time() - start_time
                            
                            # Store data
                            time_data.append(current_time)
                            r_data.append(r)
                            g_data.append(g)
                            b_data.append(b)
                            c_data.append(c)
                            
                            # Write to CSV
                            csv_writer.writerow([timestamp, r, g, b, c])
                            csvfile.flush()  # Ensure data is written immediately
                            os.fsync(csvfile.fileno())  # Force OS to write to disk
                            
                            print(f"Logged: {timestamp} - R:{r} G:{g} B:{b} C:{c}")
                            
                            # Update plot periodically (only if live graph is enabled)
                            if ENABLE_LIVE_GRAPH:
                                data_counter += 1
                                if data_counter % UPDATE_INTERVAL == 0:
                                    for idx, channel in enumerate(colors_list):
                                        lines[channel].set_data(time_data, data_map[channel])
                                        axes_flat[idx].relim()
                                        axes_flat[idx].autoscale_view()
                                    
                                    fig.canvas.draw_idle()
                                    fig.canvas.flush_events()
                                    plt.pause(0.001)
            else:
                # Small delay to prevent CPU spinning when no data is available
                time.sleep(0.01)
    
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        print(f"Make sure {SERIAL_PORT} is correct and the device is connected.")
    except KeyboardInterrupt:
        print("\n\nStopping data logging...")
        print(f"Data saved to: {csv_filename}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Turn off interactive plotting (only if it was enabled)
        if ENABLE_LIVE_GRAPH:
            plt.ioff()
        
        # Ensure file is properly closed
        if csvfile is not None:
            try:
                csvfile.flush()
                os.fsync(csvfile.fileno())
                csvfile.close()
                print("CSV file closed and saved.")
            except:
                pass
        
        # Ensure serial port is closed
        if ser is not None and ser.is_open:
            ser.close()
            print("Serial port closed.")
        
        if ENABLE_LIVE_GRAPH:
            print("Close the plot window to exit completely.")
        else:
            print("Exiting...")

if __name__ == "__main__":
    main()

