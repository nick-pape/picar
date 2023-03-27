import sys
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

        cv2.imshow('Image', bounded_image)
        cv2.waitKey(1)

        # send confirmation to the client
        self.socket.send(b"Ready for next image")

    def recv_with_timeout(self, timeout = 10000):
        # Receive an image from RPi
        socks = dict(self.poller.poll(timeout=10000))
        if self.socket in socks and socks[self.socket] == zmq.POLLIN:
            return self.socket.recv()
        else:
            print("Client disconnected")
            raise Exception("Client disconnected")

    def close(self):
        self.socket.close()
        self.context.term()
        cv2.destroyAllWindows()
