#define out1 2 //direction pin1
#define out2 3 //direction pin2
#define out3 5 //speed
#include <String.h>

String txtMsg = "";
String rawData = "";
boolean itreadmill = false;
boolean stringComplete = false;
boolean nazad = false;
boolean treadmill_init = false;
int Speed = 0;
int sch = 0;

void setup() {
  Settings();
}

void loop() {
  question(itreadmill, treadmill_init, Speed, stringComplete, txtMsg);
  answer(stringComplete, txtMsg, treadmill_init, itreadmill);
  working(txtMsg, treadmill_init, nazad)


  sch++;
  if (sch >= 10) itreadmill = false;
  stringComplete = false;
  txtMsg = "";
  rawData = "";
}

char inChar;
void serialEvent()
{
  while (Serial.available())
  {
    char inChar = (char)Serial.read();
    if (inChar == '.')
    {
      stringComplete = true;
      istr = strstr(rawData, '-');
      rawData = "";
      if ( istr == NULL)
        nazad = false;
      else
        nazad = true;
    }
    if (inChar == '-')
      nazad = true;
    else
      txtMsg += inChar;
    rawData += inChar;
    itreadmill = true;
    sch = 0;
  }
}
