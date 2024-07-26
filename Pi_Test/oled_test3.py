import csv
from smbus2 import SMBus, i2c_msg
import time

# I2C address and bus
I2C_ADDRESS = 0x3C
I2C_BUS = 1
CHUNK_SIZE = 31  # Effective chunk size after accounting for the control byte

# Function to read CSV and write hex values to I2C
def read_hex_csv_and_write_i2c(file_path):
    bus = SMBus(I2C_BUS)
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) > 1:  # Ensure there's a second column
                hex_data = row[1].split()  # Split the space-separated hex values
                if len(hex_data) > 1:
                    register_address = int(hex_data[0], 16)  # First byte is the register address
                    data_to_write = [int(hex_value, 16) for hex_value in hex_data[1:]]  # Rest are data bytes

                    # Write the data in chunks if necessary
                    for i in range(0, len(data_to_write), CHUNK_SIZE):
                        chunk = data_to_write[i:i + CHUNK_SIZE]
                        # Combine register address, control byte, and data chunk
                        message = i2c_msg.write(I2C_ADDRESS, [register_address] + chunk)
                        bus.i2c_rdwr(message)
                        print(f"{message}")

    bus.close()

# Example usage
file_path = 'oled_1.csv'
read_hex_csv_and_write_i2c(file_path)
# time.sleep(5)
# # Example usage
# file_path = 'oled_2.csv'
# read_hex_csv_and_write_i2c(file_path)