#define out1 2
#define out2 3
#define out3 5

int symbol = 33;
String txtMsg;
String bill = "treadmill";
String NewText;
boolean stringComplete = false;
int t = 0;
int Speed = 0;
void setup() {
  Serial.begin(115200);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("Loading");
  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT);
  pinMode(out3, OUTPUT);
  delay(1000);
}

void loop() {
  if (txtMsg == 0){
    digitalWrite(LED_BUILTIN, HIGH);
    }
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
      Speed = txtMsg.toInt();
      digitalWrite(out1, LOW);
      digitalWrite(out2, HIGH);
      analogWrite(out3, Speed);
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
    if (inChar == '.') stringComplete = true;
    else txtMsg += inChar;
  }
}
