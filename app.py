import streamlit as st
import requests
import urllib.parse
import re

ZENROWS_KEY = "238066cb237646e8ed58605882a123b14f2628cd"

st.set_page_config(page_title="DrShipz Tracker", page_icon="📦", layout="centered")

# Modern Styling & Custom Cards
st.markdown("""
<style>
    /* Global Container Adjustments */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 720px;
    }
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Header Card */
    .brand-header {
        text-align: center;
        padding: 24px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    .brand-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    .brand-subtitle {
        color: #38bdf8;
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 1.15rem !important;
        font-weight: 700;
    }

    /* Timeline Milestones */
    .timeline-item {
        position: relative;
        padding-left: 24px;
        margin-bottom: 20px;
        border-left: 2px solid #38bdf8;
    }
    .timeline-dot {
        position: absolute;
        left: -6px;
        top: 3px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #38bdf8;
        box-shadow: 0 0 8px #38bdf8;
    }
    .timeline-time {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 2px;
    }
    .timeline-activity {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f8fafc;
    }
    .timeline-hub {
        font-size: 0.82rem;
        color: #64748b;
        margin-top: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Custom Header Display
st.markdown("""
<div class="brand-header">
    <div class="brand-title">📦 DrShipz</div>
    <div class="brand-subtitle">The Most Reliable Carrier</div>
</div>
""", unsafe_allow_html=True)

awb_input = st.text_input("Track your shipment:", value="33827139983026", placeholder="Enter AWB / Waybill number...")

def fetch_shipment(awb):
    target_url = urllib.parse.quote(f"https://shipprime.live/track-order?awb={awb}", safe='')
    api_url = f"https://api.zenrows.com/v1/?apikey={ZENROWS_KEY}&url={target_url}&js_render=true&wait=3000"

    resp = requests.get(api_url)
    if resp.status_code != 200:
        return None, f"Failed with HTTP error {resp.status_code}"

    html = resp.text

    order_id = "-"
    m_order = re.search(r"Order\s*#\s*([0-9A-Za-z_-]+)", html, re.I)
    if m_order:
        order_id = f"#{m_order.group(1)}"

    courier = "DELHIVERY"
    m_courier = re.search(r"\b(DELHIVERY|XPRESSBEES|BLUEDART|EKART|SHADOWFAX|DTDC)\b", html, re.I)
    if m_courier:
        courier = m_courier.group(1).upper()

    status = "Shipped"
    m_status = re.search(r"<h2[^>]*>\s*([A-Za-z\s]+)\s*</h2>", html, re.I)
    if m_status and "Frequently" not in m_status.group(1):
        status = m_status.group(1).strip()

    clean = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->|<[^>]+>", "\n", html)
    lines = [re.sub(r"^[*#_~`]+|[*#_~`]+$", "", l).strip() for l in clean.splitlines()]
    lines = [l for l in lines if l and l != "LATEST"]

    current_loc = "-"
    for l in lines:
        if "_" in l and "(" in l:
            current_loc = l
            break

    checkpoints = []
    if "Shipment Journey" in lines:
        start = lines.index("Shipment Journey")
        sub = lines[start + 1:]
        j = 0
        while j < len(sub):
            if re.match(r"^\d{1,2}\s+[A-Za-z]{3,4}$", sub[j]):
                date_str = sub[j]
                time_str = sub[j+1] if j+1 < len(sub) and re.search(r"(?:am|pm)", sub[j+1], re.I) else ""
                if time_str: j += 1
                act_str = sub[j+1] if j+1 < len(sub) and not re.match(r"^\d{1,2}\s+[A-Za-z]{3,4}$", sub[j+1]) else ""
                if act_str: j += 1
                hub_str = sub[j+1] if j+1 < len(sub) and ("(" in sub[j+1] or "_" in sub[j+1]) else ""
                if hub_str: j += 1

                checkpoints.append({
                    "time": f"{date_str} {time_str}".strip(),
                    "activity": act_str,
                    "location": hub_str
                })
            j += 1

    return {
        "order_id": order_id,
        "courier": courier,
        "status": status,
        "location": current_loc,
        "checkpoints": checkpoints
    }, None

if st.button("Track Package", type="primary", use_container_width=True):
    if not awb_input.strip():
        st.warning("Please enter an AWB number.")
    else:
        with st.spinner("Connecting to live carrier network..."):
            data, err = fetch_shipment(awb_input.strip())
            if err:
                st.error(err)
            else:
                st.write("")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Order ID", data["order_id"])
                c2.metric("Courier", data["courier"])
                c3.metric("Status", data["status"])
                c4.metric("Current Hub", data["location"])

                st.write("")
                st.subheader("📍 Transit Milestones")
                
                if data["checkpoints"]:
                    for item in data["checkpoints"]:
                        hub_html = f'<div class="timeline-hub">📍 {item["location"]}</div>' if item["location"] else ""
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-dot"></div>
                            <div class="timeline-time">{item['time']}</div>
                            <div class="timeline-activity">{item['activity']}</div>
                            {hub_html}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No transit checkpoints available.")
