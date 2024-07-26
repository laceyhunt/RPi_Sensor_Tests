import smbus2
import time

# Constants
I2C_ADDRESS = 0x3C  # Change this to your display's I2C address
WIDTH = 128
HEIGHT = 64
CHUNK_SIZE = 32

# Commands
CMD_DISPLAY_OFF = 0xAE
CMD_DISPLAY_ON = 0xAF
CMD_SET_DISPLAY_CLOCK_DIV = 0xD5
CMD_SET_MULTIPLEX = 0xA8
CMD_SET_DISPLAY_OFFSET = 0xD3
CMD_SET_START_LINE = 0x40
CMD_CHARGE_PUMP = 0x8D
CMD_MEMORY_MODE = 0x20
CMD_SEG_REMAP = 0xA1
CMD_COM_SCAN_DEC = 0xC8
CMD_SET_CONTRAST = 0x81
CMD_SET_PRECHARGE = 0xD9
CMD_SET_VCOM_DETECT = 0xDB
CMD_DISPLAY_ALL_ON_RESUME = 0xA4
CMD_NORMAL_DISPLAY = 0xA6

# Initialization sequence for SSD1306
init_sequence = [
    CMD_DISPLAY_OFF,
    CMD_SET_DISPLAY_CLOCK_DIV, 0x80,
    CMD_SET_MULTIPLEX, HEIGHT - 1,
    CMD_SET_DISPLAY_OFFSET, 0x00,
    CMD_SET_START_LINE | 0x00,
    CMD_CHARGE_PUMP, 0x14,
    CMD_MEMORY_MODE, 0x00,
    CMD_SEG_REMAP | 0x01,
    CMD_COM_SCAN_DEC,
    CMD_SET_CONTRAST, 0xCF,
    CMD_SET_PRECHARGE, 0xF1,
    CMD_SET_VCOM_DETECT, 0x40,
    CMD_DISPLAY_ALL_ON_RESUME,
    CMD_NORMAL_DISPLAY,
    CMD_DISPLAY_ON
]

# Create the bus
bus = smbus2.SMBus(1)  # 1 indicates /dev/i2c-1

def send_command(command):
    bus.write_byte_data(I2C_ADDRESS, 0x00, command)

def send_data(data):
    for i in range(0, len(data), CHUNK_SIZE):
        chunk = data[i:i + CHUNK_SIZE]
        bus.write_i2c_block_data(I2C_ADDRESS, 0x40, chunk)
        time.sleep(0.001)  # Short delay to ensure stability

def initialize_display():
    for cmd in init_sequence:
        send_command(cmd)

def set_all_pixels_white():
    # Each pixel needs one bit, so we need 128 * 64 / 8 bytes
    white_data = [0xFF] * (WIDTH * HEIGHT // 8)
    send_data(white_data)

# Initialize the display
initialize_display()

# Set all pixels to white
set_all_pixels_white()
