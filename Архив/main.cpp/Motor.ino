#ifndef H_Motor
#define H_Motor

// Подключаем библиотеки
#include <Arduino.h>
#include <AFMotor.h>

// Подключаем моторы
AF_DCMotor motor1(1);
AF_DCMotor motor2(2);
AF_DCMotor motor3(3);
AF_DCMotor motor4(4);

// Задаем скорость ШИМ
int maxSpeed = 255;
int mediumSpeed = 150;
int minSpeed = 0;

void moveForwardFull()
{
  motor1.setSpeed(maxSpeed);
  motor1.run(FORWARD);
  motor2.setSpeed(maxSpeed);
  motor2.run(FORWARD);
  motor3.setSpeed(maxSpeed);
  motor3.run(FORWARD);
  motor4.setSpeed(maxSpeed);
  motor4.run(FORWARD);
}

void moveForwardSlow()
{
  motor1.setSpeed(mediumSpeed);
  motor1.run(FORWARD);
  motor2.setSpeed(mediumSpeed);
  motor2.run(FORWARD);
  motor3.setSpeed(mediumSpeed);
  motor3.run(FORWARD);
  motor4.setSpeed(mediumSpeed);
  motor4.run(FORWARD);
}

void moveBackwardFull()
{
  motor1.setSpeed(maxSpeed);
  motor1.run(BACKWARD);
  motor2.setSpeed(maxSpeed);
  motor2.run(BACKWARD);
  motor3.setSpeed(maxSpeed);
  motor3.run(BACKWARD);
  motor4.setSpeed(maxSpeed);
  motor4.run(BACKWARD);
}

void moveBackwardSlow()
{
  motor1.setSpeed(mediumSpeed);
  motor1.run(BACKWARD);
  motor2.setSpeed(mediumSpeed);
  motor2.run(BACKWARD);
  motor3.setSpeed(mediumSpeed);
  motor3.run(BACKWARD);
  motor4.setSpeed(mediumSpeed);
  motor4.run(BACKWARD);
}

void moveLeftFull()
{
  motor1.setSpeed(mediumSpeed);
  motor1.run(BACKWARD);
  motor2.setSpeed(maxSpeed);
  motor2.run(FORWARD);
  motor3.setSpeed(maxSpeed);
  motor3.run(FORWARD);
  motor4.setSpeed(mediumSpeed);
  motor4.run(BACKWARD);
}

void moveLeftSlow()
{
  motor1.setSpeed(mediumSpeed);
  motor1.run(FORWARD);
  //motor2.setSpeed(mediumSpeed);
  motor2.run(RELEASE);
  //motor3.setSpeed(mediumSpeed);
  motor3.run(RELEASE);
  motor4.setSpeed(mediumSpeed);
  motor4.run(FORWARD);
}

void moveRightFull()
{
motor1.setSpeed(maxSpeed);
  motor1.run(FORWARD);
  motor2.setSpeed(mediumSpeed);
  motor2.run(BACKWARD);
  motor3.setSpeed(mediumSpeed);
  motor3.run(BACKWARD);
  motor4.setSpeed(maxSpeed);
  motor4.run(FORWARD);
}

void moveRightSlow()
{
  //motor1.setSpeed(mediumSpeed);
  motor1.run(RELEASE);
  motor2.setSpeed(mediumSpeed);
  motor2.run(FORWARD);
  motor3.setSpeed(mediumSpeed);
  motor3.run(FORWARD);
  //motor4.setSpeed(mediumSpeed);
  motor4.run(RELEASE);
}

void moveStop()
{
  //motor1.setSpeed(mediumSpeed);
  motor1.run(RELEASE);
  //motor2.setSpeed(mediumSpeed);
  motor2.run(RELEASE);
  //motor3.setSpeed(mediumSpeed);
  motor3.run(RELEASE);
  //motor4.setSpeed(mediumSpeed);
  motor4.run(RELEASE);
}

#endif
