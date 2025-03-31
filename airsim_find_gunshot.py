import airsim
import time
import random
import keyboard
import airsim_spawn_gunshot
import asyncio
from airsim import Vector3r
from airsim_drone import Drone
import numpy as np

# calculates position of sound based on positions of sensors and time delay between each sensor hearing the sound
def calcSoundEmitPosition(sensorSpots : list, audioTimes : list, mediumSpeed = 343):
        
    if(len(audioTimes) != len(sensorSpots)):
        raise ValueError("The length of audioTimes should be the same as the length of sensor spots. (and directly correspond with indices)")

    size = len(sensorSpots)

    # distances relative to sensor that heard the sound first
    relativeDists = []
    for i, audioTime in enumerate(audioTimes):
        relativeDists.append(audioTime * mediumSpeed)
        if(audioTime == 0): # for algorithm below, reference sensor can be any one but I'm picking the one thats closest and hears the sound first
            referenceSensorId = i

    # for this algorithm see https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1145216

    # S_j in the paper. N-1x3 matrix of xyz coord of each sensor relative to reference sensor
    sensorOffsetsToReference = np.zeros((size - 1,3))

    # mew_j in the paper. I don't have an intuitive understanding/name for this. 
    # Also in the paper the definition of this is slightly misprinted, all values need to be squared
    mew = np.zeros(size - 1) 

    # rho_j in the paper. Vector of the range differences between each sensor and reference sensor. 
    # Since the chosen reference sensor has relativeDist 0 as defined above, this is just the relativeDists array
    rangeDifferences = np.zeros(size - 1)
    
    referenceSensorPos = sensorSpots[referenceSensorId]

    for j, sensorSpot in enumerate(sensorSpots):
        if(j == referenceSensorId):
            continue
        
        rowj = j if j < referenceSensorId else j-1 # lets us skip the reference sensor row in the following matrices
        
        sensorOffsetsToReference[rowj] = np.array(
            (sensorSpot.x_val - referenceSensorPos.x_val,
            sensorSpot.y_val - referenceSensorPos.y_val,
            sensorSpot.z_val - referenceSensorPos.z_val)
        )

        mew[rowj] = (sensorSpot.get_length()**2 - referenceSensorPos.get_length()**2 - relativeDists[j]**2)/2 
        rangeDifferences[rowj] = relativeDists[j]


    # M_j in the paper. called distance remover because this is multiplied by rho_j to always get 0 and 
    # this removes R_j_s (dist from reference sensor to source, which is what we want to find) from the equation.
    # leaving x_s (position of source) as the only unknown
    circularShift = np.roll(np.identity(size - 1), (1, 0), axis=(1, 0))
    d_j = np.linalg.inv(np.diag(rangeDifferences))
    distanceRemover = np.matmul((np.identity(size - 1) - (circularShift)), d_j)
    
    # compute position of source X_s
    first_term = np.matmul(np.matmul(np.matmul(np.transpose(sensorOffsetsToReference), np.transpose(distanceRemover)), distanceRemover), sensorOffsetsToReference)
    x_source = np.matmul(np.matmul(np.matmul(np.matmul(np.linalg.inv(first_term), np.transpose(sensorOffsetsToReference)), np.transpose(distanceRemover)), distanceRemover), mew)

    return Vector3r(x_source[0], x_source[1], x_source[2])


def simSpawnGunshotToFind(client : airsim.MultirotorClient, drone : Drone, pos : Vector3r):

    airsim_spawn_gunshot.simSpawnGunshotAtPos(client, pos)
    print(f"spawned gunshot at {pos}")

    timeDiffs = drone.simGetAudioTimeDifferences(pos)
    print(f"time difference on arrival vals {timeDiffs}")

    estimatedSoundPosition = calcSoundEmitPosition([sensorSpot+drone.simGetPosition() for sensorSpot in drone.sensorSpots], timeDiffs)
    print(f"algo thought gunshot at {estimatedSoundPosition}")

    client.moveToPositionAsync(estimatedSoundPosition.x_val, estimatedSoundPosition.y_val, -20, 10).join()

def findGunshotLoop(client : airsim.MultirotorClient):
    client.enableApiControl(True)

    print("Drone gunshot detection control activated. Press ESC to disable")

    flightHeight = 20
    client.takeoffAsync(10)

    sensorSpots = [Vector3r(0.5, 0, 0.1), Vector3r(0, 0.5, 0.1), Vector3r(0, -0.5, 0.1), Vector3r(-0.5, 0, 0.1), Vector3r(0, 0, 0.3)]
    mainDrone = Drone(client, sensorSpots)
    
    while True:
        key = airsim.wait_key('waiting for console input')
        if(key == b']'):
            simSpawnGunshotToFind(client, mainDrone, Vector3r(0, 10, 0))
            simSpawnGunshotToFind(client, mainDrone, Vector3r(10, 20, 0))
            simSpawnGunshotToFind(client, mainDrone, Vector3r(100, 30, -1))
            simSpawnGunshotToFind(client, mainDrone, Vector3r(-20, 50, 0))
        if(key == b'\x1b'):
            break
        

    print("Drone gunshot detection control deactivated")
    client.enableApiControl(False)
    

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    findGunshotLoop(client)
