import RPi.GPIO as GPIO
import time

ledPin = 22
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.output(ledPin, GPIO.LOW)
while True:
    GPIO.output(ledPin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(ledPin, GPIO.LOW)
    time.sleep(0.1)
