import csv
from smbus2 import SMBus

# I2C address and bus
I2C_ADDRESS = 0x3C
I2C_BUS = 1

# Function to read CSV and write hex values to I2C
def read_hex_csv_and_write_i2c(file_path):
    bus = SMBus(I2C_BUS)
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) > 1:  # Ensure there's a second column
                hex_data = row[1].split()  # Split the space-separated hex values
                data_to_write = []
                for hex_value in hex_data:
                    # Convert hex string to integer and add to the list
                    data_to_write.append(int(hex_value, 16))
                # Write the data to I2C device
                if data_to_write:
                    # bus.write_i2c_block_data(I2C_ADDRESS, 0x00, data_to_write)
                    write_i2c_data(I2C_ADDRESS,data_to_write)

    bus.close()

def write_i2c_data(address, data):
    bus = SMBus(1)  # Use SMBus(0) for older Raspberry Pi versions
    try:
        bus.write_byte(address, data)
        print(f"Data 0x{data:02X} written to address 0x{address:02X}")
    except Exception as e:
        print(f"Failed to write to address 0x{address:02X}: {e}")
    finally:
        bus.close()


# Example usage
file_path = 'oled_1.csv'
read_hex_csv_and_write_i2c(file_path)