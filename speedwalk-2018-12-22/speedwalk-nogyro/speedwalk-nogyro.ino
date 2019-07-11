#include "main.h"

// global
uint8_t globalState;
Server server(Serial);
// main motor
uint32_t time = 0, lastPkgTime = 0;
double spdSetpoint = 0, spdInput = 0, spdOutput = 0;
PID pidSpd(&spdInput, &spdOutput, &spdSetpoint,
  MOTOR_PID_P, MOTOR_PID_I, MOTOR_PID_D, REVERSE);
// angle motor
angle_t angleX;

void setup() {
  // global initialization
  TCCR0B = TCCR0B & 0b11111000 | 0x02; // PWM clock (5/6) *= 8, time /= 8
  angleX.buffer = (int16_t*) malloc(sizeof(int16_t) * ANGLE_AVG_COUNT);

  // read stored values from EEPROM
  uint8_t calibrated = EEPROM.read(ADDR_CAL_STATE);
  if (calibrated == CAL_MAGIC_NUMBER) {
    angleX.zero = EEPROM.read(ADDR_ANGLE_ZERO_L);
    angleX.zero |= (int16_t) EEPROM.read(ADDR_ANGLE_ZERO_H) << 8;
  } else {
    angleX.zero = ANGLE_ZERO_DEF;
  }

  angleX.target = angleX.zero;
  
  if (HW_DEBUG_ON) {
    pinMode(DBG_PIN_1, OUTPUT);
    digitalWrite(DBG_PIN_1, HIGH);
    pinMode(DBG_PIN_2, OUTPUT);
    digitalWrite(DBG_PIN_2, HIGH);
    pinMode(DBG_PIN_3, OUTPUT);
    digitalWrite(DBG_PIN_3, HIGH);
    pinMode(DBG_PIN_4, OUTPUT);
    digitalWrite(DBG_PIN_4, HIGH);
  }

  // actuating peripherials init
  pinMode(MOTOR_PIN, OUTPUT);
  analogWrite(MOTOR_PIN, MOTOR_MIN);
  pinMode(ANGLE_PIN, OUTPUT);
  analogWrite(ANGLE_PIN, ANGLE_SPD_MIN);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, DIR_NORMAL);
  pinMode(MOTOR_DIR_F, OUTPUT);
  digitalWrite(MOTOR_DIR_F, HIGH);
  pinMode(MOTOR_DIR_R, OUTPUT);
  digitalWrite(MOTOR_DIR_R, LOW);
  

  // sensors init
  calibrateAngleX();

  // turn the PID on
  pidSpd.SetSampleTime(MOTOR_ST);
  pidSpd.SetOutputLimits(MOTOR_MIN, MOTOR_MAX);
  pidSpd.SetMode(AUTOMATIC);

  // interfaces init
  Serial.begin(SRV_SERIAL_SPEED);
  applyState(STATE_NC);
}

void loop() {
  if (HW_DEBUG_ON) digitalWrite(DBG_PIN_1, LOW); // DEBUG
  readAngleX();
  
  switch (globalState) {
    case STATE_NC:
      if (HW_DEBUG_ON) digitalWrite(DBG_PIN_4, LOW); // DEBUG
      server.connect();
      if (HW_DEBUG_ON) digitalWrite(DBG_PIN_4, HIGH); // DEBUG
      delay(SRV_CONNECT_DELAY);
      break;
    case STATE_IDLE:
      break;
    case STATE_RUN:
      time = millis();
      if (time - lastPkgTime > SRV_MAX_SPD_DELAY) {
        server.sendAction(SRV_MT_NO_POS_X);
        lastPkgTime = time;
        spdInput = 0;
      }

      if (pidSpd.Compute()) {
        if (HW_DEBUG_ON) digitalWrite(DBG_PIN_3, LOW); // DEBUG
        analogWrite(MOTOR_PIN, spdOutput);
        if (HW_DEBUG_ON) digitalWrite(DBG_PIN_3, HIGH); // DEBUG
      }

      if (correctAngleX()) {
        if (HW_DEBUG_ON) digitalWrite(DBG_PIN_4, LOW); // DEBUG
        analogWrite(ANGLE_PIN, angleX.spd);
        if (HW_DEBUG_ON) digitalWrite(DBG_PIN_4, HIGH); // DEBUG
      }
      break;
    case STATE_SVC:
      server.sendInt16(SRV_MT_SVC_ACVAL, angleX.current);
      delay(SERVICE_DELAY);
      break;
  }

  if (HW_DEBUG_ON) digitalWrite(DBG_PIN_1, HIGH); // DEBUG
}

void serialEvent() {
  if (HW_DEBUG_ON) digitalWrite(DBG_PIN_2, LOW); // DEBUG

  if (server.getCommand()) {
    command *cmd = server.getCommandData();
    switch (cmd->data[SRV_DIDX_TYPE]) {
      case SRV_MT_CLOSE:
        applyState(STATE_NC);
        break;
      case SRV_MT_STATE:
        digitalWrite(DBG_PIN_3, LOW); // DEBUG
        applyState(cmd->data[SRV_DIDX_STATE]);
        digitalWrite(DBG_PIN_3, HIGH); // DEBUG
        break;
      case SRV_MT_POS_X:
        spdInput = cmd->data[SRV_DIDX_POS_X];
        if (globalState == STATE_RUN)
          lastPkgTime = millis();
        break;
      case SRV_MT_ANGLE:
        angleX.input = cmd->data[SRV_DIDX_ANGLE];
        computeAngleX();
        break;
    }

    if (globalState == STATE_SVC) {
      switch (cmd->data[SRV_DIDX_TYPE]) {
        case SRV_MT_SVC_AINC:
          angleXStep(true);
          break;
        case SRV_MT_SVC_ADEC:
          angleXStep(false);
          break;
        case SRV_MT_SVC_ASET0:
          angleX.zero = angleX.current;
          server.sendInt16(SRV_MT_SVC_A0VAL, angleX.zero);
          delay(SERVICE_DELAY);
          computeAngleX();
          break;
        case SRV_MT_MEM_STORE:
          storeEEPROM();
          break;
        case SRV_MT_MEM_CLEAR:
          clearEEPROM();
          break;
      }
    }
  }

  if (HW_DEBUG_ON) digitalWrite(DBG_PIN_2, HIGH); // DEBUG
}

void applyState(uint8_t state) {
  if (state == globalState)
    return;
  spdOutput = MOTOR_MIN;
  angleX.spd = ANGLE_SPD_MIN;
  analogWrite(MOTOR_PIN, spdOutput);
  analogWrite(ANGLE_PIN, angleX.spd);
  applyAngleXDir(DIR_NORMAL);
  
  globalState = state;
  if (globalState != STATE_NC)
    server.sendState(globalState);

  switch (globalState) {
    case STATE_RUN:
      lastPkgTime = millis();
      break;
    case STATE_SVC:
      delay(SERVICE_DELAY);
      server.sendInt16(SRV_MT_SVC_A0VAL, angleX.zero);
      break;
  }
}

void applyAngleXDir(uint8_t dir) {
  if (angleX.dir != dir) {
    digitalWrite(RELAY_PIN, angleX.dir = dir);
    delay(DIR_CHANGE_DELAY);
  }
}

void computeAngleX() {
  angleX.target = angleX.zero + angleX.input * ANGLE_TO_ADC;
}

void calibrateAngleX() {
  for (int i = 0; i < ANGLE_AVG_COUNT; i++) {
    angleX.buffer[i] = analogRead(SENSOR_PIN);
    delay(ANGLE_READ_DELAY);
  }
}

void readAngleX() {
  delay(ANGLE_READ_DELAY);
  angleX.buffer[angleX.bufferPos] = analogRead(SENSOR_PIN);
  for (int i = 0; i < ANGLE_AVG_COUNT; i++)
    angleX.current += angleX.buffer[i];
  angleX.current /= ANGLE_AVG_COUNT;
  if (angleX.bufferPos++ == ANGLE_AVG_COUNT)
    angleX.bufferPos = 0;
}

bool correctAngleX() {
  uint8_t tmp = angleX.spd;
  if (angleX.current < ANGLE_MIN)
    angleX.target = ANGLE_MIN + ANGLE_DELTA * 2;
  if (angleX.current > ANGLE_MAX)
    angleX.target = ANGLE_MAX - ANGLE_DELTA * 2;
  angleX.delta = angleX.target - angleX.current;
  if (abs(angleX.delta) > ANGLE_DELTA) {
    if (angleX.needChangeDir) {
      applyAngleXDir(angleX.dir ^ DIR_CHANGE_MASK);
      angleX.needChangeDir = false;
    } else {
      if (angleX.delta < 0 && angleX.dir == DIR_NORMAL
        || angleX.delta > 0 && angleX.dir == DIR_REVERSE) {
        angleX.spd = ANGLE_SPD_MIN;
        angleX.needChangeDir = true;
      } else {
        angleX.spd = ANGLE_SPD_MAX;
      }
    }
  } else
    angleX.spd = ANGLE_SPD_MIN;
  return angleX.spd != tmp;
}

void angleXStep(bool direction) {
  applyAngleXDir(direction ?
    DIR_NORMAL : DIR_REVERSE);
  analogWrite(ANGLE_PIN, ANGLE_SPD_MAX);
  delay(ANGLE_STEP_DELAY);
  analogWrite(ANGLE_PIN, ANGLE_SPD_MIN);
}

void storeEEPROM() {
  EEPROM.write(ADDR_ANGLE_ZERO_H, (uint8_t) (angleX.zero >> 8));
  EEPROM.write(ADDR_ANGLE_ZERO_L, (uint8_t) (angleX.zero & 0xff));
  EEPROM.write(ADDR_CAL_STATE, CAL_MAGIC_NUMBER);
  server.sendAction(SRV_MT_MEM_STORE);
}

void clearEEPROM() {
  EEPROM.write(ADDR_CAL_STATE, EEPROM_EMPTY);
  EEPROM.write(ADDR_ANGLE_ZERO_H, EEPROM_EMPTY);
  EEPROM.write(ADDR_ANGLE_ZERO_L, EEPROM_EMPTY);
  server.sendAction(SRV_MT_MEM_CLEAR);
}
