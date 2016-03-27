/* ArduinoSerialControl */
/* Makes use of code from Adafruit's strandtest */
/* Daniel Winker */

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif

#define LONGEST_STRIP 10 // How many LEDs are in the longest LED strip
const int noStrips = 3; // Number of strips (even if it's just 1 LED in a strip) are connected?
// ^^^^Important

String readString;
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
int ledOffset = 0;
char tmpChar1;
byte byteGot;
int pin = 0;
char tmpIterator1 = 0;

/* WS2812 */
// Popular RGB LEDs, also known as Neopixels
// WS_LEDs[number of pins connected to WS2812's][which pin, how many LEDs's]

Adafruit_NeoPixel strips[noStrips]; // Objects for the strips
int WS_LEDs[noStrips][2]; // Holds the info regarding WS2812 LED connections
unsigned int LED_Values[noStrips][LONGEST_STRIP][3]; // Hold the RGB values for each strip of LEDs; [how many strips][the LEDs][R,G,B]
// End WS2812 define

void setup() {
  // Turn the Serial Protocol ON
  Serial.begin(38400);
  // reserve 300 bytes for the inputString:
  inputString.reserve(300);
  // Initialize the LED strip objects

  /* WS2812 define */
  WS_LEDs[0][0] = 8; // Which pin
  WS_LEDs[0][1] = 3; // How many LEDs
  WS_LEDs[1][0] = 10; // Which pin
  WS_LEDs[1][1] = 5; // How many LEDs
  WS_LEDs[2][0] = 9; // Which pin
  WS_LEDs[2][1] = 10; // How many LEDs
  for (int i = 0; i < noStrips; i++) {
    strips[i] = Adafruit_NeoPixel(WS_LEDs[i][1], WS_LEDs[i][0], NEO_GRB + NEO_KHZ800);
  }
  for (int i = 0; i < noStrips; i++) {
    strips[i].begin();
    strips[i].show(); // Initialize all pixels to 'off'
  }
  for (int i = 0; i < noStrips; i++) {
    for (int j = 0; j < WS_LEDs[i][1]; j++) {
      // Set strip i pin j to the given RGB values
      LED_Values[i][j][0] = 0;
      LED_Values[i][j][1] = 0;
      LED_Values[i][j][2] = 0;
    }
    strips[i].show();
  }
  // End WS2812 define
}



void loop() {
  if (stringComplete) { // If a new message has arrived
    stringComplete = false;
    tmpChar1 = inputString.charAt(0);
    /* Handle a Pin setting */
    if (tmpChar1 == 'W') {//-------------------------------------------
      tmpChar1 = inputString.charAt(6);
      if (tmpChar1 == '?') { // Report back to the computer with information regarding the connected WS2812's
        Serial.print(noStrips); // Tell the computer how many strips there are
        Serial.print(",");
        for (int i = 0; i < noStrips; i++) {
          Serial.print(WS_LEDs[i][1]); // Tell the computer how many LEDs are on that pin
          Serial.print(",");
        }
      } else if (tmpChar1 == 'S') { // Set some LEDs
        // The computer sends all of the RGB values as one long string of numbers
        ledOffset = 7;
        for (tmpIterator1 = 0; tmpIterator1 < noStrips; tmpIterator1++) { // Loop through the strips
          for (int i = 0; i < WS_LEDs[tmpIterator1][1]; i++) { // Loop through the LEDs on the strip
            //substring(inclusive, not inclusive)
            LED_Values[tmpIterator1][i][0] = inputString.substring(ledOffset, ledOffset + 3).toInt(); // Set red
            ledOffset += 3; // Increment
            //  Serial.print("G"); // G for Good Job, Arduino got the number, time for another (this is like a clock in SPI)
            LED_Values[tmpIterator1][i][1] = inputString.substring(ledOffset, ledOffset + 3).toInt(); // Set green
            ledOffset += 3; // Increment
            //  Serial.print("G"); // G for Good Job, Arduino got the number, time for another (this is like a clock in SPI)
            LED_Values[tmpIterator1][i][2] = inputString.substring(ledOffset, ledOffset + 3).toInt(); // Set blue
            ledOffset += 3; // Increment
            //  Serial.print("G"); // G for Good Job, Arduino got the number, time for another (this is like a clock in SPI)
            // Serial.print("I am here. Setting group ");
            // Serial.print(group);
          }
        }
      }
    } else if (tmpChar1 == 'P') { // Set pin; must then send, seperate from the P, a 2 digit number
      setPin();
    } else if (tmpChar1 == 'O') { // O, set pin as an output----------------------------------------------
      pinMode(pin, OUTPUT);
    } else if (tmpChar1 == 'I') { // I, set pin as an input----------------------------------------------
    pinMode(pin, INPUT);
    } else if (tmpChar1 == 'H') { // H, set pin high----------------------------------------------
    digitalWrite(pin, HIGH);
    } else if (tmpChar1 == 'L') { // L, set pin low----------------------------------------------
    digitalWrite(pin, LOW);
    }
  inputString = "";
  }
  serialEvent();
  updateStrips(); // Refresh the LED strips
}

// ---Functions----------------------------------------------------------------------------------------------------

/* Gets one byte from the serial port, or waits forever */
int getByte() {
  while (!Serial.available()) {} // wait for data to arrive
  while (1) {
    /*  check if data has been sent from the computer: */
    if (Serial.available()) {
      /* read the most recent byte. This reads in one byte */
      return Serial.read();
    }
  }
  return 32767; // Max int
}

/* Figures out what number pin is being sent to the arduino, and sets the variable pin to that */
/* Pin numbers should always be sent as two digits; works from 00 to 29 */
void setPin() {
  pin = 0; // Start fraiche. Creme fraiche.
  byteGot = getByte(); /* Get the first digit */
  if (byteGot == '1') {
    pin = pin + 10;
  } else if (byteGot == '2') {
    pin = pin + 20;
  }

  byteGot = getByte(); /* Get the next digit */
  pin = pin + byteGot - 48; // 0 in ascii is 48
  return;
}

// Take in the string waiting on the buffer
String getString() {
  readString = "";
  char c;
  while (!Serial.available()) {} // wait for data to arrive
  while (Serial.available())
  {
    delay(30); // Let the buffer fill
    c = Serial.read();  //gets one byte from serial buffer
    readString += c; //makes the string readString
  }
  return readString;
}

// Refresh the LED strips
void updateStrips() {
  for (int i = 0; i < noStrips; i++) {
    for (int j = 0; j < WS_LEDs[i][1]; j++) {
      // Set strip i pin j to the given RGB values
      strips[i].setPixelColor(j, LED_Values[i][j][0], LED_Values[i][j][1], LED_Values[i][j][2]);
    }
    strips[i].show();
  }
}

/*
  SerialEvent occurs whenever a new data comes in the
  hardware serial RX.  This routine is run between each
  time loop() runs, so using delay inside loop can delay
  response.  Multiple bytes of data may be available.
*/
// Sadly, the event does not work.
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString = inputString + inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

