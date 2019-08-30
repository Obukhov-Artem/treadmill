void question(boolean itreadmill, boolean treadmill_init, int Speed, boolean stringComplete, String txtMsg) {
  if (itreadmill == false)
  {
    if (Speed > 0) {
      Speed = (Speed * 0,92).toInt;
      delay(50);
      if (Speed <= 0) Serial.println("treadmill");
    }
  }
  else
  {
    if (stringComplete)
    {
      if (txtMsg == "treadmill")
      {
        treadmill_init = true;
        }
    }
  }
  
}
