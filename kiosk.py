import cv2
import os
import subprocess
import threading
import time
import platform

# Set up paths (cross-platform)
video_path = os.path.join("videos", "welcome.mp4")
cascade_path = os.path.join("haarcascades", "haarcascade_frontalface_default.xml")
spa_url = "https://www.google.com"  # Replace with your spa website URL later

# A flag to tell us when a face is detected
face_detected = False

# Function to detect faces using the webcam
def detect_faces():
    global face_detected
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam!")
        return
    
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("Error: Could not load Haar cascade file!")
        return

    while not face_detected:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from webcam!")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) > 0:
            print("Face detected!")
            face_detected = True
            break
        
        time.sleep(0.1)
    
    cap.release()

# Main program
print("Starting video playback...")
if platform.system() == "Windows":
    vlc_process = subprocess.Popen([r"C:\Program Files\VideoLAN\VLC\vlc.exe", "--loop", "--fullscreen", video_path])
else:
    vlc_process = subprocess.Popen(["vlc", "--loop", "--fullscreen", video_path])

print("Starting face detection...")
face_thread = threading.Thread(target=detect_faces)
face_thread.start()

while not face_detected:
    time.sleep(1)

vlc_process.terminate()
print("Video stopped. Showing spa menu...")

if platform.system() == "Windows":
    subprocess.run(["start", "chrome", "--kiosk", spa_url], shell=True)
else:
    subprocess.run(["chromium-browser", "--kiosk", spa_url])