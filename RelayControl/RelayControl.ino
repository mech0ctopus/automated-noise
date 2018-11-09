//Connect Relay Control Pins (relay board) to Digital pins (Arduino) as defined below
//M1: Module 1, M2: Module 2
//Wire VCC (relay board) to 5.5V (Arduino)
//Wire GND (relay board) to  GND in power section (Arduino)

//To do:
//End loop after all relays have been tested (move loop to setup, leave empty loop)

//Define array of Arduino Pins
int M1relayPins[]={1, 2, 3, 4, 5, 6, 7, 8};
int M2relayPins[]={22, 24, 26, 28, 30, 32, 34, 36};
int relayCount=8; //length of relayPins (must be same for M1 & M2)

//Define sample time interval (msec)
int SAMPLE_TIME = 40000;
//Define time delay interval (msec) between relays
int TIME_DELAY = 1000;
//Initiazize current time variable
unsigned int currentMillis;
//Initialize previous time variable
int previousMillis = 0;

void setup() {
  //Open Serial port at 9600 Baud
  //Serial.begin(9600);
  //Initialize each pin as output
  for (int currentRelay=1; currentRelay < (relayCount+1); currentRelay++) {
    //M1relayPins & M2relayPins elements are numbered from 0 to (relayCount-1)
    pinMode(M1relayPins[currentRelay-1], OUTPUT); 
    pinMode(M2relayPins[currentRelay-1], OUTPUT); 
    //Open N.O. relays on M1 and M2
    digitalWrite(M1relayPins[currentRelay-1], HIGH);
    digitalWrite(M2relayPins[currentRelay-1], HIGH);
  }
}

void loop() {
  //Turn each relay on and off
  for (int currentRelay=1; currentRelay < (relayCount+1); currentRelay++) {   
    //Close N.O. relay
    digitalWrite(M1relayPins[currentRelay-1], LOW);
    digitalWrite(M2relayPins[currentRelay-1], LOW);
    //Define current time
    currentMillis = millis();

    //Delay while waiting for SAMPLE_TIME to finish
    do
    {
      delay(5); //Delay 0.005s
      //Define current time
      currentMillis = millis();

      //Serial.print("current time: ");
      //Serial.print(currentMillis);
      //Serial.print(", reference time: ");
      //Serial.print(previousMillis);
      //Serial.print(", Diff: ");
      //Serial.print(currentMillis-previousMillis);
      //Serial.println("");
     
      if((currentMillis-previousMillis)>=SAMPLE_TIME){
        break;
      }
    } while((currentMillis-previousMillis)<SAMPLE_TIME);
    
    //Open N.O. relay
    digitalWrite(M1relayPins[currentRelay-1], HIGH);
    digitalWrite(M2relayPins[currentRelay-1], HIGH);
    //Delay in between relays
    delay(TIME_DELAY);
    //Define new reference time
    previousMillis=currentMillis;

  }
}
