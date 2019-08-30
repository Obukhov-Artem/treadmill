String txtMsg;
boolean stringComplete = false;

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

  Serial.begin(115200);
  Serial.println("Loading");
  delay(2000);

  Serial.println("Programm load");
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() 
{
  if (stringComplete) 
  {
    Serial.println(txtMsg);
    if (txtMsg == "ForwardFull.")
        moveForwardFull();

      if (txtMsg == "ForwardSlow.")
        moveForwardSlow();

      if (txtMsg == "LeftFull.")
        moveLeftFull();

      if (txtMsg == "LeftSlow.")
        moveLeftSlow();

      if (txtMsg == "RightFull.")
        moveRightFull();

      if (txtMsg == "RightSlow.")
        moveRightSlow();

      if (txtMsg == "BackwardFull.")
        moveBackwardFull();

      if (txtMsg == "BackwardSlow.")
        moveBackwardSlow();

      if (txtMsg == "Stop.")
        moveStop();
    stringComplete = false;
    txtMsg = "";
  }
}

void serialEvent() 
{
  while (Serial.available()) 
  {
    char inChar = (char)Serial.read();
    txtMsg += inChar;
    if (inChar == '.') stringComplete = true;
  }
}
