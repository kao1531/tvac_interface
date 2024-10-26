import csv
import RPi.GPIO as GPIO
import time
from max31855.max31855 import MAX31855, MAX31855Error

# RPi setup
A3 = 17
A2 = 16
A1 = 27
A0 = 26
# D = pin 3 of TC reader

CS = 24
SO = 22
SCK = 23

thermocouple = MAX31855(CS, SCK, SO)

# GPIO.setmode(GPIO.BOARD)
GPIO.setup(A3, GPIO.OUT)
GPIO.setup(A2, GPIO.OUT)
GPIO.setup(A1, GPIO.OUT)
GPIO.setup(A0, GPIO.OUT)

temps = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

def read_tc(tc_num):
    # output to read TC value from TC #tc_num
    
    s0 = tc_num & 0x01  # Least significant bit (S0)
    s1 = (tc_num >> 1) & 0x01  # Second bit (S1)
    s2 = (tc_num >> 2) & 0x01  # Third bit (S2)
    s3 = (tc_num >> 3) & 0x01  # Most significant bit (S3)
    GPIO.output(A0, s0)
    GPIO.output(A1, s1)
    GPIO.output(A2, s2)
    GPIO.output(A3, s3)

    time.sleep(0.1)

    thermocouple_temp_c = thermocouple.get()

    return thermocouple_temp_c
while True:
    for i in range(16):
        temps[i] = read_tc(i)
    #temps[0] = read_tc(0)
    with open('temp.csv', 'w', newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(temps)

