from pycocotools.coco import COCO

from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_320_fpn
from torchvision.models.detection import ssdlite320_mobilenet_v3_large

from torchvision.utils import draw_bounding_boxes

class ObjectDetector:
    def __init__(self, threshold = 0.5):
        #self.object_detection_model = fasterrcnn_resnet50_fpn(pretrained=True, progress=False)
        #self.object_detection_model = fasterrcnn_mobilenet_v3_large_320_fpn(pretrained=True)
        self.object_detection_model = ssdlite320_mobilenet_v3_large(pretrained=True)
        self.object_detection_model.eval()
        self.threshold = threshold

        annFile='annotations/instances_val2017.json'
        self.coco=COCO(annFile)
        
    def getLabels(self, image_int_tensor):
        # Normalize integer tensor and squeeze (since model can accept multiple images)
        img_tensor = image_int_tensor / 255.0
        img_tensor = img_tensor.unsqueeze(dim=0)

        # Get predictions
        preds = self.object_detection_model(img_tensor)[0]

        # Filter for predictions above threshold
        preds["boxes"] = preds["boxes"][preds["scores"] > self.threshold]
        preds["labels"] = preds["labels"][preds["scores"] > self.threshold]
        preds["scores"] = preds["scores"][preds["scores"] > self.threshold]

        # allegedly works
        labels = self.coco.loadCats(preds["labels"].numpy())

        return preds, labels

    def getBoundedImage(self, image_int_tensor, labels, preds):
        annot_labels = ["{}-{:.2f}".format(label["name"], prob) for label, prob in zip(labels, preds["scores"].detach().numpy())]

        return draw_bounding_boxes(image=image_int_tensor,
                                    boxes=preds["boxes"],
                                    labels=annot_labels,
                                    colors=["red" if label["name"]=="person" else "green" for label in labels],
                                    width=2)

