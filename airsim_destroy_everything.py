
import airsim

# deletes some objects

client = airsim.MultirotorClient()
client.confirmConnection()

all_objects = client.simListSceneObjects("Ground.*")

[client.simDestroyObject(obj) if obj != "Ground_2" else '' for obj in all_objects]