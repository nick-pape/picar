from zmq_manager import ZmqManager

from camera import BaseCamera
from drive import BaseDrivetrain

class Client():
    def __init__(self, args, drive: BaseDrivetrain, camera: BaseCamera):
        self.drive = drive
        self.camera = camera
        self.socket = ZmqManager.getSocket(args.ip)

    def execute(self):
        
        image = self.camera.snap()

        # send the image to the server
        self.socket.send(image)

        # wait for confirmation from server
        message = self.socket.recv_timeout()

        print(message)
        parts = message.split(' ')
        left = float(parts[0])
        right = float(parts[1])

        self.drive.setThrottle(left, right)

    def close(self):
        # release resources
        self.drive.stop()
        self.camera.close()
        ZmqManager.close()