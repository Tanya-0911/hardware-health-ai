import json
import random
import time
from datetime import datetime

def generate_reading():
    """Generate simulated hardware telemetry with occasional faults."""

    voltage = round(random.uniform(4.9, 5.1), 3)
    current = round(random.uniform(80, 130), 2)
    temperature = round(random.uniform(28, 34), 2)

    scenario = random.random()

    if scenario < 0.10:
        # Simulated high-current fault
        current = round(random.uniform(175, 220), 2)

    elif scenario < 0.15:
        # Simulated overheating
        temperature = round(random.uniform(37, 48), 2)

    elif scenario < 0.20:
        # Simulated low-voltage fault
        voltage = round(random.uniform(4.4, 4.7), 3)

    power = round(voltage * current, 2)

    status = "NORMAL"

    if voltage < 4.8 or voltage > 5.2:
        status = "WARNING"
    elif current > 170 or temperature > 36:
        status = "WARNING"

    return {
        "timestamp": datetime.now().isoformat(),
        "voltage_v": voltage,
        "current_ma": current,
        "power_mw": power,
        "temperature_c": temperature,
        "status": status,
        "source": "virtual_esp32",
    }


if __name__ == "__main__":
    print("Virtual ESP32 telemetry simulator started.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            reading = generate_reading()
            print(json.dumps(reading))
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nVirtual ESP32 simulator stopped.")