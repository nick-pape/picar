import time
from adafruit_servokit import ServoKit
kit = ServoKit(channels=8)
servos = kit.continuous_servo

servos[0].throttle = 1
time.sleep(5)
servos[0].throttle = 0
