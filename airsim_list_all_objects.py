import airsim

# prints a list of every object in the scene
def printAllObjects(client : airsim.MultirotorClient):
    print("\n---EVERY OBJECT IN CURRENT AIRSIM CLIENT---\n")
    all_objects = client.simListSceneObjects()
    all_objects.sort()
    [print(name) for name in all_objects]
    print("\n-\n")

def printAllAvailAssets(client : airsim.MultirotorClient):
    print("\n---EVERY ASSET AVAILABLE TO CURRENT AIRSIM CLIENT---\n")
    all_objects = client.simListAssets()
    all_objects.sort()
    [print(name) for name in all_objects]
    print("\n-\n")

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    printAllObjects(client)