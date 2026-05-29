import pigpio
from time import sleep

pin = 17
pi = pigpio.pi()
pin_setup = pi.set_mode(pin, pigpio.OUTPUT)


def run():
    pi.write(pin, 1)
    sleep(5)
    pi.write(pin, 0)
    sleep(1)

run()
