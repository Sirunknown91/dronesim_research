import airsim
import time
from threading import Thread
from playsound import playsound
from pathlib import Path
import random
import keyboard
import asyncio

def simSpawnGunshotAtPos(client : airsim.MultirotorClient, pos : airsim.Vector3r):
    pose = airsim.Pose(position_val=pos)
    scale = airsim.Vector3r(1, 1, 1)
    new_light_name = client.simSpawnObject("GunshotLight", "GunshotLightBase2", pose, scale, False, True)

    dronePose = client.simGetVehiclePose()
    dist = pose.position.distance_to(dronePose.position)
    
    soundTime = dist/343
    client.simPrintLogMessage(f"Spawned gunshot!", f"   Distance: {round(dist,2)} meters away. Should play sound after {round(soundTime,2)} seconds")
    time.sleep(soundTime)
    playableAudioNums = [1, 2, 5]
    audioToPlay = random.choice(playableAudioNums)
    playsound(f"C:\\Users\\sirun\\Documents\\grad school stuff\\Research Assistant Work\\dronesim_research\\gunshotaudio\\{audioToPlay}.wav", block=False)

def simSpawnGunshotFromRandomNearbyGroundPoint(client : airsim.MultirotorClient):
    dronePose = client.simGetVehiclePose()
    gunshotPos = airsim.Vector3r(dronePose.position.x_val, dronePose.position.y_val, -3)
    
    droneHeight = dronePose.position.z_val
    randSpawnRangeFactor = (droneHeight / 2) + 5

    gunshotPos += airsim.Vector3r(random.uniform(-randSpawnRangeFactor, randSpawnRangeFactor), random.uniform(-randSpawnRangeFactor, randSpawnRangeFactor), random.uniform(-2, 2))
    simSpawnGunshotAtPos(client, gunshotPos)

def spawnGunshotsOnTimer(client : airsim.MultirotorClient, n : int):
    for i in range(n):
        simSpawnGunshotFromRandomNearbyGroundPoint(client)
        time.sleep(2)

def spawnGunshotsFromInput(client : airsim.MultirotorClient):
    keyboard.add_hotkey(']', simSpawnGunshotFromRandomNearbyGroundPoint, args=[client], timeout=0.5)
    keyboard.wait('esc')

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    spawnGunshotsFromInput(client)
