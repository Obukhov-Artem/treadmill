int symbol = 33;
String txtMsg;
String bill = "treadmill";
String NewText;
boolean stringComplete = false;
int t = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Loading");
  delay(1000);
}

void loop() {
  if (t <= 1)
  {
    Serial.println(bill);
    t += 1;
  }
  else
  {
    bill="";
    if (stringComplete)
    {
      Serial.println(txtMsg);
      stringComplete = false;
      txtMsg = "";
    }
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
