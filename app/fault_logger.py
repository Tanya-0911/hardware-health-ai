
import csv
from datetime import datetime
from pathlib import Path

# Resolve paths relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
FAULT_LOG = REPORTS_DIR / "fault_events.csv"

FIELDNAMES = [
    "timestamp",
    "data_source",
    "severity",
    "voltage_v",
    "current_ma",
    "temperature_c",
    "power_mw",
    "findings",
]


def log_fault(readings, report, data_source="simulated"):
    """
    Append a warning or critical event to the fault history CSV.

    Only WARNING and CRITICAL reports are logged.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Extract severity from the generated diagnostic report.
    severity = "INFO"

    for line in report.splitlines():
        if line.startswith("## Severity:"):
            severity = line.split(":", 1)[1].strip()
            break

    # Do not log normal readings as faults.
    if severity not in {"WARNING", "CRITICAL"}:
        return False

    findings = []
    inside_findings = False

    for line in report.splitlines():
        if line.strip() == "## 2. Findings":
            inside_findings = True
            continue

        if inside_findings and line.startswith("## "):
            break

        if inside_findings and line.startswith("- "):
            findings.append(line[2:].strip())

    file_exists = FAULT_LOG.exists() and FAULT_LOG.stat().st_size > 0

    row = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "data_source": data_source,
        "severity": severity,
        "voltage_v": readings.get("voltage_v", ""),
        "current_ma": readings.get("current_ma", ""),
        "temperature_c": readings.get("temperature_c", ""),
        "power_mw": readings.get("power_mw", ""),
        "findings": "; ".join(findings),
    }

    with FAULT_LOG.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    return True


if __name__ == "__main__":
    print(f"Fault log location: {FAULT_LOG}")