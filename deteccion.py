import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import time
import requests

# Load YOLO model
model = YOLO("yolov8n.pt")  # Usa tu modelo adecuado

# Open video file
cap = cv2.VideoCapture("D:/IA_VehicleClassifier-CNN/Data/video3.mp4")
assert cap.isOpened(), "Error reading video file"

cv2.namedWindow("Vehicle Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Vehicle Detection", 500, 700)

# Get video properties
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("vehicle_detection.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# API endpoint to send vehicle data
API_URL = "http://localhost:8000/vehiculos"

# Define lane divider (center of the road)
lane_divider = w // 2

# Define horizontal lines
line_top = 520
line_bottom = 1200

# Distance between lines in meters
distance_meters = 15.0

# Trackers
vehicle_tracks = defaultdict(list)
lane_changes = set()
vehicle_ids = {}
timestamps_top = {}
timestamps_bottom = {}
next_id = 0

frame_count = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_count += 1

    results = model(frame)[0]

    for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
        x1, y1, x2, y2 = map(int, box[:4])
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # Determine current lane
        current_lane = "Left" if center_x < lane_divider else "Right"

        # Get vehicle type
        class_id = int(cls)
        vehicle_type = model.names[class_id]

        # Assign ID
        vehicle_id = None
        for id, (x, y) in vehicle_ids.items():
            if abs(center_x - x) < 50 and abs(center_y - y) < 50:
                vehicle_id = id
                break

        if vehicle_id is None:
            vehicle_id = next_id
            next_id += 1

        vehicle_ids[vehicle_id] = (center_x, center_y)

        # Track lane changes
        previous_lanes = vehicle_tracks[vehicle_id]
        if previous_lanes and previous_lanes[-1] != current_lane:
            lane_changes.add(vehicle_id)

        vehicle_tracks[vehicle_id].append(current_lane)

        # Timestamp when crossing lines
        if line_top - 10 < center_y < line_top + 10 and vehicle_id not in timestamps_top:
            timestamps_top[vehicle_id] = time.time()

        if line_bottom - 10 < center_y < line_bottom + 10 and vehicle_id not in timestamps_bottom:
            timestamps_bottom[vehicle_id] = time.time()

            # Calculate speed
            t1 = timestamps_top.get(vehicle_id)
            t2 = timestamps_bottom.get(vehicle_id)

            if t1 and t2:
                time_diff = t2 - t1
                if time_diff > 0:
                    speed_m_s = distance_meters / time_diff
                    speed_kmh = speed_m_s * 3.6

                    # Prepare data to send
                    vehiculo_data = {
                        "id": vehicle_id,
                        "tipo": vehicle_type,
                        "carril": current_lane,
                        "velocidad": round(speed_kmh, 2),
                        "cambio_carril": vehicle_id in lane_changes
                    }

                    try:
                        requests.post(API_URL, json=vehiculo_data)
                        print(f"Data sent: {vehiculo_data}")
                    except Exception as e:
                        print(f"Failed to send data: {e}")

        # Draw bounding box
        color = (0, 255, 0) if vehicle_id in lane_changes else (255, 0, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        label = f"ID: {vehicle_id} | {vehicle_type} | {current_lane}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Draw lines
    cv2.line(frame, (lane_divider, 0), (lane_divider, h), (0, 255, 255), 2)
    cv2.line(frame, (0, line_top), (w, line_top), (255, 0, 255), 2)
    cv2.line(frame, (0, line_bottom), (w, line_bottom), (255, 0, 255), 2)

    # Display frame
    cv2.imshow("Vehicle Detection", frame)
    video_writer.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()
