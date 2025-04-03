import airsim
from airsim import Vector3r
import numpy as np
import scipy
from math import sqrt
import utm

class Drone:

    # client = currently connected airsim multirotor client
    # sensorSpots = list of positions (Vector3r) audio listening sensors relative to center of the drone
    # vehicleName = vehicle name (should match name according to client)
    # shouldSpawn = whether this vehicle should be spawned here in the script (used if not new vehicle defined in settings)
    # spawnPosition = where to spawn (used if shouldSpawn)
    def __init__(self, client : airsim.MultirotorClient, sensorSpots = [], vehicleName = '', shouldSpawn = False, spawnPosition = Vector3r(0, 0, 0), pawn_path = ""):
        self.client = client
        self.vehicleName = vehicleName
        self.sensorSpots = sensorSpots
        self.speed_of_sound_mps = 343
        if(shouldSpawn):
            self.client.simAddVehicle(self.vehicleName, "simpleflight", airsim.Pose(spawnPosition), pawn_path=pawn_path)

        self.startingPosition = spawnPosition

        self.resetStartingAltitude()

    def resetStartingAltitude(self):
        self.starting_altitude = self.client.getGpsData(vehicle_name=self.vehicleName).gnss.geo_point.altitude

    def getUTMPosition(self):
        geo_point = self.client.getGpsData(vehicle_name=self.vehicleName).gnss.geo_point
        utm_pos = utm.from_latlon(geo_point.latitude, geo_point.longitude)
        
        return Vector3r(utm_pos[0], utm_pos[1], geo_point.altitude - self.starting_altitude)

    def getWorldPosition(self):
        return self.client.getMultirotorState(self.vehicleName).kinematics_estimated.position + self.startingPosition
    
    def getSensorWorldPos(self):
        return [sensorSpot + self.getWorldPosition() for sensorSpot in self.sensorSpots]

    def simGetAudioTimes(self, soundEmitPoint : Vector3r):

        # calculating the time it would take to reach each sensor
        audioTimes = []
        
        for sensorSpot in self.getSensorWorldPos():
            dist = soundEmitPoint.distance_to(sensorSpot)
            time = dist / self.speed_of_sound_mps
            audioTimes.append(time)

        return audioTimes
    
    def moveToWorldPosition(self, position : airsim.Vector3r, velocity : float = 10, duration : float = 60):
        worldPosition = position - self.startingPosition
        return self.client.moveToPositionAsync(worldPosition.x_val, worldPosition.y_val, worldPosition.z_val, velocity, duration, vehicle_name=self.vehicleName)
    
    # DEPRECATED use version that can take any number of sensors. will be more useful for multi drone sensor readings
    # calculates approximate position of emitted audio based on time differences from each sensor when hearing the sound (works with 3 sensors)
    '''
    def calcSoundEmitPosition(self, audioTimes):
        
        if(len(audioTimes) != len(self.sensorSpots)):
            raise ValueError("The length of audioTimes should be the same as the length of sensor spots. (and directly correspond with indices)")

        # distances relative to sensor that heard the sound first
        relativeDists = []
        for i, audioTime in enumerate(audioTimes):
            relativeDists.append(audioTime * self.speed_of_sound_mps)
            if(audioTime == 0): # for algorithm below, reference sensor can be any one but I'm picking the one thats closest and hears the sound first
                referenceSensorId = i

        # for this algorithm see https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1145216

        # S_j in the paper. N-1x3 matrix of xyz coord of each sensor relative to reference sensor
        sensorOffsetsToReference = np.zeros((len(self.sensorSpots) - 1,3))

        # mew_j in the paper. I don't have an intuitive understanding/name for this. 
        # Also in the paper the definition of this is slightly misprinted, all values need to be squared
        mew = np.zeros(len(self.sensorSpots) - 1) 

        # rho_j in the paper. Vector of the range differences between each sensor and reference sensor. 
        # Since the chosen reference sensor has relativeDist 0 as defined above, this is just the relativeDists array
        rangeDifferences = np.zeros(len(self.sensorSpots) - 1)
        
        referenceSensorPos = self.sensorSpots[referenceSensorId]

        for j, sensorSpot in enumerate(self.sensorSpots):
            if(j == referenceSensorId):
                continue

            rowj = j if j < referenceSensorId else j-1 # lets us skip the reference sensor row in the following matrices
            
            sensorOffsetsToReference[rowj] = np.array(
                (sensorSpot.x_val - referenceSensorPos.x_val,
                sensorSpot.y_val - referenceSensorPos.y_val,
                sensorSpot.z_val - referenceSensorPos.z_val)
            )
            trueSensorSpot = sensorSpot + self.simGetPosition() # TODO fix because this only works in sim
            mew[rowj] = (trueSensorSpot.get_length()**2 - (referenceSensorPos + self.simGetPosition()).get_length()**2 - relativeDists[j]**2)/2 
            rangeDifferences[rowj] = relativeDists[j]


        # M_j in the paper. called distance remover because this is multiplied by rho_j to always get 0 and 
        # this removes R_j_s (dist from reference sensor to source, which is what we want to find) from the equation.
        # leaving x_s (position of source) as the only unknown
        circularShift = np.roll(np.identity(len(self.sensorSpots) - 1), (1, 0), axis=(1, 0))
        d_j = np.linalg.inv(np.diag(rangeDifferences))
        distanceRemover = np.matmul((np.identity(len(self.sensorSpots) - 1) - (circularShift)), d_j)
        
        # compute position of source X_s
        first_term = np.matmul(np.matmul(np.matmul(np.transpose(sensorOffsetsToReference), np.transpose(distanceRemover)), distanceRemover), sensorOffsetsToReference)
        x_source = np.matmul(np.matmul(np.matmul(np.matmul(np.linalg.inv(first_term), np.transpose(sensorOffsetsToReference)), np.transpose(distanceRemover)), distanceRemover), mew)

        return Vector3r(x_source[0], x_source[1], x_source[2])'
        '''