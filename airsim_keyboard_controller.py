import airsim
import time
import keyboard
import numpy
from airsim import Pose
from airsim_list_all_objects import printAllObjects, printAllAvailAssets
from threading import Thread
from time import sleep
import airsim_splitscreen
import airsim_minimap
from airsim_drone import Drone
import os 
from typing import Dict
from collections.abc import Callable
# relevant documentation: https://microsoft.github.io/AirSim/apis/

class DroneKeyboardController:

    def __init__(self, drone : Drone, controls : Dict[str, str] = {}, input_rate = 1/30):
        
        self.drone = drone
        self.input_rate = input_rate

        # setting up controls
        self.inputs_held = {
            "up" : False,
            "down" : False,
            "forward" : False,
            "back" : False,
            "left" : False,
            "right" : False,
            "rot_left" : False,
            "rot_right" : False,
            "take_image": False,
            }
        
        controls.setdefault("up", "space")
        controls.setdefault("down", "ctrl")
        
        controls.setdefault("forward", "w")
        controls.setdefault("back", "s")

        controls.setdefault("left", "a")
        controls.setdefault("right", "d")

        controls.setdefault("rot_left", "q")
        controls.setdefault("rot_right", "e") 

        controls.setdefault("take_image", ".") 

        self.controls = controls

        self.imageTaken = False

        # start listening for key presses
        keyboard.hook(lambda e : self.onKeyAction(e))

    def onKeyAction(self, event : keyboard.KeyboardEvent):
        key = event.name
        if event.event_type == keyboard.KEY_DOWN:
            [self.setInputHeld(input, True) for input, value in self.controls.items() if value == key]
        if event.event_type == keyboard.KEY_UP:
            [self.setInputHeld(input, False) for input, value in self.controls.items() if value == key]

    def setInputHeld(self, input, held):
        self.inputs_held[input] = held

    # returns list of futures to join of and wait for operations started here to finish
    def process(self):  
        futures = []
        # setting flight direction based on keyboard input
        vel = [0, 0, 0]

        speed = 10
        
        # vertical movement
        if(self.inputs_held["up"]):
            vel[2] += -speed
        if(self.inputs_held["down"]):
            vel[2] += speed

        # forward/back movement
        if(self.inputs_held["forward"]):
            vel[0] += speed
        if(self.inputs_held["back"]):
            vel[0] += -speed

        # left/right movement
        if(self.inputs_held["left"]):
            vel[1] += -speed
        if(self.inputs_held["right"]):
            vel[1] += speed
    
        # telling the sim drone to fly
        futures.append(self.drone.client.moveByVelocityBodyFrameAsync(*vel, self.input_rate, vehicle_name=self.drone.vehicleName))

        rot = [0, 0, 0]
        shouldRot = False
        if(self.inputs_held["rot_left"]):
            rot[2] += 1
            shouldRot = True
        if(self.inputs_held["rot_right"]):
            rot[2] += -1
            shouldRot = True

        if(shouldRot):
            futures.append(self.drone.client.moveByAngleRatesThrottleAsync(*rot, throttle=10, duration=self.input_rate, vehicle_name=self.drone.vehicleName))

        if(self.inputs_held["take_image"] and not self.imageTaken):
            self.saveImage()
            self.imageTaken = True #makes only one image be taken per keypress

        if(not self.inputs_held["take_image"] and self.imageTaken):
            self.imageTaken = False

        return futures

    # take image from drone camera and saves it. camera ids: https://microsoft.github.io/AirSim/image_apis/#multirotor
    def saveImage(self, cameraId = "bottom_center", img_path = "test_image.png"):
        png_image = self.drone.client.simGetImage(camera_name=cameraId, image_type=airsim.ImageType.Scene, vehicle_name=self.drone.vehicleName)

        with open(img_path, 'wb') as imgfile:
            imgfile.write(png_image)

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

    defaultDrone = Drone(client)
    controller = DroneKeyboardController(defaultDrone)

    while True:
        
        futures = controller.process()
        
        trueVel = client.getGpsData().gnss.velocity

        client.simPrintLogMessage("Approximate flight Velocity (NED): ", ", ".join([str(round(v, 2)) for v in trueVel]))
 
        droneHeightMeters = client.getGpsData().gnss.geo_point.altitude - startingDroneHeightMeters
        droneHeightFeet = droneHeightMeters * 3.28084
        client.simPrintLogMessage("Approximate height off ground: ", f"{round(droneHeightMeters, 2)} meters ({round(droneHeightFeet, 2)} feet)")

        # disable script
        if(keyboard.is_pressed('esc')):
            break

        for future in futures : future.join()

    print("Drone keyboard control deactivated")
    client.enableApiControl(False)

def incControlledIndex():
    global controlledIndex, controllers
    controlledIndex += 1
    controlledIndex %= len(controllers)

def decControlledIndex():
    global controlledIndex, controllers
    controlledIndex -= 1
    controlledIndex %= len(controllers)

# Loop that lets you control many drones with the keyboard
def controlDroneSwappableLoop(client : airsim.MultirotorClient):
    global controlledIndex, controllers

    vehicleNames = client.listVehicles()

    drones = []
    for droneName in vehicleNames:
        drones.append(Drone(client, vehicleName=droneName))

    for drone in drones : client.enableApiControl(True, drone.vehicleName) 

    controllers = []
    for drone in drones:
        controllers.append(DroneKeyboardController(drone))

    controlledIndex = 0

    hotkeynext = keyboard.add_hotkey("9", incControlledIndex)
    hotkeyprev = keyboard.add_hotkey("8", decControlledIndex)  

    while True:
        currentController = controllers[controlledIndex]
        futures = currentController.process()

        if(keyboard.is_pressed("esc")):
            break

        for future in futures: future.join()

    keyboard.remove_hotkey(hotkeynext)
    keyboard.remove_hotkey(hotkeyprev)
        
    for drone in drones : client.enableApiControl(False, drone.vehicleName) 


def incControlledDrone():
    global controlledIndex, drones
    controlledIndex += 1
    controlledIndex %= len(drones)

def decControlledDrone():
    global controlledIndex, drones
    controlledIndex -= 1
    controlledIndex %= len(drones)

def updateCameraFollow():
    global controlledIndex, drones, _droneswappedlisteners
    currentDrone = drones[controlledIndex]
    airsim_splitscreen.simSetFutureCameraOffset(currentDrone.client, -300, 0, 250)
    airsim_splitscreen.simAttachCameraToDrone(currentDrone.client, droneName=currentDrone.vehicleName, cameraName="LeftScreenCapture")
    airsim_splitscreen.simSetFutureCameraOffset(currentDrone.client, -50, 0, 750)
    airsim_splitscreen.simAttachCameraToDrone(currentDrone.client, droneName=currentDrone.vehicleName, cameraName="RightScreenCapture")

def controlDroneSwappableCameraLoop(client : airsim.MultirotorClient):
    global controlledIndex, drones

    vehicleNames = client.listVehicles()
    
    drones = []
    for droneName in vehicleNames:
        drones.append(Drone(client, vehicleName=droneName))

    for drone in drones : client.enableApiControl(True, drone.vehicleName) 

    controllers = []
    for drone in drones:
        controllers.append(DroneKeyboardController(drone, input_rate=1/10))

    controlledIndex = 0
    lastControlledIndex = -1

    updateCameraFollow()

    hotkeynext = keyboard.add_hotkey("9", incControlledDrone)
    hotkeyprev = keyboard.add_hotkey("8", decControlledDrone)  

    while True:
        futures = []
        currentController = controllers[controlledIndex]
        #for currentController in controllers:
        futures += currentController.process()

        if(lastControlledIndex != controlledIndex):
            lastControlledIndex = controlledIndex
            updateCameraFollow()
            currentDrone = drones[controlledIndex]
            for listener in _droneswappedlisteners:
                listener(currentDrone)

        airsim_minimap.simUpdateMinimapWidthToKeepDronesVis(client, drones, drones[controlledIndex], buffer=1000)
        if(keyboard.is_pressed("esc")):
            break

        for future in futures: future.join()

    keyboard.remove_hotkey(hotkeynext)
    keyboard.remove_hotkey(hotkeyprev)
        
    for drone in drones : client.enableApiControl(False, drone.vehicleName) 

_droneswappedlisteners = []

def AddDroneSwappedListener(listener : Callable):
    _droneswappedlisteners.append(listener)

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    controlDroneLoop(client)