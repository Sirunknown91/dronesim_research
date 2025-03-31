import airsim

# Replaces a specified object's texture (requires absolute path to image file)
def textureReplace(client : airsim.MultirotorClient, obj_name : str, path : str):
    client.simSetObjectMaterialFromTexture(obj_name, path)

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    testImagePath = "C:\\Users\\sirun\\Documents\\grad school stuff\\Research Assistant Work\\dronesim_research\\sat_testimage_4.png"
    
    textureReplace(client, "VariableSatImagePlane_1", testImagePath)