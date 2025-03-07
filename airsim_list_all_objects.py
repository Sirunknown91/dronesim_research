import airsim

# prints a list of every object in the scene
def printAllObjects(client : airsim.MultirotorClient):
    print("\n---EVERY OBJECT IN CURRENT AIRSIM CLIENT---\n")
    all_objects = client.simListSceneObjects()
    [print(name) for name in all_objects]
    print("\n-\n")

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    printAllObjects(client)