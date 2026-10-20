# Smart Hardware Health Monitor & Failure Analysis Assistant

**An embedded systems and hardware diagnostics project combining sensor telemetry, anomaly detection, rule-based fault analysis, and an interactive monitoring dashboard.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/ESP32-Integration%20in%20progress-E7352C?logo=espressif&logoColor=white" alt="ESP32"/>
  <img src="https://img.shields.io/badge/Testing-5%2F5%20scenarios%20passed-brightgreen" alt="Test results"/>
  <img src="https://img.shields.io/badge/Status-Prototype-orange" alt="Prototype"/>
</p>

## Overview

The **Smart Hardware Health Monitor & Failure Analysis Assistant** is a prototype designed to monitor electronic hardware operating conditions, identify potentially abnormal measurements, and generate structured diagnostic reports.

The project combines embedded hardware monitoring concepts with Python-based data analysis. It currently supports simulated telemetry, an interactive Streamlit dashboard, statistical anomaly detection, rule-based diagnostics, severity classification, and automated fault-scenario evaluation.

The planned hardware implementation uses an ESP32 microcontroller with voltage/current monitoring and temperature sensing. A future extension will explore semiconductor device analysis using Sentaurus TCAD simulation data.

The goal is to build a demonstrable engineering project at the intersection of **Embedded Systems, Hardware Diagnostics, Data Analysis, and Semiconductor Device Engineering**.

## Key Features

- **Live-style telemetry dashboard:** Displays voltage, current, power, and temperature measurements.
- **Telemetry simulation:** Generates synthetic sensor readings for development without physical hardware.
- **Time-series visualization:** Uses Plotly to visualize changes in monitored parameters.
- **Statistical anomaly detection:** Uses an Isolation Forest model when enough readings are available.
- **Rule-based fault analysis:** Identifies configured voltage, current, and temperature threshold violations.
- **Severity classification:** Assigns `INFO`, `WARNING`, or `CRITICAL` based on configurable demonstration thresholds.
- **Diagnostic report generation:** Produces structured reports containing observations, findings, recommended tests, and limitations.
- **Report export:** Supports downloading diagnostic reports from the dashboard.
- **Automated testing:** Checks diagnostic findings and severity classification against predefined fault scenarios.
- **ESP32 serial reader:** A Python module has been prepared to receive newline-delimited JSON telemetry over USB serial.

> **Current status:** The software prototype and simulated fault evaluation are implemented. Physical ESP32/sensor integration, real-hardware validation, and Sentaurus TCAD integration remain planned work. The current diagnostic engine is rule-based, not a generative AI diagnostic system.

## System Architecture

```text
              Synthetic Telemetry
                      |
                      v
             Telemetry Data (CSV)
                      |
                      v
             Python Data Pipeline
                      |
             +--------+--------+
             |                 |
             v                 v
      Anomaly Detection   Rule-Based Analysis
             |                 |
             +--------+--------+
                      |
                      v
              Severity Assessment
                      |
                      v
              Diagnostic Report
                      |
                      v
             Streamlit Dashboard
```

### Planned hardware data path

```text
Voltage / Current Sensor + Temperature Sensor
                      |
                      v
                    ESP32
                      |
                 USB Serial
                      |
                      v
             Python Serial Reader
                      |
                      v
              Telemetry Pipeline
                      |
                      v
           Dashboard and Diagnostics
```

The serial reader is implemented and import-tested. End-to-end communication with a physical ESP32 has not yet been validated.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Dashboard | Streamlit |
| Data processing | Pandas, NumPy |
| Visualization | Plotly |
| Anomaly detection | Scikit-learn Isolation Forest |
| Serial communication | PySerial |
| Diagnostic logic | Python rule-based engine |
| Embedded platform | ESP32 — integration pending |
| Planned current/voltage sensing | INA219 |
| Planned temperature sensing | DS18B20 |
| Planned semiconductor analysis | Synopsys Sentaurus TCAD |

## Project Structure

```text
hardware-health-ai/
│
├── app/
│   ├── dashboard.py
│   ├── simulate_sensor.py
│   ├── diagnostics.py
│   └── serial_reader.py
│
├── firmware/
│   └── esp32_setup_test.ino
│
├── data/
│   └── simulated_telemetry.csv
│
├── reports/
│   └── fault_evaluation_results.csv
│
├── tests/
│   ├── test_diagnostics.py
│   ├── fault_scenarios.csv
│   └── evaluate_faults.py
│
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

*Note: Generated CSV files and `.env` may be excluded from Git by `.gitignore`. The tree represents the intended project organization; only files actually committed will appear in the repository.*

## Getting Started

### 1. Prerequisites

Install the following:

- Python 3.11 or a compatible Python version
- Git
- Visual Studio Code or another Python editor

Physical hardware is not required to run the software prototype.

### 2. Clone the repository

Replace the URL below with your actual public repository URL if the repository name or visibility differs.

```bash
git clone https://github.com/Tanya-0911/hardware-health-ai.git
cd hardware-health-ai
```

### 3. Create and activate a virtual environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If dependencies have not yet been recorded in `requirements.txt`, install the packages used by the application:

```bash
pip install streamlit pandas numpy plotly scikit-learn pyserial
```

### 5. Generate simulated telemetry

Open a terminal in the project root and run:

```bash
python app/simulate_sensor.py
```

The simulator generates synthetic voltage, current, power, and temperature readings and saves them to:

```text
data/simulated_telemetry.csv
```

Keep the simulator running while you explore the dashboard.

### 6. Launch the dashboard

Open another terminal, activate the same virtual environment, and run:

```bash
streamlit run app/dashboard.py
```

Open the local URL printed in the terminal by Streamlit.

The dashboard displays the available readings, time-series charts, anomaly information, and diagnostic reporting interface.

### 7. Generate a diagnostic report

Use the **Generate Diagnostic Report** button in the dashboard.

The report includes:

- Observed voltage, current, power, and temperature
- Severity classification
- Detected rule-based findings
- Recommended next tests
- Limitations and safety notes

The current report generation uses local rules and does not require an OpenAI API key.

## Diagnostic and Severity Logic

The prototype uses illustrative thresholds to demonstrate how measurement-based diagnostics can work.

| Parameter | Illustrative normal range | Warning condition | Critical condition |
|---|---|---|---|
| Voltage | 4.8–5.2 V | Below 4.8 V or above 5.2 V | Below 4.5 V or above 5.5 V |
| Current | At or below 170 mA | Above 170 mA | Above 200 mA |
| Temperature | At or below 36 °C | Above 36 °C | Above 45 °C |

Severity is assigned according to the highest applicable configured threshold:

- `INFO` — no configured warning or critical threshold is crossed and no statistical anomaly is flagged.
- `WARNING` — at least one warning threshold is crossed, or the anomaly detector flags the reading.
- `CRITICAL` — at least one critical threshold is crossed.

**These are demonstration thresholds, not universal hardware safety limits.** They must be validated against the actual sensor accuracy, power supply, monitored load, and component datasheets before real hardware use.

## Anomaly Detection

The dashboard includes a statistical anomaly detection stage using Scikit-learn's Isolation Forest.

The model is intended to help identify measurements that differ from the observed data distribution. It complements the rule-based diagnostic engine rather than replacing it.

An anomaly flag does not, by itself, establish that a component has failed. Performance on synthetic data also does not establish detection accuracy on real hardware.

## Automated Testing

Run the unit tests:

```bash
python -m unittest tests.test_diagnostics -v
```

Run the fault-scenario evaluator:

```bash
python tests/evaluate_faults.py
```

### Current evaluation results

| Test | Result |
|---|---:|
| Diagnostic unit tests | 3/3 passed |
| Predefined fault scenarios | 5/5 passed |
| Finding checks | 5/5 passed |
| Severity checks | 5/5 passed |
| Overall synthetic rule-check pass rate | 100% |

The five predefined scenarios cover normal readings, high current, high temperature, low voltage, and a combined warning-level fault.

The evaluator writes its results to:

```text
reports/fault_evaluation_results.csv
```

These results demonstrate consistency with the configured rules on the tested synthetic inputs. They are **not a measurement of real-world fault-detection accuracy**. The current scenario set also needs a critical-level test to verify the `CRITICAL` path automatically.

## ESP32 Integration

The planned hardware version will use an ESP32 to collect telemetry from external sensors.

### Planned components

- ESP32 development board
- INA219 voltage/current monitoring module
- DS18B20 temperature sensor
- Suitable low-voltage test load
- Breadboard and jumper wires
- Appropriate power supply and required pull-up resistor

### Planned communication format

The Python serial reader expects one JSON telemetry message per line, for example:

```json
{
  "voltage_v": 5.0,
  "current_ma": 100.0,
  "power_mw": 500.0,
  "temperature_c": 30.0,
  "status": "NORMAL"
}
```

The ESP32 firmware will need to transmit a compatible format over USB serial, normally at 115200 baud.

### Planned integration milestones

1. Implement and test the ESP32 sensor-reading firmware.
2. Transmit newline-delimited JSON readings over USB serial.
3. Verify the serial data format and sensor values.
4. Connect the serial reader to the dashboard.
5. Compare simulated and measured telemetry.
6. Validate thresholds and diagnostic behavior using safe, controlled tests.

Physical integration and real-sensor validation are not yet complete.

## Future Work

### 1. Embedded hardware integration
Connect the ESP32 to the monitoring sensors and verify the full sensor-to-dashboard pipeline.

### 2. Improved fault evaluation
Add critical-level scenarios, boundary-value tests, invalid sensor readings, and tests for missing or malformed serial data.

### 3. Semiconductor device analysis
Extend the project to process Sentaurus TCAD MOSFET simulation results, such as transfer characteristics (\(I_D\) versus \(V_G\)).

Potential device metrics include threshold voltage, on-current, off-current, transconductance, and subthreshold swing. Extraction methods will need to be chosen and validated for the simulated device and its bias conditions.

### 4. GenAI-assisted failure analysis
Explore an optional AI-assisted explanation layer that summarizes measured evidence, suggests further diagnostic tests, and explains potential failure mechanisms. This extension will require a configured model/API and careful validation.

### 5. Validation and reporting
Compare predictions with known test cases, document false positives and false negatives, and evaluate the system on measured data before making reliability claims.

## Safety Considerations

- Use only suitable low-voltage DC supplies for initial testing.
- Do not connect mains voltage or unsafe fault-injection circuits to the prototype.
- Do not route monitored load current through the ESP32's 3.3 V pin.
- Verify sensor wiring, current ratings, grounding, and component datasheets.
- Treat thresholds as provisional until validated.
- Do not use this prototype as a safety interlock or as the sole basis for operating decisions.

## Limitations

- Current telemetry can be simulated rather than measured.
- The diagnostic engine is rule-based and is not currently a generative AI system.
- Statistical anomalies do not prove component failure.
- Thresholds are illustrative and are not validated for a specific physical circuit.
- Physical ESP32/sensor integration has not been verified.
- Sentaurus TCAD integration remains future work.
- The current automated evaluation covers five predefined synthetic scenarios.

## Project Summary

This project demonstrates a modular approach to hardware health monitoring by combining telemetry generation, visualization, statistical anomaly detection, rule-based diagnostics, severity classification, and automated testing.

Its next development stage is to connect real ESP32 sensor data to the existing software pipeline, validate the diagnostics against controlled measurements, and explore semiconductor device analysis and AI-assisted failure explanations.
