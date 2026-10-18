# Test 9 - IR Transmitter Code integrated with the Joystick (Serial Monitor)
# Combines test6TX (IR transmitter) + analog joystick.
#   Joystick up    -> FORWARD  (0x01)
#   Joystick down  -> BACKWARD (0x02)
#   Joystick left  -> LEFT     (0x03)
#   Joystick right -> RIGHT    (0x04)
#   Released       -> STOP     (0x00)
#
# Joystick wiring: VCC -> 3V3 (not VBUS), GND -> GND,
#                  VRx -> GP27 (ADC1), VRy -> GP26 (ADC0)

import time
from machine import Pin, ADC
from ir_tx.nec import NEC

#IR transmitter - test 6
tx_pin = Pin(17, Pin.OUT, value=0)
device_addr = 0x01
transmitter = NEC(tx_pin)

#joystick
joy_x = ADC(Pin(27))
joy_y = ADC(Pin(26))

# read_u16() gives 0..65535, about 32768 when the stick is centered.
# Outside these limits counts as pushed in that direction.
LOW = 16000
HIGH = 49000

# commands
STOP     = 0x00
FORWARD  = 0x01
BACKWARD = 0x02
LEFT     = 0x03
RIGHT    = 0x04
NAMES = {STOP: "STOP", FORWARD: "FORWARD", BACKWARD: "BACKWARD",
         LEFT: "LEFT", RIGHT: "RIGHT"}


def read_joystick():
    x = joy_x.read_u16()
    y = joy_y.read_u16()
    # If a direction comes out backwards, swap that pair below
    if y > HIGH:
        return FORWARD
    if y < LOW:
        return BACKWARD
    if x < LOW:
        return LEFT
    if x > HIGH:
        return RIGHT
    return STOP


def send(command):
    transmitter.transmit(device_addr, command)
    print("COMMAND", hex(command), NAMES[command], "TRANSMITTED.")
    time.sleep_ms(120)   # an NEC frame takes ~68 ms; let it finish


if __name__ == "__main__":
    last = STOP
    print("Joystick transmitter ready.")
    while True:
        command = read_joystick()
        if command != STOP:
            send(command)            # keep resending while the stick is held
        elif last != STOP:
            for _ in range(3):       # stick released: send STOP a few times
                send(STOP)           # so a single missed frame can't leave
                                     # the robot driving
        last = command
        time.sleep_ms(30)
