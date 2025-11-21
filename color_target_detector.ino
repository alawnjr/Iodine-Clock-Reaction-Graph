#include "Adafruit_APDS9960.h"

Adafruit_APDS9960 apds;

// ========== CONFIGURATION ==========
// Set your target time in seconds (change this value as needed)
const float TARGET_TIME = 300.0;  // Example: 300 seconds (5 minutes)
// ===================================

// Reference data from CSV (Clear channel values at 1-second intervals)
const int NUM_DATA_POINTS = 479;
const uint16_t CLEAR_DATA[NUM_DATA_POINTS] PROGMEM = {
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23,
  24, 26, 28, 29, 31, 33, 34, 35, 36, 38, 39, 40, 42, 43, 44, 45, 45, 46, 47, 48,
  49, 49, 50, 51, 52, 52, 53, 54, 54, 55, 56, 56, 57, 58, 59, 60, 60, 61, 62, 62,
  63, 64, 65, 65, 65, 66, 66, 67, 68, 68, 68, 69, 69, 70, 71, 71, 71, 72, 72, 72,
  72, 73, 73, 73, 73, 73, 74, 74, 75, 75, 75, 75, 75, 76, 76, 76, 76, 76, 77, 77,
  77, 77, 77, 78, 78, 78, 78, 79, 79, 79, 79, 80, 80, 80, 80, 80, 80, 80, 81, 81,
  81, 82, 82, 82, 82, 82, 83, 83, 83, 83, 84, 84, 84, 84, 85, 85, 85, 85, 85, 85,
  85, 86, 86, 86, 86, 87, 87, 87, 87, 87, 88, 88, 88, 88, 88, 89, 89, 89, 89, 89,
  90, 90, 90, 90, 91, 91, 91, 91, 91, 92, 92, 92, 93, 93, 93, 93, 94, 94, 94, 94,
  95, 95, 95, 95, 96, 96, 96, 96, 97, 97, 97, 97, 98, 98, 98, 98, 99, 99, 99, 99,
  99, 100, 100, 100, 101, 101, 101, 101, 102, 102, 102, 102, 102, 103, 103, 103, 104, 104, 104, 104,
  104, 105, 105, 105, 106, 106, 106, 106, 106, 107, 107, 107, 108, 108, 108, 108, 109, 109, 109, 109,
  109, 110, 110, 110, 110, 111, 111, 111, 111, 111, 111, 112, 112, 113, 113, 113, 113, 114, 114, 114,
  114, 115, 115, 115, 116, 116, 116, 117, 117, 117, 118, 118, 118, 118, 119, 119, 119, 119, 120, 120,
  120, 120, 121, 121, 121, 121, 121, 122, 122, 123, 123, 123, 123, 123, 124, 124, 124, 124, 124, 124,
  125
};

// Variables
unsigned long startTime;
bool targetReached = false;
uint16_t targetClearValue;

// Function to get Clear value from PROGMEM array
uint16_t getClearValue(int index) {
  return pgm_read_word(&CLEAR_DATA[index]);
}

// Get target value at a given time (simple lookup, no interpolation needed)
uint16_t getTargetValue(float t) {
  // Round to nearest second
  int index = (int)(t + 0.5);
  
  // Check bounds
  if (index < 0) {
    index = 0;
  }
  if (index >= NUM_DATA_POINTS) {
    index = NUM_DATA_POINTS - 1;
  }
  
  return getClearValue(index);
}

// Linear interpolation function (COMMENTED OUT - not needed since values differ by 1 at most)
/*
float interpolate(float t) {
  // t is the target time in seconds
  // Data points are at 1-second intervals starting from 0
  
  // Check bounds
  if (t <= 0) {
    return getClearValue(0);
  }
  if (t >= NUM_DATA_POINTS - 1) {
    return getClearValue(NUM_DATA_POINTS - 1);
  }
  
  // Find the two points to interpolate between
  int idx1 = (int)t;  // Lower index
  int idx2 = idx1 + 1;  // Upper index
  float fraction = t - idx1;  // Fractional part
  
  // Get the values
  float val1 = getClearValue(idx1);
  float val2 = getClearValue(idx2);
  
  // Linear interpolation
  return val1 + (val2 - val1) * fraction;
}
*/

void setup() {
  Serial.begin(115200);
  
  if (!apds.begin()) {
    Serial.println("ERROR: Failed to initialize APDS9960!");
    while (1);
  }
  
  apds.enableColor(true);
  
  // Get target Clear value (simple lookup, rounded to nearest second)
  targetClearValue = getTargetValue(TARGET_TIME);
  
  Serial.println("===== Color Sensor Target Detection =====");
  Serial.print("Target Time: ");
  Serial.print(TARGET_TIME);
  Serial.println(" seconds");
  Serial.print("Target Clear Value: ");
  Serial.println(targetClearValue);
  Serial.println("==========================================");
  Serial.println();
  Serial.println("Starting measurements...");
  Serial.println("Format: Time(ms), R, G, B, C, Status");
  Serial.println();
  
  startTime = millis();
}

void loop() {
  uint16_t r, g, b, c;
  
  // Wait for color data to be ready
  while (!apds.colorDataReady()) {
    delay(5);
  }
  
  // Read color data
  apds.getColorData(&r, &g, &b, &c);
  
  // Calculate elapsed time
  unsigned long currentTime = millis() - startTime;
  float elapsedSeconds = currentTime / 1000.0;
  
  // Print data
  Serial.print(currentTime);
  Serial.print(", ");
  Serial.print(r);
  Serial.print(", ");
  Serial.print(g);
  Serial.print(", ");
  Serial.print(b);
  Serial.print(", ");
  Serial.print(c);
  Serial.print(", ");
  
  // Check if we've reached the target
  if (!targetReached && c >= targetClearValue) {
    Serial.println("STOP");
    targetReached = true;
  } else {
    Serial.print("Running (");
    Serial.print((int)((c * 100.0) / targetClearValue));
    Serial.println("% of target)");
  }
  
  delay(100);
}

