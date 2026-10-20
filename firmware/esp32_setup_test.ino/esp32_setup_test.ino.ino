
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// Temporary serial telemetry test.
// Sensor libraries are retained for the next hardware stage.

const unsigned long SEND_INTERVAL_MS = 2000;
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  randomSeed(micros());

  Serial.println("Smart Hardware Health Monitor");
  Serial.println("ESP32 telemetry test starting...");
}

void loop() {
  unsigned long now = millis();

  if (now - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = now;

    // Temporary simulated values, not sensor measurements.
    float voltage = random(480, 521) / 100.0f;
    float current = random(80, 181);
    float temperature = random(280, 381) / 10.0f;
    float power = voltage * current;

    StaticJsonDocument<256> doc;

    doc["voltage_v"] = voltage;
    doc["current_ma"] = current;
    doc["power_mw"] = power;
    doc["temperature_c"] = temperature;

    if (temperature > 36.0f || current > 170.0f) {
      doc["status"] = "WARNING";
    } else {
      doc["status"] = "NORMAL";
    }

    // One JSON object per line for Python serial_reader.py.
    serializeJson(doc, Serial);
    Serial.println();
  }
}
