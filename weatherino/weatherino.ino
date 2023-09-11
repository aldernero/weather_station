#include <ArduinoMqttClient.h>
#include <WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include "Adafruit_PM25AQI.h"
#include "SparkFun_AS3935.h"

#define INDOOR 0x12 
#define OUTDOOR 0xE
#define LIGHTNING_INT 0x08
#define DISTURBER_INT 0x04
#define NOISE_INT 0x01

// sensors
SparkFun_AS3935 lightning;
Adafruit_PM25AQI aqi = Adafruit_PM25AQI();

// Interrupt pin for lightning detection 
const int lightningInt = 4; 
int spiCS = 5; //SPI chip select pin

// This variable holds the number representing the lightning or non-lightning
// event issued by the lightning detector. 
int intVal = 0;
int noise = 7; // Value between 1-7 
int disturber = 10; // Value between 1-10

const long interval = 1000;
unsigned long previousMillis = 0;

void setup() {
  delay(100);
  Serial.begin(115200);
  while (!Serial) {
    ;
  }

  // Setup lightning detector
  // When lightning is detected the interrupt pin goes HIGH.
  pinMode(lightningInt, INPUT); 
  Serial.println("AS3935 Franklin Lightning Detector"); 
  SPI.begin(); 
  if( !lightning.beginSPI(spiCS) ){ 
    Serial.println ("Lightning Detector did not start up, freezing!"); 
    while(1); 
  }
  else
    Serial.println("Lightning Detector Ready!");
  lightning.setIndoorOutdoor(OUTDOOR);
  lightning.setNoiseLevel(noise);
  lightning.watchdogThreshold(disturber); 


  // Setup air quality sensor
  Serial.println("Adafruit PMSA003I Air Quality Sensor");
  if (! aqi.begin_I2C()) {      // connect to the sensor over I2C
    Serial.println("Could not find PM 2.5 sensor!");
    while (1) delay(10);
  }

  Serial.println("PM25 found!");

}

void loop() {

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    Serial.printf("data,%d,", currentMillis);
    // Lightning detector
    int signal = -1;
    int distance = -1;
    if(digitalRead(lightningInt) == HIGH){
      intVal = lightning.readInterruptReg();
      signal = int(intVal);
      if(intVal == LIGHTNING_INT){
        distance = int(lightning.distanceToStorm()); 
      }
    }
    Serial.printf("%d,%d,", signal, distance);

    // Air quality sensor
    PM25_AQI_Data data;
    
    bool hasAirQualityData = aqi.read(&data);
    if (hasAirQualityData) {
      Serial.printf("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n", data.pm10_standard, data.pm25_standard, data.pm100_standard, data.pm10_env, data.pm25_env, data.pm100_env, data.particles_03um, data.particles_05um, data.particles_10um, data.particles_25um, data.particles_50um, data.particles_100um);
    }
  }
}


