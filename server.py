import zmq
import os
import cv2
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")   # binds to all network interfaces

while True:
    # wait for client request
    message = socket.recv()
    print("Received request")

    # Decode the image data into a numpy array
    image_array = np.frombuffer(message, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Display the image using cv2.imshow()
    cv2.imshow('Image', img)

    # Wait for 1ms and check if a key is pressed
    key = cv2.waitKey(1)

    # Exit the loop if 'q' is pressed
    if key == ord('q'):
        break

    # send confirmation to the client
    socket.send(b"Image received successfully")

cv2.destroyAllWindows()