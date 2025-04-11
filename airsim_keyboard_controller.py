import airsim
import time
import keyboard
import numpy
from airsim import Pose
from airsim_list_all_objects import printAllObjects, printAllAvailAssets
from threading import Thread
from time import sleep
import airsim_splitscreen
from airsim_drone import Drone
import os 
from typing import Dict
# relevant documentation: https://microsoft.github.io/AirSim/apis/

class DroneKeyboardController:

    def __init__(self, drone : Drone, controls : Dict[str, str], input_rate = 1/30):
        
        self.drone = drone
        self.controls = controls
        self.input_rate = input_rate
        

    def process(self):  
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
        self.drone.client.moveByVelocityBodyFrameAsync(*vel, self.input_rate, vehicle_name=self.drone.vehicleName)

# take image from drone camera and saves it. camera ids: https://microsoft.github.io/AirSim/image_apis/#multirotor
def saveImage(client : airsim.MultirotorClient, cameraId = "bottom_center", img_path = "test_image.png"):
    
    png_image = client.simGetImage(cameraId, airsim.ImageType.Scene)

    with open(img_path, 'wb') as imgfile:
        imgfile.write(png_image)

# Loop that controls the drone with your keyboard
def controlDroneLoop(client : airsim.MultirotorClient):
    client.enableApiControl(True)

    print("Drone keyboard control activated. Press ESC to disable")
    
    #client.moveByVelocityAsync(0, 0, -5, 0.1).join() # used previously to make drone realize its not on ground in old janky version

    imageTaken = False

    input_rate = 0.016

    startingDroneHeightMeters = client.getGpsData().gnss.geo_point.altitude

    while True:
        
        futures = []

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
        futures.append(client.moveByVelocityBodyFrameAsync(*vel, input_rate))

        #rotation
        #   roll pitch yaw
        rot = [0, 0, 0]
        shouldRot = False
        if(keyboard.is_pressed('q')):
            rot[2] += 1
            shouldRot = True
        if(keyboard.is_pressed('e')):
            rot[2] += -1
            shouldRot = True

        if(shouldRot):
            futures.append(client.moveByAngleRatesThrottleAsync(*rot, throttle=10, duration=input_rate))
        
        trueVel = client.getGpsData().gnss.velocity

        client.simPrintLogMessage("Approximate flight Velocity (NED): ", ", ".join([str(round(v, 2)) for v in trueVel]))
 
        droneHeightMeters = client.getGpsData().gnss.geo_point.altitude - startingDroneHeightMeters
        droneHeightFeet = droneHeightMeters * 3.28084
        client.simPrintLogMessage("Approximate height off ground: ", f"{round(droneHeightMeters, 2)} meters ({round(droneHeightFeet, 2)} feet)")

        if(keyboard.is_pressed('.') and not imageTaken):
            imageTaken = True
            saveImage(client)
        
        #makes sure image is only taken once per press of . instead of once per frame while holding .
        if(not keyboard.is_pressed('.')):
            imageTaken = False

        # disable script
        if(keyboard.is_pressed('esc')):
            break

        #for future in futures : future.join()
        time.sleep(input_rate)

    print("Drone keyboard control deactivated")
    client.enableApiControl(False)


if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    controlDroneLoop(client)