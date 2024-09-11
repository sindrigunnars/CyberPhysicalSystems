import board, time, digitalio, threading, math, busio
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import adafruit_ssd1306
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D25)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

print(mcp.reference_voltage)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

# setup for the I2C bus for the sensor
i2c = board.I2C()

# oled init
WIDTH = 128
HEIGHT = 64
BORDER = 5
oled_reset = digitalio.DigitalInOut(board.D4)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# flag for exit thread
exit_program = False

def listen_for_exit():
    global exit_program
    input("Press Enter to exit...\n")
    exit_program = True

def voltage_to_distance(voltage):
    """
    Convert voltage to distance based on the GP2Y0A02YK sensor.
    The voltage-to-distance conversion is non-linear and requires empirical fitting.
    """
    if voltage < 0.17:
        return 150
    elif voltage > 0.17 and voltage < 0.33:
        return 140
    elif voltage > 0.33 and voltage < 0.44:
        return 120
    elif voltage > 0.44 and voltage < 0.59:
        return 100
    elif voltage > 0.59 and voltage < 0.72:
        return 80
    elif voltage > 0.72 and voltage < 0.87:
        return 70
    elif voltage > 0.87 and voltage < 1.07:
        return 60
    elif voltage > 1.07 and voltage < 1.22:
        return 50
    elif voltage > 1.22 and voltage < 1.47:
        return 40
    elif voltage > 1.47 and voltage < 1.9:
        return 30
    elif voltage > 1.9:
        return 20
    return -1.0

# Start the thread to listen for the Enter key
exit_thread = threading.Thread(target=listen_for_exit)
exit_thread.start()

max_v, min_v = 0.0, 1000.0

while not exit_program:
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a white background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    # Draw a smaller inner rectangle
    draw.rectangle(
        (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
        outline=0,
        fill=0,
    )

    # print(chan0.voltage)

    # Load default font.
    font = ImageFont.load_default()

    max_v = max(chan0.voltage, max_v)
    min_v = min(chan0.voltage, min_v)
    # print(f'Val: {chan0.value}')

    text = f'V: {chan0.voltage:.5f}\nD: {voltage_to_distance(chan0.voltage):.4f}'

    # Draw it into a box.
    bbox = font.getbbox(text)
    (font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )

    # Display image
    oled.image(image)
    oled.show()

    time.sleep(0.5)



print("Exiting program...")
print(f'Max voltage: {max_v}')
print(f'Min voltage: {min_v}')
oled.fill(0)
oled.show()
