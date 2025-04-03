import airsim
import cv2
import keyboard
import time
import numpy

def viewLoop(client : airsim.MultirotorClient):
    while True:
        rawBottomImage = client.simGetImage("bottom_center", airsim.ImageType.Scene, vehicle_name="MainDrone")
        rawBottomImage2 = client.simGetImage("bottom_center", airsim.ImageType.Scene, vehicle_name="Drone2")

        rawImages = [rawBottomImage, rawBottomImage2]

        pngs = [cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_COLOR) for rawImage in rawImages]

        pngs = [cv2.resize(png, (256, 256)) for png in pngs]

        combinedPng = numpy.concatenate(pngs, axis = 0)

        cv2.imshow("Combined", combinedPng)

        key = cv2.waitKey(1)
        if(key == 27 or keyboard.is_pressed('esc')):
            break

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    viewLoop(client)