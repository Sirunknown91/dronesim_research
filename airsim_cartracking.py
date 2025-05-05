import airsim_splitscreen
import airsim_keyboard_controller
from airsim_drone import Drone
import airsim
import keyboard
import cv2
import os
import time
import ultralytics
from ultralytics import YOLO

# demonstrates tracking cars
def tracking_demo(client : airsim.MultirotorClient):

    time.sleep(1) # delay a bit so things get set up properly
    mainDrone = Drone(client, vehicleName="MainDrone")

    airsim_splitscreen.simSplitScreen(client)
    
    airsim_splitscreen.simSetFutureCameraOffset(client, -300, 0, 250)
    airsim_splitscreen.simAttachCameraToDrone(client, droneName=mainDrone.vehicleName, cameraName="LeftScreenCapture")
    
    model = YOLO("yolo11s.pt")

    while True:

        # image processing for right side screen capture
        raw_image = client.simGetImage(camera_name="bottom_center", image_type=airsim.ImageType.Scene, vehicle_name=mainDrone.vehicleName)

        image = cv2.imdecode(airsim.string_to_uint8_array(raw_image), cv2.IMREAD_COLOR)

        try:    
            # sent image to model
            results = model.predict(image)
            result = results[0]

            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                class_id = box.cls[0].item()
                conf = box.conf[0].item()

                somewhat_light_red = (50, 50, 255)

                detection_name = result.names[class_id]

                display_text = f"{detection_name}. ({round(conf*100, 1)}%)"

                image = cv2.putText(img=image, text=display_text, org=(int(x1), int(y1 - 10)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.3, color=somewhat_light_red)
                image = cv2.rectangle(img=image, pt1=(int(x1), int(y1)), pt2=(int(x2), int(y2)), color=somewhat_light_red, thickness=1)
        
        except Exception as e:
            print(f"Error during model usage: {e}")
        

        # padding image so it is not stretched in split screen view
        #image = cv2.copyMakeBorder(image, 66, 66, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        # adding stuff for display
        image = cv2.resize(image, (512, 564))

        # save image to file
        img_path = "demo_image.png"
        cv2.imwrite(img_path, image)

        # displaying image (needs to get image from file, which is why we have to save it above)
        dir_path = os.path.dirname(os.path.realpath(__file__))

        absolute_img_path = dir_path + "\\" + img_path

        airsim_splitscreen.simSetSplitScreenToImageFile(client, absolute_img_path, rightSide=True)

        # disable script
        if(keyboard.is_pressed('esc')):
            break
        
        time.sleep(0.1)
        

if __name__ == "__main__":
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    tracking_demo(client)