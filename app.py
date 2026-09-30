import streamlit as st
import requests
import urllib.parse
import re

ZENROWS_KEY = "238066cb237646e8ed58605882a123b14f2628cd"

st.set_page_config(
    page_title="DrShipz Enterprise Cargo Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom High-End Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1080px;
    }

    #MainMenu, footer, header {
        visibility: hidden !important;
    }

    /* Tall Sovereign Header */
    .hero-header {
        position: relative;
        background: linear-gradient(135deg, #090d16 0%, #0d1527 50%, #09101d 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 24px;
        padding: 42px 48px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        overflow: hidden;
    }

    .hero-header::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }

    .hero-topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .brand-group {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .brand-icon {
        font-size: 2.2rem;
        background: linear-gradient(135deg, #ff9933 0%, #ffffff 50%, #138808 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 12px rgba(255, 153, 51, 0.35));
    }

    .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
        line-height: 1;
    }

    .brand-tag {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 2px;
        padding: 6px 14px;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(255, 153, 51, 0.15), rgba(19, 136, 8, 0.15));
        border: 1px solid rgba(255, 153, 51, 0.4);
        color: #f8fafc;
        text-transform: uppercase;
        box-shadow: 0 0 20px rgba(255, 153, 51, 0.15);
    }

    .hero-desc {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 600px;
        margin: 0;
        font-weight: 500;
        line-height: 1.5;
    }

    /* Enterprise Stats Card */
    .stat-container {
        background: #0d131f;
        border: 1px solid #1e293b;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 24px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    }

    /* Stepper Header */
    .step-track {
        display: flex;
        justify-content: space-between;
        position: relative;
        margin: 36px 0 24px 0;
    }

    .step-track::before {
        content: "";
        position: absolute;
        top: 20px;
        left: 50px;
        right: 50px;
        height: 3px;
        background: #1e293b;
        z-index: 1;
    }

    .node {
        position: relative;
        z-index: 2;
        text-align: center;
        width: 140px;
    }

    .node-icon {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        margin: 0 auto 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        font-weight: 700;
        background: #090d16;
        border: 2px solid #334155;
        color: #64748b;
        transition: all 0.3s ease;
    }

    .node.done .node-icon {
        background: #059669;
        border-color: #10b981;
        color: #ffffff;
        box-shadow: 0 0 18px rgba(16, 185, 129, 0.4);
    }

    .node.active .node-icon {
        background: #0284c7;
        border-color: #38bdf8;
        color: #ffffff;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
        animation: pulse 2s infinite;
    }

    .node-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
    }

    .node.done .node-title { color: #10b981; }
    .node.active .node-title { color: #38bdf8; }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.06); }
        100% { transform: scale(1); }
    }

    /* Core Metrics Hub */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 28px;
    }

    .kpi-card {
        background: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 18px 20px;
    }

    .kpi-tag {
        font-size: 0.72rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }

    .kpi-data {
        font-size: 1.25rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Sovereign Authority Header
st.markdown("""
<div class="hero-header">
    <div class="hero-topline">
        <div class="brand-group">
            <div class="brand-icon">⚡</div>
            <div class="brand-name">DrShipz</div>
        </div>
        <div class="brand-tag">GREAT INDIAN CARRIER ENGINE</div>
    </div>
    <p class="hero-desc">
        Unified real-time logistics telemetry powering express freight, hyper-local distribution, and national line-haul tracking across India.
    </p>
</div>
""", unsafe_allow_html=True)

# Search Input Module
c1, c2 = st.columns([5, 1.4])
with c1:
    awb_input = st.text_input(
        "AWB / Tracking Number",
        value="33827139983026",
        placeholder="Enter Waybill or Consignment Reference...",
        label_visibility="collapsed"
    )
with c2:
    track_clicked = st.button("TRACK SHIPMENT", type="primary", use_container_width=True)

def fetch_shipment(awb):
    target_url = urllib.parse.quote(f"https://shipprime.live/track-order?awb={awb}", safe='')
    api_url = f"https://api.zenrows.com/v1/?apikey={ZENROWS_KEY}&url={target_url}&js_render=true&wait=5000"

    resp = requests.get(api_url)
    if resp.status_code != 200:
        return None, f"Telemetry uplink rejected (Status: {resp.status_code})"

    html = resp.text

    # Extract Order ID
    order_id = "-"
    m_order = re.search(r"Order\s*#\s*([0-9A-Za-z_-]+)", html, re.I)
    if m_order:
        order_id = f"#{m_order.group(1)}"

    # Extract Courier
    courier = "DELHIVERY"
    m_courier = re.search(r"\b(DELHIVERY|XPRESSBEES|BLUEDART|EKART|SHADOWFAX|DTDC)\b", html, re.I)
    if m_courier:
        courier = m_courier.group(1).upper()

    # Clean text lines
    clean = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->|<[^>]+>", "\n", html)
    lines = [re.sub(r"^[*#_~`]+|[*#_~`]+$", "", l).strip() for l in clean.splitlines()]
    lines = [l for l in lines if l and l != "LATEST"]

    # Extract Current Hub
    current_loc = "-"
    for l in lines:
        if "_" in l and "(" in l:
            current_loc = l
            break

    # Parse Milestones
    checkpoints = []
    start = 0
    for idx, l in enumerate(lines):
        if "Shipment Journey" in l or "Tracking History" in l:
            start = idx + 1
            break
            
    sub = lines[start:] if start > 0 else lines
    j = 0
    while j < len(sub):
        if re.match(r"^\d{1,2}\s+[A-Za-z]{3,4}(?:\s+\d{4})?$", sub[j]):
            date_str = sub[j]
            time_str = sub[j+1] if j+1 < len(sub) and re.search(r"(?:am|pm|\d{1,2}:\d{2})", sub[j+1], re.I) else ""
            if time_str: j += 1
            act_str = sub[j+1] if j+1 < len(sub) and not re.match(r"^\d{1,2}\s+[A-Za-z]{3,4}", sub[j+1]) else ""
            if act_str: j += 1
            hub_str = sub[j+1] if j+1 < len(sub) and ("(" in sub[j+1] or "_" in sub[j+1] or "Hub" in sub[j+1]) else ""
            if hub_str: j += 1

            checkpoints.append({
                "time": f"{date_str} {time_str}".strip(),
                "activity": act_str,
                "location": hub_str
            })
        j += 1

    # Status Detection: Checks Delivered, RTO, Out for Delivery, or In Transit
    status = "In Transit"
    if re.search(r"\b(Delivered|Successfully Delivered)\b", html, re.I):
        status = "Delivered"
    elif re.search(r"\b(RTO Initiated|RTO Delivered|Returned to Origin|RTO in Transit|RTO)\b", html, re.I):
        status = "RTO"
    elif re.search(r"\b(Out for Delivery)\b", html, re.I):
        status = "Out for Delivery"
    else:
        m_status = re.search(r"<h2[^>]*>\s*([A-Za-z\s]+)\s*</h2>", html, re.I)
        if m_status and "Frequently" not in m_status.group(1):
            status = m_status.group(1).strip()

    # Verify status from latest checkpoint if available
    if checkpoints:
        latest_act = checkpoints[0]["activity"].lower()
        if "delivered" in latest_act and "undelivered" not in latest_act:
            status = "Delivered"
        elif "rto" in latest_act or "returned" in latest_act:
            status = "RTO"
        elif "out for delivery" in latest_act:
            status = "Out for Delivery"

    return {
        "order_id": order_id,
        "courier": courier,
        "status": status,
        "location": current_loc,
        "checkpoints": checkpoints
    }, None

if track_clicked:
    if not awb_input.strip():
        st.warning("Enter a valid consignment tracking number.")
    else:
        with st.spinner("Accessing DrShipz National Line-haul Grid..."):
            data, err = fetch_shipment(awb_input.strip())
            if err:
                st.error(err)
            else:
                st.write("")
                s_lower = data["status"].lower()
                n1 = "done" if ("shipped" in s_lower or "transit" in s_lower or "out" in s_lower or "delivered" in s_lower or "rto" in s_lower) else "active"
                n2 = "done" if ("out" in s_lower or "delivered" in s_lower or "rto" in s_lower) else ("active" if "transit" in s_lower or "shipped" in s_lower else "")
                n3 = "done" if "delivered" in s_lower else ("active" if ("out" in s_lower or "rto" in s_lower) else "")
                n4 = "done" if "delivered" in s_lower else ""

                status_color = "#ef4444" if data['status'] == "RTO" else ("#10b981" if data['status'] == "Delivered" else "#38bdf8")

                # Main Overview Hub Card
                st.markdown(f"""
                <div class="stat-container">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 20px;">
                        <div>
                            <div style="font-size: 0.78rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Consignment Number</div>
                            <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc; font-family: 'Space Grotesk', sans-serif;">{awb_input.strip()}</div>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid {status_color}; color: {status_color}; padding: 8px 18px; border-radius: 999px; font-weight: 800; font-size: 0.85rem; letter-spacing: 0.5px;">
                            ● {data['status'].upper()}
                        </div>
                    </div>

                    <!-- Visual Step Progression -->
                    <div class="step-track">
                        <div class="node {n1}">
                            <div class="node-icon">✓</div>
                            <div class="node-title">Origin Hub</div>
                        </div>
                        <div class="node {n2}">
                            <div class="node-icon">2</div>
                            <div class="node-title">National Transit</div>
                        </div>
                        <div class="node {n3}">
                            <div class="node-icon">3</div>
                            <div class="node-title">Last-Mile Out</div>
                        </div>
                        <div class="node {n4}">
                            <div class="node-icon">4</div>
                            <div class="node-title">{"RTO" if data['status'] == "RTO" else "Delivered"}</div>
                        </div>
                    </div>

                    <!-- KPI Statistics Grid -->
                    <div class="kpi-row">
                        <div class="kpi-card">
                            <div class="kpi-tag">Merchant Order</div>
                            <div class="kpi-data">{data['order_id']}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-tag">Carrier Partner</div>
                            <div class="kpi-data">{data['courier']}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-tag">Active Hub Scan</div>
                            <div class="kpi-data" style="font-size: 1rem;">{data['location']}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-tag">Routing Mode</div>
                            <div class="kpi-data" style="color: #38bdf8;">Priority Express</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Compact Waypoint Audit Trail (zero excessive gaps, no raw HTML bugs)
                if data["checkpoints"]:
                    st.markdown("""
                    <div style="font-size: 1.25rem; font-weight: 800; color: #f8fafc; margin: 28px 0 14px 0; font-family: 'Space Grotesk', sans-serif;">
                        📍 Live Waypoint Audit Trail
                    </div>
                    """, unsafe_allow_html=True)

                    for cp in data["checkpoints"]:
                        hub_tag = f" &nbsp;•&nbsp; <code style='font-size:0.75rem; color:#10b981;'>{cp['location']}</code>" if cp["location"] else ""
                        st.markdown(f"""
                        <div style="padding: 8px 14px; background: #0d131f; border-left: 3px solid #38bdf8; border-bottom: 1px solid #1e293b; border-radius: 6px; margin-bottom: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <span style="color: #f8fafc; font-weight: 700; font-size: 0.95rem;">{cp['activity']}</span>
                                <span style="color: #38bdf8; font-weight: 600; font-size: 0.82rem;">{cp['time']}</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 3px;">
                                Terminal:{hub_tag}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No waypoint checkpoints scanned yet.")
