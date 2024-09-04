import board, time, digitalio, threading, math
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import adafruit_lsm303dlh_mag
import adafruit_tcs34725
import adafruit_ssd1306

# setup for the I2C bus for the sensor
i2c = board.I2C()
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
rgb = adafruit_tcs34725.TCS34725(i2c)

# oled init
WIDTH = 128
HEIGHT = 64
BORDER = 5
oled_reset = digitalio.DigitalInOut(board.D4)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Use GPIO17 for the LED
led = digitalio.DigitalInOut(board.D17)
led.direction = digitalio.Direction.OUTPUT # led.value = True means its on

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# flag for exit thread
exit_program = False

def listen_for_exit():
    global exit_program
    input("Press Enter to exit...\n")
    exit_program = True


# changes the magnenometer from x, y vals to heading in degrees
def vector_2_degrees(x, y):
    angle = math.degrees(math.atan2(y, x))
    if angle < 0:
        angle += 360
    return angle

# calls vector_2_degrees with x, y vals from sensor
def get_heading(_sensor):
    magnet_x, magnet_y, _ = _sensor.magnetic
    return vector_2_degrees(magnet_x, magnet_y)


# Start the thread to listen for the Enter key
exit_thread = threading.Thread(target=listen_for_exit)
exit_thread.start()

# State of led, default off
led_state = False

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

    # Load default font.
    font = ImageFont.load_default()

    # Debug print for the heading numbers
    print("heading: {:.2f} degrees".format(get_heading(mag)))

    # get heading from the sensor
    heading = get_heading(mag)
    if heading < 30 or heading > 330:
        led_state = True
    else:
        led_state = False

    led.value = led_state

    # get rgb vals from the sensor
    r, g, b = rgb.color_rgb_bytes
    text = ''
    if r > g and r > b:
        text = "RED"
    elif g > r and g > b:
        text = "GREEN"
    elif b > r and b > g:
        text = "BLUE"
    else:
        text = "UNDEFINED"

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
oled.fill(0)
oled.show()
