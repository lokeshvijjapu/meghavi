import cv2
import os
import numpy as np

base_dir = r"C:\Users\lokes\OneDrive\Desktop\meghavi\meghavi"
model_path = os.path.join(base_dir, "dnn_model", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
config_path = os.path.join(base_dir, "dnn_model", "deploy.prototxt")
net = cv2.dnn.readNetFromCaffe(config_path, model_path)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x2, y2) = box.astype("int")
            face_width = x2 - x
            print(f"Face width: {face_width} pixels")
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
    cv2.imshow('Calibration', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()