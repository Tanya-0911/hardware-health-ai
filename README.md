GenAI-Based Smart Hardware Health Monitoring and Failure Analysis Assistant

Project status: Design and implementation roadmap. The hardware, firmware, trained model, dashboard, and performance results are not yet complete. This README describes the intended prototype and defines what should be demonstrated before making accuracy claims.

Why build it? Hardware faults often produce indirect symptoms: a rise in current, a voltage drop, a hot component, or unusual vibration. A single threshold can flag one symptom but rarely explains the cause. HardwareSage correlates multiple measurements and produces a diagnostic report that distinguishes observations, possible causes, and recommended checks.

The initial target is a low-voltage DC motor and driver board. It provides repeatable operating conditions and safe, measurable fault scenarios. The same architecture could later monitor other embedded boards after adapting the sensors and baseline model. Planned features

Live voltage, current, power, temperature, and optional vibration monitoring.
Timestamped telemetry collection and visual trends.
Rule-based alerts for explicit operating limits.
Anomaly detection trained on normal operating data.
GenAI-generated explanations tied to actual readings and documented fault signatures.
Diagnostic reports showing severity, evidence, possible causes, and next tests.
Evaluation against labeled fault-injection runs and a rule-based baseline. Diagnostic boundary: An anomaly score shows that behavior differs from the baseline. The assistant presents hypotheses; it cannot prove that a specific component failed solely from these sensors. Immediate protection decisions must come from deterministic firmware rules, independently of the GenAI service. System architecture

The controller samples sensors and sends timestamped records to the backend.
The backend stores readings and computes rolling features such as mean current, voltage sag, temperature slope, and vibration RMS.
Rules check known limits; an anomaly model compares recent behavior with healthy runs.
The assistant receives a compact evidence packet and a curated troubleshooting guide. It returns a structured report with uncertainty and suggested verification steps. Hardware plan Part Purpose Notes ESP32 development board Data acquisition and Wi-Fi Use a stable USB supply during development. INA219 module Bus voltage and shunt current Place in series with the monitored low-voltage supply; check the module's shunt and current rating. Contact temperature sensor Driver or board temperature Attach near the component of interest, with electrical insulation as needed. Small DC motor and suitable driver Device under test Use a separate, appropriately rated motor supply. Accelerometer, optional Motor vibration Add after electrical and thermal sensing work reliably. BME280, optional Ambient temperature and humidity Ambient temperature is context, not a direct measurement of driver junction temperature.
Example signal map Signal Connection INA219 SDA/SCL ESP32 I²C bus, for example GPIO 21/22 on a compatible development board Temperature sensor GPIO or I²C according to the selected device Accelerometer SDA/SCL Shared I²C bus if supported, with a nonconflicting address Motor supply Through the correctly rated current-sensing path to the driver ESP32 ground Common reference with the monitored low-voltage circuit where required

Verify the exact board pinout, voltage levels, sensor addresses, supply limits, and driver wiring before assembly. Do not connect a motor directly to an ESP32 GPIO or use mains-powered equipment for fault injection. Software stack (planned) Layer Proposed choice Firmware ESP-IDF or Arduino framework for ESP32 Transport Local Wi-Fi with HTTP or MQTT Backend Python and FastAPI Storage SQLite for a single-device prototype Analysis Python, pandas, scikit-learn Dashboard Streamlit GenAI Configurable LLM API with structured JSON output

These choices are a starting point, not a claim that the corresponding modules are already implemented. Keep API credentials only on the backend, in environment variables; never embed them in firmware or commit them to Git.

The LLM input should contain the numerical evidence, operating state, model output, and relevant troubleshooting notes. Reject invented measurements and require the report to say when evidence is insufficient. Fault scenarios for the prototype Scenario Expected observable evidence Caveat Healthy operation Stable readings within the normal range Capture at multiple loads. Increased mechanical load Often higher current and temperature Confirm under controlled, limited load. Supply undervoltage Lower measured bus voltage Behavior depends on the motor driver. Cooling restriction Rising board temperature Do not exceed rated temperatures. Added vibration Change in vibration features Requires the optional accelerometer. Sensor disconnect Missing or invalid readings Treat as a sensor fault, not a DUT fault.

Use controlled, reversible conditions and stop each run before equipment ratings are approached. Label data by the injected condition, not by an assumed internal failure mechanism. Development roadmap

Hardware bring-up: Read each sensor independently and log calibrated readings with units.
Data collection: Capture repeated healthy runs across idle, start-up, and steady operation; record operating state and load.
Rules: Add missing-sensor, overcurrent, undervoltage, and overtemperature alerts with documented limits.
Fault dataset: Collect repeated runs for each controlled condition, with run IDs and timestamps.
Anomaly model: Train on healthy runs, select a threshold using validation runs, and evaluate on held-out runs.
Assistant: Generate evidence-linked reports from structured inputs and a small fault guide.
Dashboard: Show trends, alerts, annotated events, and downloadable reports.
Evaluation: Compare model and rules; publish plots, confusion matrix, latency, and limitations. Planned repository layout HardwareSage/ ├── firmware/ # ESP32 sensor acquisition and transport ├── backend/ # Ingestion, storage, alerts, report API ├── analysis/ # Feature extraction, training, evaluation ├── dashboard/ # Live plots and reports ├── docs/ # Wiring, calibration, fault guide, architecture ├── data/README.md # Dataset format and collection procedure ├── tests/ # Parser, feature, and report-contract tests ├── .env.example # Variable names only; no secrets └── README.md Reproducibility target: Once implementation exists, document the exact board variant, firmware commands, wiring diagram, sensor calibration, Python dependencies, backend/dashboard start commands, and a small sample dataset here. No installation commands are listed yet because the project code has not been created. Evaluation plan Split data by run, rather than randomly splitting adjacent samples from the same run. Report:
Fault detection precision, recall, F1, and false alarms per hour.
Results for each injected condition and for normal operation.
Detection delay from the start of a condition to an alert.
Performance under different loads and ambient temperatures.
Diagnostic quality: whether the report cites real measurements, expresses uncertainty, and proposes discriminating tests.
A comparison with simple threshold rules using the same held-out runs. Never present generated or synthetic data as a physical experiment. Publish the sampling interval, sensor calibration method, labeling method, train/test split, and raw run metadata alongside any claimed results. VLSI and embedded-systems relevance This project applies measurement, power monitoring, thermal analysis, signal processing, fault classification, and evidence-based debugging to a physical embedded system. It is a practical bridge between hardware engineering and GenAI. The prototype monitors board-level behavior; chip-level fault localization would require additional instrumentation and validation. Future extensions
Deploy a compact anomaly model on the microcontroller for offline detection.
Add a PCB or regulator health-monitoring target with rail ripple and thermal measurements.
Link reports to schematics, datasheets, and board-specific troubleshooting procedures.
Track drift across devices and operating conditions. References
Espressif ESP-IDF getting started guide
Texas Instruments INA219 product and documentation
Bosch Sensortec BME280 product page
Edge Impulse anomaly detection overview
