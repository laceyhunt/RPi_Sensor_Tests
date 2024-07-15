# import smbus
import time
# from collections import deque
# import RPi.GPIO as GPIO

import pandas as pd
from smbus2 import SMBus

OLED_ADDRESS = 0x3C # oled address

# Initialize GPIO pins
# reset_pin = 27       
# input_pin = 22   # aka DRDY, note this is not used in this ex b/c of delays
# i2c_enable_pin = 23 # used for the buffer chip
# GPIO.setmode(GPIO.BCM) # GPIO numbering 
# GPIO.setup(reset_pin, GPIO.OUT) # reset
# GPIO.setup(i2c_enable_pin, GPIO.OUT) # i2c buffer enable pin
# GPIO.setup(input_pin, GPIO.IN) # input

# Function to write data to I2C device
def write_i2c_data(address, data):
    bus = SMBus(1)  # Use SMBus(0) for older Raspberry Pi versions
    try:
        bus.write_byte(address, data)
        print(f"Data 0x{data:02X} written to address 0x{address:02X}")
    except Exception as e:
        print(f"Failed to write to address 0x{address:02X}: {e}")
    finally:
        bus.close()

# Main function
def main():
    # Load the CSV file
    csv_file = "oled_init.csv"
    df = pd.read_csv(csv_file, usecols=['Addr', 'Data', 'Ack'])

    # Split the DataFrame into two chunks based on '12W'
    chunk1 = []
    chunk2 = []
    found_12w = False
    # Ensure column names are correctly specified
    df.columns = ['Addr', 'Data', 'Ack']

    for _, row in df.iterrows():
        instruction = row['Addr'].strip()
        if instruction.startswith("3CW") and not found_12w:
            address = int(instruction[0:2], 16)
            data_str = row['Data'].strip().replace(" ", "")  # Remove spaces
            data = int(data_str, 16)  # Convert hex string to integer
            chunk1.append((address, data))
        elif instruction.startswith("12W"):
            found_12w = True
        elif instruction.startswith("3CW") and found_12w:
            address = int(instruction[0:2], 16)
            data_str = row['Data'].strip().replace(" ", "")  # Remove spaces
            data = int(data_str, 16)  # Convert hex string to integer
            chunk2.append((address, data))
        time.sleep(.1)

    # Write the first chunk
    print("Writing first chunk...")
    for address, data in chunk1:
        write_i2c_data(address, data)

    # # Wait for a specified amount of time
    # wait_time = 5  # seconds
    # print(f"Waiting for {wait_time} seconds...")
    # time.sleep(wait_time)

    # # Write the second chunk
    # print("Writing second chunk...")
    # for address, data in chunk2:
    #     write_i2c_data(address, data)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Process interrupted by user.")