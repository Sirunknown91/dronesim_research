import airsim
import time
import keyboard
from airsim import Pose, Vector3r


def saveImage(client : airsim.MultirotorClient, cameraId = "bottom_center", img_path = "test_image.png"):
    png_image = client.simGetImage(cameraId, airsim.ImageType.Scene)
    with open(img_path, 'wb') as imgfile:
        imgfile.write(png_image)

def updateCameraPose(client : airsim.MultirotorClient, camera_name = "bottom_center"):
    # Get current drone pose
    drone_pose = client.simGetVehiclePose()
    
    # Set camera position (1 meter above the drone)
    camera_position = Vector3r(0, 0, 1)
    
    # Set camera orientation (45 degrees downward)
    camera_orientation = airsim.to_quaternion(-45, 0, 0)
    
    # Create camera pose
    camera_pose = Pose()
    camera_pose.position = camera_position
    camera_pose.orientation = camera_orientation
    
    # Update camera pose
    client.simSetCameraPose(camera_name=camera_name, pose=camera_pose)

def setupCamera(client : airsim.MultirotorClient, camera_name = "bottom_center"):
    # Set camera position and orientation
    camera_pose = Pose()
    camera_pose.position = Vector3r(0, 0, 1)
    camera_pose.orientation = airsim.to_quaternion(-45, 0, 0)
    
    # Apply camera settings
    client.simSetCameraPose(camera_name=camera_name, pose=camera_pose)
    client.simSetCameraFov(camera_name=camera_name, fov_degrees=90)

def controlDroneLoop(client : airsim.MultirotorClient):
    client.enableApiControl(True)
    
    print("Drone keyboard control activated with fixed camera angle. Press ESC to disable")
    
    # Setup camera parameters
    setupCamera(client)
    
    imageTaken = False
    input_rate = 0.016
    startingDroneHeightMeters = client.getGpsData().gnss.geo_point.altitude

    while True:
        # Set flight direction
        vel = [0, 0, 0]
        
        # Vertical movement
        if(keyboard.is_pressed('space')):
            vel[2] += -10
        if(keyboard.is_pressed('ctrl')):
            vel[2] += 10

        # Forward/backward movement
        if(keyboard.is_pressed('w')):
            vel[0] += 10
        if(keyboard.is_pressed('s')):
            vel[0] += -10

        # Left/right movement
        if(keyboard.is_pressed('d')):
            vel[1] += 10
        if(keyboard.is_pressed('a')):
            vel[1] += -10
        
        # Control drone flight
        client.moveByVelocityBodyFrameAsync(*vel, input_rate)

        # Rotation control
        rot = [0, 0, 0]
        shouldRot = False
        if(keyboard.is_pressed('q')):
            rot[2] += 1
            shouldRot = True
        if(keyboard.is_pressed('e')):
            rot[2] += -1
            shouldRot = True

        if(shouldRot):
            client.moveByAngleRatesThrottleAsync(*rot, throttle=10, duration=input_rate)
        
        # Update camera pose
        updateCameraPose(client)
        
        # Display current speed
        trueVel = client.getGpsData().gnss.velocity
        client.simPrintLogMessage("Approximate flight Velocity (NED): ", ", ".join([str(round(v, 2)) for v in trueVel]))
 
        # Display height information
        droneHeightMeters = client.getGpsData().gnss.geo_point.altitude - startingDroneHeightMeters
        droneHeightFeet = droneHeightMeters * 3.28084
        client.simPrintLogMessage("Approximate height off ground: ", f"{round(droneHeightMeters, 2)} meters ({round(droneHeightFeet, 2)} feet)")

        # Photo capture functionality
        if(keyboard.is_pressed('.') and not imageTaken):
            imageTaken = True
            saveImage(client)
        
        if(not keyboard.is_pressed('.')):
            imageTaken = False

        # Exit control
        if(keyboard.is_pressed('esc')):
            break

        time.sleep(input_rate)

    print("Drone keyboard control deactivated")
    client.enableApiControl(False)

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    controlDroneLoop(client)
