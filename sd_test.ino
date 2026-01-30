#include <SPI.h>
#include <SD.h>

// Standard CS pin for most SD modules is 4. 
// Change this if you wired it to a different pin.
const int chipSelect = 10;
const int relayPin = 8;

void setup() {
  Serial.begin(9600);

  pinMode(7, OUTPUT);
  pinMode(relayPin, OUTPUT);

  digitalWrite(7, HIGH);
  digitalWrite(relayPin, HIGH);

  while (!Serial) {
    ; // Wait for serial port to connect (needed for Leonardo/Mega)
  }

  Serial.print("Initializing SD card...");

  // Check if the card is present and can be initialized
  if (!SD.begin(chipSelect)) {
    Serial.println("Initialization failed! Things to check:");
    Serial.println("1. Is the card inserted?");
    Serial.println("2. Is your wiring correct?");
    Serial.println("3. Is the chipSelect pin correct?");
    return;
  }
  Serial.println("initialization done.");

  // --- WRITE SECTION ---
  File myFile = SD.open("test.txt", FILE_WRITE);

  if (myFile) {
    Serial.print("Writing to test.txt...");
    myFile.println("Hello! This is a test entry.");
    myFile.println("Time since start: " + String(millis()) + "ms");
    myFile.close(); // Always close the file to save the data!
    Serial.println("done.");
  } else {
    Serial.println("error opening test.txt for writing");
  }

  // --- READ SECTION ---
  myFile = SD.open("test.txt");
  if (myFile) {
    Serial.println("Contents of test.txt:");
    while (myFile.available()) {
      Serial.write(myFile.read());
    }
    myFile.close();
  } else {
    Serial.println("error opening test.txt for reading");
  }
}

void loop() {
  digitalWrite(7, HIGH);
  digitalWrite(relayPin, HIGH);

  // Nothing happens here for this basic test
}