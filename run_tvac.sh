#!/bin/bash

python tvac_interface.py &
python thermo.py &
python heater_control.py &

# add more scripts as necessary