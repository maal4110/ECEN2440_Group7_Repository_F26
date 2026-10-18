import time
from machine import Pin, I2C
from ir_tx.nec import NEC
import seesaw

# IR transmitter
tx_pin = Pin(17, Pin.OUT, value=0)
device_addr = 0x01
transmitter = NEC(tx_pin)

# Adafruit I2C gamepad
i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=100000)
seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

# Seesaw internal joystick pins (not Pico GPIO)
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15

CENTER_X = 511
CENTER_Y = 497
THRESHOLD = 50

# Commands
STOP     = 0x00
FORWARD  = 0x01
BACKWARD = 0x02
LEFT     = 0x04
RIGHT    = 0x03

NAMES = {STOP: "STOP", FORWARD: "FORWARD", BACKWARD: "BACKWARD",
         LEFT: "LEFT", RIGHT: "RIGHT"}


def read_joystick():
    x = seesaw_device.analog_read(JOYSTICK_X_PIN)
    y = seesaw_device.analog_read(JOYSTICK_Y_PIN)

    if y < CENTER_Y - THRESHOLD:
        return FORWARD
    if y > CENTER_Y + THRESHOLD:
        return BACKWARD
    if x < CENTER_X - THRESHOLD:
        return LEFT
    if x > CENTER_X + THRESHOLD:
        return RIGHT
    return STOP


def send(command):
    transmitter.transmit(device_addr, command)
    print("COMMAND", hex(command), NAMES[command], "TRANSMITTED.")
    time.sleep_ms(120)


if __name__ == "__main__":
    last = STOP
    print("Joystick transmitter ready.")
    while True:
        command = read_joystick()
        if command != STOP:
            send(command)
        elif last != STOP:
            for _ in range(3):
                send(STOP)
        last = command
        time.sleep_ms(30)
