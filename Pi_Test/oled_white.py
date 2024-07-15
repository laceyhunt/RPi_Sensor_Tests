import board
import busio
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

# Define the display dimensions (128x64 pixels)
WIDTH = 128
HEIGHT = 64

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the SSD1306 OLED display using I2C
disp = Adafruit_SSD1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear display
disp.fill(0)
disp.show()

# Create a blank image for the OLED
image = Image.new("1", (WIDTH, HEIGHT))

# Get drawing object to draw on image
draw = ImageDraw.Draw(image)

# Draw a white filled box to clear the image
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=255, fill=255)

# Display image
disp.image(image)
disp.show()
