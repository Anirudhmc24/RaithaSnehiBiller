# config/settings.py

import os

# ─────────────────────────────────────────────────────────────────────────────
# SHOP CONSTANTS  — edit these once
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH         = os.path.abspath(os.path.join(os.getcwd(), "slv_traders.db"))
GST_DB_PATH     = os.path.abspath(os.path.join(os.getcwd(), "gst_data.db"))
SHOP_NAME       = "Sri Lakshmi Venkateshwara Traders"
SHOP_ADDRESS1   = "#20, Near Bank Of Baroda"
SHOP_ADDRESS2   = "Mysore Bangalore Expressway, Thubinakere"
SHOP_ADDRESS3   = "Mandya, Karnataka — 571402"
SHOP_PHONE      = "+91-9743007647"
SHOP_EMAIL      = "chandana4192@gmail.com"
SHOP_ADDR1      = SHOP_ADDRESS1 + ", " + SHOP_ADDRESS2
SHOP_ADDR2      = SHOP_ADDRESS3
SHOP_STATE      = "Karnataka — 29"
GSTIN           = "29CDTPB8883L1ZH"
STATE_CODE      = "29"                # 29 = Karnataka
LOW_STOCK_ALERT = 10                  # show alert below this qty

# Purchase → Sales conversion ratios (from Oct-2025 actuals)
RATIO_18_TO_18 = 0.912
RATIO_18_TO_12 = 0.0064
RATIO_5_TO_5   = 1.25
RATIO_EX_TO_EX = 0.865

# ─────────────────────────────────────────────────────────────────────────────
# GST RATE MASTER
# Intra-state: total GST split 50:50 into CGST + SGST
# ─────────────────────────────────────────────────────────────────────────────
GST_RATES = {
    "0%  — Exempt (Seeds/Organic)"   : 0.00,
    "5%  — Fertilizers (Ch.31)"      : 0.05,
    "12% — Pesticides (Ch.38)"       : 0.12,
    "18% — Micronutrients/Chemicals" : 0.18,
    "28% — Specialty Chemicals"      : 0.28,
}
DEFAULT_GST_LABEL = "5%  — Fertilizers (Ch.31)"

# ─────────────────────────────────────────────────────────────────────────────
# GST REGISTERS CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
MON_ABBR = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
            7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}

MONTHS = [
    ("11-2025", "November 2025"),
    ("12-2025", "December 2025"),
    ("01-2026", "January 2026"),
    ("02-2026", "February 2026"),
    ("03-2026", "March 2026"),
    ("04-2026", "April 2026"),
    ("05-2026", "May 2026"),
]

MONTH_FP = {
    "11-2025":"112025", "12-2025":"122025",
    "01-2026":"012026", "02-2026":"022026", "03-2026":"032026",
    "04-2026":"042026",
    "05-2026":"052026",
}

OCT_LAST_VNO = 474          # October sales ended at voucher 474
OCT_LAST_PUR_VNO = 61       # October purchase ended at voucher 61

VOUCHER_START = {
    "11-2025": 475,
    "12-2025": 592,
    "01-2026": 714,
    "02-2026": 834,
    "03-2026": 940,
    "04-2026": 1071,
}

NAV_PAGES = [
    ("🏠", "Dashboard"),
    ("📦", "Inventory"),
    ("🔬", "QR Scanner"),
    ("🧾", "New Bill"),
    ("📊", "Reports"),
    ("🔍", "Search Product"),
    ("📋", "GST Registers"),
    ("🏪", "Shop Layout"),
]

def load_active_shop_config():
    import streamlit as st
    try:
        from database.db_main import get_shop_settings
        db_settings = get_shop_settings()
    except Exception:
        db_settings = {}

    st.session_state["shop_name"] = db_settings.get("shop_name", SHOP_NAME)
    st.session_state["shop_address1"] = db_settings.get("shop_address1", SHOP_ADDRESS1)
    st.session_state["shop_address2"] = db_settings.get("shop_address2", SHOP_ADDRESS2)
    st.session_state["shop_address3"] = db_settings.get("shop_address3", SHOP_ADDRESS3)
    st.session_state["shop_phone"] = db_settings.get("shop_phone", SHOP_PHONE)
    st.session_state["shop_email"] = db_settings.get("shop_email", SHOP_EMAIL)
    st.session_state["shop_gstin"] = db_settings.get("shop_gstin", GSTIN)
    st.session_state["invoice_prefix"] = db_settings.get("invoice_prefix", "RS-")

    st.session_state["shop_addr1"] = f'{st.session_state["shop_address1"]}, {st.session_state["shop_address2"]}'
    st.session_state["shop_addr2"] = st.session_state["shop_address3"]
