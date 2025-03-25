import airsim
import time
from threading import Thread
from playsound import playsound
from pathlib import Path
import random

def simSpawnGunshot(client : airsim.MultirotorClient, pos):
    pose = airsim.Pose(position_val=pos)
    scale = airsim.Vector3r(1, 1, 1)
    new_light_name = client.simSpawnObject("GunshotLight", "GunshotLightBase2", pose, scale, False, True)
    print("spawned gunshot")

    dronePose = client.simGetVehiclePose()
    dist = pose.position.distance_to(dronePose.position)
    
    soundTime = dist/343
    client.simPrintLogMessage(f"Spawned gunshot!", f"   Distance: {round(dist,2)} meters away. Should play sound after {round(soundTime,2)} seconds")
    time.sleep(soundTime)
    playsound("C:\\Users\\sirun\\Documents\\grad school stuff\\Research Assistant Work\\dronesim_research\\gunshotaudio\\1.wav", block=False)
    
if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    for i in range(100):
        dronePose = client.simGetVehiclePose()
        gunshotPos = airsim.Vector3r(dronePose.position.x_val, dronePose.position.y_val, -3)
        
        droneHeight = dronePose.position.z_val
        randSpawnRangeFactor = (droneHeight / 2) + 5

        gunshotPos += airsim.Vector3r(random.uniform(-randSpawnRangeFactor, randSpawnRangeFactor), random.uniform(-randSpawnRangeFactor, randSpawnRangeFactor), random.uniform(-2, 2))
        simSpawnGunshot(client, gunshotPos)
        time.sleep(2)