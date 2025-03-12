import airsim
import time
import keyboard
import numpy
from airsim import Pose
from airsim_list_all_objects import printAllObjects, printAllAvailAssets
from threading import Thread
from time import sleep


# relevant documentation: https://microsoft.github.io/AirSim/apis/

# take image from drone camera and saves it. camera ids: https://microsoft.github.io/AirSim/image_apis/#multirotor
def saveImage(client : airsim.MultirotorClient, cameraId = "bottom_center", img_path = "test_image.png"):
    
    png_image = client.simGetImage(cameraId, airsim.ImageType.Scene)

    with open(img_path, 'wb') as imgfile:
        imgfile.write(png_image)

# Loop that controls the drone with your keyboard
def controlDroneLoop(client : airsim.MultirotorClient):
    client.enableApiControl(True)

    print("Drone keyboard control activated. Press ESC to disable")

    imageTaken = False
    
    #client.moveByVelocityAsync(0, 0, -5, 0.1).join() # used previously to make drone realize its not on ground in old janky version

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
        
        # if(keyboard.is_pressed(']')):
        #     gunshotPos = airsim.Vector3r(dronePose.position.x_val, dronePose.position.y_val, -3)
        #     # runs gunshot spawning on seperate thread so this loop keeps going and controlling the drone
        #     gunshotThread = Thread(target=simSpawnGunshot, args=(client, gunshotPos))
        #     gunshotThread.start()
        

        client.simPrintLogMessage("Input velocity: ", ", ".join([str(v) for v in vel]))

        dronePose = client.simGetVehiclePose()
        client.simPrintLogMessage("Approximate height off ground: ", str(round(-dronePose.position.z_val, 2)) + " meters")

        # disable script
        if(keyboard.is_pressed('esc')):
            break

        time.sleep(input_rate)

    print("Drone keyboard control deactivated")
    client.simPrintLogMessage("Input velocity: ", "DISABLED")
    client.enableApiControl(False)


if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    controlDroneLoop(client)