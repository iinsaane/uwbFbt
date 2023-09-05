#line 1 "C:\\Users\\user\\Desktop\\distance measurement\\esp32-rewrite\\tag\\dw1000ctrl.cpp"
#include "dw1000ctrl.h"
#include <stdint.h>

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define DW_CS 4
#define PIN_RST 27
#define PIN_IRQ 34

void setupDW1000()
{
    // setup DW1000
    pinMode(PIN_RST, INPUT);
    pinMode(PIN_IRQ, INPUT);
    pinMode(DW_CS, OUTPUT);
    delay(1);
    // read on rising edge
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, DW_CS);
}

void readRegister(uint8_t reg, uint8_t *data, uint8_t length = 4, uint16_t offset)
{ // read 32 bits
    uint8_t header[3];
    uint8_t headerLength = 1;
    /*
    header[0] = r/w bit, sub-addressing bit, 5-bit register address
    header[1] = extended sub-addressing bit, 7-bit offset (low order)
    header[2] = 8-bit offset (high order)
    if extended sub-addressing bit is set, offset is 15 bits
    */
    if (offset > 0 && offset < 128)
    {
        header[0] = 0x40 | reg;
        header[1] = offset;
        headerLength = 2;
    }
    else if (offset >= 128 && offset < 32768)
    {
        header[0] = 0x80 | reg;
        header[1] = offset & 0x7F;
        header[2] = offset >> 7;
        headerLength = 3;
    }
    else
    {
        header[0] = reg & 0x3F;
    }

    SPI.beginTransaction(SPISettings(16000000L, MSBFIRST, SPI_MODE0));
    digitalWrite(DW_CS, LOW);
    delayMicroseconds(5);
    for (int i = 0; i < headerLength; i++)
    {
        SPI.transfer(header[i]);
    }
    for (int i = 0; i < length; i++)
    {
        data[i] = SPI.transfer(0x00);
    }
    delayMicroseconds(5);
    digitalWrite(DW_CS, HIGH);
    SPI.endTransaction();
}

void writeRegister(uint8_t reg, uint8_t *data, uint8_t length, uint16_t offset)
{
    uint8_t header[3];
    uint8_t headerLength = 1;
    /*
    header[0] = r/w bit, sub-addressing bit, 5-bit register address
    header[1] = extended sub-addressing bit, 7-bit offset (low order)
    header[2] = 8-bit offset (high order)
    if extended sub-addressing bit is set, offset is 15 bits
    */
    if (offset > 0 && offset < 128)
    {
        header[0] = 0xC0 | reg;
        header[1] = offset;
        headerLength = 2;
    }
    else if (offset >= 128 && offset < 32768)
    {
        header[0] = 0x80 | reg;
        header[1] = offset & 0x7F;
        header[2] = offset >> 7;
        headerLength = 3;
    }
    else
    {
        header[0] = 0x80 | reg;
    }

    SPI.beginTransaction(SPISettings(16000000L, MSBFIRST, SPI_MODE0));
    digitalWrite(DW_CS, LOW);
    delayMicroseconds(5);
    for (int i = 0; i < headerLength; i++)
    {
        SPI.transfer(header[i]);
    }
    for (int i = 0; i < length; i++)
    {
        SPI.transfer(data[i]);
    }
    delayMicroseconds(5);
    digitalWrite(DW_CS, HIGH);
    SPI.endTransaction();
}

void sleepDW1000()
{
    // read first byte of 2C:06, set bit 0, write back
    uint8_t data[1];
    readRegister(0x2C, data, 1, 0x06);
    data[0] |= 0b00000001;
    writeRegister(0x2C, data, 1, 0x06);

    // upload config 2C:02 bit 2
    readRegister(0x2C, data, 1, 0x02);
    data[0] |= 0b00000100;
    writeRegister(0x2C, data, 1, 0x02);

    // hehe get put to sleep dumbass
}

void wakeDW1000()
{
    // pull cs down for 1000 μs
    digitalWrite(DW_CS, LOW);
    delayMicroseconds(1000);
    digitalWrite(DW_CS, HIGH);

    // wait for chip to wake
    while (!digitalRead(PIN_RST))
        ;
    delayMicroseconds(10);
}

void sendMessage(uint8_t *dataToTransmit, uint8_t length)
{

    // transmit frame control
    uint8_t data[5];
    readRegister(0x08, data, 5);
    data[0] = length & 0b01111111;  // data length in bytes (7 bits)
    data[1] = data[1] | 0b11100000; // set data rate to 6.8mbps (13, 14), tell receiver its for ranging (15)
    data[2] = data[2] | 0b00000001; // 16 mhz prf (16, 17)
    data[2] = data[2] | 0b00100100; // 256 preamble length (18, 19, 20, 21)
    writeRegister(0x08, data, 5);

    // upload data to be transfered
    writeRegister(0x09, dataToTransmit, length);

    // send data
    readRegister(0x0D, data, 1);
    data[0] = data[0] | 0b00000010;
    writeRegister(0x0D, data, 1);

    // wait until done
    readRegister(0x0F, data, 1);
    while ((data[0] & 0b10000000) == 0)
    {
        readRegister(0x0F, data, 1);
    }

    // sent data :3
    Serial.println("sent data");
}

void startListening(void (*callback)(void))
{
    uint8_t data[4];
    // interrupt mask
    data[0] = 0b00000000;
    data[1] = 0b00000010;
    writeRegister(0x0E, data, 2);

    // PAC size 16
    data[0] = 0x31; // 0x311A002D
    data[1] = 0x1A;
    data[2] = 0x00;
    data[3] = 0x2D;
    writeRegister(0x27, data, 4, 8);

    // set callback on iqr line (falling edge)
    // attachInterrupt(digitalPinToInterrupt(PIN_IRQ), callback, FALLING);

    // start listening
    readRegister(0x0D, data, 1, 1);
    data[0] = data[0] | 0b00000001;
    writeRegister(0x0D, data, 1, 1);
}