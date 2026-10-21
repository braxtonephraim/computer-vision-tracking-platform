import serial
import time
import cv2
import math
from ultralytics import YOLO

# -----------------------------
# CONFIGURATION
# -----------------------------
ARDUINO_PORT = "COM3" 
BAUD_RATE = 9600
SEND_INTERVAL = 0.05   # Maximum 20 updates per second

MODEL_PATH = "yolo26n.pt"
CAMERA_INDEX = 0

CONFIDENCE_THRESHOLD = 0.45
IMAGE_SIZE = 416

# Maximum distance (pixels) between consecutive
# detections to associate them with the same target.
MAX_MATCH_DISTANCE = 120

# Number of frames to retain a lost target before
# allowing a new target to be selected.
MAX_LOST_FRAMES = 30


# INITIALIZE YOLO AI AND CAMERA


print("Loading tracking model...")
model = YOLO(MODEL_PATH)

camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():
    print("ERROR: Could not open laptop camera.")
    raise SystemExit

print("Person tracker started.")
print("Press Q to quit.")
print("Press R to reset target selection.")

# Target state
target_center = None
target_box = None
lost_frames = 0

arduino = serial.Serial(
    ARDUINO_PORT,
    BAUD_RATE,
    timeout=0.1,
    write_timeout=0.1
)

time.sleep(2)  # Allow Arduino to reset
arduino.reset_input_buffer()

last_send_time = 0
try:
    while True:
        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read camera frame.")
            break

        height, width = frame.shape[:2]

        image_center_x = width // 2
        image_center_y = height // 2

        # Detect objects in this frame
        results = model.predict(
            frame,
            imgsz=IMAGE_SIZE,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )

        # Collect detections belonging to the person class
        people = []

        for box in results[0].boxes:
            class_id = int(box.cls[0])

            # COCO class 0 = person
            if class_id != 0:
                continue

            x1, y1, x2, y2 = map(
                int, box.xyxy[0].tolist()
            )

            confidence = float(box.conf[0])

            person_center = (
                (x1 + x2) // 2,
                (y1 + y2) // 2
            )

            people.append({
                "box": (x1, y1, x2, y2),
                "center": person_center,
                "confidence": confidence
            })

        selected_person = None

        # ---------------------------------
        # SELECT OR REACQUIRE A TARGET
        # ---------------------------------

        if target_center is None:
            # Initially select the person closest
            # to the center of the camera image.
            if people:
                selected_person = min(
                    people,
                    key=lambda p: math.hypot(
                        p["center"][0] - image_center_x,
                        p["center"][1] - image_center_y
                    )
                )

        else:
            # Associate detections with the previous
            # target using its last known center.
            candidates = []

            for person in people:
                distance = math.hypot(
                    person["center"][0] - target_center[0],
                    person["center"][1] - target_center[1]
                )

                if distance <= MAX_MATCH_DISTANCE:
                    candidates.append((distance, person))

            if candidates:
                # Choose the closest matching detection.
                _, selected_person = min(
                    candidates,
                    key=lambda item: item[0]
                )

        # ---------------------------------
        # UPDATE TARGET STATE
        # ---------------------------------

        if selected_person is not None:
            target_center = selected_person["center"]
            target_box = selected_person["box"]
            lost_frames = 0

        elif target_center is not None:
            lost_frames += 1

            # Keep the target selection briefly if it
            # disappears, rather than switching instantly.
            if lost_frames > MAX_LOST_FRAMES:
                target_center = None
                target_box = None
                lost_frames = 0

        # ---------------------------------
        # DRAW IMAGE CENTER
        # ---------------------------------

        cv2.drawMarker(
            frame,
            (image_center_x, image_center_y),
            (255, 255, 255),
            cv2.MARKER_CROSS,
            22,
            2
        )

        cv2.putText(
            frame,
            "IMAGE CENTER",
            (image_center_x + 10, image_center_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        # ---------------------------------
        # DRAW SELECTED TARGET AND OFFSETS
        # ---------------------------------

        if selected_person is not None:
            x1, y1, x2, y2 = selected_person["box"]
            tx, ty = selected_person["center"]

            # Draw the selected person's bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Mark the target center
            cv2.circle(
                frame,
                (tx, ty),
                6,
                (0, 255, 0),
                -1
            )

            # Draw the offset from image center to target
            cv2.line(
                frame,
                (image_center_x, image_center_y),
                (tx, ty),
                (0, 255, 255),
                2
            )

        if target_center is not None and lost_frames == 0:
            offset_x = target_center[0] - image_center_x
            offset_y = target_center[1] - image_center_y
            now = time.monotonic()

            if now - last_send_time >= SEND_INTERVAL:
                message = f"TRACK,{offset_x},{offset_y}\n"
                arduino.write(message.encode("utf-8"))
                last_send_time = now
            status = "TRACKING PERSON"

            if arduino.in_waiting:
                response = arduino.readline().decode(
                    "utf-8", errors="replace"
                ).strip()

                if response:
                    print(response)

            cv2.putText(
                frame,
                status,
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"X offset: {offset_x:+d} px",
                (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Y offset: {offset_y:+d} px",
                (15, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Confidence: {selected_person['confidence']:.2f}",
                (15, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # Prepared for future Arduino integration:
            # offset_x and offset_y are the tracking errors.
            # No serial commands or servo movement yet.

        elif target_center is not None:
            cv2.putText(
                frame,
                f"TARGET LOST: {lost_frames}/{MAX_LOST_FRAMES}",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 165, 255),
                2
            )

        else:
            cv2.putText(
                frame,
                "SEARCHING FOR PERSON",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 165, 255),
                2
            )

        cv2.imshow("Turret Person Tracking", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord("r"):
            # Manually reset the selected target
            target_center = None
            target_box = None
            lost_frames = 0
            print("Target selection reset.")

finally:
    camera.release()
    cv2.destroyAllWindows()
    print("Person tracker stopped.")
    camera.release()
    cv2.destroyAllWindows()
    arduino.close()
    print("Tracker stopped.")
