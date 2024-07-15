import smbus
from PIL import Image, ImageDraw, ImageFont

# Define I2C bus number (0 or 1, depending on your Raspberry Pi model)
i2c_bus = 1  # Replace with 0 if using Raspberry Pi model prior to 4

# Initialize I2C bus
i2c = smbus.SMBus(i2c_bus)

# SSD1306 display setup constants
SSD1306_I2C_ADDR = 0x3C  # I2C address of the SSD1306 display
WIDTH = 128
HEIGHT = 64

# SSD1306 display initialization sequence
def ssd1306_init():
    commands = [
        0xAE,           # Display off
        0xD5, 0x80,     # Set display clock divide ratio/oscillator frequency
        0xA8, 0x3F,     # Set multiplex ratio (1 to 64)
        0xD3, 0x00,     # Set display offset
        0x40,           # Set start line address
        0x8D, 0x14,     # Charge pump setting (0x14 enable charge pump)
        0x20, 0x00,     # Set memory mode to horizontal addressing mode
        0xA1,           # Set segment remap with column address 127 mapped to SEG0
        0xC8,           # Set COM output scan direction, scan from COM63 to COM0
        0xDA, 0x12,     # Set COM pins hardware configuration
        0x81, 0xCF,     # Set contrast control
        0xD9, 0xF1,     # Set pre-charge period
        0xDB, 0x40,     # Set VCOMH deselect level
        0xA4,           # Entire display on (resume to RAM content display)
        0xA6,           # Set normal display (A7 for inverse display)
        0xAF            # Display on
    ]

    for cmd in commands:
        i2c.write_byte_data(SSD1306_I2C_ADDR, 0x00, cmd)

# Clear the SSD1306 display buffer
def clear_display():
    buffer = [0x00] * (WIDTH * HEIGHT // 8)  # Calculate total buffer size
    chunk_size = 32  # Maximum chunk size for write_i2c_block_data

    for i in range(0, len(buffer), chunk_size):
        chunk = buffer[i:i + chunk_size]
        if chunk:  # Ensure chunk is not empty
            command = [0x40] + chunk  # 0x40 is the command to write data to RAM
            i2c.write_i2c_block_data(SSD1306_I2C_ADDR, 0x00, command)



# Initialize the display
ssd1306_init()

# Clear display buffer
clear_display()

# Create a blank image for the OLED
image = Image.new("1", (WIDTH, HEIGHT))

# Get drawing object to draw on image
draw = ImageDraw.Draw(image)

# Draw a white filled box to clear the image
draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=255, fill=255)

# Display image
data = list(image.getdata())
buffer = bytearray(data)

i2c.write_i2c_block_data(SSD1306_I2C_ADDR, 0x40, buffer)
