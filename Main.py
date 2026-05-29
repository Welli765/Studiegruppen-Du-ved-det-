rom machine import PWM, Pin, I2C
from neopixel import NeoPixel
from time import sleep, ticks_ms, ticks_diff
from hcsr04 import HCSR04

import network
import espnow
import time

last_stats_time = time.time()
stats_interval = 10  
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=1)  
sta.disconnect()


e = espnow.ESPNow()
try:
    e.active(True)
except OSError as err:
    print("Failed to initialize ESP-NOW:", err)
    raise


sender_mac = b'\x68\x25\xdd\xf0\xcb\x18'  

def print_stats():
    stats = e.stats()
    print("\nESP-NOW Statistics:")
    print(f"  Packets Sent: {stats[0]}")
    print(f"  Packets Delivered: {stats[1]}")
    print(f"  Packets Dropped (TX): {stats[2]}")
    print(f"  Packets Received: {stats[3]}")
    print(f"  Packets Dropped (RX): {stats[4]}")

print("Listening for ESP-NOW messages...")





IN1 = PWM(Pin(33), freq=1000)
IN2 = PWM(Pin(25), freq=1000)


IN3 = PWM(Pin(26), freq=1000)
IN4 = PWM(Pin(27), freq=1000)


MAX_DUTY = 65535

def set_motor(pin_forward, pin_reverse, speed):
    speed = max(min(speed, 100), -100) 

    duty = int(abs(speed) * MAX_DUTY / 100) 

    if speed > 0:
        pin_forward.duty_u16(duty)
        pin_reverse.duty_u16(0)

    elif speed < 0:
        pin_forward.duty_u16(0)
        pin_reverse.duty_u16(duty)

    else:
        pin_forward.duty_u16(0)
        pin_reverse.duty_u16(0)

def motorA(speed):
    set_motor(IN1, IN2, speed)

def motorB(speed):
    set_motor(IN3, IN4, speed)
       
       

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.integral = 0


    def compute (self, process_variable, dt):
        
        error = process_variable - self.setpoint
   
        
        P_out = self.Kp * error
   
      
        self.integral += error * dt
        I_out = self.Ki * self.integral
   
       
        derivative = (error - self.previous_error) /dt
        D_out = self.Kd * derivative
   
        
        output = P_out + I_out + D_out
   
     
        self.previous_error = error
   
        return output

setpoint = 60.0  

last_time = ticks_ms()


pid = PIDController (1.0, 0, 0.1, setpoint) 


np = NeoPixel(Pin(14,Pin.OUT),24)

servo = PWM(Pin(32, Pin.OUT))

servofin = PWM(Pin(18, Pin.OUT))

ultralyd = HCSR04(15,16)

def set_color(r,g,b):
    for i in range(24):
        np[i] = (r,g,b)        
    np.write()

set_color(255,255,255)
set_color(0,0,0)

servofin.freq(50)
servo.freq(50)

dutti = 26

findutti = 77
servofin.duty(findutti)



while True:
  
    try:
        
        host, msg = e.recv(10000)
        if msg:
            print(f"Received from {host.hex()}: {msg.decode()}")
            break
       
    except KeyboardInterrupt:
        print("Stopping receiver...")
        e.active(False)
        sta.active(False)

        break
  
while True:  
    distance = ultralyd.distance_cm()
    print(distance, "cm")
    sleep(0.05)
    servo.duty(dutti)
    sleep(0.05)
    dutti += 10
    grad = 1.764705882 * (dutti-10) + -45.882352896
    print(round(grad),"grader")
    if dutti >= 128:
        dutti = 26
    
    if distance >= 0 and distance < 60:
        servofin.duty(77)
        set_color(255,255,255)
       
    if distance > 60:
        set_color(255,0,0)
        findutti = -1 * (dutti-10) + 154 
        servofin.duty(dutti)
        sleep(3)
        
 
    current_time = ticks_ms()
    dt = ticks_diff(current_time, last_time) / 1000
    last_time = current_time

    if dt <= 0:
        dt = 0.01

    process_variable = ultralyd.distance_cm()

    motor_speed = pid.compute(process_variable, dt)

    motor_speed = max(min(motor_speed, 100), -100)

    motorA(motor_speed)
    motorB(motor_speed)
    print("speed:", motor_speed)
    time.sleep(0.05)