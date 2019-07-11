#include "Server.h"

Server::Server(Stream &stream, bool flushSerialBeforeTx)
  : m_serialPort(stream),
    m_flushSerialBeforeTx(flushSerialBeforeTx) {
  inCommand.data = (uint8_t *) malloc(SRV_BUFFER_SIZE);
  outBuffer = (char *) malloc(SRV_BUFFER_SIZE);
  inBufferPos = 0;
  endCounter = 0;
}

void Server::connect() {
  outBuffer[SRV_DIDX_TYPE] = SRV_MT_INIT;
  sendMessage(1);
}

void Server::sendState(uint8_t state) {
  outBuffer[SRV_DIDX_TYPE] = SRV_MT_STATE;
  outBuffer[SRV_DIDX_STATE] = state;
  sendMessage(2);
}

void Server::sendAction(uint8_t action) {
  outBuffer[SRV_DIDX_TYPE] = action;
  sendMessage(1);
}

void Server::sendInt16(uint8_t header, int16_t value) {
  outBuffer[SRV_DIDX_TYPE] = header;
  outBuffer[SRV_DIDX_ANGLE_L] = (uint8_t) (value & 0xff);
  outBuffer[SRV_DIDX_ANGLE_H] = (uint8_t) (value >> 8);
  sendMessage(3);
}

bool Server::getCommand() {
  uint8_t dataByte;
  bool isCmdRecieved = false;

  while (Serial.available()) {
    dataByte = (uint8_t) Serial.read();
    inCommand.data[inBufferPos++] = dataByte;

    if (dataByte == SRV_PKG_END) {
      if (++endCounter == SRV_PKG_END_LEN) {
        inCommand.length = inBufferPos - SRV_PKG_END_LEN;
        isCmdRecieved = true;
        inBufferPos = 0;
        endCounter = 0;
      }
    } else {
      endCounter = 0;
    }
  }

  return isCmdRecieved;
}

void Server::sendMessage(uint8_t length) {
  if (m_flushSerialBeforeTx)
    m_serialPort.flush();

  uint8_t total = length + SRV_PKG_END_LEN;
  for (uint8_t i = length; i < total; i++)
    outBuffer[i] = SRV_PKG_END;
  m_serialPort.write(outBuffer, total);
}