=====================================================================
 Sri Lakshmi Venkateshwara Traders — Integrated Shop Manager
 GSTIN: 29CDTPB8883L1ZH
=====================================================================

YOUR FILES:
  app.py               ← Single integrated app
  START_SHOP.bat       ← Double-click to launch
  slv_traders.db       ← Shop data (invoices, inventory, billing)
  gst_data.db          ← GST purchase bills (auto-created on first run)
  Sales_Registers_Generated/  ← Pre-generated sales for Nov–Mar

=====================================================================
 SETUP (first time only)
=====================================================================

STEP 1 — Copy all files into one folder:
  C:\SLVTraders\
    app.py
    START_SHOP.bat
    slv_traders.db
    Sales_Registers_Generated\  (whole folder)

  If you already have a C:\SLVTraders\ folder, just replace app.py
  and START_SHOP.bat — your existing slv_traders.db is preserved.

STEP 2 — Double-click START_SHOP.bat
  → Opens at http://localhost:8501
  → All 7 pages available in the sidebar

STEP 3 — Get free Gemini API key (for AI bill photo scanning):
  Go to https://aistudio.google.com → Get API key
  Enter it in the sidebar when on the GST Registers page

=====================================================================
 PAGES
=====================================================================

  🏠 Dashboard      — daily/weekly/monthly sales overview
  📦 Inventory      — stock management
  🔬 QR Scanner     — scan barcodes to bill or restock
  🧾 New Bill       — create invoices, print PDF
  📊 Reports        — GSTR-1 Excel export, invoice history
  🔍 Search Product — find products by name/QR
  📋 GST Registers  — purchase bills entry + generate:
                        • Sales Register .xlsx  (Tally format)
                        • Purchase Register .xlsx
                        • GSTR-1 .json for portal upload

=====================================================================
 DATA FILES — BACK THESE UP
=====================================================================

  slv_traders.db  — all your billing, inventory, invoices
  gst_data.db     — all your purchase bills for GST filing

  Back up both files regularly to USB / Google Drive.

=====================================================================
