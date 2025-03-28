import airsim

def list_scene_objects(client: airsim.MultirotorClient):
    """List all objects in the scene"""
    objects = client.simListSceneObjects()
    print("Objects in the scene:")
    for obj in objects:
        print(f"- {obj}")
    return objects

def textureReplace(client: airsim.MultirotorClient, obj_name: str, path: str):
    """Replace the texture of a specified object"""
    try:
        client.simSetObjectMaterialFromTexture(obj_name, path)
        print(f"Successfully replaced texture for object {obj_name}")
    except Exception as e:
        print(f"Error replacing texture for object {obj_name}: {str(e)}")

def replace_all_ground_textures(client: airsim.MultirotorClient, texture_path: str):
    """Replace textures for all ground objects"""
    # List all objects
    objects = list_scene_objects(client)
    
    # Find all possible ground objects (based on naming conventions)
    ground_objects = [obj for obj in objects if any(keyword in obj.lower() 
                     for keyword in ['ground', 'plane', 'terrain', 'floor', 'sat'])]
    
    if not ground_objects:
        print("No potential ground objects found")
        return
    
    print(f"Found {len(ground_objects)} potential ground objects:")
    for obj in ground_objects:
        print(f"- {obj}")
        textureReplace(client, obj, texture_path)

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    testImagePath = r"C:\Users\zrinf\OneDrive\Desktop\TEST_SET.4.png"
    
    # Replace textures for all ground objects
    replace_all_ground_textures(client, testImagePath)