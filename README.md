# computer-vision-tracking-platform

A personal engineering project integrating computer vision, embedded systems, servo control, and CAD to develop a two-axis target-tracking platform.

# Project Overview

This project uses real-time computer vision to detect and track a person using a camera. Python calculates the target's position relative to the center of the image and transmits the coordinates to an Arduino UNO R4 WiFi. The Arduino processes the incoming data and controls two servo motors to follow the target horizontally and vertically.

The mechanical assembly is being designed in SolidWorks to create a functional, compact tracking platform.

# System Architecture

1. **Computer Vision:** Python processes the laptop camera feed to detect a person and determine their position within the image.
2. **Coordinate Processing:** The target's horizontal and vertical offsets from the image center are calculated in real time.
3. **Serial Communication:** Target coordinates are transmitted from Python to the Arduino UNO R4 WiFi over serial communication.
4. **Servo Control:** The Arduino uses the received coordinates to control two MG90S servo motors for two-axis tracking.
5. **Mechanical Design:** A custom base, horizontal rotation mechanism, and vertical tilt assembly are being designed in SolidWorks.

## Technologies and Components

**Software**
- Python
- Computer vision and real-time object detection
- Serial communication

**Electronics**
- Arduino UNO R4 WiFi
- Two MG90S servo motors
- Laptop camera

**Mechanical Design**
- SolidWorks CAD
- Custom two-axis mechanical assembly

## Current Progress

- [x] Implemented real-time person detection using a camera.
- [x] Calculated target position relative to the image center.
- [x] Established serial communication between Python and Arduino.
- [x] Implemented Arduino-based control of two servo motors.
- [x] Tested servo movement in response to tracking data.
- [x] Designed the initial mechanical assembly in SolidWorks.
- [ ] Complete the mechanical assembly and physical integration.
- [ ] Calibrate tracking response and servo movement.
- [ ] Align laser diodes.
- [ ] Evaluate ultrasonic distance sensing as a supplementary input.
- [ ] Test and refine overall tracking performance.

## Engineering Challenges

This project involves coordinating multiple subsystems, including computer vision, serial communication, embedded control, and mechanical design. A key challenge is translating image-space coordinates into appropriate servo movement while accounting for the mechanical limits and response of the tracking platform.

The project is being developed iteratively, with individual components tested before full system integration.

## Future Improvements

- Complete and assemble the SolidWorks mechanical design.
- Improve tracking accuracy and responsiveness.
- Calibrate servo movement to reduce tracking error.
- Investigate ultrasonic distance sensing for supplementary distance measurements.
- Evaluate system performance under different lighting and movement conditions.

## Project Status

**In Development**

The computer-vision pipeline, Python-to-Arduino communication, and basic servo response have been tested successfully. Mechanical integration, calibration, and further system-level testing remain in progress.

