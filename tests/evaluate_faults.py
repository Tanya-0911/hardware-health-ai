
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.diagnostics import analyze_readings

DATA_FILE = "tests/fault_scenarios.csv"


def evaluate_scenario(row):
    readings = {
        "voltage_v": row["voltage_v"],
        "current_ma": row["current_ma"],
        "power_mw": row["voltage_v"] * row["current_ma"],
        "temperature_c": row["temperature_c"],
        "status": "NORMAL",
        "anomaly_detected": False,
    }

    report = analyze_readings(
        readings,
        data_source="simulated",
    ).lower()

    expected = row["expected_finding"]

    if expected == "none":
        passed = "no configured rule was triggered" in report
    else:
        expected_terms = {
            "current": ["current exceeds"],
            "temperature": ["temperature exceeds"],
            "voltage": ["voltage is below"],
        }

        if expected == "current_temperature_voltage":
            terms = (
                expected_terms["current"]
                + expected_terms["temperature"]
                + expected_terms["voltage"]
            )
        else:
            terms = expected_terms[expected]

        passed = all(term in report for term in terms)

    return passed


def main():
    df = pd.read_csv(DATA_FILE)
    df["passed"] = df.apply(evaluate_scenario, axis=1)

    print("\nFault Scenario Evaluation")
    print("=========================")
    print(df[["scenario", "expected_finding", "passed"]].to_string(index=False))

    total = len(df)
    passed = int(df["passed"].sum())
    percentage = (passed / total * 100) if total else 0

    print(f"\nScenarios passed: {passed}/{total}")
    print(f"Rule-check pass rate: {percentage:.1f}%")

    output = "reports/fault_evaluation_results.csv"
    df.to_csv(output, index=False)
    print(f"Results saved to: {output}")


if __name__ == "__main__":
    main()
