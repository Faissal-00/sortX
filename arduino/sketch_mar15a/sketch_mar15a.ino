#include <Servo.h>

Servo diverterMotor;

void setup() {
  // 1. Open the Serial connection
  Serial.begin(9600);
  
  // 2. Attach the motor to Pin 9
  diverterMotor.attach(9);
  
  // 3. Set the Initial State (Vertical / 0 degrees)
  diverterMotor.write(0); 
  
  Serial.println("System Ready! Waiting for AI to send 1 or 2...");
}

void loop() {
  // Check if Python sent a command
  if (Serial.available() > 0) {      // 👉 I PUT THIS LINE BACK IN
    char command = Serial.read();    // 👉 AND THIS LINE!

    // --- CASE 1: SMALL CALIBRE ---
// --- CASE 1: SMALL CALIBRE ---
    if (command == '1') {
      Serial.println("Received 1: SMALL CALIBRE! INSTANT HIT!");
      
      // ⏱️ VARIABLE 1: TRAVEL TIME IS NOW DELETED!
      // Because the green line is exactly where the arm is, we don't wait at all!
      
      Serial.println("Sweeping to 90 degrees.");
      diverterMotor.write(60);
      
      // ⏱️ VARIABLE 2: HOLD TIME
      // We keep this delay so the arm stays out long enough to push the tomato off
      delay(1000);              
      
      diverterMotor.write(0);   // Go back to normal (0 degrees)

      // Clear out any extra 1s or 2s that piled up in memory
      while (Serial.available() > 0) {
        Serial.read();
      }
    }
    
    // --- CASE 2: BIG CALIBRE ---
    else if (command == '2') {
      Serial.println("Received 2: BIG CALIBRE! Perfect tomato, doing nothing.");
      diverterMotor.write(0);   // Keep at 0 degrees, let it go straight

      // Clear memory here too
      while (Serial.available() > 0) {
        Serial.read();
      }
    }
  } // 👉 Closes the if(Serial.available() > 0)
}