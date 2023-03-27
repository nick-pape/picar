import zmq
import cv2
import time
import sys

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://10.0.0.5:5555")   # connect to server

# capture an image using the default camera
cap = cv2.VideoCapture(0)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]   # JPEG quality (0-100)
    
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

i=0

try:
    while True:
        try:
            ret, frame = cap.read()
            i+=1
            # convert the image to JPEG format
            image = cv2.imencode('.jpg', frame, encode_param)[1].tobytes()

            # send the image to the server
            socket.send(image)
            print(f"Image {i} sent to server")

            # wait for confirmation from server
            message = socket.recv().decode()
            print(message)

            if (message == "EXIT"):
                break

        except zmq.error.ZMQError as e:
            print(f"Socket error: {e}")
            break

except KeyboardInterrupt:
    print("Interrupted")

# release resources
cap.release()
socket.close()
context.term()
sys.exit()