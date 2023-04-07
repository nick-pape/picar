import cv2
from collections import namedtuple

# Define a named tuple class
PictureDimensions = namedtuple('PictureDimensions', 'width height')

class BaseCamera():
    def __init__(self, dimensions: PictureDimensions = PictureDimensions(640, 480)):
        self.dimensions: PictureDimensions = dimensions
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]   # JPEG quality (0-100)

    def snap(self):
        raise NotImplementedError()
    
    def close(self):
        raise NotImplementedError()

class Camera(BaseCamera):
    def __init__(self):
        super().__init__()

        # capture an image using the default camera
        self.cap = cv2.VideoCapture(0)
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.dimensions.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.dimensions.height)

    def snap(self):
        _, frame = self.cap.read()
        # convert the image to JPEG format
        return cv2.imencode('.jpg', frame, self.encode_param)[1].tobytes()

    def close(self):
        self.cap.release()


class MockCamera(BaseCamera):
    def __init__(self):
        super().__init__(self)
        image = cv2.imread('mock.jpg')
        self.encoded = cv2.imencode('.jpg', image, self.encode_param)[1].tobytes()

    def snap(self):
        print("MockCamera.snap()")
        return self.encoded

    def close(self):
        print("MockCamera.close()")
        return # no-op
