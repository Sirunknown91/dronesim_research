import airsim
import airsim_keyboard_controller
import airsim_texture_replacement
import airsim_list_all_objects
import airsim_destroy_everything
import airsim_find_gunshot
import airsim_splitscreen
from airsim_drone import Drone
import os
import time

# relevant documentation: https://microsoft.github.io/AirSim/apis/

testImagePaths = {"testimage1":"C:\\Users\\sirun\\Documents\\grad school stuff\\Research Assistant Work\\dronesim_research\\sat_testimage_4.png"}

# takes the provided-by-airsim blocks map and converts it to custom satellite image map. (dont use if already have custom stuff)
def reworkBlocksScene(client):
    # delay a bit and wait for airsim to set some things up
    client.simPrintLogMessage("Setting Up: ", "In Progress")
    time.sleep(0.5) 

    # preparing environment

    #airsim_list_all_objects.printAllObjects(client)

    airsim_destroy_everything.destroyBlocksStuff(client)

    scale_factor_x = 5e2
    scale_factor_y = 2.5e2
    scale = airsim.Vector3r(scale_factor_x * 100, scale_factor_y * 100, 1.0)

    asset_name = 'S_1_Unit_Plane'

    for i in range(-1, 2):
        for j in range(-1, 2):

            pose = airsim.Pose(position_val=airsim.Vector3r(scale_factor_x * i, scale_factor_y * j, 3.0))
            
            obj_name = client.simSpawnObject(f"sat_image_plane_{i}_{j}", asset_name, pose, scale, physics_enabled=False)
            airsim_texture_replacement.textureReplace(client, obj_name, testImagePaths["testimage1"])

    #print(f"Created object {obj_name} from asset {asset_name} at pose {pose}, scale {scale}")

    # destroys everything a second time because ??? dark magic lets blocks survive sometimes
    airsim_destroy_everything.destroyBlocksStuff(client)

    client.simPrintLogMessage("Setting Up: ", "Done!")

def launchAirsim():
    # starting airsim
    os.system("MarsPlaneDroneSim\\WindowsNoEditor\\run.bat")

    # delay a bit and wait for airsim to launch
    #time.sleep(1) 

    # creating client
    client = airsim.MultirotorClient()
    client.confirmConnection()

    #fix screen tearing
    client.simRunConsoleCommand("r.vsync 1")
    
    
    mainDrone = Drone(client, vehicleName="MainDrone")
    controller = airsim_keyboard_controller.DroneKeyboardController(mainDrone, {})

    client.enableApiControl(True, mainDrone.vehicleName)

    while True:
        controller.process()

if __name__ == '__main__':
    launchAirsim()