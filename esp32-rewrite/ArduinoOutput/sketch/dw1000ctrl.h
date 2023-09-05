#line 1 "C:\\Users\\user\\Desktop\\distance measurement\\esp32-rewrite\\tag\\dw1000ctrl.h"
#ifndef DW1000_CTRL_H
#define DW1000_CTRL_H

#include <Arduino.h>
#include <stdint.h>
#include "SPI.h"

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define DW_CS 4
#define PIN_RST 27
#define PIN_IRQ 34

void setupDW1000();

void sleepDW1000();

// read and write functions. 64 registers, x bytes each
void readRegister(uint8_t reg, uint8_t *data, uint8_t length, uint16_t offset = 0);

void writeRegister(uint8_t reg, uint8_t *data, uint8_t length, uint16_t offset = 0);

void sleepDW1000();
void wakeDW1000();

void sendMessage(uint8_t *dataToTransmit, uint8_t length);

void startListening(void (*callback)(void));

#endif
