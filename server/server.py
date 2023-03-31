import datetime
import time

import cv2
import zmq
import numpy as np

from image_helper import ImageHelper
from object_detection import ObjectDetector
from fps_counter import FpsCounter
from label_diff import LabelDiff

from joystick import getThrottle

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
        message = self.recv_with_timeout(30000 if not self.connected else 2000)
        self.connected = True

        self.fps_counter.start()

        image_int_tensor = ImageHelper.ImageBufferToIntegerTensor(message)

        #preds, labels = self.object_detector.getLabels(image_int_tensor)

        #bounded_image = ImageHelper.IntegerTensorToCV(
        #    self.object_detector.getBoundedImage(image_int_tensor, labels, preds)
        #)

        #self.label_diff.printDiff(labels)

        # Calculate the elapsed seconds
        self.fps_counter.addFrame()
        # print(f'FPS: {self.fps_counter.getFps()}')

        final_image =  ImageHelper.IntegerTensorToCV(image_int_tensor)

        left, right = getThrottle()

        final_image = self.detect_sidewalk(final_image)
        final_image = self.add_servo_monitor(final_image, left, right)
        final_image = self.add_timestamp(final_image)
        self.show_image(final_image)
        self.video.write(final_image)


        # send confirmation to the client
        msg = "{} {}".format(left, right)
        print(msg)

        self.socket.send(msg.encode())


    def detect_sidewalk(self, image):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Apply Hough transform to detect straight lines
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)

        # Convert the lines to a binary image
        line_image = np.zeros_like(gray)
        for x1, y1, x2, y2 in lines[:, 0]:
            cv2.line(line_image, (x1, y1), (x2, y2), 255, 2)

        # Combine the edge and line images
        combined = cv2.bitwise_and(edges, line_image)

        # Find contours in the combined image
        contours, hierarchy = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the contour with the largest area
        largest_contour = max(contours, key=cv2.contourArea)

        # Compute the convex hull of the largest contour
        hull = cv2.convexHull(largest_contour)

        # Find the minimum area rectangle that encloses the convex hull
        rect = cv2.minAreaRect(hull)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # Draw the minimum area rectangle on the input image
        cv2.drawContours(image, [box], 0, (0, 0, 255), 2)

        # Compute the predicted path along the sidewalk
        path = np.array([box[0], box[1], box[2], box[3], box[0]])
        cv2.polylines(image, [path], False, (0, 255, 0), 2)

        return image

    def add_servo_monitor(self, image, left, right):
        width = 20
        max_height = 10
        main_start = (5, 50)

        green = (0, 255, 0)
        red = (0, 0, 255)
        yellow = (0, 255, 255)

        cutoff = 0.05

        thickness = -1

        left_start = main_start
        right_start = (main_start[0] + width, main_start[1])

        def getRectangle(start, strength):
            height = int(-strength * max_height)
        
            # Ending coordinate, here (220, 220)
            # represents the bottom right corner of rectangle
            end_point = (start[0] + width, start[1] + height)

            color = yellow if abs(strength) < cutoff else \
                red if strength < 0 else green

            return start, end_point, color, thickness

        image = cv2.rectangle(image, *getRectangle(left_start, left))
        image = cv2.rectangle(image, *getRectangle(right_start, right))
  
        return image


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
