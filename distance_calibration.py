import cv2
import os

cascade_path = os.path.join("haarcascades", "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cascade_path)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            print(f"Face width: {w} pixels")
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow('Calibration', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()