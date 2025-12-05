#include "Adafruit_APDS9960.h"
Adafruit_APDS9960 apds;

void setup() {
  Serial.begin(115200);

  if (!apds.begin()) {
    // Don’t print extra text before the header!
    // Instead, just blink LED or halt if needed
    while (1);
  }

  apds.enableColor(true);
  apds.enableProximity(false);
  apds.enableGesture(false);
  // integration time in milliseconds
  apds.setADCIntegrationTime(150);
  apds.setADCGain(APDS9960_AGAIN_16X);

  Serial.println("Red Green Blue Clear");
}

void loop() {
  uint16_t r, g, b, c;

  while (!apds.colorDataReady()) {
    delay(5);
  }

  apds.getColorData(&r, &g, &b, &c);

  // Print values in the same order as header
  Serial.print(r); Serial.print(" ");
  Serial.print(g); Serial.print(" ");
  Serial.print(b); Serial.print(" ");
  Serial.println(c);

  delay(200);
}
