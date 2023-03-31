class BaseDrivetrain():
    def setThrottle(self, left: float, right: float):
        raise NotImplementedError()
    
    def forward(self, throttle: float = 1.0):
        raise NotImplementedError()

    def back(self, throttle: float = 1.0):
        raise NotImplementedError()
    
    def stop(self):
        raise NotImplementedError()
    
    def left(self, throttle: float = 1.0):
        raise NotImplementedError()
    
    def right(self, throttle: float = 1.0):
        raise NotImplementedError()


class FourWheelDrivetrain(BaseDrivetrain):
    def __init__(self):
        super().__init__()
        from adafruit_servokit import ServoKit
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

    def setThrottle(self, left: float, right: float):
        for servo in self.right_side:
            servo.throttle = left
        for servo in self.left_side:
            servo.throttle = right

    def forward(self, throttle: float = 1.0):
        for servo in self.all:
            servo.throttle = throttle

    def back(self, throttle: float = 1.0):
        for servo in self.all:
            servo.throttle = throttle

    def stop(self):
        for servo in self.all:
            servo.throttle = 0

    def left(self, throttle: float = 1.0):
        for servo in self.right_side:
            servo.throttle = throttle
        for servo in self.left_side:
            servo.throttle = -throttle

    def right(self, throttle: float = 1.0):
        for servo in self.right_side:
            servo.throttle = -throttle
        for servo in self.left_side:
            servo.throttle = throttle


class MockFourWheelDrivetrain(BaseDrivetrain):
    def setThrottle(self, left: float, right: float):
        print(f"Drivetrain.setThrottle({left}, {right})")
    
    def forward(self, throttle: float = 1.0):
        print(f"Drivetrain.forward({throttle})")

    def back(self, throttle: float = 1.0):
        print(f"Drivetrain.back({throttle})")
    
    def stop(self):
        print(f"Drivetrain.stop()")
    
    def left(self, throttle: float = 1.0):
        print(f"Drivetrain.setThrottle({throttle})")
    
    def right(self, throttle: float = 1.0):
        print(f"Drivetrain.setThrottle({throttle})")
