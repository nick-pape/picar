import zmq
import os
import cv2
import numpy as np
import torch
import sys
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_320_fpn
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from pycocotools.coco import COCO
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from PIL import Image
from torchvision.transforms.functional import pil_to_tensor
import datetime

print("Setting up 0MQ")
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")   # binds to all network interfaces

print("Setting up CNN")
#object_detection_model = fasterrcnn_resnet50_fpn(pretrained=True, progress=False)
#object_detection_model = fasterrcnn_mobilenet_v3_large_320_fpn(pretrained=True)
object_detection_model = ssdlite320_mobilenet_v3_large(pretrained=True)
object_detection_model.eval()
THRESHOLD = 0.5

print("Setting up annotations")
annFile='annotations/instances_val2017.json'
coco=COCO(annFile)

print("READY")

frame_count = 0
init_time = False

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

try:
    # DO THINGS
    while True:
        # wait for client request

        socks = dict(poller.poll(timeout=10000))  # timeout after 5s
        if socket in socks and socks[socket] == zmq.POLLIN:
            message = socket.recv()
            print("Received image")
        else:
            print("Client disconnected")
            break

        if (init_time == False):
            init_time = datetime.datetime.now()

        # Decode the image data into a numpy array
        image_array = np.frombuffer(message, dtype=np.uint8)

        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        int_tensor = pil_to_tensor(img_pil)
        
        img_tensor = int_tensor / 255.0
        img_tensor = img_tensor.unsqueeze(dim=0)

        #print(img_tensor.shape)

        preds = object_detection_model(img_tensor)

        #print(preds)

        preds[0]["boxes"] = preds[0]["boxes"][preds[0]["scores"] > THRESHOLD]
        preds[0]["labels"] = preds[0]["labels"][preds[0]["scores"] > THRESHOLD]
        preds[0]["scores"] = preds[0]["scores"][preds[0]["scores"] > THRESHOLD]

        # allegedly works
        labels = coco.loadCats(preds[0]["labels"].numpy())
        annot_labels = ["{}-{:.2f}".format(label["name"], prob) for label, prob in zip(labels, preds[0]["scores"].detach().numpy())]


        bounded_image = draw_bounding_boxes(image=int_tensor,
                                    boxes=preds[0]["boxes"],
                                    labels=annot_labels,
                                    colors=["red" if label["name"]=="person" else "green" for label in labels],
                                    width=2)


        # change back to bounded_image
        pil_image = to_pil_image(bounded_image)
        cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Display the image using cv2.imshow()
        cv2.imshow('Image', cv2_image)

        # Calculate the elapsed seconds
        elapsed_seconds = ( datetime.datetime.now() - init_time).total_seconds()
        frame_count += 1

        print(f'FPS: {frame_count / elapsed_seconds}')

        # Wait for 1ms and check if a key is pressed
        key = cv2.waitKey(1)

        # Exit the loop if 'q' is pressed
        if key == ord('q'):
            raise KeyboardInterrupt()

        # send confirmation to the client
        socket.send(b"Image received successfully")

except zmq.error.ZMQError:
    print("Client disconnected")

except KeyboardInterrupt:
    print("Interrupted")

socket.close()
context.term()
cv2.destroyAllWindows()
sys.exit()
