import smbus
import time
from collections import deque
import RPi.GPIO as GPIO

print("Starting...")

DEVICE_ADDRESS=0x12
NEW_ADDRESS=0x13

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
    
def change_addr():
    global DEVICE_ADDRESS, NEW_ADDRESS
    old=read_i2c_block(0x2,3)
    print(f"Old Address={old}")
    time.sleep(0.1)
    # DEVICE_ADDRESS=NEW_ADDRESS
    write_i2c_block(0x4, [NEW_ADDRESS,00])
    DEVICE_ADDRESS=NEW_ADDRESS
    old=read_i2c_block(0x2,3)
    print(f"New Address={old}")
    time.sleep(0.1)

change_addr()