import json
import RPi.GPIO as GPIO

# Heater control
H1 = 12
H2 = 13
LN2 = 18

GPIO.setup(H1, GPIO.OUT)
GPIO.setup(H2, GPIO.OUT)
GPIO.setup(LN2, GPIO.OUT)

while (1):
    # read from json file
    with open('heater_control.json', 'r') as file:
        data = json.load(file)

    # turn on controls based on status
    if int(data["H1"]):
        GPIO.output(H1, GPIO.HIGH)
    else:
        GPIO.output(H1, GPIO.LOW)

    if int(data["H2"]):
        GPIO.output(H2, GPIO.HIGH)
    else:
        GPIO.output(H2, GPIO.LOW)

    if int(data["LN2"]):
        GPIO.output(LN2, GPIO.HIGH)
    else:
        GPIO.output(LN2, GPIO.LOW)
