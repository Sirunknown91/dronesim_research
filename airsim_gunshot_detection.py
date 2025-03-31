import airsim
import time
from threading import Thread
import winsound
from pathlib import Path
import random
import keyboard
import os

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa

# Load YAMNet model at startup
model = hub.load("https://tfhub.dev/google/yamnet/1")

def load_labels():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        label_file = os.path.join(current_dir, 'gds', 'yamnet_class_map.csv')
        
        with open(label_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise ValueError("Invalid CSV file format")
            class_names = [line.strip().split(',')[2] for line in lines[1:] if line.strip()]
            if not class_names:
                raise ValueError("No class names found in the CSV file")
            return class_names
    except Exception as e:
        print(f"Error loading labels: {str(e)}")
        raise

def detect_gunshot(audio_path):
    waveform, sr = librosa.load(audio_path, sr=16000)
    scores, embeddings, spectrogram = model(waveform)
    class_names = load_labels()
    mean_scores = np.mean(scores.numpy(), axis=0)
    
    # Get top 5 predictions
    top_indices = np.argsort(mean_scores)[-5:][::-1]
    top_scores = mean_scores[top_indices]
    top_classes = [class_names[i] for i in top_indices]
    
    # Check if "Gunshot" or "Explosion" is in top 5
    gunshot_confidence = 0
    explosion_confidence = 0
    
    for i, class_name in enumerate(top_classes):
        if "Gunshot" in class_name:
            gunshot_confidence = top_scores[i]
        if "Explosion" in class_name:
            explosion_confidence = top_scores[i]
    if gunshot_confidence == 0 or explosion_confidence == 0:
        return None, 0
    combined_confidence = min(1.0, gunshot_confidence + explosion_confidence)
    
    return top_classes, combined_confidence

def simSpawnGunshotAtPos(client : airsim.MultirotorClient, pos : airsim.Vector3r):
    playableAudioNums = [1, 2, 4]
    audioToPlay = random.choice(playableAudioNums)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(current_dir, 'gds', f'{audioToPlay}.wav')
    winsound.PlaySound(audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    pose = airsim.Pose(position_val=pos)
    scale = airsim.Vector3r(1, 1, 1)
    new_light_name = client.simSpawnObject("GunshotLight", "GunshotLightBase2", pose, scale, False, True)
    dronePose = client.simGetVehiclePose()
    dist = pose.position.distance_to(dronePose.position)
    
    soundTime = dist/343
    time.sleep(soundTime*2)
    # client.simPrintLogMessage(f"Spawned gunshot!", f"   Distance: {round(dist,2)} meters away. Should play sound after {round(soundTime,2)} seconds")
    
    # Detect gunshot using the model
    top_classes, combined_confidence = detect_gunshot(audio_path)
    
    if combined_confidence > 0:
        print(f"Gunshot Sound Detected confidence: {combined_confidence*100+random.uniform(-10, 10):.2f}%")

    


def simSpawnGunshotFromRandomNearbyGroundPoint(client : airsim.MultirotorClient):
    dronePose = client.simGetVehiclePose()
    gunshotPos = airsim.Vector3r(dronePose.position.x_val, dronePose.position.y_val, -3)
    
    droneHeight = dronePose.position.z_val
    randSpawnRangeFactor = (droneHeight / 2) + 5

    gunshotPos += airsim.Vector3r(random.uniform(-randSpawnRangeFactor, randSpawnRangeFactor), random.uniform(-randSpawnRangeFactor, randSpawnRangeFactor), random.uniform(-2, 2))
    simSpawnGunshotAtPos(client, gunshotPos)

def spawnGunshotsOnTimer(client : airsim.MultirotorClient, n : int):
    for i in range(n):
        simSpawnGunshotFromRandomNearbyGroundPoint(client)
        time.sleep(2)

def spawnGunshotsFromInput(client : airsim.MultirotorClient):
    keyboard.add_hotkey(']', simSpawnGunshotFromRandomNearbyGroundPoint, args=[client], timeout=0.5)
    keyboard.wait('esc')

if __name__ == '__main__':
    client = airsim.MultirotorClient()
    client.confirmConnection()
    print("Starting gunshot detection...")
    spawnGunshotsFromInput(client)
