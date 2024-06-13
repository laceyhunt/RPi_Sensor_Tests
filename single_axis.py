import smbus
import time
from collections import deque
import RPi.GPIO as GPIO

print("starting...")
# Initialize GPIO pins
reset_pin=27
input_pin=22
GPIO.setmode(GPIO.BCM) # GPIO numbering 
GPIO.setup(reset_pin, GPIO.OUT) # reset
GPIO.setup(input_pin, GPIO.IN) # input

# set reset low, wait, high, wait
GPIO.output(reset_pin,GPIO.LOW)
time.sleep(0.01)
GPIO.output(reset_pin,GPIO.HIGH)
print("done with GPIO init")
time.sleep(2)

# Initialize I2C bus
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

# Device address (detected by i2cdetect)
DEVICE_ADDRESS = 0x12

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
    data = read_i2c_block(0x00, 3)  # Read 2 bytes from register 0x00
    print(data)
    if data is not None:
        integer_part = data[0]
        fractional_part = data[1]
        angle = integer_part + fractional_part / 256.0  # Assuming fractional part is in 1/256 units
        return angle
    else:
        return None

# Sequence of writes to initialize the sensor
# while GPIO.input(input_pin)!=GPIO.LOW:
#     pass
# write_i2c_block(0x0A, [0, 0])
# time.sleep(0.1)
# while GPIO.input(input_pin)!=GPIO.LOW:
#     pass

# data=read_i2c_block(0x02, 2)
# print(data)
# time.sleep(0.1)

# write_i2c_block(0x0A, [0, 3])
# time.sleep(0.1)

# data=read_i2c_block(0x02, 2)
# print(data)
# time.sleep(0.1)

# write_i2c_block(0x06, [0, 0])
# time.sleep(0.1)

# data=read_i2c_block(0x01, 2)
# print(data)
# time.sleep(0.1)
"""
    ADS_1_HZ   = 16384,					// 1 sample per second, Interrupt Mode
	ADS_10_HZ  = 1638,					// 10 samples per second, Interrupt Mode
	ADS_20_HZ  = 819,					// 20 samples per second, Interrupt Mode
	ADS_50_HZ  = 327,					// 50 samples per second, Interrupt Mode
	ADS_100_HZ = 163,					// 100 samples per second, Interrupt Mode
	ADS_200_HZ = 81,					// 200 samples per second, Interrupt Mode, max rate for bend + stretch
	ADS_333_HZ = 49,					// 333 samples per second, Interrupt Mode
	ADS_500_HZ = 32,					// 500 samples per second, Interrupt Mode, max rate
"""
# write_i2c_block(0x01, [16384, 00])
# time.sleep(0.1)

# write_i2c_block(0x09, [0, 0])
# time.sleep(0.1)

# write_i2c_block(0x01, [0xA3, 00])
# time.sleep(0.1)

write_i2c_block(0x00, [1, 00])
time.sleep(0.1)
print("Done with i2c init")

# Now the sensor should be running

# Moving average filter
class MovingAverage:
    def __init__(self, size):
        self.size = size
        self.buffer = deque([0.0] * size, maxlen=size)

    def add(self, value):
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)

# Callback function for data ready interrupt
# def data_ready_callback(channel):
#     print("Data ready pin went low, reading sensor data...")
#     read_sensor_data()
# GPIO.add_event_detect(input_pin, GPIO.FALLING, callback=data_ready_callback)

print("Waiting for data ready interrupt...")

# Main loop to continuously read from the sensor
try:
    # filter_size = 10  # Size of the moving average filter
    # moving_average = MovingAverage(filter_size)

    while True:
        angle = read_sensor_data()
    #     if angle is not None:
    #         pass # because read_sensor_data handles printing raw data
    #         # smoothed_angle = moving_average.add(angle)
    #         # print(f" {smoothed_angle:.2f}")
    #     else:
    #         print("Failed to read sensor data.")
    #     # change to just read when interrupted
        time.sleep(0.1)  # Adjust the sleep time as needed (e.g., for 10Hz sampling rate, use 0.1s)
    #     # inp=GPIO.input(input_pin)
        # while GPIO.input(input_pin)!=GPIO.LOW:
    #     # while inp!=0:
    #         # print(f"Input={inp}")
    #         # inp=GPIO.input(input_pin)
            # pass

except KeyboardInterrupt:
    print("Program stopped, cleaning up...")
    GPIO.cleanup()
    bus.close()
    quit()