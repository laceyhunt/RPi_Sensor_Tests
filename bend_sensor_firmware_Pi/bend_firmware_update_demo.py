import time
import smbus2
import RPi.GPIO as GPIO

# Initialize I2C bus
bus = smbus2.SMBus(1)  # 1 indicates /dev/i2c-1


# Constants
ADS_TRANSFER_SIZE = 32
ADS_GET_DEV_ID = 0x00  # Replace with the actual command for getting device ID
ADS_DEV_ID = 0xAB  # Replace with the actual device ID constant
# ADS_DEV_ONE_AXIS_V1 = 0x01  # Replace with actual values
# ADS_DEV_ONE_AXIS_V2 = 0x02  # Replace with actual values
# ADS_DEV_TWO_AXIS_V1 = 0x03  # Replace with actual values
ADS_DEV_UNKNOWN = 0xFF
ADS_OK = 0
ADS_ERR_IO = -1
ADS_ERR_DEV_ID = -1
ADS_DEFAULT_ADDR = 0x12

ADS_GET_FW_VER = 0x01  # Replace with the actual command for getting firmware version
ADS_FW_VER = 0xAB  # Replace with the actual firmware version constant

# Define firmware versions (these should be defined according to your actual firmware versions)
# ADS_FW_REV = 0x0100  # Example version for ADS_ONE_AXIS_V1
# ADS_FW_V2_REV = 0x0200  # Example version for ADS_ONE_AXIS_V2

# Placeholder for ads_uint16_decode function (to decode 2 bytes into a uint16_t)
def ads_uint16_decode(bytes):
    return bytes[0] | (bytes[1] << 8)


# GPIO pins
ADS_RESET_PIN = 27
ADS_INTERRUPT_PIN = 22

# I2C address
_address = ADS_DEFAULT_ADDR
I2C_ADDRESS = ADS_DEFAULT_ADDR

# Global buffer for reading data
read_buffer = [0] * ADS_TRANSFER_SIZE

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ADS_RESET_PIN, GPIO.OUT)
GPIO.setup(ADS_INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Stub function for callback
def ads_data_callback(sample, sample_type):
    pass

# ADS initialization structure
class ADSInit:
    def __init__(self, sps, callback, reset_pin, interrupt_pin, addr):
        self.sps = sps
        self.callback = callback
        self.reset_pin = reset_pin
        self.interrupt_pin = interrupt_pin
        self.addr = addr

# Initialize the sensor
def ads_init(init):
    # GPIO.output(init.reset_pin, GPIO.HIGH)
    # time.sleep(0.1)
    # GPIO.output(init.reset_pin, GPIO.LOW)
    # time.sleep(0.1)
    # GPIO.output(init.reset_pin, GPIO.HIGH)
    # note reset pin does not go through i2c so no need to set buffer
    GPIO.output(init.reset_pin,GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(init.reset_pin,GPIO.HIGH)
    time.sleep(1)
    print("done with GPIO and reset init")
    time.sleep(1)
    # Add additional initialization code here
    return 0  # Return ADS_OK

# Get device type
def ads_get_dev_type():
    buffer = [ADS_GET_DEV_ID] + [0] * (ADS_TRANSFER_SIZE - 1)
    
    # Disable interrupt to prevent callback from reading out device id
    ads_hal_pin_int_enable(False)
    
    # Write buffer to device
    ret = ads_hal_write_buffer(buffer)
    if ret != ADS_OK:
        return ADS_ERR_DEV_ID, ADS_DEV_UNKNOWN
    
    ads_hal_delay(2)
    
    # Read buffer from device
    ret = ads_hal_read_buffer(buffer, ADS_TRANSFER_SIZE)
    if ret != ADS_OK:
        return ADS_ERR_DEV_ID, ADS_DEV_UNKNOWN
    
    # Enable interrupt
    ads_hal_pin_int_enable(True)
    
    if buffer[0] == ADS_DEV_ID:
        # if buffer[1] in (ADS_DEV_ONE_AXIS_V1, ADS_DEV_ONE_AXIS_V2, ADS_DEV_TWO_AXIS_V1):
        return ADS_OK, buffer[1]
    
    return ADS_ERR_DEV_ID, ADS_DEV_UNKNOWN


# Check if firmware update is needed
def ads_dfu_check(ads_dev_type):
    buffer = [ADS_GET_FW_VER, 0, 0]
    
    ads_hal_pin_int_enable(False)
    
    ret = ads_hal_write_buffer(buffer)
    if ret != ADS_OK:
        ads_hal_pin_int_enable(True)
        return False
    
    ads_hal_delay(2)
    
    ret = ads_hal_read_buffer(buffer, ADS_TRANSFER_SIZE)
    ads_hal_pin_int_enable(True)
    
    if ret != ADS_OK:
        return False
    
    if buffer[0] == ADS_FW_VER:
        fw_ver = ads_uint16_decode(buffer[1:3])
    else:
        return False
    
    if ads_dev_type == ADS_DEV_ONE_AXIS_V1:
        return fw_ver < ADS_FW_REV
    elif ads_dev_type == ADS_DEV_ONE_AXIS_V2:
        return fw_ver < ADS_FW_V2_REV
    
    return False


# Reset the device for firmware update
def ads_dfu_reset():
    GPIO.output(ADS_RESET_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(ADS_RESET_PIN, GPIO.HIGH)

# Update the firmware
def ads_dfu_update(dev_type):
    # Replace with actual firmware update code
    return 0  # Return 0 on success

# Delay function
def ads_hal_delay(ms):
    time.sleep(ms / 1000.0)

# Main function
def main():
    print("Press Enter to update firmware...")
    input()
    
    print("Initializing One Axis sensor")
    
    init = ADSInit(
        sps=100,  # 100 Hz sample rate
        callback=ads_data_callback,
        reset_pin=ADS_RESET_PIN,
        interrupt_pin=ADS_INTERRUPT_PIN,
        addr=I2C_ADDRESS
    )
    
    ret_val = ads_init(init)
    if ret_val != 0:
        print(f"One Axis ADS initialization failed with reason: {ret_val}")
        return
    else:
        print("One Axis ADS initialization succeeded...")
    
    ret_val, dev_type = ads_get_dev_type()
    if ret_val != 0:
        print(f"One Axis ADS get device type failed with reason: {ret_val}")
        return
    
    if not ads_dfu_check(dev_type):
        print("One Axis ADS firmware is up to date.")
        return
    
    print("Updating One Axis ADS firmware...")
    
    ads_dfu_reset()
    ads_hal_delay(50)  # Give ADS time to reset
    
    ret_val = ads_dfu_update(dev_type)
    ads_hal_delay(2000)  # Let it reinitialize
    
    if ret_val != 0:
        print(f"Failed up with reason: {ret_val}")
    else:
        print("Update complete.")

# GPIO Pin interrupt enable/disable
def ads_hal_pin_int_enable(enable):
    global ads_interrupt_enabled
    ads_interrupt_enabled = enable
    if enable:
        GPIO.add_event_detect(ADS_INTERRUPT_PIN, GPIO.FALLING, callback=ads_hal_interrupt)
    else:
        GPIO.remove_event_detect(ADS_INTERRUPT_PIN)

# GPIO Pin write
def ads_hal_gpio_pin_write(pin, val):
    GPIO.output(pin, val)

# Delay function
def ads_hal_delay(ms):
    time.sleep(ms / 1000.0)

# Write buffer to device
def ads_hal_write_buffer(buffer):
    try:
        bus.write_i2c_block_data(_address, buffer[0], buffer[1:])
        return ADS_OK
    except:
        return ADS_ERR_IO

# Read buffer from device
def ads_hal_read_buffer(buffer, length):
    try:
        data = bus.read_i2c_block_data(_address, buffer[0], length)
        buffer[:len(data)] = data
        return ADS_OK
    except:
        return ADS_ERR_IO

# Interrupt handler
def ads_hal_interrupt(channel):
    if ads_hal_read_buffer(read_buffer, ADS_TRANSFER_SIZE) == ADS_OK:
        ads_read_callback(read_buffer)

# Initialize pin interrupt
def ads_hal_pin_int_init():
    GPIO.setup(ADS_INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(ADS_INTERRUPT_PIN, GPIO.FALLING, callback=ads_hal_interrupt)

# I2C initialization
def ads_hal_i2c_init():
    bus = smbus2.SMBus(1)
    # Set I2C frequency to 400kHz if necessary (smbus2 sets this by default)

# Reset the device
def ads_hal_reset():
    GPIO.output(ADS_RESET_PIN, GPIO.LOW)
    ads_hal_delay(10)
    GPIO.output(ADS_RESET_PIN, GPIO.HIGH)

# Initialize hardware abstraction layer
def ads_hal_init(callback, reset_pin, datardy_pin):
    global ADS_RESET_PIN, ADS_INTERRUPT_PIN, ads_read_callback
    ADS_RESET_PIN = reset_pin
    ADS_INTERRUPT_PIN = datardy_pin
    ads_read_callback = callback
    ads_hal_reset()
    ads_hal_delay(2000)
    ads_hal_pin_int_init()
    ads_hal_i2c_init()
    return ADS_OK


def ads_get_dev_type():
    buffer = [ADS_GET_DEV_ID] + [0] * (ADS_TRANSFER_SIZE - 1)
    
    # Disable interrupt to prevent callback from reading out device id
    ads_hal_pin_int_enable(False)
    
    # Write buffer to device
    ret = ads_hal_write_buffer(buffer)
    if ret != ADS_OK:
        return ADS_ERR_DEV_ID, ADS_DEV_UNKNOWN
    
    ads_hal_delay(2)
    
    # Read buffer from device
    ret = ads_hal_read_buffer(buffer, ADS_TRANSFER_SIZE)
    if ret != ADS_OK:
        return ADS_ERR_DEV_ID, ADS_DEV_UNKNOWN
    
    # Enable interrupt
    ads_hal_pin_int_enable(True)
    
    if buffer[0] == ADS_DEV_ID:
        # if buffer[1] in (ADS_DEV_ONE_AXIS_V1, ADS_DEV_ONE_AXIS_V2, ADS_DEV_TWO_AXIS_V1):
        return ADS_OK, buffer[1]
    
    return ADS_ERR_DEV_ID, ADS_DEV_UNKNOWN



if __name__ == "__main__":
    main()
