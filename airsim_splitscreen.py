#this file provides functions for dealing with my custom splitscreen functionality for airsim

import airsim
import airsim_keyboard_controller
from airsim_drone import Drone
from airsim import Vector3r
import time
import os 
import cv2
import numpy as np
import keyboard

screenSplit = False

# splits screen into two cameras
def simSplitScreen(client : airsim.MultirotorClient):
    global screenSplit
    client.simRunConsoleCommand("ce SplitScreen")
    screenSplit = True

# returns screen to normal
def simUnsplitScreen(client : airsim.MultirotorClient):
    global screenSplit
    client.simRunConsoleCommand("ce UnsplitScreen")
    screenSplit = False

# allows you to attach split screen camera to a drone
# Camera names are LeftScreenCapture and RightScreenCapture.
def simAttachCameraToDrone(client : airsim.MultirotorClient, droneName = "", cameraName = "LeftScreenCapture"):
    client.simRunConsoleCommand(f"ce AttachCameraToDrone {droneName} {cameraName}")

# allows you to set image displayed on half of screen to an image retrieved from a file
# note: apsect ratio of image halfs is approximately 1:1.1 (the exact value is 980:1080) (that is 10% taller than wide.) 
# other image apsect ratios will be stretched slightly 
def simSetSplitScreenToImageFile(client : airsim.MultirotorClient, fileName = "", rightSide = True):
    client.simRunConsoleCommand(f"ce SetSplitScreenImageFromFile {rightSide} {fileName}")

# sets the future offset of camera from drone (as in it'll only take effect when you attach a camera
# to a drone. Also this uses Unreal's coordinate system rather than AirSim's so be careful)
# default value is -300 0 250
def simSetFutureCameraOffset(client : airsim.MultirotorClient, x, y, z):
    client.simRunConsoleCommand(f"ce SetCameraOffset {x} {y} {z}")

def splitScreenDemo(client : airsim.MultirotorClient):

    #client.simRunConsoleCommand("DisableAllScreenMessages")

    mainDrone = Drone(client, vehicleName="MainDrone")
    secondDrone = Drone(client, vehicleName="Drone2", shouldSpawn=True, spawnPosition=Vector3r(5, -5, -0.5), pawn_path="QuadrotorAlt1")  

    drones = [mainDrone, secondDrone]

    # spliting screen and attaching cameras to follow the drones
    simSplitScreen(client)
    
    simAttachCameraToDrone(client, droneName=mainDrone.vehicleName, cameraName="RightScreenCapture")
    
    # simSetFutureCameraOffset(client, 0, 0, 150)
    simAttachCameraToDrone(client, droneName=secondDrone.vehicleName, cameraName="LeftScreenCapture")

    # readying up drones
    time.sleep(1)
    
    [client.enableApiControl(True, drone.vehicleName) for drone in drones]
    [client.armDisarm(True, drone.vehicleName) for drone in drones]

    futures = [client.takeoffAsync(20, drone.vehicleName) for drone in drones]
    [future.join() for future in futures]

    airsim.wait_key("press any key to show flying around")

    future1 = mainDrone.moveToWorldPosition(Vector3r(0, -15, -3), 5, 20)
    future2 = secondDrone.moveToWorldPosition(Vector3r(-5, -15, -3), 5, 20)
    future1.join()
    future2.join()

    # future1 = mainDrone.moveToWorldPosition(Vector3r(0, -15, -5), 5, 20)
    # future2 = secondDrone.moveToWorldPosition(Vector3r(-5, -15, -3), 5, 20)
    # future1.join()
    # future2.join()

    # future1 = mainDrone.moveToWorldPosition(Vector3r(0, -30, -3), 5, 20)
    # future2 = secondDrone.moveToWorldPosition(Vector3r(-5, -30, -3), 5, 20)
    # future1.join()
    # future2.join()

    # airsim.wait_key("press any key to show color changing")

    # # # this resets the screen split so that we have access to both cameras again
    # # simUnsplitScreen(client)
    # # simSplitScreen(client)

    # secondDrone.changeColor(1, 1, 0)
    # time.sleep(1)
    # secondDrone.changeColor(0, 1, 1)
    # time.sleep(1)
    # secondDrone.changeColor(0.2, 0, 0.4)

    airsim.wait_key("press any key to show custom images on half")

    future1 = mainDrone.moveToWorldPosition(Vector3r(0, -100, -80), 7, 20)

    time.sleep(0.1)

    # while drone is moving, take images
    while client.simGetGroundTruthKinematics(mainDrone.vehicleName).linear_velocity.get_length() > 0.1:

        raw_image = client.simGetImage(camera_name="bottom_center", image_type=airsim.ImageType.Scene, vehicle_name=mainDrone.vehicleName)

        # padding image so it is not stretched
        image = cv2.imdecode(airsim.string_to_uint8_array(raw_image), cv2.IMREAD_COLOR)

        image = cv2.copyMakeBorder(image, 66, 66, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        # adding stuff for display
        image = cv2.resize(image, (512, 564))

        somewhat_light_red = (50, 50, 255)

        #image = cv2.putText(img=image, text="pretend image detection", org=(256, 296), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=somewhat_light_red)
        image = cv2.rectangle(img=image, pt1=(256, 296), pt2=(186, 226), color=somewhat_light_red, thickness=2)

        # save image to file
        img_path = "demo_image.png"
        cv2.imwrite(img_path, image)

        # displaying image (needs to get image from file, which is why we have to save it above)
        dir_path = os.path.dirname(os.path.realpath(__file__))

        absolute_img_path = dir_path + "\\" + img_path

        simSetSplitScreenToImageFile(client, absolute_img_path, rightSide=False)
        time.sleep(0.1)

    future1.join()

    
    airsim.wait_key("press any key to disable api control")
    [client.enableApiControl(False, drone.vehicleName) for drone in drones]

def splitScreenKeyboardDemo(client : airsim.MultirotorClient):
    client.simRunConsoleCommand("DisableAllScreenMessages")

    mainDrone = Drone(client, vehicleName="MainDrone")
    secondDrone = Drone(client, vehicleName="Drone2", shouldSpawn=True, spawnPosition=Vector3r(5, -5, -0.5), pawn_path="QuadrotorAlt1")  

    drones = [mainDrone, secondDrone]

    mainDrone.changeColor(.3, 0, .8)
    secondDrone.changeColor(.2, .8, 0)

    # spliting screen and attaching cameras to follow the drones
    simSplitScreen(client)
    
    simAttachCameraToDrone(client, droneName=mainDrone.vehicleName, cameraName="LeftScreenCapture")
    simAttachCameraToDrone(client, droneName=secondDrone.vehicleName, cameraName="RightScreenCapture")

    # readying up drones
    time.sleep(1)
    
    [client.enableApiControl(True, drone.vehicleName) for drone in drones]
    [client.armDisarm(True, drone.vehicleName) for drone in drones]

    futures = [client.takeoffAsync(20, drone.vehicleName) for drone in drones]
    [future.join() for future in futures]

    # drone controllers    
    controller1 = airsim_keyboard_controller.DroneKeyboardController(mainDrone, {})
    controller2 = airsim_keyboard_controller.DroneKeyboardController(secondDrone, {"forward": "i", "back": "k", "left" : "j", "right" : "l", "up": ".", "down": ","})

    while True:
        controller1.process()
        controller2.process()

        if(keyboard.is_pressed("esc")):
            break

        time.sleep(controller1.input_rate)

    [client.enableApiControl(False, drone.vehicleName) for drone in drones]

def splitScreenKeyboardSwappableDemo(client : airsim.MultirotorClient):
    client.simRunConsoleCommand("DisableAllScreenMessages")

    mainDrone = Drone(client, vehicleName="MainDrone")
    secondDrone = Drone(client, vehicleName="Drone2", shouldSpawn=True, spawnPosition=Vector3r(5, -5, -0.5), pawn_path="QuadrotorAlt1")  

    drones = [mainDrone, secondDrone]

    mainDrone.changeColor(.1, 0, .3)
    secondDrone.changeColor(.6, .7, .95)

    # spliting screen and attaching cameras to follow the drones
    simSplitScreen(client)
    
    simAttachCameraToDrone(client, droneName=mainDrone.vehicleName, cameraName="LeftScreenCapture")
    simAttachCameraToDrone(client, droneName=secondDrone.vehicleName, cameraName="RightScreenCapture")

    airsim_keyboard_controller.controlDroneSwappableLoop(client)

if __name__ == "__main__":
    client = airsim.MultirotorClient()
    client.confirmConnection()

    splitScreenKeyboardSwappableDemo(client)