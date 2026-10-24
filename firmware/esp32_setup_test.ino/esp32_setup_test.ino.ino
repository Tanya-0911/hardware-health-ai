
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// ESP32 pin configuration
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#define ONE_WIRE_PIN 16

// Illustrative demo thresholds only
#define LOW_VOLTAGE_V 4.8
#define HIGH_VOLTAGE_V 5.2
#define HIGH_CURRENT_MA 170.0
#define HIGH_TEMPERATURE_C 36.0

Adafruit_INA219 ina219;
OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature temperatureSensor(&oneWire);

bool ina219Ready = false;
bool temperatureSensorReady = false;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  Serial.println("Smart Hardware Health Monitor");
  Serial.println("Starting sensor initialization...");

  ina219Ready = ina219.begin();

  temperatureSensor.begin();
  temperatureSensorReady =
      temperatureSensor.getDeviceCount() > 0;

  Serial.printf(
      "INA219: %s\n",
      ina219Ready ? "READY" : "NOT DETECTED"
  );

  Serial.printf(
      "DS18B20: %s\n",
      temperatureSensorReady ? "READY" : "NOT DETECTED"
  );

  if (ina219Ready && temperatureSensorReady) {
    Serial.println("Sensor initialization successful.");
  } else {
    Serial.println(
        "Connect sensors before testing live telemetry."
    );
  }
}

void loop() {
  // Hardware is not connected yet, so don't fabricate readings.
  if (!ina219Ready || !temperatureSensorReady) {
    delay(2000);
    return;
  }

  temperatureSensor.requestTemperatures();

  float temperatureC =
      temperatureSensor.getTempCByIndex(0);

  float voltageV = ina219.getBusVoltage_V();
  float currentMA = ina219.getCurrent_mA();

  if (temperatureC == DEVICE_DISCONNECTED_C ||
      isnan(temperatureC) ||
      isnan(voltageV) ||
      isnan(currentMA)) {
    Serial.println("Invalid sensor reading; check wiring.");
    delay(2000);
    return;
  }

  float powerMW = voltageV * currentMA;

  const char* status = "NORMAL";

  if (voltageV < LOW_VOLTAGE_V ||
      voltageV > HIGH_VOLTAGE_V ||
      currentMA > HIGH_CURRENT_MA ||
      temperatureC > HIGH_TEMPERATURE_C) {
    status = "WARNING";
  }

  // One JSON object per line, compatible with serial_reader.py.
  Serial.printf(
      "{\"voltage_v\":%.3f,"
      "\"current_ma\":%.2f,"
      "\"power_mw\":%.2f,"
      "\"temperature_c\":%.2f,"
      "\"status\":\"%s\"}\n",
      voltageV,
      currentMA,
      powerMW,
      temperatureC,
      status
  );

  delay(2000);
}
