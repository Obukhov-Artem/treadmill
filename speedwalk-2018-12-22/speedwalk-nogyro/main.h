#include <PID_v1.h>
#include <inttypes.h>
#include <EEPROM.h>
#include <PID_v1.h>
#include "Server.h"
#include "config.h"

void applyState(uint8_t state);

void readAngleX();
void calibrateAngleX();
void computeAngleX();
bool correctAngleX();
void applyAngleXDir(uint8_t dir);
void angleXStep(bool direction);

void storeEEPROM();
void clearEEPROM();

typedef struct {
  int8_t  input = 0;
  int16_t zero = 0;
  int16_t target = 0;
  int16_t current = 0;
  int16_t delta = 0;
  int16_t *buffer;
  uint8_t bufferPos = 0;
  uint8_t spd = 0;
  uint8_t dir = DIR_NORMAL;
  bool    needChangeDir = false;
} angle_t;
