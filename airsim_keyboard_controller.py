import airsim
import time
import keyboard

# relevant documentation: https://microsoft.github.io/AirSim/apis/

# Controls the drone with your keyboard

def saveImage():
    global client
    #cameras: 0-2 forward, 3 downward, 4+ ???
    png_image = client.simGetImage("3", airsim.ImageType.Scene)

    with open("test_image.png", 'wb') as imgfile:
        imgfile.write(png_image)

def controlDroneLoop():
    client.enableApiControl(True)

    print("Should be connected")

    imageTaken = False

    while True:
        # getting flight direction based on keyboard input
        vel = [0, 0, 0]
        
        # vertical movement
        if(keyboard.is_pressed('space')):
            vel[2] += -10
        if(keyboard.is_pressed(',')):
            vel[2] += 10

        # north dim movement
        if(keyboard.is_pressed('w')):
            vel[0] += 10
        if(keyboard.is_pressed('s')):
            vel[0] += -10

        # east dim movement
        if(keyboard.is_pressed('d')):
            vel[1] += 10
        if(keyboard.is_pressed('a')):
            vel[1] += -10

        client.simPrintLogMessage("Input velocity: ", ", ".join([str(v) for v in vel]))

        if(keyboard.is_pressed('.') and not imageTaken):
            imageTaken = True
            saveImage()
        
        #makes sure image is only take once per press of . instead of once per frame while holding .
        if(not keyboard.is_pressed('.')):
            imageTaken = False
            
        # telling the sim drone to fly
        client.moveByVelocityAsync(*vel, 0.1).join()
        
        # break loop if client closes (or atleast it should)
        if(not client.ping()):
            break

        # disable script
        if(keyboard.is_pressed('esc')):
            break

        
    print("Done")
    client.enableApiControl(False)


if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    controlDroneLoop()