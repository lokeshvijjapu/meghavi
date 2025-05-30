import cv2
import os
import subprocess
import threading
import time
import platform

# Set up paths (cross-platform)
video_path = os.path.join("videos", "welcome.mp4")
cascade_path = os.path.join("haarcascades", "haarcascade_frontalface_default.xml")
spa_url = "https://meghavi-kiosk-outlet.onrender.com/#/shop/67e22caf39c9f87925bea576"  # Replace with your spa website URL later

# A flag to control video playback and face detection
face_detected = False

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

    # Threshold for face width (in pixels) for ~1 meter distance
    distance_threshold = 150  # Adjust based on your calibration

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from webcam!")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) > 0:
            # Find the largest face by width
            largest_face_width = max([w for (x, y, w, h) in faces])
            print(f"Detected face width: {largest_face_width} pixels")
            if largest_face_width > distance_threshold:
                if not face_detected:
                    print("Face detected within 1 meter!")
                    face_detected = True
        else:
            if face_detected:
                print("No face detected, returning to video playback...")
                face_detected = False
        
        time.sleep(0.1)
    
    cap.release()

# Main program
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
            # Keep checking for no faces to resume video
            time.sleep(1)

# Start face detection in a separate thread
print("Starting face detection...")
face_thread = threading.Thread(target=detect_faces)
face_thread.daemon = True  # Allow program to exit even if thread is running
face_thread.start()

# Run main loop
main()