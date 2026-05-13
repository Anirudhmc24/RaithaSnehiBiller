# 🌱 Raitha Snehi Biller - Complete User Guide

Welcome to the **Raitha Snehi Biller** (formerly SLVT GST Tool). This professional-grade application is designed specifically for Fertilizer, Pesticide, and Seed retail shops to manage inventory, automate billing, and simplify GST compliance.

---

## 🚀 1. Getting Started from Scratch

### Method A: Running the Executable (Recommended)
1. Navigate to the `dist/` folder.
2. Double-click **`Raitha_Snehi.exe`**.
3. A console window will open, and your web browser will automatically launch the interface at `http://localhost:8501`.

### Method B: Running from Source
If you are a developer or have Python installed:
1. Open the folder and double-click **`START_SHOP.bat`**.
2. This script will automatically check for Python, install required libraries (`streamlit`, `pandas`, `reportlab`, etc.), and launch the app.

### Initial Configuration
Before making your first bill:
1. Go to **⚙️ Settings** in the sidebar.
2. Enter your **Shop Name**, **GSTIN**, **Address**, and **Contact Details**.
3. Set your **Invoice Prefix** (e.g., `RSB/24-25/`).
4. Click **Save Shop Settings**. These details will now appear on all your PDF invoices.

---

## 📦 2. Inventory Management

### Adding Products
Go to **📦 Inventory** → **Add / Edit Product**:
- **Master Database**: Start typing in the "Master Database" dropdown. We have pre-loaded common fertilizers and pesticides with their HSN codes and GST rates. Selecting one auto-fills the form.
- **QR Code**: Click the input and scan the product's barcode/QR code to link it.
- **Location**: Use the visual selector to assign the product to a specific Rack/Slot in your shop.
- **Opening Stock**: Enter your current stock levels and unit (Kg, Bag, Litre, etc.).

### Restocking
- Scroll down to **🔄 Restock a Product**.
- Select the item and enter the new quantity received.

---

## 🔬 3. QR Scanner (Purchase & Registration)

This module is used when you receive new stock or want to register a product's barcode for the first time.
1. **Scan Barcode**: Point your scanner at a product.
2. **If recognized**: It shows the current stock and location.
3. **If new**: It prompts you to register it. You can pick from the Master Database to quickly link a new barcode to a known product.

### AI Bill Scanning (Purchase)
In **📋 GST Registers** (explained below), you can upload photos of your supplier invoices. The **Gemini AI** will automatically read the supplier name, GSTIN, invoice date, and taxable values for each GST slab, saving you minutes of manual entry.

---

## 🧾 4. New Bill (Sales)

The sales module is designed for speed during peak hours.

1. **Step 1: Scan Product**: Click the scan box and scan the product QR code. The item is added to the cart instantly.
2. **Manual Entry**: If a product doesn't have a barcode, use the "Add item manually" expander.
3. **Step 2: Cart Management**:
   - **Quantity**: Items are added as 1 unit by default. Scanning again increases quantity.
   - **Discounts**: You can apply a **Fixed Amount** or **Percentage** discount. The tax values (CGST/SGST) are automatically recalculated proportionally.
4. **Step 3: Generate Bill**:
   - Enter **Customer Name** (optional, defaults to "Cash Customer").
   - Click **✅ GENERATE BILL**.
   - The app deducts stock, saves the record, and provides a **Download PDF** button for a professional GST invoice.

---

## 📋 5. GST Registers & Compliance

This is the "Brain" of the tool, located in the **📋 GST Registers** tab.

### Monthly Tabs
Navigation is split by months. Select the month you are filing for.

### 📥 Purchase Bills
- **Manual Entry**: A detailed form to enter supplier bills, split by 5%, 12%, and 18% slabs.
- **AI Scan**: Upload invoice photos. Requires a **Gemini API Key** (enter in sidebar).
- **HSN Line Items**: For each purchase bill, you can add granular HSN data. This is crucial for accurate GSTR-1 HSN reporting.

### 📊 Sales (Derived)
This tool uses a "Purchase-to-Sales" derivation logic:
- It calculates your estimated sales based on what you purchased.
- **Smart Sales Override**: Enter your **Desired Total Sales** for the month (e.g., ₹ 15,00,000). The tool will automatically distribute this amount across all days of the month using a realistic pattern, splitting it between 18% and 5% slabs.

### 🔢 HSN Summary
- Click **🔄 Auto-compute HSN rows from bills**.
- The tool aggregates all HSN codes from your purchase bills and calculates the output sales quantities and values automatically.

### 📤 Download Documents
At the end of the month, download:
1. **Sales Register (Excel)**: Detailed daily sales for your accountant.
2. **Purchase Register (Excel)**: List of all supplier bills and ITC.
3. **GSTR-1 JSON**: The exact file required by the **GST Portal**. You can upload this directly to `gst.gov.in` to file your returns in seconds.

---

## ⚙️ 6. Advanced Settings & Features

### Shop Layout
- Go to **🏪 Shop Layout** to define your Racks and Shelves.
- This helps you find products quickly and manage a large inventory.

### Reports
- **📊 Reports** provides a high-level view of your sales and purchase history across different months.

### Gemini AI Key
- To use the AI scanning feature, get a free key from [aistudio.google.com](https://aistudio.google.com).
- Paste it into the sidebar. It is saved in your local session for privacy.

---

## 🔄 7. Common Workflows

### Filing GSTR-1 in 5 Minutes
1. **Upload**: Photos of all purchase bills in **📋 GST Registers** -> **📥 Purchase Bills**.
2. **Review**: Check and fix any AI scanning errors in the "Review" expanders.
3. **Set Target**: Go to **📊 Sales (derived)** and use **Smart Sales Override** to set your monthly sales target.
4. **HSN**: Go to **🔢 HSN Summary** and click **Auto-compute**.
5. **File**: Download the **GSTR-1 JSON** and upload it to the GST Portal.

### Adding a New Product to the Shop
1. **Inventory**: Go to **📦 Inventory** -> **Add Product**.
2. **Scan**: Scan the product barcode.
3. **Auto-fill**: Select the product name from the Master Database.
4. **Locate**: Pick the Rack/Slot where you will keep it.
5. **Save**: Click **Add Product**. Now it can be scanned for billing immediately.

---

## 🛠️ 8. Troubleshooting

- **"QR Code not recognized"**: Ensure the product is registered in the **📦 Inventory** tab with that specific code.
- **"Database Locked"**: Ensure only one instance of the application is running.
- **PDF Not Opening**: Check if your browser has a pop-up blocker or if the file was downloaded to your "Downloads" folder.

---

**Raitha Snehi Biller** — *Empowering Farmers through Digital Efficiency.*
