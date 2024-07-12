import smbus
import time
from collections import deque
import RPi.GPIO as GPIO

print("Starting...")

# Function to get user input and set DEVICE_ADDRESS
def get_device_address():
    while True:
        user_input = input("Enter 1 or 2 to select device address: ")
        if user_input == '1':
            num_read=3
            return 0x12
        elif user_input == '2':
            num_read=5
            return 0x13
        else:
            print("Invalid input. Please enter either 1 or 2.")

DEVICE_ADDRESS = get_device_address()
# Initialize GPIO pins
reset_pin = 27       
input_pin = 22   # aka DRDY, note this is not used in this ex b/c of delays
i2c_enable_pin = 23 # used for the buffer chip
GPIO.setmode(GPIO.BCM) # GPIO numbering 
GPIO.setup(reset_pin, GPIO.OUT) # reset
GPIO.setup(i2c_enable_pin, GPIO.OUT) # i2c buffer enable pin
GPIO.setup(input_pin, GPIO.IN) # input
num_read =3 #3 for single, 5 for two

# GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set reset low, wait, high, wait
# note reset pin does not go through i2c so no need to set buffer
GPIO.output(reset_pin, GPIO.LOW)
time.sleep(0.01)
GPIO.output(reset_pin, GPIO.HIGH)
time.sleep(2)
# set i2c enable to HI then LO for initializing ... set to HI anytime I2C is going
GPIO.output(i2c_enable_pin, GPIO.HIGH)
time.sleep(0.01)
GPIO.output(i2c_enable_pin, GPIO.LOW)
time.sleep(2)
print("Done with GPIO and reset init")
time.sleep(2)

# Initialize I2C bus
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1


def write_i2c_block(address, data):
    bus.write_i2c_block_data(DEVICE_ADDRESS, address, data)
    time.sleep(0.01)  # Small delay to ensure the command is processed

def read_i2c_block(address, length):
    try:
        return bus.read_i2c_block_data(DEVICE_ADDRESS, address, length)
    except OSError as e:
        print(f"Error reading I2C data: {e}")
        return None

def read_sensor_data():
    data = read_i2c_block(0x00, num_read)  # Read 2 bytes from register 0x00
    print(f"Raw: {data}") 
    if data is not None:
        decoded_value = ads_int16_decode_single(data)
        print(f"Decoded: {decoded_value}")
        if(DEVICE_ADDRESS==0x13):
            decoded_value = ads_int16_decode_two(data)
            print(f"Decoded: {decoded_value}")
        return decoded_value
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

# Sequence of writes to initialize the sensor
GPIO.output(i2c_enable_pin, GPIO.HIGH)
write_i2c_block(0x05, [1, 1])  # polled mode
time.sleep(0.1)
write_i2c_block(0x01, [163, 00])  # Set the desired sample rate
time.sleep(0.1)
write_i2c_block(0x00, [1, 00])  # Run command
time.sleep(0.1)
print("Done with I2C init")
GPIO.output(i2c_enable_pin, GPIO.LOW)

# Now the sensor should be running


print("Waiting for data ready interrupt...")

# Main loop to continuously read from the sensor
try:
    while True:
        GPIO.output(i2c_enable_pin, GPIO.HIGH)
        time.sleep(0.01)
        angle = read_sensor_data()
        write_i2c_block(0x00, [1, 00])  # RUN COMMAND
        time.sleep(0.01)
        GPIO.output(i2c_enable_pin, GPIO.LOW)
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Program stopped, cleaning up...")
    GPIO.cleanup()
    bus.close()
    quit()
