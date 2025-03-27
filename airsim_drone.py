import airsim
from airsim import Vector3r
import numpy as np
import scipy
from math import sqrt

class Drone:

    # client = currently connected airsim multirotor client
    # sensorSpots = list of positions (Vector3r) audio listening sensors relative to center of the drone
    # vehicleName = vehicle name (should match name according to client)
    def __init__(self, client : airsim.MultirotorClient, sensorSpots = [], vehicleName = ''):
        self.client = client
        self.vehicleName = vehicleName
        self.sensorSpots = sensorSpots
        self.speed_of_sound_mps = 343

    def simGetPosition(self):
        return self.client.simGetVehiclePose(self.vehicleName).position

    def simGetAudioTimeDifferences(self, soundEmitPoint : Vector3r):
        pos = self.simGetPosition()

        # calculating the time it would take to reach each sensor
        audioTimes = []
        
        for sensorSpot in self.sensorSpots:
            trueSensorSpot = sensorSpot + pos
            dist = soundEmitPoint.distance_to(trueSensorSpot)
            time = dist / self.speed_of_sound_mps
            audioTimes.append(time)
        
        # subtracting by lowest value so one time is 0 and the other times are relative to that
        minTime = min(audioTimes)
        audioTimes = [audioTime - minTime for audioTime in audioTimes]

        return audioTimes
    
    # calculates approximate position relative to this drone of emitted audio based on time differences from each sensor when hearing the sound (works with 3 sensors)
    def calcSoundEmitPosition(self, audioTimes):
        
        # distances relative to sensor that heard the sound first
        relativeDists = []
        for audioTime in audioTimes:
            relativeDists.append(audioTime * self.speed_of_sound_mps)

        distDeltas = [
            abs(relativeDists[0] - relativeDists[1]),
            abs(relativeDists[1] - relativeDists[2]),
            abs(relativeDists[2] - relativeDists[0]),
            ]
        
        print(distDeltas)

        return Vector3r(0, 0, 0)