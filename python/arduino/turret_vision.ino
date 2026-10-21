#include <Servo.h>

// Servo signal pins
const int HORIZONTAL_PIN = 9;
const int VERTICAL_PIN = 10;

Servo horizontalServo;
Servo verticalServo;

// Safe software limits for initial testing
const int H_MIN = 20;
const int H_MAX = 160;
const int V_MIN = 45;
const int V_MAX = 135;

// Image tracking settings
const float X_GAIN = 0.12;
const float Y_GAIN = 0.12;
const int DEADZONE = 12;

// Smoothing: smaller means smoother, slower movement
const float SMOOTHING = 0.20;

// Current and desired angles
float currentH = 90;
float currentV = 90;
float targetH = 90;
float targetV = 90;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(10);

  horizontalServo.attach(HORIZONTAL_PIN);
  verticalServo.attach(VERTICAL_PIN);

  horizontalServo.write(90);
  verticalServo.write(90);

  Serial.println("TURRET_READY");
}

void loop() {
  // Read tracking commands from Python
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "PING") {
      Serial.println("PONG");
    }
    else if (command.startsWith("TRACK,")) {
      int comma = command.indexOf(',', 6);

      if (comma > 0) {
        float offsetX =
            command.substring(6, comma).toFloat();

        float offsetY =
            command.substring(comma + 1).toFloat();

        // Ignore small errors near image center
        if (abs(offsetX) < DEADZONE) {
          offsetX = 0;
        }

        if (abs(offsetY) < DEADZONE) {
          offsetY = 0;
        }

        // Convert pixel offsets into servo angles.
        // Direction may need reversing after physical testing.
        targetH = 90 - offsetX * X_GAIN;
        targetV = 90 + offsetY * Y_GAIN;

        // Enforce angle limits
        targetH = constrain(targetH, H_MIN, H_MAX);
        targetV = constrain(targetV, V_MIN, V_MAX);

        // Report calculated angles to Python
        Serial.print("ANGLES,");
        Serial.print(targetH, 1);
        Serial.print(",");
        Serial.println(targetV, 1);
      }
    }
  }

  // Smoothly approach the target angles
  currentH += (targetH - currentH) * SMOOTHING;
  currentV += (targetV - currentV) * SMOOTHING;

  // Send positions to servo control pins
  horizontalServo.write((int)(currentH + 0.5));
  verticalServo.write((int)(currentV + 0.5));

  delay(10);
}
