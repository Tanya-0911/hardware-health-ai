
def analyze_readings(readings, data_source="simulated"):
    """
    Free, rule-based diagnostic assistant.
    Does not call any external API.
    """

    voltage = float(readings.get("voltage_v", 0))
    current = float(readings.get("current_ma", 0))
    power = float(readings.get("power_mw", voltage * current))
    temperature = float(readings.get("temperature_c", 0))
    anomaly = bool(readings.get("anomaly_detected", False))
    status = str(readings.get("status", "UNKNOWN")).upper()

    findings = []
    recommendations = []

    # These are illustrative thresholds for our simulator.
    # Calibrate them for your actual circuit before hardware use.
    if voltage < 4.8:
        findings.append(
            "Voltage is below the illustrative 4.8 V threshold."
        )
        recommendations.append(
            "Check the supply voltage, wiring, and connections."
        )
    elif voltage > 5.2:
        findings.append(
            "Voltage is above the illustrative 5.2 V threshold."
        )
        recommendations.append(
            "Verify the supply voltage using a suitable multimeter."
        )

    if current > 170:
        findings.append(
            "Current exceeds the simulator's illustrative 170 mA threshold."
        )
        recommendations.append(
            "Check the load rating and compare current with its expected value."
        )

    if temperature > 36:
        findings.append(
            "Temperature exceeds the simulator's illustrative 36 °C threshold."
        )
        recommendations.append(
            "Check sensor placement and compare the reading with a reference thermometer."
        )

    if anomaly:
        findings.append(
            "The statistical anomaly detector flagged this reading."
        )
        recommendations.append(
            "Compare this reading with nearby readings and investigate the largest changes."
        )

    if status == "WARNING" and not findings:
        findings.append(
            "The input status is WARNING, but no specific rule was triggered."
        )

    if not findings:
        findings.append(
            "No configured rule was triggered by this reading."
        )
        recommendations.append(
            "Continue monitoring and compare readings with a validated baseline."
        )

    source_note = (
        "SIMULATED DATA: findings are demonstrations, not real hardware diagnoses."
        if data_source == "simulated"
        else
        "HARDWARE DATA: verify sensor accuracy and circuit specifications before acting."
    )

    return f"""
# Hardware Diagnostic Report

**Data source:** {data_source.upper()}

## 1. Observed readings
- Voltage: {voltage:.3f} V
- Current: {current:.2f} mA
- Power: {power:.2f} mW
- Temperature: {temperature:.2f} °C
- Anomaly flagged: {"Yes" if anomaly else "No"}

## 2. Findings
""" + "\n".join(f"- {item}" for item in findings) + """

## 3. Recommended next tests
""" + "\n".join(f"- {item}" for item in recommendations) + f"""

## 4. Limitations and safety
- This is a rule-based demonstration, not a generative AI diagnosis.
- Thresholds are illustrative and must be validated for your circuit.
- A statistical anomaly does not prove a component has failed.
- {source_note}
"""


if __name__ == "__main__":
    sample = {
        "voltage_v": 4.80,
        "current_ma": 178.0,
        "power_mw": 854.4,
        "temperature_c": 37.4,
        "status": "WARNING",
        "anomaly_detected": True,
    }

    print(analyze_readings(sample, data_source="simulated"))
