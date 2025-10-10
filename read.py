import serial
import csv
import datetime
import time
import os

# Configuration
SERIAL_PORT = 'COM3'  # Change this to your Arduino's port (e.g., COM3, COM4, /dev/ttyUSB0, etc.)
BAUD_RATE = 115200      # Make sure this matches your Arduino's baud rate
TIMEOUT = 1           # Serial timeout in seconds

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
    
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)  # Wait for Arduino to reset after serial connection
        print("Connected! Reading data... (Press Ctrl+C to stop)")
        
        # Open CSV file for writing with line buffering
        csvfile = open(csv_filename, 'w', newline='', buffering=1)
        csv_writer = csv.writer(csvfile)
        
        # Write header
        csv_writer.writerow(['Timestamp', 'R', 'G', 'B', 'C'])
        csvfile.flush()  # Flush header immediately
        
        # Read and log data
        while True:
            if ser.in_waiting > 0:
                # Read line from serial
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    print(f"Received: {line}")
                    
                    # Parse the color data
                    color_data = parse_color_data(line)
                    
                    if color_data:
                        r, g, b, c = color_data
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        
                        # Write to CSV
                        csv_writer.writerow([timestamp, r, g, b, c])
                        csvfile.flush()  # Ensure data is written immediately
                        os.fsync(csvfile.fileno())  # Force OS to write to disk
                        
                        print(f"Logged: {timestamp} - R:{r} G:{g} B:{b} C:{c}")
    
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        print(f"Make sure {SERIAL_PORT} is correct and the device is connected.")
    except KeyboardInterrupt:
        print("\n\nStopping data logging...")
        print(f"Data saved to: {csv_filename}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
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

if __name__ == "__main__":
    main()

