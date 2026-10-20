
import json
import time

import serial
from serial import SerialException


def read_esp32_serial(port, baudrate=115200, timeout=2):
    """
    Read one JSON telemetry message from the ESP32 over USB serial.

    Expected JSON format per line:
    {
        "voltage_v": 5.0,
        "current_ma": 100.0,
        "power_mw": 500.0,
        "temperature_c": 30.0,
        "status": "NORMAL"
    }

    Returns a dictionary, or None if no valid message is received.
    """

    try:
        with serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
        ) as connection:

            # Some ESP32 boards reset when serial opens.
            time.sleep(2)
            connection.reset_input_buffer()

            deadline = time.monotonic() + timeout

            while time.monotonic() < deadline:
                line = connection.readline()

                if not line:
                    continue

                try:
                    message = json.loads(
                        line.decode("utf-8").strip()
                    )
                except (UnicodeDecodeError, json.JSONDecodeError):
                    # Ignore startup messages that aren't JSON.
                    continue

                required = {
                    "voltage_v",
                    "current_ma",
                    "temperature_c",
                }

                if not required.issubset(message):
                    continue

                # Convert sensor fields to numeric values.
                for key in required:
                    message[key] = float(message[key])

                # Calculate power if the firmware doesn't provide it.
                message.setdefault(
                    "power_mw",
                    message["voltage_v"] * message["current_ma"],
                )
                message["power_mw"] = float(message["power_mw"])

                message.setdefault("status", "UNKNOWN")
                message.setdefault("anomaly_detected", False)

                return message

    except (SerialException, OSError, ValueError) as error:
        raise RuntimeError(
            f"Could not read ESP32 serial data from {port}: {error}"
        ) from error

    return None


if __name__ == "__main__":
    port = input(
        "Enter ESP32 serial port (for example COM3): "
    ).strip()

    reading = read_esp32_serial(port)

    if reading is None:
        print("No valid JSON telemetry received.")
    else:
        print("ESP32 telemetry received:")
        print(json.dumps(reading, indent=2))
