
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import IsolationForest

DATA_FILE = Path("data/simulated_telemetry.csv")

st.set_page_config(
    page_title="Smart Hardware Health Monitor",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Smart Hardware Health Monitor")
st.caption("Prototype dashboard — simulated telemetry")

if not DATA_FILE.exists():
    st.warning("No telemetry file found. Run the simulator first.")
    st.stop()

df = pd.read_csv(DATA_FILE)

if df.empty:
    st.info("No readings available yet.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

if df.empty:
    st.warning("No valid timestamps found.")
    st.stop()

# Display latest readings
latest = df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Voltage", f"{latest['voltage_v']:.3f} V")
c2.metric("Current", f"{latest['current_ma']:.2f} mA")
c3.metric("Power", f"{latest['power_mw']:.2f} mW")
c4.metric("Temperature", f"{latest['temperature_c']:.2f} °C")

st.subheader("Telemetry over time")

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
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Anomaly detection")

features = ["voltage_v", "current_ma", "power_mw", "temperature_c"]
df["anomaly"] = False

if len(df) >= 20:
    detector = IsolationForest(
        contamination=0.05,
        random_state=42,
    )
    df["anomaly"] = detector.fit_predict(df[features]) == -1

    anomalies = df[df["anomaly"]]

    if anomalies.empty:
        st.success("No statistical anomalies detected.")
    else:
        st.warning(f"{len(anomalies)} potential anomalies detected.")
        st.dataframe(
            anomalies[
                ["timestamp", *features, "status"]
            ].tail(20),
            use_container_width=True,
        )
else:
    st.info("Collect at least 20 readings to enable anomaly detection.")

st.subheader("Recent readings")
st.dataframe(df.tail(20), use_container_width=True)

# Refresh periodically while the dashboard is open
time.sleep(3)
st.rerun()
