
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

hallpin = 27
ledpin = 13


gpio.setup(hallpin,gpio.IN)
gpio.setup(ledpin, gpio.OUT)
gpio.output(ledpin, False)

while True:
    if(gpio.input(hallpin) == False):
        gpio.output(ledpin, True)
        print("Portaloo Closed")
    else:
        gpio.output(ledpin, False)
        print("Portaloo Open")