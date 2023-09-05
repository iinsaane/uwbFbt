# 1 "C:\\Users\\user\\Desktop\\distance measurement\\esp32-rewrite\\tag\\tag.ino"
# 2 "C:\\Users\\user\\Desktop\\distance measurement\\esp32-rewrite\\tag\\tag.ino" 2
# 3 "C:\\Users\\user\\Desktop\\distance measurement\\esp32-rewrite\\tag\\tag.ino" 2

# 5 "C:\\Users\\user\\Desktop\\distance measurement\\esp32-rewrite\\tag\\tag.ino" 2

// function to write every bit of a uint8_t to the serial monitor
void printByte(uint8_t byte)
{
  for (int i = 7; i >= 0; i--)
  {
    Serial.print((((byte) >> (i)) & 0x01));
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
    bool currentValue = digitalRead(34);
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
