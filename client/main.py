import zmq
import cv2
import time
import sys

from drive import FourWheelDrivetrain

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://10.0.0.5:5555")   # connect to server

# capture an image using the default camera
cap = cv2.VideoCapture(0)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]   # JPEG quality (0-100)
    
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

i=0

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

drive = FourWheelDrivetrain()

try:
    while True:
        ret, frame = cap.read()
        i+=1
        # convert the image to JPEG format
        image = cv2.imencode('.jpg', frame, encode_param)[1].tobytes()

        # send the image to the server
        socket.send(image)
        # print(f"Image {i} sent to server")

        # wait for confirmation from server
        socks = dict(poller.poll(timeout=10000))  # timeout after 1s
        if socket in socks and socks[socket] == zmq.POLLIN:
            message = socket.recv().decode()
            print(message)
            parts = message.split(' ')
            left = float(parts[0])
            right = float(parts[1])



            drive.setThrottle(left, right)

        else:
            print("Server disconnected")
            break

except zmq.error.ZMQError as e:
    print(f"Socket error: {e}")

except KeyboardInterrupt:
    print("Interrupted")

drive.stop()

# release resources
cap.release()
socket.close()
context.term()
sys.exit()