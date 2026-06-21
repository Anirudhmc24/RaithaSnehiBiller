import streamlit as st

st.set_page_config(
    page_title="Raitha Snehi Biller",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom css stylesheet
import os
css_path = os.path.join(os.path.dirname(__file__), "ui", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("Custom stylesheet ui/style.css not found.")

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

if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Dashboard"

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

# Authentication Page Guard
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    from ui.login import page_login
    page_login()
    st.stop()

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand-wrapper">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135800.png" width="42" style="border-radius: 8px;">
        <div class="sidebar-brand-text">
            <h2>Raitha Snehi Biller</h2>
            <span>Fertilizer & Pesticide Management</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Large navigation buttons
    pages = [
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
    if st.session_state.get("user_role") == "admin":
        pages.append("👥 Admin Panel")
    for p in pages:
        is_active = (st.session_state.active_page == p)
        if st.button(
            p,
            key=f"nav_btn_{p}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.active_page = p
            st.rerun()

    if st.session_state.cart:
        st.markdown("---")
        st.markdown(f"🛒 **Cart:** {len(st.session_state.cart)} item(s)")
        if st.button("Proceed to Bill", key="sidebar_proceed_bill", use_container_width=True):
            st.session_state.page_nav_override = "🧾 New Bill"
            st.rerun()

# Handle external navigation override
if st.session_state.get("page_nav_override"):
    st.session_state.active_page = st.session_state.page_nav_override
    del st.session_state["page_nav_override"]

page = st.session_state.active_page

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
elif page == "👥 Admin Panel":
    from ui.admin_panel import page_admin_panel
    page_admin_panel()

with st.sidebar:
    st.markdown("---")
    st.markdown("**Gemini API Key** (AI bill scan)")
    _gkey = st.text_input("Gemini API Key", value=st.session_state.get("gemini_key", ""),
                          type="password", placeholder="AIza…",
                          label_visibility="collapsed", key="gemini_key_sb")
    if _gkey:
        st.session_state.gemini_key = _gkey
    st.caption("✓ Key set" if st.session_state.get("gemini_key") else "Get free key: aistudio.google.com")
    
    st.markdown("---")
    if st.button("🚪 Sign Out", key="sidebar_signout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.toast("Signed out successfully!", icon="🚪")
        st.rerun()

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 0.72rem; color: #64748b; line-height: 1.4; padding: 4px 0;">
        🏪 Active Store:<br>
        <span style="font-weight: 700; color: #334155;">{st.session_state.get('shop_name', 'Sri Lakshmi Venkateshwara Traders')}</span>
    </div>
    """, unsafe_allow_html=True)

# Floating Action Button for New Bill
if st.session_state.active_page != "🧾 New Bill":
    st.markdown('<div class="floating-btn-wrap">', unsafe_allow_html=True)
    if st.button("🧾 Quick Bill", key="floating_new_bill", use_container_width=True):
        st.session_state.active_page = "🧾 New Bill"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

