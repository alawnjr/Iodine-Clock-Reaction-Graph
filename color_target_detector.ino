#include "Adafruit_APDS9960.h"
#include <SPI.h>
#include <SD.h>

#define REACTION_1
#define RELAY_PIN 5
#define HALL_PIN 2
#define SD_CARD
#define HALL_EFFECT

const int chipSelect = 10;
volatile int hallCount = 0;

Adafruit_APDS9960 apds;
const uint8_t REQUIRED_HITS = 3;
unsigned long startTime;
File dataFile;

void hallISR() {
  hallCount++;
}

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);
  pinMode(HALL_PIN, INPUT_PULLUP);

  #ifdef HALL_EFFECT
  attachInterrupt(digitalPinToInterrupt(HALL_PIN), hallISR, FALLING);
  #endif

  Serial.begin(115200);

  while (!Serial);

  #ifdef SD_CARD
  // Initialize SD card
  Serial.print("Initializing SD card...");
  if (!SD.begin(chipSelect)) {
    Serial.println("SD card initialization failed!");
    while (1);
  }
  Serial.println("done.");

  #endif

  // Initialize color sensor
  if (!apds.begin()) {
    Serial.println("ERROR: Failed to initialize APDS9960!");
    while (1);
  }

  apds.enableColor(true);
  apds.enableProximity(false);
  apds.enableGesture(false);
  // integration time in milliseconds
  apds.setADCIntegrationTime(150);
  apds.setADCGain(APDS9960_AGAIN_16X);

  // Remove old data file and write header

  #ifdef SD_CARD
  SD.remove("data.txt");
  dataFile = SD.open("data.txt", FILE_WRITE);
  if (dataFile) {
    dataFile.println("Red Green Blue Clear Encoder");
    dataFile.close();
  } else {
    Serial.println("Error opening data.txt for writing");
  }

  #endif

  Serial.println("Red Green Blue Clear");

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

  // Print values to serial
  Serial.print(r); Serial.print(" ");
  Serial.print(g); Serial.print(" ");
  Serial.print(b); Serial.print(" ");
  Serial.print(c); Serial.print(" ");
  Serial.println(hallCount);


  #ifdef SD_CARD
  // Write values to SD card
  dataFile = SD.open("data.txt", FILE_WRITE);
  if (dataFile) {
    dataFile.print(r); dataFile.print(" ");
    dataFile.print(g); dataFile.print(" ");
    dataFile.print(b); dataFile.print(" ");
    dataFile.print(c); dataFile.print(" ");
    dataFile.println(hallCount);
    dataFile.close();
  }
  #endif


  //only stop if c value is low and at least 5 seconds have passed

  if (c < 1000 && millis() - startTime > 5000) {
    digitalWrite(RELAY_PIN, LOW);
  }



  // Debounce: require consecutive readings above the target
  // if (c >= targetClearValue) {
  //   consecutiveHits++;
  // } else {
  //   consecutiveHits = 0;
  // }

  // // Check if we've reached the target after REQUIRED_HITS readings
  // if (!targetReached && consecutiveHits >= REQUIRED_HITS) {
  //   Serial.println("STOP");
  //   targetReached = true;
  //   // Add motor-off or other stop actions here if needed
  // }

  delay(100);
}
