import streamlit as st
import requests
import re

# 1. Page Configuration
st.set_page_config(
    page_title="DrShipz",
    page_icon="📦",
    layout="centered"
)

# 2. Aggressively hide GitHub links, header toolbar, footer, and menu
hide_style = """
    <style>
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    [data-testid="stHeader"] {visibility: hidden !important; display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 3. Branding
st.title("📦 DrShipz")
st.caption("Live carrier scan and checkpoint tracker")

# 4. Input Field
awb_input = st.text_input(
    "Enter AWB Number:", 
    value="33827139983026", 
    placeholder="e.g. 33827139983026"
)

# 5. Fetch Shipment Data
def fetch_shipment(awb):
    api_key = st.secrets["ZENROWS_KEY"] if "ZENROWS_KEY" in st.secrets else "238066cb237646e8ed58605882a123b14f2628cd"
    target_url = f"https://shipprime.live/track-order?awb={awb}"
    
    api_url = f"https://api.zenrows.com/v1/?apikey={api_key}&url={target_url}&js_render=true&premium_proxy=true"

    resp = requests.get(api_url)
    if resp.status_code != 200:
        return None, f"Failed with HTTP error {resp.status_code}"

    html = resp.text

    order_id = "-"
    m_order = re.search(r"Order\s*#\s*([0-9A-Za-z_-]+)", html, re.I)
    if m_order:
        order_id = f"#{m_order.group(1)}"

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
        "status": status,
        "location": current_loc,
        "checkpoints": checkpoints
    }, None

# 6. Action Button & Results Display
if st.button("Track Shipment", type="primary"):
    if not awb_input.strip():
        st.warning("Please enter an AWB number.")
    else:
        with st.spinner("Connecting to live carrier network..."):
            data, err = fetch_shipment(awb_input.strip())
            if err:
                st.error(err)
            else:
                # 3-Column Display: Order ID, Status, Current Hub
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
                            if item['location']:
                                st.caption(f"Hub: `{item['location']}`")
                            st.divider()
                else:
                    st.info("No transit checkpoints available.")
