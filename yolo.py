import cv2
import numpy as np
from ultralytics import YOLO
import os.path

class YOLODetector:
    # Predefined color palette for different classes
    COLOR_PALETTE = [
        (0, 0, 255),    # Red
        (0, 255, 0),    # Green
        (255, 0, 0),    # Blue
        (255, 255, 0),  # Cyan
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Yellow
        (128, 0, 0),    # Dark Blue
        (0, 128, 0),    # Dark Green
        (0, 0, 128),    # Dark Red
        (128, 128, 0),  # Dark Cyan
        (128, 0, 128),  # Dark Magenta
        (0, 128, 128),  # Dark Yellow
        (192, 192, 192),# Light Gray
        (128, 128, 128),# Gray
        (153, 153, 255),# Light Blue
        (153, 255, 153),# Light Green
        (255, 153, 153),# Light Red
    ]
    
    # Predefined colors for specific classes
    PREDEFINED_COLORS = {
        "vehicle": "#FF0000",     
        "large_vehicle": "#0000FF",   
        "pool": "#8300a4"        
    }
    
    # Class-wide dictionary to track colors assigned to class names across all models
    class_colors = {}
    next_color_index = 0
    
    # Dictionary for class name mapping
    class_name_mapping = {
        # Vehicle mappings
        "car": "vehicle",
        "truck": "vehicle",
        # "tractor": "vehicle",
        # "camping_car": "vehicle",
        "van": "vehicle",
        # "bus": "vehicle",
        "pickup": "vehicle",
        # "other": "vehicle",
        # Previous mappings commented out
        # "truck": "large_vehicle",
        # "van": "large_vehicle",
        # "person": "human",
    }
    
    # List of classes to ignore in detection results
    IGNORE_CLASSES = ["other","camping_car","plane","ship","tractor"]
    
    # Dictionary for class-specific confidence thresholds
    CLASS_CONF_THRESHOLDS = {
        "large_vehicle": 0.4,
        "vehicle": 0.4,
        "pool": 0.7
        # Add more class-specific thresholds as needed
    }
    
    def __init__(self, model_path="runs/detect/train3/weights/best.pt", device="cuda"):
        self.model = YOLO(model_path).to(device)
        self.model_name = os.path.basename(model_path)
        
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color string to BGR tuple (OpenCV format)"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (rgb[2], rgb[1], rgb[0])  # Convert RGB to BGR
    
    @classmethod
    def get_color_for_class(cls, class_name):
        """Get a consistent color for a class name across all models"""
        # First check if the class has a predefined color (after mapping)
        if class_name in cls.PREDEFINED_COLORS:

            print(cls.PREDEFINED_COLORS[class_name])
            return cls.hex_to_rgb(cls.PREDEFINED_COLORS[class_name])
            
        # If not in predefined colors, check if we've already assigned a color
        if class_name not in cls.class_colors:
            # Assign a new color from the palette
            color_index = cls.next_color_index % len(cls.COLOR_PALETTE)
            cls.class_colors[class_name] = cls.COLOR_PALETTE[color_index]
            cls.next_color_index += 1
        return cls.class_colors[class_name]
        
    def process_image(self, image, conf_threshold=0.2):
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
        results = self.model.predict(image, conf=conf_threshold, iou=0.7)
        
        # Process results
        targets_found = False
        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                targets_found = True
                for box in boxes:
                    conf = box.conf.item()
                    class_id = int(box.cls.item())
                    class_name = self.model.names[class_id]
                    
                    # Skip if class is in ignore list
                    if class_name in self.__class__.IGNORE_CLASSES:
                        continue
                    
                    # Apply class name mapping if exists
                    if class_name in self.__class__.class_name_mapping:
                        class_name = self.__class__.class_name_mapping[class_name]
                    
                    # Check class-specific confidence threshold
                    if class_name in self.__class__.CLASS_CONF_THRESHOLDS:
                        class_threshold = self.__class__.CLASS_CONF_THRESHOLDS[class_name]
                        if conf < class_threshold:
                            continue
                    
                    bx1, by1, bx2, by2 = [int(x) for x in box.xyxy[0]]
                    
                    # Get consistent color for this class
                    color = self.get_color_for_class(class_name)
                    
                    # Increased line thickness from 2 to 4
                    cv2.rectangle(detection_image, (bx1, by1), (bx2, by2), color, 4)
                    conf_text = f"{class_name}: {conf:.2%}"
                    # Increased font scale from 0.6 to 1.0 and thickness from 2 to 3
                    cv2.putText(detection_image, conf_text, (bx1, by1-15), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
        
        return detection_image, results
        
    def draw_detections(self, image, results):
        """
        Draw detection results on an image
        """
        detection_image = image.copy()
        
        # Convert RGBA to RGB if needed
        if detection_image.shape[-1] == 4:
            detection_image = cv2.cvtColor(detection_image, cv2.COLOR_RGBA2RGB)
        
        targets_found = False
        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                targets_found = True
                for box in boxes:
                    conf = box.conf.item()
                    class_id = int(box.cls.item())
                    class_name = self.model.names[class_id]
                    
                    # Skip if class is in ignore list
                    if class_name in self.__class__.IGNORE_CLASSES:
                        continue
                    
                    # Apply class name mapping if exists
                    if class_name in self.__class__.class_name_mapping:
                        class_name = self.__class__.class_name_mapping[class_name]
                    
                    # Check class-specific confidence threshold
                    if class_name in self.__class__.CLASS_CONF_THRESHOLDS:
                        class_threshold = self.__class__.CLASS_CONF_THRESHOLDS[class_name]
                        if conf < class_threshold:
                            continue
                    
                    bx1, by1, bx2, by2 = [int(x) for x in box.xyxy[0]]
                    
                    # Get consistent color for this class
                    color = self.get_color_for_class(class_name)
                    
                    cv2.rectangle(detection_image, (bx1, by1), (bx2, by2), color, 2)
                    conf_text = f"{class_name}: {conf:.2%}"
                    cv2.putText(detection_image, conf_text, (bx1, by1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return detection_image
