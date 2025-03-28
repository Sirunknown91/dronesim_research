import airsim
import cv2
import keyboard
import time
import numpy as np
from yolo import YOLODetector

def detect_pool(client):
    try:
        # Initialize YOLO detector
        detector = YOLODetector("./model/pool.pt")
        
        # Set camera resolution using ImageRequest
        responses = client.simGetImages([
            airsim.ImageRequest("bottom_center", airsim.ImageType.Scene, False, False)
        ])
        
        camera_pose = airsim.Pose()
        camera_pose.position = airsim.Vector3r(0, 0, -1)
        camera_pose.orientation = airsim.to_quaternion(0, 0, 0)

        camera_info = airsim.CameraInfo()
        camera_info.pose = camera_pose
        camera_info.fov_degrees = 90
        camera_info.width = 512  
        camera_info.height = 512  
        camera_info.proj_mat = [1, 0, 0, 0, 1, 0, 0, 0, 1]

        client.simSetCameraPose(camera_name="bottom_center", pose=camera_pose)
        client.simSetCameraFov(camera_name="bottom_center", fov_degrees=90)

        while True:
            rawImage = client.simGetImage("bottom_center", airsim.ImageType.Scene)
            if rawImage is None:
                print("Failed to get image")
                break

            png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
            if png is None:
                print("Failed to decode image")
                break

            # Process image with YOLO detector
            detection_image, _ = detector.process_image(png)

            # Resize images to 2x for display
            display_png = cv2.resize(png, (png.shape[1], png.shape[0]))
            display_detection = cv2.resize(detection_image, (detection_image.shape[1], detection_image.shape[0]))

            # Show both windows with enlarged images
            cv2.imshow("Bottom Camera View", display_png)
            cv2.imshow("Detection Results", display_detection)
            
            if cv2.getWindowProperty("Bottom Camera View", cv2.WND_PROP_VISIBLE) < 1 or \
               cv2.getWindowProperty("Detection Results", cv2.WND_PROP_VISIBLE) < 1:
                break
                
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27 or keyboard.is_pressed('esc'): 
                break

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        client = airsim.MultirotorClient()
        client.confirmConnection()
        detect_pool(client)
    except Exception as e:
        print(f"Connection error: {str(e)}")
    finally:
        cv2.destroyAllWindows()