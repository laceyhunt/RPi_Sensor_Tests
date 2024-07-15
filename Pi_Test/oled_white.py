import smbus
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

# Define I2C bus number (0 or 1, depending on your Raspberry Pi model)
i2c_bus = 1  # Replace with 0 if using Raspberry Pi model prior to 4

# Initialize I2C bus
i2c = smbus.SMBus(i2c_bus)

# SSD1306 display setup
WIDTH = 128
HEIGHT = 64
oled = Adafruit_SSD1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear display
oled.fill(0)
oled.show()

# Create a blank image for the OLED
image = Image.new("1", (WIDTH, HEIGHT))

# Get drawing object to draw on image
draw = ImageDraw.Draw(image)

# Draw a white filled box to clear the image
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=255, fill=255)

# Display image
oled.image(image)
oled.show()
