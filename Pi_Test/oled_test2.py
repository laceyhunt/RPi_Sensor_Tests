import csv
from smbus2 import SMBus, i2c_msg
import time
import RPi.GPIO as GPIO

# I2C address and bus
I2C_ADDRESS = 0x3C
BEND_ADDRESS = 0x13
I2C_BUS = 1
CHUNK_SIZE = 31  # Effective chunk size after accounting for the control byte
NUM_BYTES=5
reset_pin=27       
bus = SMBus(I2C_BUS)
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

# init sensor
GPIO.setmode(GPIO.BCM) # GPIO numbering 
GPIO.setup(reset_pin, GPIO.OUT) # reset
GPIO.output(reset_pin,GPIO.LOW)
time.sleep(0.01)
GPIO.output(reset_pin,GPIO.HIGH)
time.sleep(2)
print("done with GPIO and reset init")

def write_i2c_block(address, data):
    bus.write_i2c_block_data(BEND_ADDRESS, address, data)
    time.sleep(0.01)  # Small delay to ensure the command is processed
def read_i2c_block(address, length):
    try:
        return bus.read_i2c_block_data(BEND_ADDRESS, address, length)
    except OSError as e:
        print(f"Error reading I2C data: {e}")
        return None
def read_sensor_data():
    data = read_i2c_block(0x00, NUM_BYTES)  # Read 3 bytes from register 0x00, 5 instead of 3
    # print(f"raw: {data}") 
    if data is not None:
        decoded_value1 = ads_int16_decode_single(data)
        if(BEND_ADDRESS==0x12):
            print(f"Decoded: {decoded_value1}      Raw: {data}")
        if(BEND_ADDRESS==0x13):
            decoded_value2 = ads_int16_decode_two(data)
            # print(f"Decoded: {decoded_value2}")
            print(f"Decoded: {decoded_value1}, {decoded_value2}      Raw: {data}")
        return decoded_value1
    else:
        return None
def ads_int16_decode_single(data):
    if len(data) < 3:
        raise ValueError("Input data must contain at least three bytes")
    # Combine the bytes to get the raw 16-bit value
    raw_value = (data[2] << 8) | data[1] # equal to data[2]*256+data[1]
    # Convert raw_value to signed 16-bit integer
    if raw_value & 0x8000:  # Check if the sign bit is set
        decoded_value = raw_value - 0x10000
    else:
        decoded_value = raw_value
    # Scale the value
    decoded_value = decoded_value / 64
    return decoded_value
def ads_int16_decode_two(data):
    if len(data) < 3:
        raise ValueError("Input data must contain at least three bytes")
    # Combine the bytes to get the raw 16-bit value
    raw_value2 = (data[4] << 8) | data[3] # equal to data[2]*256+data[1]
    # Convert raw_value to signed 16-bit integer
    if raw_value2 & 0x8000:  # Check if the sign bit is set
        decoded_value2 = raw_value2 - 0x10000
    else:
        decoded_value2 = raw_value2
    # Scale the value
    decoded_value2 = decoded_value2 / 64
    return decoded_value2


def get_device_address():
    global BEND_ADDRESS
    global NUM_BYTES
    sensor_type=read_i2c_block(0xA,NUM_BYTES) # read device id
    print(f"{sensor_type}-axis sensor...")
    if(sensor_type[0]==0x1):
        BEND_ADDRESS=0x12
        NUM_BYTES=3
        print("SINGLE!!")
    elif(sensor_type[0]==0x2):
        BEND_ADDRESS==0x13
        NUM_BYTES=5
        print("DOUBLE!!")

# time.sleep(5)
# file_path = 'oled_2.csv'
# read_hex_csv_and_write_i2c(file_path)

# for i in range(10):
try:
    # get_device_address()
    # init oled
    file_path = 'oled_1.csv'
    read_hex_csv_and_write_i2c(file_path)
    print("Done with oled init")
    # Sequence of writes to initialize the sensor
    if(BEND_ADDRESS==0x12):
        write_i2c_block(0x05, [1, 1])  # polled mode
        time.sleep(0.1)
        write_i2c_block(0x01, [163, 00])
        time.sleep(0.1)
        write_i2c_block(0x00, [1, 00])
        time.sleep(0.1)
    elif(BEND_ADDRESS==0x13):
        write_i2c_block(0x05, [1, 1, 0, 0])  # polled mode
        time.sleep(0.1)
        write_i2c_block(0x01, [163, 00, 00, 00])
        time.sleep(0.1)
        write_i2c_block(0x00, [1, 00, 00, 00])
        time.sleep(0.1)
    print("Done with sensor init")
    print("Now, reading from sensor...")
    # while(True):
    # for i in range (1,20):
    #     time.sleep(0.01)
    #     angle = read_sensor_data()
    #     if(BEND_ADDRESS==0x12):
    #         write_i2c_block(0x00, [1, 00]) # RUN COMMAND
    #     elif(BEND_ADDRESS==0x13):
    #         write_i2c_block(0x00, [1, 00, 00, 00]) # RUN COMMAND
    #     time.sleep(0.05)
    # print("Read 20 samples.")

    time.sleep(5)

    print("Running oled...")
    file_path = 'oled_2.csv'
    read_hex_csv_and_write_i2c(file_path)
    print("Done with second oled")
    # print("Running sensor...")
    # while(True):
    # # for i in range (1,20):
    #     time.sleep(0.01)
    #     angle = read_sensor_data()
    #     if(BEND_ADDRESS==0x12):
    #         write_i2c_block(0x00, [1, 00]) # RUN COMMAND
    #     elif(BEND_ADDRESS==0x13):
    #         write_i2c_block(0x00, [1, 00, 00, 00]) # RUN COMMAND
    #     time.sleep(0.05)

except KeyboardInterrupt:
    print("Program stopped, cleaning up...")
    GPIO.cleanup()
    bus.close()

    print("read some vals")
    quit()


    # auto detect sensor type
    # init oled
    # take samples
    # do oled sequence
    # take more 