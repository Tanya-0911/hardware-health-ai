
import unittest

from app.diagnostics import analyze_readings


class TestDiagnostics(unittest.TestCase):

    def test_high_current_is_reported(self):
        readings = {
            "voltage_v": 5.0,
            "current_ma": 190.0,
            "power_mw": 950.0,
            "temperature_c": 30.0,
            "status": "WARNING",
            "anomaly_detected": False,
        }

        report = analyze_readings(readings)

        self.assertIn("Current", report)
        self.assertIn("170 mA", report)

    def test_high_temperature_is_reported(self):
        readings = {
            "voltage_v": 5.0,
            "current_ma": 100.0,
            "power_mw": 500.0,
            "temperature_c": 40.0,
            "status": "WARNING",
            "anomaly_detected": False,
        }

        report = analyze_readings(readings)

        self.assertIn("Temperature", report)
        self.assertIn("36", report)

    def test_normal_readings_are_not_overstated(self):
        readings = {
            "voltage_v": 5.0,
            "current_ma": 100.0,
            "power_mw": 500.0,
            "temperature_c": 30.0,
            "status": "NORMAL",
            "anomaly_detected": False,
        }

        report = analyze_readings(readings)

        self.assertIn("No configured rule was triggered", report)
        self.assertIn("SIMULATED", report)


if __name__ == "__main__":
    unittest.main()
