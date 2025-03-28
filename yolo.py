import cv2
import numpy as np
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path="runs/detect/train3/weights/best.pt", device="cuda"):
        self.model = YOLO(model_path).to(device)
        
    def process_image(self, image, conf_threshold=0.5):
        """
        Process an image using YOLO detection and return both the original and annotated images
        """
        # Create a copy for detection results
        detection_image = image.copy()
        
        # Convert RGBA to RGB if needed
        if image.shape[-1] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            detection_image = cv2.cvtColor(detection_image, cv2.COLOR_RGBA2RGB)
            
        # Perform YOLO detection
        results = self.model.predict(image, conf=conf_threshold, iou=0.4)
        
        # Process results
        targets_found = False
        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                targets_found = True
                for box in boxes:
                    conf = box.conf.item()
                    bx1, by1, bx2, by2 = [int(x) for x in box.xyxy[0]]
                    cv2.rectangle(detection_image, (bx1, by1), (bx2, by2), (0, 0, 255), 2)
                    class_id = int(box.cls.item())
                    class_name = self.model.names[class_id]
                    conf_text = f"{class_name}: {conf:.2%}"
                    cv2.putText(detection_image, conf_text, (bx1, by1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        if not targets_found:
            cv2.putText(detection_image, "No Target", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        return detection_image, targets_found
