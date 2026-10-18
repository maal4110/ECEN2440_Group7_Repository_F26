# Test 9 - Integrated Motor Control w/ IR Receiver (Serial Monitor & LEDs)
# Combines test6RX (IR receiver) + Test4 (DRV8835 motor control)

# Pair with Test09_Joystick/tx_pico (joystick transmitter).
#
# LEDs: LED1 = driving forward
#       LED2 = driving backward
#       LED3 = turning (left or right)
#       all off = stopped

import time
from machine import Pin, PWM
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging

time.sleep(1) # Wait for USB to become ready

#motors
pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(13, freq = pwm_rate, duty_u16 = 0)
bin1_ph = Pin(14, Pin.OUT)
bin2_en = PWM(15, freq = pwm_rate, duty_u16 = 0)

pwm = min(max(int(2**16 * abs(1)), 0), 65535)

# user LEDS
# check GPIO pins
led_fwd  = Pin(18, Pin.OUT, value=0)
led_back = Pin(19, Pin.OUT, value=0)
led_turn = Pin(20, Pin.OUT, value=0)

# IR commands
DEVICE_ADDR = 0x01
STOP     = 0x00
FORWARD  = 0x01
BACKWARD = 0x02
LEFT     = 0x03
RIGHT    = 0x04
NAMES = {STOP: "STOP", FORWARD: "FORWARD", BACKWARD: "BACKWARD",
         LEFT: "LEFT", RIGHT: "RIGHT"}


def motor_a(direction):   # 1 = forward, -1 = backward, 0 = off
    if direction == 0:
        ain2_en.duty_u16(0)
    else:
        ain1_ph.value(0 if direction > 0 else 1)
        ain2_en.duty_u16(pwm)


def motor_b(direction):
    if direction == 0:
        bin2_en.duty_u16(0)
    else:
        bin1_ph.value(0 if direction > 0 else 1)
        bin2_en.duty_u16(pwm)


def drive(cmd):
    if cmd == FORWARD:
        motor_a(1);  motor_b(1)
    elif cmd == BACKWARD:
        motor_a(-1); motor_b(-1)
    elif cmd == LEFT:          # spin left: A back, B forward
        motor_a(-1); motor_b(1)
    elif cmd == RIGHT:         # spin right: A forward, B back
        motor_a(1);  motor_b(-1)
    else:
        motor_a(0);  motor_b(0)
    led_fwd.value(1 if cmd == FORWARD else 0)
    led_back.value(1 if cmd == BACKWARD else 0)
    led_turn.value(1 if cmd in (LEFT, RIGHT) else 0)


#IR receiver - test 6
new_cmd = None

# Callback function to execute when an IR code is received
def ir_callback(data, addr, _):
    global new_cmd
    if data < 0:               # NEC repeat code, no new command
        return
    if addr != DEVICE_ADDR:
        print(f"Ignored command 0x{data:02X} from addr 0x{addr:02X}")
        return
    new_cmd = data             # handled in the main loop

# Setup the IR receiver
ir_pin = Pin(17, Pin.IN, Pin.PULL_UP) # Adjust the pin number based on your wiring

ir_receiver = NEC_8(ir_pin, callback=ir_callback)

# print_error function for debugging
ir_receiver.error_function(print_error)

# main loop
drive(STOP)
print("SumoBot ready, waiting for IR commands...")
try:
    while True:
        if new_cmd is not None:
            cmd = new_cmd
            new_cmd = None
            drive(cmd)
            print(f"Received NEC command! Data: 0x{cmd:02X} -> {NAMES.get(cmd, 'UNKNOWN')}")
        time.sleep_ms(5)
except KeyboardInterrupt:
    pass
finally:
    drive(STOP)
    ir_receiver.close()
    print("Motors stopped.")
