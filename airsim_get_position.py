import airsim
import time

def get_drone_position():
    # Connect to the AirSim simulator
    client = airsim.MultirotorClient()
    
    # Confirm connection
    client.confirmConnection()
    
    # Get the drone's state
    state = client.getMultirotorState()
    
    # Extract position from the state
    position = state.kinematics_estimated.position
    
    # Print the position
    print(f"Drone Position:")
    print(f"X: {position.x_val:.2f} meters")
    print(f"Y: {position.y_val:.2f} meters")
    print(f"Z: {position.z_val:.2f} meters")
    
    return position

if __name__ == "__main__":
    try:
        while True:
            position = get_drone_position()
            time.sleep(5)  # Wait for 1 second before next reading
    except KeyboardInterrupt:
        print("\nStopping position monitoring...")
