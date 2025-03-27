import airsim
import time
import random
import keyboard
import airsim_spawn_gunshot
import asyncio
from airsim import Vector3r
from airsim_drone import Drone



def simSpawnGunshotToFind(client : airsim.MultirotorClient, drone : Drone, pos : Vector3r):

    airsim_spawn_gunshot.simSpawnGunshotAtPos(client, pos)
    timeDiffs = drone.simGetAudioTimeDifferences(pos)
    drone.calcSoundEmitPosition(timeDiffs)

def findGunshotLoop(client : airsim.MultirotorClient):
    client.enableApiControl(True)

    print("Drone gunshot detection control activated. Press ESC to disable")

    flightHeight = 20
    client.takeoffAsync(10)

    sensorSpots = [Vector3r(0.5, 0, 0.1), Vector3r(0, 0.5, 0.1), Vector3r(0, -0.5, 0.1)]
    mainDrone = Drone(client, sensorSpots)
    
    while True:
        key = airsim.wait_key('waiting for console input')
        if(key == b']'):
            simSpawnGunshotToFind(client, mainDrone, Vector3r(0, 10, 0))
            simSpawnGunshotToFind(client, mainDrone, Vector3r(0, 50, 0))
            simSpawnGunshotToFind(client, mainDrone, Vector3r(0, 100, 0))
        if(key == b'\x1b'):
            break
        

    print("Drone gunshot detection control deactivated")
    client.enableApiControl(False)

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    findGunshotLoop(client)
