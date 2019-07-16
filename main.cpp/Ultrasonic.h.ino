#ifndef H_Ultrasonic
#define H_Ultrasonic

#include <Arduino.h>

// Определение дистанции до объекта в см
int readDistance(int trig, int echo)
{
  int distance = 10000;
  
  while ((distance > 1000) || (distance == 0))
  {  
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);

    distance = pulseIn(echo, HIGH) * 1.7 * 0.01;
  }
  
  Serial.print("distance cm = ");
  Serial.println(distance);
  
  return distance;
}

#endif
