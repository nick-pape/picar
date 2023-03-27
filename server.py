import datetime
import time

import cv2
import zmq

from image_helper import ImageHelper
from object_detection import ObjectDetector
from fps_counter import FpsCounter
from label_diff import LabelDiff


class Server():
    def __init__(self):
        self.init_zmq()
        self.init_model()
        self.init_utils()
        self.init_cv()
        self.connected = False
        print("READY")


    def init_zmq(self):
        print("Initializing 0MQ")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")   # binds to all network interfaces

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    def init_model(self):
        print("Initializing Model")
        self.object_detector = ObjectDetector()

    def init_utils(self):
        print("Initializing Utilities")
        self.fps_counter = FpsCounter()
        self.label_diff = LabelDiff()

    def init_cv(self):
        self.WINDOW_NAME = "Live Stream"
        # start window thread for better performance
        cv2.startWindowThread()

        # create a window
        cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)

        # set window to be on top of other windows
        cv2.setWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video = cv2.VideoWriter('output.mp4', fourcc, 5, (640, 480))

    def execute(self):
        message = self.recv_with_timeout(30000 if not self.connected else 1000)
        self.connected = True

        self.fps_counter.start()

        image_int_tensor = ImageHelper.ImageBufferToIntegerTensor(message)

        preds, labels = self.object_detector.getLabels(image_int_tensor)

        bounded_image = ImageHelper.IntegerTensorToCV(
            self.object_detector.getBoundedImage(image_int_tensor, labels, preds)
        )

        self.label_diff.printDiff(labels)

        # Calculate the elapsed seconds
        self.fps_counter.addFrame()
        # print(f'FPS: {self.fps_counter.getFps()}')

        final_image = self.add_timestamp(bounded_image)
        self.show_image(final_image)
        self.video.write(final_image)

        # send confirmation to the client
        self.socket.send(b"Ready for next image")

    def add_timestamp(self, image):
        # get the current date and time
        now = datetime.datetime.now()

        # format the date and time as a string
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # define the font and font scale
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.5

        # define the position and color of the text
        color = (255, 255, 255)
        position = (10, 30)

        # draw the text onto the image
        cv2.putText(image, timestamp, position, font, fontScale, color, thickness=1)
        return image

    def show_image(self, image):
        cv2.resizeWindow(self.WINDOW_NAME, image.shape[1], image.shape[0])
        cv2.imshow(self.WINDOW_NAME, image)
        cv2.waitKey(1)

    def recv_with_timeout(self, timeout = 10000):
        # Receive an image from RPi
        socks = dict(self.poller.poll(timeout))
        if self.socket in socks and socks[self.socket] == zmq.POLLIN:
            return self.socket.recv()
        else:
            print("Client disconnected")
            raise Exception("Client disconnected")

    def close(self):
        self.socket.close()
        self.context.term()
        cv2.destroyAllWindows()
        self.video.release()
