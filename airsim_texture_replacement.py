import airsim

# Replaces a specified object's texture (requires absolute path to image file)
def textureReplace(client : airsim.MultirotorClient, obj_name : str, path : str):
    client.simSetObjectMaterialFromTexture(obj_name, path)

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    testImagePath = "C:\\Users\\sirun\\Downloads\\map_output.png"
    test2 = "test_image.png"
    
    textureReplace(client, "VariableSatImagePlane_1", testImagePath)