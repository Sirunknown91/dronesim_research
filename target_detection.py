import airsim
import cv2
import keyboard
import time
import multiprocessing
from yolo import YOLODetector

def run_target_detection(stop_event):
    """
    Run target detection in a separate process
    """
    try:
        # Connect to AirSim
        client = airsim.MultirotorClient()
        client.confirmConnection()
        
        # Initialize YOLO detector
        detector = YOLODetector("model/best.pt")
        
        # Setup camera
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
        client.simSetCameraInfo(camera_name="bottom_center", camera_info=camera_info)

        print("Target detection started")
        
        while not stop_event.is_set():
            try:
                # Get image from camera
                rawImage = client.simGetImage("bottom_center", airsim.ImageType.Scene)
                if rawImage is None:
                    print("Failed to get image")
                    continue

                # Decode image
                png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
                if png is None:
                    print("Failed to decode image")
                    continue

                # Process image with YOLO detector
                detection_image, targets_found = detector.process_image(png)

                # Show images
                cv2.imshow("Bottom Camera View", png)
                cv2.imshow("Detection Results", detection_image)
                
                # Check if windows are closed
                if cv2.getWindowProperty("Bottom Camera View", cv2.WND_PROP_VISIBLE) < 1 or \
                   cv2.getWindowProperty("Detection Results", cv2.WND_PROP_VISIBLE) < 1:
                    break
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or keyboard.is_pressed('esc'):
                    break

            except Exception as e:
                print(f"Error in detection loop: {str(e)}")
                time.sleep(1)  # Prevent rapid error loops

    except Exception as e:
        print(f"Error in target detection process: {str(e)}")
    finally:
        cv2.destroyAllWindows()
        print("Target detection stopped") 