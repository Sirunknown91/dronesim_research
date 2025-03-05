
import airsim

# gets a list of every object in the scene

client = airsim.MultirotorClient()
client.confirmConnection()

def printAllObjects():
    all_objects = client.simListSceneObjects()
    [print(name) for name in all_objects]


if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    printAllObjects()