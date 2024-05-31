import smbus
import time
# Initialize I2C bus
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

# Device address
DEVICE_ADDRESS = 0x12

def write_i2c_block(address, data):
    bus.write_i2c_block_data(DEVICE_ADDRESS, address, data)
    time.sleep(0.01)  # Small delay to ensure the command is processed

def read_i2c_block(address, length):
    return bus.read_i2c_block_data(DEVICE_ADDRESS, address, length)

# Sequence of writes to initialize the sensor
write_i2c_block(0x0A, [0, 0])
write_i2c_block(0x0A, [0, 3])
write_i2c_block(0x05, [0, 1])
write_i2c_block(0x00, [0, 1])

# Now the sensor should be running

# Function to read data from the sensor
def read_sensor_data():
    data = read_i2c_block(0x00, 2)  # Read 2 bytes from register 0x00
    integer_part = data[0]
    fractional_part = data[1]
    angle = integer_part + fractional_part / 256.0  # Assuming fractional part is in 1/256 units
    return angle

# Main loop to continuously read from the sensor
try:
    while True:
        angle = read_sensor_data()
        print(f"Angle: {angle} degrees")
        time.sleep(0.1)  # Adjust the sleep time as needed (e.g., for 10Hz sampling rate, use 0.1s)
except KeyboardInterrupt:
    print("Program stopped")