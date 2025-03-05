import airsim

# Replaces a specified object's texture (requires absolute path to image file)

def textureReplace(obj_name, path):
    client.simSetObjectMaterialFromTexture(obj_name, path)


if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()

    test_obj_name1 = 'TemplateCube_Rounded_138'
    test_obj_name2 = 'TemplateCube_Rounded_150'
    ground_name = 'Ground_2'

    testImagePath = "C:\\Users\\sirun\\Documents\\grad school stuff\\Research Assistant Work\\dronesim\\sat_testimage_4.png"
    
    textureReplace(test_obj_name2, testImagePath)