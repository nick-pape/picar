import zmq
import cv2
import numpy as np
import sys

from image_helper import ImageHelper
from object_detection import ObjectDetector
from fps_counter import FpsCounter
from label_diff import LabelDiff

print("Setting up 0MQ")
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")   # binds to all network interfaces

print("Setting up CNN")
object_detector = ObjectDetector()

print("READY")

frame_count = 0
init_time = False

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

fps_counter = FpsCounter()
label_diff = LabelDiff()

try:
    while True:
        # Receive an image from RPi
        socks = dict(poller.poll(timeout=10000))
        if socket in socks and socks[socket] == zmq.POLLIN:
            message = socket.recv()
        else:
            print("Client disconnected")
            break

        fps_counter.start()

        image_int_tensor = ImageHelper.ImageBufferToIntegerTensor(message)

        preds, labels = object_detector.getLabels(image_int_tensor)

        bounded_image = ImageHelper.IntegerTensorToCV(
            object_detector.getBoundedImage(image_int_tensor, labels, preds)
        )

        label_diff.printDiff(labels)

        # Calculate the elapsed seconds
        fps_counter.addFrame()
        print(f'FPS: {fps_counter.getFps()}')

        cv2.imshow('Image', bounded_image)
        key = cv2.waitKey(1) # Wait for 1ms and check if a key is pressed

        # Exit the loop if 'q' is pressed
        if key == ord('q'):
            raise KeyboardInterrupt()

        # send confirmation to the client
        socket.send(b"Ready for next image")

except zmq.error.ZMQError:
    print("Client disconnected")

except KeyboardInterrupt:
    print("Interrupted")

socket.close()
context.term()
cv2.destroyAllWindows()
sys.exit()
