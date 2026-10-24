
import unittest
from unittest.mock import patch, MagicMock

from app.serial_reader import read_esp32_serial


class TestSerialReader(unittest.TestCase):

    @patch("app.serial_reader.time.monotonic")
    @patch("app.serial_reader.time.sleep")
    @patch("app.serial_reader.serial.Serial")
    def test_reads_valid_sensor_json(
        self, mock_serial, mock_sleep, mock_monotonic
    ):
        connection = MagicMock()

        # Correctly mock: with serial.Serial(...) as connection
        mock_serial.return_value.__enter__.return_value = connection

        connection.readline.return_value = (
            b'{"voltage_v":5.0,"current_ma":100.0,'
            b'"power_mw":500.0,"temperature_c":30.0,'
            b'"status":"NORMAL"}\n'
        )

        # First call starts the deadline; second enters the loop.
        mock_monotonic.side_effect = [0, 0.5]

        result = read_esp32_serial("COM3")

        self.assertIsNotNone(result)
        self.assertEqual(result["voltage_v"], 5.0)
        self.assertEqual(result["current_ma"], 100.0)
        self.assertEqual(result["temperature_c"], 30.0)
        self.assertEqual(result["power_mw"], 500.0)
        self.assertEqual(result["status"], "NORMAL")

        print("\nSerial reader successfully parsed sensor JSON.")


if __name__ == "__main__":
    unittest.main()
