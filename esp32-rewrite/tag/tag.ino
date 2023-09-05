#include <Arduino.h>
#include "SPI.h"
#include <stdint.h>
#include "dw1000ctrl.h"

// function to write every bit of a uint8_t to the serial monitor
void printByte(uint8_t byte)
{
  for (int i = 7; i >= 0; i--)
  {
    Serial.print(bitRead(byte, i));
  }
}

void setup()
{
  Serial.begin(115200);
  while (!Serial)
  {
    delay(10);
  }
  setupDW1000();
  Serial.println("Setup done");

  // send 8 1's
  uint8_t data[1] = {0xFF};
  sendMessage(data, 1);

  startListening(receiveMessage);

  // get event mask
  uint8_t mask[4];
  readRegister(0x0E, mask, 4);

  // print event mask. [0] is the lowest byte. print higest byte to lowest byte
  Serial.print("Event mask: ");
  for (int i = 3; i >= 0; i--)
  {
    printByte(mask[i]);
    Serial.print(" ");
  }
  Serial.println();

  // detect interrupt pin change
  bool lastValue = false;
  while (true)
  {
    bool currentValue = digitalRead(PIN_IRQ);
    if (currentValue != lastValue)
    {
      Serial.print("Interrupt pin changed: ");
      Serial.println(currentValue);
      lastValue = currentValue;
    }
  }
}

void receiveMessage()
{
  Serial.println("Receiving message");
}

void loop()
{
}