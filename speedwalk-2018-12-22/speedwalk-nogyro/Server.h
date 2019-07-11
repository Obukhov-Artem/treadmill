#ifndef _SERVER_H_
#define _SERVER_H_

#include <inttypes.h>
#include <Arduino.h>
#include "config.h"

#define SRV_BUFFER_SIZE   32
#define SRV_SERIAL_SPEED  115200
#define SRV_CONNECT_DELAY 500 * TIME_FACTOR
#define SRV_MAX_SPD_DELAY 1000 * TIME_FACTOR

#define SRV_PKG_END       0xFF
#define SRV_PKG_END_LEN   3
// data indexes
#define SRV_DIDX_TYPE     0
#define SRV_DIDX_STATE    1
#define SRV_DIDX_POS_X    1
#define SRV_DIDX_ANGLE    1
#define SRV_DIDX_ANGLE_H  2
#define SRV_DIDX_ANGLE_L  1
// message types
#define SRV_MT_INIT       0x10
#define SRV_MT_CLOSE      0x11
#define SRV_MT_STATE      0x20
#define SRV_MT_POS_X      0x21
#define SRV_MT_ANGLE      0x22
#define SRV_MT_NO_POS_X   0x30
// service commands
#define SRV_MT_SVC_ACVAL  0x40 // current angle value
#define SRV_MT_SVC_A0VAL  0x41 // angle zero point
#define SRV_MT_SVC_AINC   0x42 // angle increment
#define SRV_MT_SVC_ADEC   0x43 // angle decrement
#define SRV_MT_SVC_ASET0  0x44 // set angle zero point
#define SRV_MT_MEM_STORE  0x50 // store settings to EPROM
#define SRV_MT_MEM_CLEAR  0x51 // clear EEPROM

typedef struct {
  uint8_t *data;
  uint8_t length;
} command;

class Server {
public:
  Server(Stream &stream, bool flushSerialBeforeTx = true);

  void connect();
  void sendState(uint8_t state);
  void sendAction(uint8_t action);
  void sendInt16(uint8_t header, int16_t value);
  
  bool getCommand();
  command *getCommandData() { return &inCommand; }
private:
  command inCommand;
  uint8_t inBufferPos, endCounter;

  char* outBuffer;
  Stream &m_serialPort;
  bool m_flushSerialBeforeTx;

  void sendMessage(uint8_t length);
};

#endif /* _SERVER_H_ */
