/* Confuguration file */

#ifndef _CONFIG_H_
#define _CONFIG_H_

// Generic
#define HW_DEBUG_ON   0
#define TIME_FACTOR   8
#define SERVICE_DELAY 20 * TIME_FACTOR

// EEPROM addersses and values
#define EEPROM_EMPTY      0xFF
#define CAL_MAGIC_NUMBER  0x69
#define ADDR_CAL_STATE    0x00
#define ADDR_ANGLE_ZERO_H 0x02
#define ADDR_ANGLE_ZERO_L 0x01

// Global state
#define STATE_NC      1 // not connected
#define STATE_IDLE    2 // connected, idle
#define STATE_RUN     3 // connected, running
#define STATE_SVC     4 // connected, service/calibration

// Pins definition
#define DBG_PIN_1     2
#define DBG_PIN_2     3
#define DBG_PIN_3     4
#define DBG_PIN_4     5
#define MOTOR_PIN     6
#define ANGLE_PIN     5
#define RELAY_PIN     8
#define SENSOR_PIN    A0
#define MOTOR_DIR_F 9
#define MOTOR_DIR_R 10


// Main motor
#define MOTOR_MIN     0
#define MOTOR_MAX     255
#define MOTOR_ST      50
#define MOTOR_PID_P   3
#define MOTOR_PID_I   0
#define MOTOR_PID_D   0

// Angle motor
#define ANGLE_ZERO_DEF    414
#define ANGLE_MIN         136
#define ANGLE_MAX         725
#define ANGLE_TO_ADC      10
#define ANGLE_READ_DELAY  5 * TIME_FACTOR
#define ANGLE_STEP_DELAY  100 * TIME_FACTOR
#define ANGLE_AVG_COUNT   16
#define ANGLE_DELTA       10
#define ANGLE_SPD_MIN     0
#define ANGLE_SPD_MAX     64
#define DIR_NORMAL        LOW
#define DIR_REVERSE       HIGH
#define DIR_CHANGE_MASK   0x01
#define DIR_CHANGE_DELAY  5 * TIME_FACTOR

#endif /* _CONFIG_H_ */
