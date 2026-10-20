
def analyze_readings(readings, data_source="simulated"):
    """
    Generate a rule-based hardware diagnostic report.

    Expected reading keys:
        voltage_v, current_ma, power_mw, temperature_c
        Optional: anomaly_detected, status

    Note: Thresholds are illustrative and must be validated
    for the actual hardware before real-world use.
    """

    # --------------------------------------------------
    # 1. Read and normalize sensor values
    # --------------------------------------------------
    voltage = float(readings.get("voltage_v", 0.0))
    current = float(readings.get("current_ma", 0.0))
    temperature = float(readings.get("temperature_c", 0.0))

    # Use provided power, or calculate it if unavailable.
    power = float(
        readings.get("power_mw", voltage * current)
    )

    anomaly = readings.get("anomaly_detected", False)
    if isinstance(anomaly, str):
        anomaly = anomaly.strip().lower() in {
            "true", "yes", "1"
        }
    else:
        anomaly = bool(anomaly)

    source = str(data_source).strip().upper()
    status = str(readings.get("status", "UNKNOWN")).upper()

    # --------------------------------------------------
    # 2. Classify severity
    # --------------------------------------------------
    critical_reasons = []
    warning_reasons = []

    # Illustrative critical thresholds only.
    if voltage < 4.5 or voltage > 5.5:
        critical_reasons.append(
            "Voltage outside the illustrative critical range."
        )

    if current > 200:
        critical_reasons.append(
            "Current exceeds the illustrative critical threshold."
        )

    if temperature > 45:
        critical_reasons.append(
            "Temperature exceeds the illustrative critical threshold."
        )

    # Illustrative warning thresholds.
    if voltage < 4.8 or voltage > 5.2:
        warning_reasons.append(
            "Voltage is outside the configured normal range."
        )

    if current > 170:
        warning_reasons.append(
            "Current is above the configured normal range."
        )

    if temperature > 36:
        warning_reasons.append(
            "Temperature is above the configured normal range."
        )

    if critical_reasons:
        severity = "CRITICAL"
        severity_reasons = critical_reasons

    elif warning_reasons or anomaly:
        severity = "WARNING"
        severity_reasons = warning_reasons.copy()

        if anomaly:
            severity_reasons.append(
                "Statistical anomaly detected; this does not "
                "confirm hardware failure."
            )

    else:
        severity = "INFO"
        severity_reasons = [
            "No configured severity rule was triggered."
        ]

    # --------------------------------------------------
    # 3. Identify findings and recommended tests
    # --------------------------------------------------
    findings = []
    recommendations = []

    if voltage < 4.8:
        findings.append("Low voltage detected.")
        recommendations.append(
            "Check the power supply, wiring, and voltage drop "
            "under load."
        )

    elif voltage > 5.2:
        findings.append("High voltage detected.")
        recommendations.append(
            "Verify the supply voltage and confirm that it is "
            "within the component ratings."
        )

    if current > 170:
        findings.append("High current detected.")
        recommendations.append(
            "Inspect the load for excessive current draw, "
            "short circuits, or unexpected operating conditions."
        )

    if temperature > 36:
        findings.append("Elevated temperature detected.")
        recommendations.append(
            "Check sensor placement, airflow, and operating "
            "conditions; compare against the component datasheet."
        )

    if anomaly:
        findings.append(
            "The statistical anomaly detector flagged this reading."
        )
        recommendations.append(
            "Compare this reading with recent measurements and "
            "a validated baseline before concluding that a fault exists."
        )

    if not findings:
        findings.append(
            "No configured rule was triggered by this reading."
        )
        recommendations.append(
            "Continue monitoring and compare readings with a "
            "validated baseline."
        )

    # Remove duplicate recommendations while preserving order.
    recommendations = list(dict.fromkeys(recommendations))

    # --------------------------------------------------
    # 4. Format report sections
    # --------------------------------------------------
    severity_text = "\n".join(
        f"- {reason}" for reason in severity_reasons
    )

    findings_text = "\n".join(
        f"- {finding}" for finding in findings
    )

    recommendations_text = "\n".join(
        f"- {item}" for item in recommendations
    )

    # --------------------------------------------------
    # 5. Build final report
    # --------------------------------------------------

# severity_text = "\n".join(
#     f"- {reason}" for reason in severity_reasons
# )

    return f"""
# Hardware Diagnostic Report

**Data source:** {source}
## Severity: {severity}

{severity_text}

## 1. Observed readings

- Voltage: {voltage:.3f} V
- Current: {current:.2f} mA
- Power: {power:.2f} mW
- Temperature: {temperature:.2f} °C
- Anomaly flagged: {"Yes" if anomaly else "No"}
- Reported sensor status: {status}

## 2. Findings

{findings_text}

## 3. Recommended next tests

{recommendations_text}

## 4. Limitations and safety

- This is a rule-based demonstration, not a generative AI diagnosis.
- Thresholds are illustrative and must be validated for your circuit.
- A statistical anomaly does not prove a component has failed.
- {source} DATA: findings are demonstrations unless confirmed using real hardware.
- Do not use this report as a safety interlock or as the sole basis for operating decisions.
""".strip()
