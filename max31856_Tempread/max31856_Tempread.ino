// This example demonstrates doing a one-shot measurement "manually".
// Separate calls are made to trigger the conversion and then check
// for conversion complete. While this typically only takes a couple
// 100 milliseconds, that times is made available by separating these
// two steps.

#include <Adafruit_MAX31856.h>
#define T_topjig 10
#define T_botjig 9

String inString = "";

// Use software SPI: CS, DI, DO, CLK
//Adafruit_MAX31856 maxthermo = Adafruit_MAX31856(10, 11, 12, 13);
// use hardware SPI, just pass in the CS pin
Adafruit_MAX31856 topjigthermo = Adafruit_MAX31856(T_topjig);
Adafruit_MAX31856 botjigthermo = Adafruit_MAX31856(T_botjig);

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
//  Serial.println("MAX31856 thermocouple test");

  if (!topjigthermo.begin()) {
    Serial.println("Could not initialize top thermocouple.");
    while (1) delay(10);
  }
  if (!botjigthermo.begin()) {
    Serial.println("Could not initialize bot thermocouple.");
    while (1) delay(10);
  }
  topjigthermo.setThermocoupleType(MAX31856_TCTYPE_K);
  botjigthermo.setThermocoupleType(MAX31856_TCTYPE_K);

//  Serial.print("Thermocouple type: ");
//  switch (maxthermo.getThermocoupleType() ) {
//    case MAX31856_TCTYPE_B: Serial.println("B Type"); break;
//    case MAX31856_TCTYPE_E: Serial.println("E Type"); break;
//    case MAX31856_TCTYPE_J: Serial.println("J Type"); break;
//    case MAX31856_TCTYPE_K: Serial.println("K Type"); break;
//    case MAX31856_TCTYPE_N: Serial.println("N Type"); break;
//    case MAX31856_TCTYPE_R: Serial.println("R Type"); break;
//    case MAX31856_TCTYPE_S: Serial.println("S Type"); break;
//    case MAX31856_TCTYPE_T: Serial.println("T Type"); break;
//    case MAX31856_VMODE_G8: Serial.println("Voltage x8 Gain mode"); break;
//    case MAX31856_VMODE_G32: Serial.println("Voltage x8 Gain mode"); break;
//    default: Serial.println("Unknown"); break;
//  }

  topjigthermo.setConversionMode(MAX31856_ONESHOT_NOWAIT);
  botjigthermo.setConversionMode(MAX31856_ONESHOT_NOWAIT);

  pinMode (T_topjig, OUTPUT);
  pinMode (T_botjig, OUTPUT);
  digitalWrite(T_topjig,HIGH);
  digitalWrite(T_botjig,HIGH);
}

void loop() {
  inString = "";
  
  //It will read the data one byte at a time from the Buffer(which holds 64 bytes)
  // All the number and string are in UTF-8 format. So they need to be saved as string. 
  while (Serial.available() > 0) {
    char inChar = Serial.read();
    inString += inChar;
  }
  
  if (inString == "t") {
    digitalWrite(T_topjig,LOW);
    digitalWrite(T_botjig,HIGH);
    delay(10);
    // trigger a conversion, returns immediately
    topjigthermo.triggerOneShot();
    // check for conversion complete and read temperature
    while (!topjigthermo.conversionComplete()) delay(10);
    Serial.print("Top Temp: ");
    Serial.println(topjigthermo.readThermocoupleTemperature());
    digitalWrite(T_topjig,HIGH);
    digitalWrite(T_botjig,HIGH);
  }
  if (inString == "b") {
    digitalWrite(T_topjig,HIGH);
    digitalWrite(T_botjig,LOW);
    delay(10);
    // trigger a conversion, returns immediately
    botjigthermo.triggerOneShot();
    // check for conversion complete and read temperature
    while (!botjigthermo.conversionComplete()) delay(10);
    Serial.print("Bot Temp: ");
    Serial.println(botjigthermo.readThermocoupleTemperature());
    digitalWrite(T_topjig,HIGH);
    digitalWrite(T_botjig,HIGH);
   }

}
