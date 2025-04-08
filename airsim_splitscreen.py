#this file provides functions for dealing with my custom splitscreen functionality for airsim

import airsim
import airsim_keyboard_controller
from airsim_drone import Drone
from airsim import Vector3r

def splitScreen(client : airsim.MultirotorClient):
    client.simRunConsoleCommand("ce SplitScreen")

def attachCameraToDrone(client : airsim.MultirotorClient, droneName = "", cameraName = "LeftScreenCapture"):
    client.simRunConsoleCommand(f"ce AttachCameraToDrone {droneName} {cameraName}")

def splitScreenTesting(client : airsim.MultirotorClient):
    mainDrone = Drone(client, vehicleName="MainDrone")
    secondDrone = Drone(client, vehicleName="Drone2", shouldSpawn=True, spawnPosition=Vector3r(5, -5, -0.5), pawn_path="QuadrotorAlt1")  

    splitScreen(client)
    attachCameraToDrone(client, droneName=mainDrone.vehicleName, cameraName="LeftScreenCapture")
    attachCameraToDrone(client, droneName=secondDrone.vehicleName, cameraName="RightScreenCapture")

    airsim_keyboard_controller.controlDroneLoop(client)

if __name__ == "__main__":
    client = airsim.MultirotorClient()
    client.confirmConnection()

    splitScreenTesting(client)