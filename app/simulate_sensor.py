
import csv
import random
import time
from datetime import datetime, timezone
from pathlib import Path

OUTPUT = Path("data/simulated_telemetry.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FIELDS = [
    "timestamp",
    "voltage_v",
    "current_ma",
    "power_mw",
    "temperature_c",
    "status",
]

print("Smart Hardware Health Monitor — Simulator")
print(f"Saving readings to: {OUTPUT.resolve()}")
print("Press Ctrl+C to stop.\n")

file_exists = OUTPUT.exists() and OUTPUT.stat().st_size > 0

try:
    with OUTPUT.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)

        if not file_exists:
            writer.writeheader()

        while True:
            # Simulated normal operating measurements
            voltage = round(random.uniform(4.8, 5.2), 3)
            current = round(random.uniform(80, 180), 2)
            temperature = round(random.uniform(28, 38), 2)

            # Calculate power in milliwatts:
            # V × mA = mW
            power = round(voltage * current, 2)

            # Illustrative thresholds for simulated data only
            status = (
                "WARNING"
                if temperature > 36 or current > 170
                else "NORMAL"
            )

            reading = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "voltage_v": voltage,
                "current_ma": current,
                "power_mw": power,
                "temperature_c": temperature,
                "status": status,
            }

            writer.writerow(reading)
            f.flush()

            print(
                f"V={voltage:.3f} V | "
                f"I={current:.2f} mA | "
                f"P={power:.2f} mW | "
                f"T={temperature:.2f} °C | "
                f"{status}"
            )

            time.sleep(2)

except KeyboardInterrupt:
    print("\nSimulator stopped. Data saved.")
