# This file provides functions for interacting with the custom mini map system.


import airsim
import math

# Shows the minimap
def simShowMinimap(client : airsim.MultirotorClient):
    client.simRunConsoleCommand("ce AddMinimap")

# Sets follow target for minimap
def simSetMinimapFollowTarget(client : airsim.MultirotorClient, droneName : str):
    client.simRunConsoleCommand(f"ce SetMinimapFollowTarget {droneName}")

# Sets width for minimap (default is 5000 unreal units which is 50 airsim units which is about 50 meters (but of course the satellite image isnt lined up 1 to 1))
def simSetMinimapWidth(client : airsim.MultirotorClient, width : float):
    client.simRunConsoleCommand(f"ce SetMinimapWidth {width}")

if __name__ == "__main__":
    client = airsim.MultirotorClient()
    client.confirmConnection()

    # minimap demonstration
    simShowMinimap(client)
    simSetMinimapFollowTarget(client, "MainDrone")

    