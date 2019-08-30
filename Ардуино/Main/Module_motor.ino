void motor(int Speed, boolean nazad)
        {
          digitalWrite(out2, LOW);
          digitalWrite(out1, HIGH);
        }
        if (nazad == true)
        {
          digitalWrite(out1, LOW);
          digitalWrite(out2, HIGH);
        }
        analogWrite(out3, Speed);
