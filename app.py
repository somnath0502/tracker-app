import streamlit as st
import requests
import urllib.parse
import re

ZENROWS_KEY = "238066cb237646e8ed58605882a123b14f2628cd"

st.set_page_config(
    page_title="DrShipz Enterprise Tracking",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise Modern UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1040px;
    }
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Top Navbar */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 24px;
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        margin-bottom: 2rem;
    }
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }
    .nav-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Modern Card Containers */
    .ds-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    /* Visual 4-Stage Progress Tracker */
    .tracker-steps {
        display: flex;
        justify-content: space-between;
        position: relative;
        margin: 28px 0 12px 0;
    }
    .tracker-steps::before {
        content: "";
        position: absolute;
        top: 16px;
        left: 40px;
        right: 40px;
        height: 3px;
        background: #374151;
        z-index: 1;
    }
    .step-item {
        position: relative;
        z-index: 2;
        text-align: center;
        width: 120px;
    }
    .step-circle {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        margin: 0 auto 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        font-weight: 700;
        background: #1f2937;
        border: 2px solid #374151;
        color: #9ca3af;
    }
    .step-item.active .step-circle {
        background: #0284c7;
        border-color: #38bdf8;
        color: #ffffff;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.45);
    }
    .step-item.completed .step-circle {
        background: #059669;
        border-color: #10b981;
        color: #ffffff;
    }
    .step-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .step-item.active .step-label {
        color: #38bdf8;
        font-weight: 700;
    }
    .step-item.completed .step-label {
        color: #10b981;
    }

    /* Grid KPI Metrics */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 18px;
    }
    .kpi-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
    }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f8fafc;
        word-break: break-all;
    }

    /* Enterprise Timeline */
    .timeline-stream {
        position: relative;
        padding-left: 28px;
        margin-top: 15px;
    }
    .timeline-stream::before {
        content: "";
        position: absolute;
        top: 8px;
        bottom: 8px;
        left: 8px;
        width: 2px;
        background: #334155;
    }
    .event-row {
        position: relative;
        margin-bottom: 24px;
    }
    .event-dot {
        position: absolute;
        left: -25px;
        top: 4px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #38bdf8;
        border: 2px solid #0f172a;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
    }
    .event-time {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 3px;
    }
    .event-action {
        font-size: 0.96rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .event-loc {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="top-nav">
    <div class="nav-brand">
        <span>⚡</span> DrShipz Logistics Platform
    </div>
    <div class="nav-badge">Global Carrier Engine</div>
</div>
""", unsafe_allow_html=True)

# Input Box Area
c_in, c_btn = st.columns([4, 1])
with c_in:
    awb_input = st.text_input(
        "AWB / Tracking Number",
        value="33827139983026",
        placeholder="Enter shipment reference or tracking number...",
        label_visibility="collapsed"
    )
with c_btn:
    track_clicked = st.button("Track Order", type="primary", use_container_width=True)

def fetch_shipment(awb):
    target_url = urllib.parse.quote(f"https://shipprime.live/track-order?awb={awb}", safe='')
    api_url = f"https://api.zenrows.com/v1/?apikey={ZENROWS_KEY}&url={target_url}&js_render=true&wait=3000"

    resp = requests.get(api_url)
    if resp.status_code != 200:
        return None, f"Carrier network returned HTTP {resp.status_code}"

    html = resp.text

    # Parse Order ID
    order_id = "-"
    m_order = re.search(r"Order\s*#\s*([0-9A-Za-z_-]+)", html, re.I)
    if m_order:
        order_id = f"#{m_order.group(1)}"

    # Parse Courier
    courier = "DELHIVERY"
    m_courier = re.search(r"\b(DELHIVERY|XPRESSBEES|BLUEDART|EKART|SHADOWFAX|DTDC)\b", html, re.I)
    if m_courier:
        courier = m_courier.group(1).upper()

    # Parse Status
    status = "In Transit"
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

if track_clicked:
    if not awb_input.strip():
        st.warning("Please provide a valid tracking number.")
    else:
        with st.spinner("Connecting to multi-carrier data stream..."):
            data, err = fetch_shipment(awb_input.strip())
            if err:
                st.error(err)
            else:
                st.write("")
                # Determine Step States
                status_lower = data["status"].lower()
                step_order = "completed" if ("shipped" in status_lower or "transit" in status_lower or "out" in status_lower or "delivered" in status_lower) else "active"
                step_transit = "completed" if ("out" in status_lower or "delivered" in status_lower) else ("active" if "transit" in status_lower or "shipped" in status_lower else "")
                step_out = "completed" if "delivered" in status_lower else ("active" if "out" in status_lower else "")
                step_del = "completed" if "delivered" in status_lower else ""

                # Overview Card
                st.markdown(f"""
                <div class="ds-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-size: 0.78rem; font-weight: 600; color: #94a3b8; text-transform: uppercase;">Tracking Number</span>
                            <div style="font-size: 1.45rem; font-weight: 800; color: #f8fafc;">{awb_input.strip()}</div>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #34d399; padding: 6px 14px; border-radius: 30px; font-weight: 700; font-size: 0.85rem;">
                            ● {data['status'].upper()}
                        </div>
                    </div>
                    
                    <!-- Progress Bar -->
                    <div class="tracker-steps">
                        <div class="step-item {step_order}">
                            <div class="step-circle">✓</div>
                            <div class="step-label">Order Confirmed</div>
                        </div>
                        <div class="step-item {step_transit}">
                            <div class="step-circle">2</div>
                            <div class="step-label">In Transit</div>
                        </div>
                        <div class="step-item {step_out}">
                            <div class="step-circle">3</div>
                            <div class="step-label">Out for Delivery</div>
                        </div>
                        <div class="step-item {step_del}">
                            <div class="step-circle">4</div>
                            <div class="step-label">Delivered</div>
                        </div>
                    </div>

                    <!-- Metrics Grid -->
                    <div class="kpi-grid">
                        <div class="kpi-box">
                            <div class="kpi-title">Order ID</div>
                            <div class="kpi-value">{data['order_id']}</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-title">Courier Partner</div>
                            <div class="kpi-value">{data['courier']}</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-title">Current Hub</div>
                            <div class="kpi-value">{data['location']}</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-title">Service Speed</div>
                            <div class="kpi-value" style="color: #38bdf8;">Standard Air</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Milestones Feed Card
                if data["checkpoints"]:
                    events_html = ""
                    for item in data["checkpoints"]:
                        loc_part = f'<div class="event-loc">📍 Location: {item["location"]}</div>' if item["location"] else ""
                        events_html += f"""
                        <div class="event-row">
                            <div class="event-dot"></div>
                            <div class="event-time">{item['time']}</div>
                            <div class="event-action">{item['activity']}</div>
                            {loc_part}
                        </div>
                        """

                    st.markdown(f"""
                    <div class="ds-card">
                        <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 20px;">
                            Detailed Activity Logs
                        </div>
                        <div class="timeline-stream">
                            {events_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No transit scans available for this consignment yet.")
