import cv2
import numpy as np
import airsim
import keyboard
import time
from yolo import YOLODetector
def saveImage(client : airsim.MultirotorClient, cameraId = "bottom_center", img_path = "test_image.png"):
    
    png_image = client.simGetImage(cameraId, airsim.ImageType.Scene)

    with open(img_path, 'wb') as imgfile:
        imgfile.write(png_image)

def get_drone_client():
    client = airsim.MultirotorClient()
    client.confirmConnection()
    return client

def start_keyboard_control(client=get_drone_client()):
    client.enableApiControl(True)
    imageTaken = False
    input_rate = 0.05

    while True:
        # setting flight direction based on keyboard input
        vel = [0, 0, 0]
        
        # vertical movement
        if(keyboard.is_pressed('space')):
            vel[2] += -10
        if(keyboard.is_pressed('ctrl')):
            vel[2] += 10

        # forward/back movement
        if(keyboard.is_pressed('w')):
            vel[0] += 10
        if(keyboard.is_pressed('s')):
            vel[0] += -10

        # left/right movement
        if(keyboard.is_pressed('d')):
            vel[1] += 10
        if(keyboard.is_pressed('a')):
            vel[1] += -10
        
        # telling the sim drone to fly
        client.moveByVelocityBodyFrameAsync(*vel, input_rate)

        #rotation
        #   roll pitch yaw
        rot = [0, 0, 0, 0]
        shouldRot = False
        if(keyboard.is_pressed('q')):
            rot[2] += -1
            shouldRot = True
        if(keyboard.is_pressed('e')):
            rot[2] += 1
            shouldRot = True

        if(shouldRot):
            pass
            #client.moveByRollPitchYawZAsync(*rot, input_rate)
        
        if(keyboard.is_pressed('.') and not imageTaken):
            imageTaken = True
            saveImage(client)
        
        #makes sure image is only take once per press of . instead of once per frame while holding .
        if(not keyboard.is_pressed('.')):
            imageTaken = False

        client.simPrintLogMessage("Input velocity: ", ", ".join([str(v) for v in vel]))

        dronePose = client.simGetVehiclePose()
        droneHeightMeters = -dronePose.position.z_val
        droneHeightFeet = droneHeightMeters * 3.28084
        client.simPrintLogMessage("Approximate height off ground: ", f"{round(droneHeightMeters, 2)} meters ({round(droneHeightFeet, 2)} feet)")

        # disable script
        if(keyboard.is_pressed('esc')):
            break

        time.sleep(input_rate)

    print("Drone keyboard control deactivated")
    client.simPrintLogMessage("Input velocity: ", "DISABLED")
    client.enableApiControl(False)


def pool_detection(client=get_drone_client()):
    client.enableApiControl(True)
    try:
        # Initialize YOLO detector
        detector = YOLODetector("./model/pool.pt")
        
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

            # Show both windows
            cv2.imshow("Bottom Camera View", png)
            cv2.imshow("Detection Results", detection_image)
            
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
