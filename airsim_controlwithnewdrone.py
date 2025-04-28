import airsim
import airsim_keyboard_controller
from airsim_drone import Drone
import keyboard
import random

def launchNewDrone(client : airsim.MultirotorClient):
    names = client.listVehicles()

    index = 2
    name = f"Drone{index}"
    while name in names:
        index += 1
        name = f"Drone{index}"

    newDrone = Drone(client, vehicleName=name, shouldSpawn=True, spawnPosition=airsim.Vector3r(3 * index), pawn_path="QuadrotorAlt1")
    newDrone.changeColor(random.uniform(0, 1), random.uniform(0,1), random.uniform(0,1))

    client.enableApiControl(True, newDrone.vehicleName)

    controller = airsim_keyboard_controller.DroneKeyboardController(newDrone)

    while True:
        futures = controller.process()

        if(keyboard.is_pressed("esc")):
            break

        for future in futures: future.join()

if __name__ == '__main__':
    client = airsim.MultirotorClient() 
    client.confirmConnection()

    launchNewDrone(client)