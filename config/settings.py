# config/settings.py

# ─────────────────────────────────────────────────────────────────────────────
# SHOP CONSTANTS  — edit these once
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH         = "slv_traders.db"
GST_DB_PATH     = "gst_data.db"
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
]

MONTH_FP = {
    "11-2025":"112025", "12-2025":"122025",
    "01-2026":"012026", "02-2026":"022026", "03-2026":"032026",
    "04-2026":"042026",
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
]
