#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <EEPROM.h>
#include "DW1000Ranging.h"
#include "DW1000.h"

// ESP32_UWB pin definitions
#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4

void calibrateAdelay();

uint16_t readAdelayFromEEPROM();

void measureDistance();

#endif