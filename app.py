import streamlit as st
import requests
import json
import re

st.set_page_config(page_title="DrShipz Tracker", page_icon="📦", layout="centered")

# Hide default Streamlit headers and footers
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.viewerBadge_container__1QSob {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("📦 DrShipz Tracker")
st.caption("Track live package movements")

# Input field
awb_input = st.text_input("Enter AWB / Tracking Number:", placeholder="e.g. 1234567890")

def fetch_shipment(awb):
    # Fetch logic using ZenRows / Carrier API
    url = f"https://api.zenrows.com/v1/?apikey={st.secrets.get('ZENROWS_KEY', '')}&url=https://track.delhivery.com/api/v1/packages/json/?waybill={awb}"
    try:
        res = requests.get(url, timeout=30)
        if res.status_code != 200:
            return None, f"Failed to retrieve tracking data (Status code: {res.status_code})"
        
        data = res.json()
        raw_data = data.get("data", [])
        if not raw_data:
            return None, "No tracking details found for this AWB."

        pkg = raw_data[0]
        order_id = pkg.get("order_id", awb)
        status = pkg.get("status", {}).get("status", "In Transit")
        current_loc = pkg.get("status", {}).get("location", "In Transit")

        scans = pkg.get("scans", [])
        checkpoints = []
        for s in scans:
            checkpoints.append({
                "time": s.get("scan_date_time", ""),
                "activity": s.get("scan_detail", ""),
                "location": s.get("scanned_location", "")
            })

        return {
            "order_id": order_id,
            "status": status,
            "location": current_loc,
            "checkpoints": checkpoints
        }, None

    except Exception as e:
        return None, str(e)

if st.button("Track Shipment", type="primary"):
    if not awb_input.strip():
        st.warning("Please enter an AWB number.")
    else:
        with st.spinner("Connecting to live carrier network..."):
            data, err = fetch_shipment(awb_input.strip())
            if err:
                st.error(err)
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Order ID", data["order_id"])
                c2.metric("Status", data["status"])
                c3.metric("Current Hub", data["location"])
                st.write("---")

                st.subheader("📍 Transit Milestones")
                if data["checkpoints"]:
                    for item in data["checkpoints"]:
                        with st.container():
                            st.markdown(f"**{item['time']}** — {item['activity']}")
                            if item["location"]:
                                st.caption(f"Hub: `{item['location']}`")
                            st.divider()
                else:
                    st.info("No transit checkpoints available.")
