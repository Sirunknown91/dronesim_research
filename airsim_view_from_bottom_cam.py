import airsim
import cv2
import keyboard
import time

def viewLoop(client):
    while True:
        rawImage = client.simGetImage("bottom_center", airsim.ImageType.Scene)

        png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
        #cv2.putText(png,'FPS ' + str(fps),textOrg, fontFace, fontScale,(255,0,255),thickness)
        cv2.imshow("Depth", png)

        time.sleep(2)

        if(keyboard.is_pressed('esc')):
            break

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    viewLoop(client)