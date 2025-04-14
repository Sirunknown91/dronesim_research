import airsim

# Replaces a specified object's texture (requires absolute path to image file)
def textureReplacePath(client : airsim.MultirotorClient, obj_name : str, path : str):
    client.simSetObjectMaterialFromTexture(obj_name, path)

def textureReplace(client: airsim.MultirotorClient, obj_tag : str, tex_id : int):
    print(client.simSwapTextures(obj_tag, tex_id))

# Resizes the texture of an object using U and V tiling. 
def textureResize(client: airsim.MultirotorClient, obj_name : str, uTiling: float, vTiling : float):
    client.simRunConsoleCommand(f"ce SetObjectMaterialTiling {obj_name} {uTiling} {vTiling}")

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    #testImagePath = "C:\\Users\\sirun\\Documents\\grad school stuff\\Research Assistant Work\\dronesim_research\\sat_testimage_4.png"
    
    # textureReplace(client, "plane", 3)
    # textureReplace(client, "plane2", 7)
    textureReplacePath(client, obj_name="VariableSatImagePlane", path="C:\\Users\\sirun\\Documents\\grad school stuff\\Research Assistant Work\\dronesim_research\\map_output.png")