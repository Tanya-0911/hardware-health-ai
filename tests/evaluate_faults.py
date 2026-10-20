
import csv
import re
import sys
from pathlib import Path

# Locate the project root and import the diagnostic engine.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.diagnostics import analyze_readings


SCENARIOS_FILE = PROJECT_ROOT / "tests" / "fault_scenarios.csv"
RESULTS_FILE = PROJECT_ROOT / "reports" / "fault_evaluation_results.csv"


def expected_severity(voltage, current, temperature, anomaly=False):
    """Calculate expected severity using the configured demo thresholds."""

    # Critical thresholds must match app/diagnostics.py.
    if voltage < 4.5 or voltage > 5.5:
        return "CRITICAL"

    if current > 200:
        return "CRITICAL"

    if temperature > 45:
        return "CRITICAL"

    # Warning thresholds must match app/diagnostics.py.
    if voltage < 4.8 or voltage > 5.2:
        return "WARNING"

    if current > 170:
        return "WARNING"

    if temperature > 36:
        return "WARNING"

    if anomaly:
        return "WARNING"

    return "INFO"


def check_expected_findings(report, expected):
    """Check that every expected fault appears in the report."""

    expected = str(expected).strip().lower()

    if expected in ("none", "", "normal"):
        return (
            "No configured rule was triggered" in report
            and "Low voltage detected" not in report
            and "High voltage detected" not in report
            and "High current detected" not in report
            and "Elevated temperature detected" not in report
        )

    finding_map = {
        "voltage": [
            "Low voltage detected",
            "High voltage detected",
        ],
        "current": ["High current detected"],
        "temperature": ["Elevated temperature detected"],
    }

    expected_faults = [
        fault
        for fault in ("voltage", "current", "temperature")
        if fault in expected
    ]

    if not expected_faults:
        raise ValueError(
            f"Unknown expected_finding value: {expected!r}"
        )

    # All expected findings must be present.
    return all(
        any(
            finding in report
            for finding in finding_map[fault]
        )
        for fault in expected_faults
    )


def evaluate_scenarios():
    if not SCENARIOS_FILE.exists():
        raise FileNotFoundError(
            f"Scenario file not found: {SCENARIOS_FILE}"
        )

    results = []

    with SCENARIOS_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as csvfile:
        reader = csv.DictReader(csvfile)

        required_columns = {
            "scenario",
            "voltage_v",
            "current_ma",
            "temperature_c",
            "expected_finding",
        }

        if not reader.fieldnames or not required_columns.issubset(
            reader.fieldnames
        ):
            raise ValueError(
                "fault_scenarios.csv must contain these columns: "
                + ", ".join(sorted(required_columns))
            )

        for row in reader:
            scenario = row["scenario"].strip()

            voltage = float(row["voltage_v"])
            current = float(row["current_ma"])
            temperature = float(row["temperature_c"])

            anomaly = str(
                row.get("anomaly_detected", "false")
            ).strip().lower() in ("true", "yes", "1")

            readings = {
                "voltage_v": voltage,
                "current_ma": current,
                "power_mw": voltage * current,
                "temperature_c": temperature,
                "anomaly_detected": anomaly,
                "status": "TEST",
            }

            report = analyze_readings(
                readings,
                data_source="simulated",
            )

            # Extract the severity actually returned by the engine.
            match = re.search(
                r"## Severity:\s*(INFO|WARNING|CRITICAL)\b",
                report,
                re.IGNORECASE,
            )

            actual_severity = (
                match.group(1).upper() if match else "MISSING"
            )

            expected_level = expected_severity(
                voltage,
                current,
                temperature,
                anomaly,
            )

            finding_pass = check_expected_findings(
                report,
                row["expected_finding"],
            )

            severity_pass = actual_severity == expected_level
            overall_pass = finding_pass and severity_pass

            results.append({
                "scenario": scenario,
                "expected_finding": row["expected_finding"],
                "finding_pass": finding_pass,
                "expected_severity": expected_level,
                "actual_severity": actual_severity,
                "severity_pass": severity_pass,
                "overall_pass": overall_pass,
            })

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as csvfile:
        fieldnames = list(results[0].keys()) if results else [
            "scenario",
            "expected_finding",
            "finding_pass",
            "expected_severity",
            "actual_severity",
            "severity_pass",
            "overall_pass",
        ]

        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(results)

    print("\nHardware Fault Evaluation")
    print("=" * 95)

    if results:
        print(
            f"{'Scenario':<22}"
            f"{'Expected':<12}"
            f"{'Actual':<12}"
            f"{'Findings':<12}"
            f"{'Severity':<12}"
            f"{'Overall':<10}"
        )
        print("-" * 95)

        for result in results:
            print(
                f"{result['scenario']:<22}"
                f"{result['expected_severity']:<12}"
                f"{result['actual_severity']:<12}"
                f"{str(result['finding_pass']):<12}"
                f"{str(result['severity_pass']):<12}"
                f"{str(result['overall_pass']):<10}"
            )

    total = len(results)
    passed = sum(r["overall_pass"] for r in results)
    finding_passed = sum(r["finding_pass"] for r in results)
    severity_passed = sum(r["severity_pass"] for r in results)

    print("\nEvaluation Summary")
    print("-" * 35)
    print(f"Scenarios evaluated: {total}")
    print(f"Finding checks passed: {finding_passed}/{total}")
    print(f"Severity checks passed: {severity_passed}/{total}")
    print(f"Overall scenarios passed: {passed}/{total}")

    if total:
        print(f"Overall rule-check pass rate: {passed / total * 100:.1f}%")

    print(f"\nResults saved to: {RESULTS_FILE}")

    if passed != total:
        sys.exit(1)


if __name__ == "__main__":
    evaluate_scenarios()
