# This file provides functions for interacting with the custom mini map system.

import airsim
import math
from airsim_drone import Drone
from typing import List

# Shows the minimap
def simShowMinimap(client : airsim.MultirotorClient):
    client.simRunConsoleCommand("ce AddMinimap")

# Hides the minimap
def simHideMinimap(client : airsim.MultirotorClient):
    client.simRunConsoleCommand("ce RemoveMinimap")

# Sets follow target for minimap
def simSetMinimapFollowTarget(client : airsim.MultirotorClient, droneName : str):
    client.simRunConsoleCommand(f"ce SetMinimapFollowTarget {droneName}")

# Sets width for minimap (default is 5000 unreal units which is 50 airsim units which is about 50 meters (but of course the satellite image isnt lined up 1 to 1))
def simSetMinimapWidth(client : airsim.MultirotorClient, width : float):
    client.simRunConsoleCommand(f"ce SetMinimapWidth {width}")

# Automatically sets minimap size to the size to keep all drones in.
def simUpdateMinimapWidthToKeepDronesVis(client : airsim.MultirotorClient, drones : List[Drone], follow_drone : Drone, buffer = 1000):
    max_dist = 0
    
    drone1Pos = follow_drone.getWorldPosition()
    drone1Pos.z_val = 0
    for drone in drones:
        drone2Pos = drone.getWorldPosition()
        drone2Pos.z_val = 0
        dist = drone2Pos.distance_to(drone1Pos) * 100 # multiply by 100 to convert to unreal engine units
        if(dist > max_dist):
            max_dist = dist

    simSetMinimapWidth(client, (max_dist + buffer) * 2)

if __name__ == "__main__":
    client = airsim.MultirotorClient()
    client.confirmConnection()

    # minimap demonstration
    client.simRunConsoleCommand("DisableAllScreenMessages")
    simShowMinimap(client)
    simSetMinimapFollowTarget(client, "MainDrone")

    