void working(String txtMsg,boolean treadmill_init, boolean nazad) {
   if (treadmill_init = false)
         {
        Speed = txtMsg.toInt();
        motor(Speed,nazad);    
                      }
   Serial.println(Speed);
   }
