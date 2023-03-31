from torchvision.transforms.functional import pil_to_tensor
from torchvision.transforms.functional import to_pil_image
from PIL import Image

import cv2
import numpy as np

class ImageHelper:
    @staticmethod
    def ImageBufferToCV(buffer):
        # Receive and decode the image
        image_array = np.frombuffer(buffer, dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def ImageBufferToIntegerTensor(buffer):
        img = ImageHelper.ImageBufferToCV(buffer)

        # Convert to PIL then to an integer tensor
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        int_tensor = pil_to_tensor(img_pil)
        
        return int_tensor
    
    @staticmethod
    def IntegerTensorToCV(image_int_tensor):
        pil_image = to_pil_image(image_int_tensor)
        cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return cv2_image