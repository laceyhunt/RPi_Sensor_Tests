import busio
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

# I2C setup (example for Raspberry Pi Pico)
i2c = busio.I2C(scl=Pin(1), sda=Pin(0))  # Replace Pin numbers with your actual GPIO pins

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
