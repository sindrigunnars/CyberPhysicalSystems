import board, time, digitalio, adafruit_ssd1306, adafruit_mpl3115a2, threading
from PIL import Image, ImageDraw, ImageFont

# sensor init
i2c = board.I2C()
sensor = adafruit_mpl3115a2.MPL3115A2(i2c)


# oled init
WIDTH = 128
HEIGHT = 64
BORDER = 5

oled_reset = digitalio.DigitalInOut(board.D4)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

TIME_INTERVAL = 1.0
timeSinceSwitch = 0.0
deltaTime = 0.0
last = time.monotonic()
temp_display = True;
exit_program = False

def listen_for_exit():
    global exit_program
    input("Press Enter to exit...\n")
    exit_program = True

# Start the thread to listen for the Enter key
exit_thread = threading.Thread(target=listen_for_exit)
exit_thread.start()

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

    now = time.monotonic()
    deltaTime = now - last
    last = now

    timeSinceSwitch += deltaTime

    if timeSinceSwitch > TIME_INTERVAL:
        timeSinceSwitch = 0.0
        temp_display = not temp_display

    if temp_display:
        text = "{0:0.1f}°C".format(sensor.temperature)
    else:
        text = "{0:0.1f}hpa".format(sensor.pressure)

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


print("Exiting program...")
oled.fill(0)
oled.show()
