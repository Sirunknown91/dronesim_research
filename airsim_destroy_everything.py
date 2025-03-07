
import airsim

# deletes all environment objects in blocks
def destroyBlocksStuff(client : airsim.MultirotorClient):
    all_objects = client.simListSceneObjects("Ground.*") 
    all_objects += client.simListSceneObjects("Template.*")
    all_objects += client.simListSceneObjects("Cylinder.*")
    all_objects += client.simListSceneObjects("Orange.*")
    all_objects += client.simListSceneObjects("Cone.*")

    [client.simDestroyObject(obj) for obj in all_objects]



if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    all_objects = client.simListSceneObjects("Ground.*")

    [client.simDestroyObject(obj) if obj != "Ground_2" else '' for obj in all_objects]