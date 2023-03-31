from adafruit_servokit import ServoKit

class FourWheelDrivetrain:
    def __init__(self):
        kit = ServoKit(channels=8)
        servos = kit.continuous_servo

        self._front_left = servos[0]
        self._front_right = servos[1]
        self._back_left = servos[2]
        self._back_right = servos[3]

        self.left_side = [self._front_left, self._back_left]
        self.right_side = [self._front_right, self._back_right]

        self.all = [
		    self._front_left,
			self._front_right,
			self._back_left,
			self._back_right
		]

    def setThrottle(self, left, right):
        for servo in self.right_side:
            servo.throttle = left
        for servo in self.left_side:
            servo.throttle = right

    def forward(self, throttle = 1):
        for servo in self.all:
            servo.throttle = throttle

    def back(self, throttle = 1):
        for servo in self.all:
            servo.throttle = throttle

    def stop(self):
        for servo in self.all:
            servo.throttle = 0

    def left(self, throttle = 1):
        for servo in self.right_side:
            servo.throttle = throttle
        for servo in self.left_side:
            servo.throttle = -throttle

    def right(self, throttle = 1):
        for servo in self.right_side:
            servo.throttle = -throttle
        for servo in self.left_side:
            servo.throttle = throttle
            
    def right(self, throttle = 1):
        for servo in self.right_side:
            servo.throttle = -throttle
        for servo in self.left_side:
            servo.throttle = throttle