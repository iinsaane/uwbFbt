#include <SPI.h>
#include "DW1000Ranging.h"
#include "DW1000.h"
#include "EEPROM.h"
 
#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4
 
#define EEPROM_SIZE 2

// connection pins
const uint8_t PIN_RST = 27; // reset pin
const uint8_t PIN_IRQ = 34; // irq pin
const uint8_t PIN_SS = 4;   // spi select pin
 
// TAG antenna delay defaults to 16384
// leftmost two bytes below will become the "short address"
char tag_addr[] = "01:00:22:EA:82:60:3B:9C";
uint16_t Adelay = 16480; //starting value
uint16_t Adelay_delta = 100; //initial binary search step size
float this_anchor_target_distance = 1.0; //measured distance to anchor in m

bool printDistance = true;
bool needsCalibration = false;

void setup()
{
  Serial.begin(115200);
  while(!Serial);
 
  // set Adelay from EEPROM
  uint16_t Adelay;
  Adelay = readAdelayFromEEPROM();
  DW1000.setAntennaDelay(Adelay);

  //init the configuration
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
  DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ); //Reset, CS, IRQ pin
 
  DW1000Ranging.attachNewRange(newRange);
  DW1000Ranging.attachNewDevice(newDevice);
  DW1000Ranging.attachInactiveDevice(inactiveDevice);
 
// start as tag, do not assign random short address
 
  DW1000Ranging.startAsTag(tag_addr, DW1000.MODE_SHORTDATA_FAST_ACCURACY, false);
}
 
void loop()
{
  DW1000Ranging.loop();
  getSerialMessage();
}
 
void newRange()
{
  measureDistance();
}

uint16_t readAdelayFromEEPROM() {
  uint8_t lowByte = EEPROM.read(0);  // read the low byte from EEPROM address 0
  uint8_t highByte = EEPROM.read(1); // read the high byte from EEPROM address 1
  uint16_t adelay = (highByte << 8) | lowByte; // combine the two bytes into a single uint16_t value
  Serial.print(highByte);
  Serial.print(" ");
  Serial.print(lowByte);
  Serial.print("          ");
  Serial.println(adelay);
  
  return adelay;
}

// main loop
void measureDistance() {
  // check for any Serial messages
  // getSerialMessage();

  if( needsCalibration ) {
    // set current adelay
    DW1000.setAntennaDelay(Adelay);
    static float last_delta = 0.0;
    Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), DEC);
  
    float dist = 0;
    for (int i = 0; i < 100; i++) {
      // get and average 100 measurements
      dist += DW1000Ranging.getDistantDevice()->getRange();
    }
    dist /= 100.0;
    Serial.print(",");
    Serial.print(dist); 
    if (Adelay_delta < 3) {
      Serial.print(", final Adelay ");
      Serial.println(Adelay);
      //    Serial.print("Check: stored Adelay = ");
      //    Serial.println(DW1000.getAntennaDelay());
      needsCalibration = false;

      // write the Adelay to the EEPROM
      uint8_t low_byte = (Adelay >> 8) & 0xFF;
      uint8_t high_byte = Adelay & 0xFF;
      EEPROM.write(0, high_byte );
      EEPROM.write(1, low_byte );
      EEPROM.commit();

      Serial.println(readAdelayFromEEPROM());

      return;
    }
  
    float this_delta = dist - this_anchor_target_distance;  //error in measured distance
  
    if ( this_delta * last_delta < 0.0) Adelay_delta = Adelay_delta / 2; //sign changed, reduce step size
      last_delta = this_delta;
    
    if (this_delta > 0.0 ) Adelay += Adelay_delta; //new trial Adelay
    else Adelay -= Adelay_delta;
    
    Serial.print(", Adelay = ");
    Serial.println (Adelay);
    //  DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ); //Reset, CS, IRQ pin
    DW1000.setAntennaDelay(Adelay);

    return;
  }

  // get device address
  if (printDistance) {
    Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), HEX);
    Serial.print(", ");

    int dist = DW1000Ranging.getDistantDevice()->getRange() * 100; // measure distance in cm
  
    Serial.println(dist);
    delay(50);

  }
}

void getSerialMessage() {
  if (Serial.available()) {
    String message = Serial.readStringUntil('\n');
    if (message == "calibrate") {
      //calibrateAdelay();
      Adelay = 16480;
      Adelay_delta = 100; //initial binary search step size
      needsCalibration = true;
    } else
    if (message == "ping") {
      Serial.print("pong");
    } else
    if (message.startsWith("adelay:")) {
      int calibrateValue = message.substring(11).toInt();
      DW1000.setAntennaDelay(Adelay);
      uint8_t low_byte = (Adelay >> 8) & 0xFF;
      uint8_t high_byte = Adelay & 0xFF;
      EEPROM.write(0, high_byte );
      EEPROM.write(1, low_byte );
      EEPROM.commit();
      Serial.print("set Adelay to ");
      Serial.println(calibrateValue);
    } else
    if (message == "printDistance") {
      printDistance = !printDistance;
    } else
    if (message == "restart") {
      esp_restart();
    }
  }
}

 
void newDevice(DW1000Device *device)
{
  Serial.print("Device added: ");
  Serial.println(device->getShortAddress(), HEX);
}
 
void inactiveDevice(DW1000Device *device)
{
  Serial.print("delete inactive device: ");
  Serial.println(device->getShortAddress(), HEX);
}