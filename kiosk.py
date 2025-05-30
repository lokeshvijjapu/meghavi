import cv2
import os
import subprocess
import threading
import time
import platform
import numpy as np

# Set up paths (cross-platform)
base_dir = r"C:\Users\lokes\OneDrive\Desktop\meghavi\meghavi"
video_path = os.path.join(base_dir, "videos", "welcome.mp4")
model_path = os.path.join(base_dir, "dnn_model", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
config_path = os.path.join(base_dir, "dnn_model", "deploy.prototxt")
spa_url = "https://meghavi-kiosk-outlet.onrender.com/#/shop/67e22caf39c9f87925bea576"  # Replace with your spa website URL later

# Rest of the code remains unchanged
# A flag to control video playback and face detection
face_detected = False

def detect_faces():
    global face_detected
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam!")
        return
    
    # Load DNN face detector
    try:
        net = cv2.dnn.readNetFromCaffe(config_path, model_path)
    except Exception as e:
        print(f"Error loading DNN model: {e}")
        return

    # Threshold for face width (in pixels) for ~1 meter distance
    distance_threshold = 130  # Adjust based on your calibration

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from webcam!")
            break
        
        # Prepare frame for DNN
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x, y, x2, y2) = box.astype("int")
                face_width = x2 - x
                faces.append((x, y, face_width, y2 - y))
        
        if len(faces) > 0:
            # Find the largest face by width
            largest_face_width = max([w for (x, y, w, h) in faces])
            print(f"Detected face width: {largest_face_width} pixels")
            if largest_face_width > distance_threshold and not face_detected:
                print("Face detected within 1 meter!")
                face_detected = True
        else:
            if face_detected:
                # Wait 5 seconds to confirm no face is detected
                print("No face detected, waiting 5 seconds...")
                no_face_start = time.time()
                while time.time() - no_face_start < 5:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
                    net.setInput(blob)
                    detections = net.forward()
                    faces = []
                    for i in range(detections.shape[2]):
                        confidence = detections[0, 0, i, 2]
                        if confidence > 0.5:
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (x, y, x2, y2) = box.astype("int")
                            face_width = x2 - x
                            faces.append((x, y, face_width, y2 - y))
                    if len(faces) > 0:
                        largest_face_width = max([w for (x, y, w, h) in faces])
                        if largest_face_width > distance_threshold:
                            print("Face re-detected within 5 seconds, staying on website!")
                            break
                    time.sleep(0.1)
                else:
                    # No face detected for 5 seconds, reset to video
                    print("No face for 5 seconds, returning to video playback...")
                    face_detected = False
        
        time.sleep(0.1)
    
    cap.release()

def main():
    global face_detected
    while True:
        if not face_detected:
            print("Starting video playback...")
            if platform.system() == "Windows":
                vlc_process = subprocess.Popen([r"C:\Program Files\VideoLAN\VLC\vlc.exe", "--loop", "--fullscreen", video_path])
            else:
                vlc_process = subprocess.Popen(["vlc", "--loop", "--fullscreen", video_path])
            # Wait until a face is detected
            while not face_detected:
                time.sleep(1)
            vlc_process.terminate()
            print("Video stopped. Showing spa menu...")
            if platform.system() == "Windows":
                subprocess.run(["start", "chrome", "--kiosk", spa_url], shell=True)
            else:
                subprocess.run(["chromium-browser", "--kiosk", spa_url])
        else:
            # Wait for face detection to signal no face
            time.sleep(1)
            if not face_detected:
                # Close browser when returning to video
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"], shell=True)
                else:
                    subprocess.run(["pkill", "chromium"], shell=True)

# Start face detection in a separate thread
print("Starting face detection...")
face_thread = threading.Thread(target=detect_faces)
face_thread.daemon = True  # Allow program to exit even if thread is running
face_thread.start()

# Run main loop
main()