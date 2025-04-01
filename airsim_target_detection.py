import airsim
import cv2
import keyboard
import time
import numpy as np
from yolo import YOLODetector
import msgpack

unpacker = msgpack.Unpacker(max_bin_len=31457280) 
def is_drone_moving(client, threshold=0.1):
    """Check if the drone is moving based on its velocity"""
    state = client.getMultirotorState()
    velocity = state.kinematics_estimated.linear_velocity
    speed = np.sqrt(velocity.x_val**2 + velocity.y_val**2 + velocity.z_val**2)
    return speed > threshold

def detect(client, model_paths):
    try:
        # Initialize multiple YOLO detectors
        detectors = [YOLODetector(path) for path in model_paths]
        
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
            # Check if drone is moving
            if not is_drone_moving(client):
                # print("Drone is stationary, waiting for movement...")
                time.sleep(0.1)  # Small delay to prevent CPU overuse
                continue

            rawImage = client.simGetImage("bottom_center", airsim.ImageType.Scene)
            if rawImage is None:
                print("Failed to get image")
                break

            png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
            if png is None:
                print("Failed to decode image")
                break

            # Create a copy for detection results
            detection_image = png.copy()
            
            # Resize images to 1024x1024 for better visibility
            png = cv2.resize(png, (1024, 1024))
            detection_image = cv2.resize(detection_image, (1024, 1024))
            
            # Process image with all YOLO detectors
            for detector in detectors:
                # Get detection results and update the same image
                _, results = detector.process_image(png)
                # Draw detections on the detection_image
                detection_image = detector.draw_detections(detection_image, results)

            # Resize images to 2x for display
            display_png = cv2.resize(png, (png.shape[1], png.shape[0]))
            display_detection = cv2.resize(detection_image, (detection_image.shape[1], detection_image.shape[0]))

            # Show both windows with enlarged images
            # cv2.imshow("Original Video", display_png)
            cv2.imshow("Detection Video", display_detection)
        
                
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27 or keyboard.is_pressed('esc'): 
                break
            # time.sleep(0.1)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        client = airsim.MultirotorClient()
        client.confirmConnection()
        # Define multiple model paths
        model_paths = [
            "./model/best_pool.pt",
            "./model/best_car.pt",
        ]
        detect(client, model_paths)
    except Exception as e:
        print(f"Connection error: {str(e)}")
    finally:
        cv2.destroyAllWindows()