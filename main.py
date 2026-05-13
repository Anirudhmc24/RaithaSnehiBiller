import streamlit as st

st.set_page_config(
    page_title="Raitha Snehi Biller",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit default styling
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 2rem;}

/* Unified Button Styling */
div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}
div.stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
}
/* Sub-page active styling (used in GST subpages) */
button[data-testid="baseButton-secondary"] {
    border: 1px solid #d0d7de !important;
}

/* Metric card styling */
div[data-testid="stMetricValue"] {
    font-size: 1.8rem;
    color: #1a3c5e;
}

/* Scanner Results Panel */
.scan-found {
    background: #f8fffe;
    border: 1px solid #a5d6a7;
    border-left: 6px solid #2e7d32;
    padding: 16px 24px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.scan-new {
    background: #fff8e1;
    border: 1px solid #ffe082;
    border-left: 6px solid #f9a825;
    padding: 16px 24px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.scan-found h3, .scan-new h3 {
    margin-top: 0;
    margin-bottom: 12px;
    color: #1a3c5e;
}
.scan-found, .scan-new {
    color: #2c3e50; /* Force dark text to contrast with the light backgrounds */
}
.detail-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 12px;
}
.detail-pill {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9rem;
    color: #424242;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Form Visibility Fix for Add Product & other forms */
div[data-testid="stForm"] {
    background-color: var(--secondary-background-color) !important;
    border: 1px solid var(--faded-text-40) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

div[data-testid="stForm"] label, div[data-testid="stForm"] .st-emotion-cache-10trblm {
    font-weight: 600 !important;
    color: var(--text-color) !important;
}

/* Fix input text and background visibility inside forms */
div[data-testid="stForm"] input, div[data-testid="stForm"] select, div[data-testid="stForm"] div[data-baseweb="select"] {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}
</style>
""", unsafe_allow_html=True)

from database.db_main import init_db as init_main_db
from database.db_gst import db_init as init_gst_db
from database.db_master import db_master_init
from ui.gst_registers import gst_ss_init

# Initialize DBs
init_main_db()
init_gst_db()
db_master_init()

# Session State Init
from config.settings import load_active_shop_config
load_active_shop_config()

if "cart" not in st.session_state:
    st.session_state.cart = []
if "last_qr_code" not in st.session_state:
    st.session_state.last_qr_code = ""
if "qr_result" not in st.session_state:
    st.session_state.qr_result = None
if "qr_is_new" not in st.session_state:
    st.session_state.qr_is_new = False

gst_ss_init()
st.session_state["bills"]          = st.session_state.gst_bills
st.session_state["sales_override"] = st.session_state.gst_overrides
st.session_state["suppliers"]      = st.session_state.gst_suppliers

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135800.png", width=60)
    st.markdown(f"## {st.session_state.get('shop_name', 'Raitha Snehi')}")
    st.caption("Fertilizer & Pesticide Management")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📦 Inventory",
            "🔬 QR Scanner",
            "🧾 New Bill",
            "🔍 Search Product",
            "📋 GST Registers",
            "🏪 Shop Layout",
            "📊 Reports",
            "⚙️ Settings",
        ]
    )

    if st.session_state.cart:
        st.markdown("---")
        st.markdown(f"🛒 **Cart:** {len(st.session_state.cart)} item(s)")
        if st.button("Proceed to Bill", use_container_width=True):
            st.session_state.page_nav_override = "🧾 New Bill"
            st.rerun()

# Handle external navigation override
if st.session_state.get("page_nav_override"):
    page = st.session_state.page_nav_override
    del st.session_state["page_nav_override"]

if page == "🏠 Dashboard":
    from ui.dashboard import page_dashboard
    page_dashboard()
elif page == "📦 Inventory":
    from ui.inventory import page_inventory
    page_inventory()
elif page == "🔬 QR Scanner":
    from ui.scanner import page_scanner
    page_scanner()
elif page == "🧾 New Bill":
    from ui.billing import page_billing
    page_billing()
elif page == "🔍 Search Product":
    from ui.search import page_search
    page_search()
elif page == "📋 GST Registers":
    from ui.gst_registers import page_month
    from config.settings import MONTHS

    st.markdown("## 📋 GST Registers")
    sub_pages = [("dashboard","🏠 Overview")] + MONTHS
    btn_cols = st.columns(len(sub_pages))
    
    def set_subpage(mk):
        st.session_state.gst_sub_page = mk
        
    for i,(mk,lbl) in enumerate(sub_pages):
        active = st.session_state.gst_sub_page == mk
        btn_cols[i].button(lbl, key=f"gstsub_{mk}", use_container_width=True,
                           type="primary" if active else "secondary",
                           on_click=set_subpage, args=(mk,))
    st.markdown("---")
    _sub = st.session_state.gst_sub_page
    if _sub == "dashboard":
        from ui.dashboard import page_dashboard
        page_dashboard()
    elif _sub in dict(MONTHS):
        from ui.gst_registers import page_month
        page_month(_sub)
    else:
        from ui.dashboard import page_dashboard
        page_dashboard()

elif page == "🏪 Shop Layout":
    from ui.shop_layout import page_shop_layout
    page_shop_layout()

elif page == "📊 Reports":
    from ui.reports import page_reports
    page_reports()

elif page == "⚙️ Settings":
    from ui.settings import page_settings
    page_settings()

with st.sidebar:
    st.markdown("---")
    st.markdown("**Gemini API Key** (AI bill scan)")
    _gkey = st.text_input("", value=st.session_state.get("gemini_key", ""),
                          type="password", placeholder="AIza…",
                          label_visibility="collapsed", key="gemini_key_sb")
    if _gkey:
        st.session_state.gemini_key = _gkey
    st.caption("✓ Key set" if st.session_state.get("gemini_key") else "Get free key: aistudio.google.com")

