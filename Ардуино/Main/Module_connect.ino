void Settings() {
  Serial.begin(115200);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("Loading");
  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT);
  pinMode(out3, OUTPUT);
  delay(1000);

}
