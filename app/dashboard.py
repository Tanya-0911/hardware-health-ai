from fault_logger import log_fault
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import IsolationForest

from diagnostics import analyze_readings
from serial_reader import read_esp32_serial
from virtual_esp32 import generate_reading


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_FILE = Path("data/simulated_telemetry.csv")

FEATURES = [
    "voltage_v",
    "current_ma",
    "power_mw",
    "temperature_c",
]

st.set_page_config(
    page_title="Smart Hardware Health Monitor",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Smart Hardware Health Monitor")
st.caption(
    "Hardware telemetry monitoring, anomaly detection, "
    "and failure analysis"
)


# --------------------------------------------------
# SELECT TELEMETRY SOURCE
# --------------------------------------------------

data_source = st.radio(
    "Select telemetry source",
    [
        "Simulated Data",
        "Virtual ESP32",
        "ESP32 Live Data",
    ],
    horizontal=True,
)


# --------------------------------------------------
# MODE 1: EXISTING CSV SIMULATION
# --------------------------------------------------

if data_source == "Simulated Data":

    st.info("Data source: Existing simulated telemetry CSV.")

    if not DATA_FILE.exists():
        st.warning(
            "No telemetry file found. "
            "Run app/simulate_sensor.py first."
        )
        st.stop()

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.info("No simulated readings are available.")
        st.stop()

    if "timestamp" not in df.columns:
        st.error("The CSV file must contain a timestamp column.")
        st.stop()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    df = df.dropna(subset=["timestamp"])

    if df.empty:
        st.warning("No valid timestamps were found in the CSV.")
        st.stop()

    if "status" not in df.columns:
        df["status"] = "UNKNOWN"

    if "anomaly_detected" not in df.columns:
        df["anomaly_detected"] = False


# --------------------------------------------------
# MODE 2: VIRTUAL ESP32
# --------------------------------------------------

elif data_source == "Virtual ESP32":

    st.info(
        "Data source: Virtual ESP32. "
        "All readings are generated simulations, not real sensor measurements."
    )

    if "virtual_readings" not in st.session_state:
        st.session_state.virtual_readings = []

    col_generate, col_clear = st.columns(2)

    with col_generate:
        generate_clicked = st.button(
            "Generate Virtual Sensor Reading",
            type="primary",
        )

    with col_clear:
        clear_clicked = st.button("Clear Virtual Readings")

    if clear_clicked:
        st.session_state.virtual_readings = []
        st.rerun()

    if generate_clicked:
        reading = generate_reading()

        # Give each virtual reading a timestamp.
        reading["timestamp"] = datetime.now().isoformat()

        # Ensure the simulator supplies the expected fields.
        reading.setdefault("status", "UNKNOWN")
        reading.setdefault("anomaly_detected", False)

        st.session_state.virtual_readings.append(reading)

        st.success("Virtual telemetry generated successfully.")

    df = pd.DataFrame(
        st.session_state.virtual_readings
    )

    if df.empty:
        st.info(
            "No virtual readings collected yet. "
            "Click 'Generate Virtual Sensor Reading' to begin."
        )
        st.stop()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    df = df.dropna(subset=["timestamp"])


# --------------------------------------------------
# MODE 3: PHYSICAL ESP32 SERIAL INPUT
# --------------------------------------------------

else:

    st.info(
        "Data source: Physical ESP32 over USB serial. "
        "A connected board and compatible sensors are required."
    )

    if "live_readings" not in st.session_state:
        st.session_state.live_readings = []

    port = st.text_input(
        "ESP32 serial port",
        value="COM3",
        help=(
            "When you have the board, enter its actual Windows "
            "serial port, such as COM3 or COM4."
        ),
    )

    if st.button(
        "Read ESP32 Sensor Data",
        type="primary",
    ):

        if not port.strip():
            st.error("Enter a serial port.")
        else:
            try:
                with st.spinner("Waiting for ESP32 telemetry..."):
                    reading = read_esp32_serial(
                        port.strip(),
                        baudrate=115200,
                        timeout=2,
                    )

                if reading is None:
                    st.warning(
                        "No valid JSON telemetry received. "
                        "Check the serial port, firmware, and connections."
                    )

                else:
                    reading["timestamp"] = datetime.now().isoformat()

                    reading.setdefault("status", "UNKNOWN")
                    reading.setdefault("anomaly_detected", False)

                    st.session_state.live_readings.append(reading)

                    st.success("ESP32 telemetry received.")

            except (RuntimeError, ValueError) as error:
                st.error(str(error))

    df = pd.DataFrame(
        st.session_state.live_readings
    )

    if df.empty:
        st.info(
            "No live readings collected. "
            "Select Virtual ESP32 to test the dashboard without hardware."
        )
        st.stop()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    df = df.dropna(subset=["timestamp"])


# --------------------------------------------------
# VALIDATE TELEMETRY
# --------------------------------------------------

missing_columns = [
    column
    for column in ["timestamp", *FEATURES]
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"Missing required telemetry columns: {missing_columns}"
    )
    st.stop()

for column in FEATURES:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )

df = df.dropna(subset=FEATURES)
df = df.sort_values("timestamp").reset_index(drop=True)

if df.empty:
    st.warning("No valid numeric telemetry readings are available.")
    st.stop()

if "status" not in df.columns:
    df["status"] = "UNKNOWN"

if "anomaly_detected" not in df.columns:
    df["anomaly_detected"] = False


# --------------------------------------------------
# LATEST TELEMETRY METRICS
# --------------------------------------------------

latest = df.iloc[-1]

st.subheader("Latest Hardware Readings")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Voltage",
    f"{latest['voltage_v']:.3f} V",
)

c2.metric(
    "Current",
    f"{latest['current_ma']:.2f} mA",
)

c3.metric(
    "Power",
    f"{latest['power_mw']:.2f} mW",
)

c4.metric(
    "Temperature",
    f"{latest['temperature_c']:.2f} °C",
)

st.caption(
    f"Readings currently displayed: {len(df)}"
)


# --------------------------------------------------
# TELEMETRY GRAPHS
# --------------------------------------------------

st.subheader("Telemetry Over Time")

for column, label, unit in [
    ("voltage_v", "Voltage", "V"),
    ("current_ma", "Current", "mA"),
    ("power_mw", "Power", "mW"),
    ("temperature_c", "Temperature", "°C"),
]:

    fig = px.line(
        df,
        x="timestamp",
        y=column,
        title=f"{label} ({unit})",
        markers=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# --------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------

st.subheader("Anomaly Detection")

# Preserve any anomaly flag supplied by the data source.
df["anomaly"] = (
    df["anomaly_detected"]
    .fillna(False)
    .astype(bool)
)

if len(df) >= 20:

    detector = IsolationForest(
        contamination=0.05,
        random_state=42,
    )

    predictions = detector.fit_predict(
        df[FEATURES]
    )

    statistical_anomalies = predictions == -1

    df["anomaly"] = (
        df["anomaly"] | statistical_anomalies
    )

    anomalies = df[df["anomaly"]]

    if anomalies.empty:
        st.success("No potential anomalies detected.")

    else:
        st.warning(
            f"{len(anomalies)} potential anomalous readings detected."
        )

        st.dataframe(
            anomalies[
                [
                    "timestamp",
                    *FEATURES,
                    "status",
                    "anomaly",
                ]
            ].tail(20),
            use_container_width=True,
        )

else:
    st.info(
        f"{len(df)} reading(s) collected. "
        "At least 20 readings are needed to run statistical "
        "anomaly detection."
    )


# --------------------------------------------------
# RECENT READINGS
# --------------------------------------------------

st.subheader("Recent Readings")

st.dataframe(
    df.tail(20),
    use_container_width=True,
)


# --------------------------------------------------
# HARDWARE FAILURE ANALYSIS ASSISTANT
# --------------------------------------------------

st.divider()

st.subheader("🤖 Hardware Failure Analysis Assistant")

st.caption(
    "Rule-based diagnostic assistant. Thresholds are illustrative "
    "and should be validated for the actual hardware."
)

if st.button("Generate Diagnostic Report"):

    latest_reading = df.iloc[-1]

    report_data = {
        "voltage_v": float(
            latest_reading["voltage_v"]
        ),
        "current_ma": float(
            latest_reading["current_ma"]
        ),
        "power_mw": float(
            latest_reading["power_mw"]
        ),
        "temperature_c": float(
            latest_reading["temperature_c"]
        ),
        "status": str(
            latest_reading["status"]
        ),
        "anomaly_detected": bool(
            latest_reading["anomaly"]
        ),
    }

    if data_source == "Simulated Data":
        source_label = "simulated"

    elif data_source == "Virtual ESP32":
        source_label = "virtual ESP32 simulated"

    else:
        source_label = "ESP32 live"

    # Generate the diagnostic report.
    report = analyze_readings(
        report_data,
        data_source=source_label,
    )

    # Automatically log WARNING and CRITICAL events.
    logged = log_fault(
        readings=report_data,
        report=report,
        data_source=source_label,
    )

    if logged:
        st.success(
            "Fault event recorded in reports/fault_events.csv"
        )

    st.markdown(report)

    st.download_button(
        label="Download Diagnostic Report",
        data=report,
        file_name="hardware_diagnostic_report.md",
        mime="text/markdown",
    )