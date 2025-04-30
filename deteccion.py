import cv2
import numpy as np
from ultralytics import YOLO
import time
import requests

# Load YOLO model with tracking capabilities
model = YOLO("yolov8n.pt")

# Video setup
cap = cv2.VideoCapture("D:/IA_VehicleClassifier-CNN/Data/video4.mp4")
assert cap.isOpened(), "Error reading video file"

# Window setup
cv2.namedWindow("Vehicle Tracking", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Vehicle Tracking", 800, 600)

# Get video properties
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("vehicle_tracking_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# API configuration
API_URL = "http://localhost:8000/vehiculos"
HEADERS = {"Content-Type": "application/json"}

# Configuration
pixels_to_meters = 0.05
known_width_m = 2.5
lane_divider = w // 2  # For lane determination

# Tracking variables
vehicle_history = {}
vehicle_speeds = {}
lane_history = {}  # Track lane positions for each vehicle
frame_count = 0
last_api_send = {}

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_count += 1
    current_time = time.time()

    # Run tracking
    results = model.track(frame, persist=True, tracker="bytetrack.yaml")

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy()

        for box, cls, track_id in zip(boxes, classes, track_ids):
            x1, y1, x2, y2 = map(int, box)
            track_id = int(track_id)
            class_name = model.names[int(cls)]
            center_x = (x1 + x2) // 2
            
            # Determine current lane
            current_lane = "Left" if center_x < lane_divider else "Right"
            
            # Initialize lane history
            if track_id not in lane_history:
                lane_history[track_id] = []
            
            # Check for lane changes
            lane_changed = False
            if lane_history[track_id] and lane_history[track_id][-1] != current_lane:
                lane_changed = True
            
            lane_history[track_id].append(current_lane)
            if len(lane_history[track_id]) > 5:
                lane_history[track_id].pop(0)

            # Calculate center and width
            center_y = (y1 + y2) // 2
            width_px = x2 - x1

            # Initialize new vehicle
            if track_id not in vehicle_history:
                vehicle_history[track_id] = {
                    'positions': [(center_x, center_y, current_time)],
                    'class': class_name,
                    'speed': 0.0
                }
                continue

            # Only process if we have previous positions
            prev_positions = vehicle_history[track_id]['positions']
            if not prev_positions:
                continue

            last_x, last_y, last_time = prev_positions[-1]
            time_diff = current_time - last_time

            # Only calculate speed if sufficient time has passed
            if time_diff > 0.1:
                # Calculate movement
                dx = center_x - last_x
                dy = center_y - last_y
                distance_px = np.sqrt(dx**2 + dy**2)
                
                # Dynamic pixel-to-meter conversion
                current_pixels_to_meters = known_width_m / width_px if width_px > 0 else pixels_to_meters
                distance_m = distance_px * current_pixels_to_meters
                
                # Calculate speed
                speed_m_s = distance_m / time_diff
                speed_kmh = speed_m_s * 3.6
                vehicle_speeds[track_id] = speed_kmh
                vehicle_history[track_id]['speed'] = speed_kmh

                # Prepare data for API (only send updates every 1 second)
                if track_id not in last_api_send or (current_time - last_api_send[track_id]) > 1.0:
                    vehicle_data = {
                        "id": track_id,
                        "tipo": class_name,
                        "velocidad": float(round(speed_kmh, 2)),  # Convert numpy.float64 to native float
                        "timestamp": current_time,
                        "carril": current_lane,
                        "cambio_carril": lane_changed
                    }

                    try:
                        response = requests.post(
                            API_URL, 
                            json=vehicle_data,
                            headers=HEADERS,
                            timeout=2.0
                        )
                        if response.status_code == 200:
                            print(f"Successfully sent data for vehicle {track_id}")
                            last_api_send[track_id] = current_time
                        else:
                            print(f"API error: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"Request failed: {str(e)}")

            # Update position history
            prev_positions.append((center_x, center_y, current_time))
            if len(prev_positions) > 5:
                prev_positions.pop(0)

            # Visualization
            color = (0, 255, 0) if not lane_changed else (0, 0, 255)  # Red if lane changed
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            speed_text = f"{vehicle_history[track_id]['speed']:.1f} km/h" if track_id in vehicle_speeds else "Calculating..."
            lane_text = f"Lane: {current_lane}" + (" (changed)" if lane_changed else "")
            label = f"ID:{track_id} {class_name} {speed_text} {lane_text}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Draw lane divider
    cv2.line(frame, (lane_divider, 0), (lane_divider, h), (0, 255, 255), 2)

    # Display frame
    cv2.imshow("Vehicle Tracking", frame)
    video_writer.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()