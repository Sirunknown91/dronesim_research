import airsim
import time
from threading import Thread

def simSpawnGunshot(client : airsim.MultirotorClient, pos):
    pose = airsim.Pose(position_val=pos)
    scale = airsim.Vector3r(1, 1, 1)
    new_light_name = client.simSpawnObject("GunshotLight", "GunshotLightBase2", pose, scale, False, True)
    print("spawned gunshot")
    time.sleep(.1)
    client.simDestroyObject(new_light_name)

    dronePose = client.simGetVehiclePose()
    dist = pose.position.distance_to(dronePose.position)
    
    soundTime = dist/343
    client.simPrintLogMessage(f"Spawned gunshot!", f"   Distance: {round(dist,2)} meters away. Should play sound after {round(soundTime,2)} seconds")
    time.sleep(soundTime)
    print(f"bang!")

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    for i in range(100):
        dronePose = client.simGetVehiclePose()
        gunshotPos = airsim.Vector3r(dronePose.position.x_val, dronePose.position.y_val, -3)
        
        simSpawnGunshot(client, gunshotPos)
        time.sleep(2)