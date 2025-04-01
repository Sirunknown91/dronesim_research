import airsim
import time
import os
from multiprocessing import Process, Event
# Connect to the AirSim simulator
bat_path = r"..\run.bat"
os.system(bat_path)
time.sleep(1) 
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

# Create results directory if it doesn't exist
results_dir = "./results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Move drone to a position and wait until it reaches there
def move_to_position(x, y, z, velocity=5):
    print(f"Moving to position: x={x}, y={y}, z={z}")
    client.moveToPositionAsync(x, y, z, velocity).join()
    time.sleep(1)  # Give some time to stabilize

# Main function to control the drone
def main():
    try:
        # Connect to AirSim
        client = airsim.MultirotorClient()
        client.confirmConnection()
        
        # Enable API control
        client.enableApiControl(True)
        
        print("Taking off...")
        client.takeoffAsync().join()
        
        try:
            stop_event = Event()
            
            # Create separate processes for target detection and keyboard control by directly calling the Python files
            detection_process = Process(target=os.system, args=("python key.py",))
            keyboard_process = Process(target=os.system, args=("python airsim_keyboard_controller.py",))
            
            # Start both processes
            detection_process.start()
            keyboard_process.start()
            
            # Wait for keyboard interrupt
            try:
                while detection_process.is_alive() and keyboard_process.is_alive():
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nReceived keyboard interrupt, stopping processes...")
                stop_event.set()
            
            # Wait for processes to finish
            detection_process.join(timeout=2.0)
            keyboard_process.join(timeout=2.0)
            
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt, stopping...")
        except Exception as e:
            print(f"Target detection error: {str(e)}")
        finally:
            # Ensure processes are terminated if they're still running
            if 'detection_process' in locals() and detection_process.is_alive():
                detection_process.terminate()
            if 'keyboard_process' in locals() and keyboard_process.is_alive():
                keyboard_process.terminate()
        
        # Cleanup
        print("Control released")
        client.enableApiControl(False)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
if __name__ == "__main__":
    main()
