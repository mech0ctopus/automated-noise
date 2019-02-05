import RPi.GPIO as GPIO
from time import sleep

#Define list of pins to control
pins=[3,5,7]
#Define control states
off=GPIO.HIGH
on=GPIO.LOW
#Define test variables
SAMPLE_PERIOD=4
TIME_DELAY=1

#Set Pin Numbering mode
GPIO.setmode(GPIO.BOARD)
#Setup pins & set initial state
GPIO.setup(pins, GPIO.OUT)
GPIO.output(pins,GPIO.HIGH)

try:
    for idx, _ in enumerate(pins):
        GPIO.output(pins[idx],on)
        sleep(SAMPLE_PERIOD)
        GPIO.output(pins[idx],off)
        sleep(TIME_DELAY)   
except KeyboardInterrupt:
    GPIO.cleanup()
finally:
    GPIO.cleanup()
