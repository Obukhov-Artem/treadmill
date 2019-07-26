int symbol = 33;
String txtMsg;
String NewText;
boolean stringComplete = false;

void setup() {
  Serial.begin(115200);
  Serial.println("Loading");
  delay(1000);
}

void loop() {
  if (stringComplete)
  {
    Serial.println(txtMsg);
    stringComplete = false;
    txtMsg = "";
  }
}
char inChar;


void serialEvent()
{
  while (Serial.available())
  {
    char inChar = (char)Serial.read();
    txtMsg += inChar;
    if (inChar == '.') stringComplete = true;
  }
}
