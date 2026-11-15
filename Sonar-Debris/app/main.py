
import time
import pandas as pd
import streamlit as st

from sensor import get_sensor_data, get_complete_scan
from reconstruction import convert_scan_to_points, get_scan_summary
from visualization import create_scan_figure, create_distance_profile


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SONAR DEBRIS",
    page_icon="📡",
    layout="wide"
)


# --------------------------------------------------
# DARK UI
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #0D1420;
    color: #E2E8F0;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
}

h1, h2, h3 {
    color: #E2E8F0;
}

[data-testid="stMetric"] {
    background: #172235;
    padding: 15px;
    border: 1px solid #263449;
    border-radius: 10px;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8;
}

[data-testid="stMetricValue"] {
    color: #22D3EE;
}

.stCaption {
    color: #94A3B8;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "last_cycle" not in st.session_state:
    st.session_state.last_cycle = -1

if "latest_scan" not in st.session_state:
    st.session_state.latest_scan = None

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

if "paused" not in st.session_state:
    st.session_state.paused = False


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📡 SONAR DEBRIS")

st.caption(
    "ULTRASONIC SCANNING  |  OBJECT DETECTION  |  RADAR RECONSTRUCTION"
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("CONTROL PANEL")

    st.session_state.paused = st.toggle(
        "Pause dashboard updates",
        value=st.session_state.paused
    )

    if st.button("Clear scan history", use_container_width=True):
        st.session_state.scan_history = []
        st.session_state.latest_scan = None
        st.session_state.last_cycle = -1
        st.rerun()

    st.divider()

    st.caption("ESP8266 SCANNER")
    st.write("Automatic continuous scanning")

    st.caption("Detection range: 2–10 cm")
    st.caption("Scan resolution: 2 degrees")


# --------------------------------------------------
# LIVE DASHBOARD
# --------------------------------------------------

@st.fragment(run_every=1)
def live_dashboard():

    # ----------------------------------------------
    # LIVE SENSOR DATA
    # ----------------------------------------------

    live = get_sensor_data()

    connected = live.get("connected", False)

    if connected:
        st.success("ESP8266 CONNECTED")
    else:
        st.error("ESP8266 DISCONNECTED")

    # ----------------------------------------------
    # AUTOMATIC SCAN UPDATE
    # ----------------------------------------------

    if connected and not st.session_state.paused:

        scan_result = get_complete_scan()

        if scan_result.get("success"):

            cycle = scan_result["cycle"]

            # Process only a newly completed cycle
            if cycle != st.session_state.last_cycle:

                raw_scan = scan_result["points"]

                reconstructed_points = convert_scan_to_points(
                    raw_scan
                )

                summary = get_scan_summary(
                    raw_scan,
                    reconstructed_points
                )

                scan_record = {
                    "cycle": cycle,
                    "raw_scan": raw_scan,
                    "points": reconstructed_points,
                    "summary": summary,
                    "timestamp": time.strftime("%H:%M:%S")
                }

                st.session_state.latest_scan = scan_record

                st.session_state.last_cycle = cycle

                st.session_state.scan_history.insert(
                    0,
                    scan_record
                )

                # Keep only the latest 50 scans
                st.session_state.scan_history = (
                    st.session_state.scan_history[:50]
                )

    # ----------------------------------------------
    # LIVE METRICS
    # ----------------------------------------------

    latest = st.session_state.latest_scan

    live_distance = live.get("distance", 0)
    live_angle = live.get("angle", 0)

    if latest:

        summary = latest["summary"]

        total_readings = len(latest["raw_scan"])
        detected_count = len(latest["points"])
        cycle_number = latest["cycle"]

    else:
        total_readings = 0
        detected_count = 0
        cycle_number = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "SCAN CYCLE",
        cycle_number
    )

    col2.metric(
        "MEASUREMENTS",
        total_readings
    )

    col3.metric(
        "DETECTED POINTS",
        detected_count
    )

    col4.metric(
        "LIVE DISTANCE",
        f"{live_distance:.2f} cm"
        if isinstance(live_distance, (int, float))
        else "N/A"
    )

    st.divider()

    # ----------------------------------------------
    # RADAR RECONSTRUCTION
    # ----------------------------------------------

    st.subheader("OBJECT RECONSTRUCTION")

    if latest:

        radar = create_scan_figure(
            latest["points"],
            latest["cycle"]
        )

        st.plotly_chart(
            radar,
            use_container_width=True,
            key="automatic_radar"
        )

        # ------------------------------------------
        # DISTANCE PROFILE
        # ------------------------------------------

        st.subheader("DISTANCE PROFILE")

        profile = create_distance_profile(
            latest["raw_scan"],
            latest["cycle"]
        )

        st.plotly_chart(
            profile,
            use_container_width=True,
            key="automatic_profile"
        )

        # ------------------------------------------
        # SCAN SUMMARY
        # ------------------------------------------

        st.subheader("SCAN INFORMATION")

        a, b, c = st.columns(3)

        a.metric(
            "VALID READINGS",
            summary.get("valid_measurements", 0)
        )

        b.metric(
            "DETECTED OBJECT REGIONS",
            summary.get("object_regions", 0)
        )

        c.metric(
            "MINIMUM DISTANCE",
            f"{summary.get('min_distance', 0):.2f} cm"
        )

        st.caption(
            f"Last completed scan: {latest['timestamp']}"
        )

        # ------------------------------------------
        # DOWNLOAD
        # ------------------------------------------

        csv_data = pd.DataFrame(
            latest["raw_scan"]
        ).to_csv(index=False)

        st.download_button(
            "Download scan data (CSV)",
            data=csv_data,
            file_name=f"sonar_scan_{latest['cycle']}.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Waiting for the first completed scan..."
        )

    # ----------------------------------------------
    # SCAN HISTORY
    # ----------------------------------------------

    st.divider()

    st.subheader("RECENT SCAN HISTORY")

    if st.session_state.scan_history:

        history_data = []

        for scan in st.session_state.scan_history:

            history_data.append({
                "Cycle": scan["cycle"],
                "Detected Points": len(scan["points"]),
                "Time": scan["timestamp"]
            })

        st.dataframe(
            pd.DataFrame(history_data),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.caption("No scan history available yet.")


# --------------------------------------------------
# RUN DASHBOARD
# --------------------------------------------------

live_dashboard()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SONAR DEBRIS | AUTOMATED ULTRASONIC SCANNING SYSTEM"
)
