import streamlit as st
import sqlite3
import datetime
from database.db_main import get_conn, register_barcode_scan
from database.db_master import get_all_master_products
from config.settings import LOW_STOCK_ALERT, GST_RATES, DEFAULT_GST_LABEL

def page_inventory():
    st.subheader("📦 Inventory Management")
    tab1, tab2 = st.tabs(["📋 View Inventory", "➕ Add / Edit Product"])

    conn = get_conn()

    with tab1:
        import pandas as pd
        products = conn.execute(
            "SELECT * FROM inventory ORDER BY section,row_no,slot"
        ).fetchall()
        if products:
            rows = []
            for p in products:
                rows.append({
                    "ID":       p["id"],
                    "QR Code":  p["qr_code"] or "—",
                    "Name":     p["name"],
                    "HSN":      p["hsn_code"],
                    "GST":      f"{(p['gst_rate'] or 0)*100:.0f}%",
                    "Section":  p["section"],
                    "Row":      p["row_no"],
                    "Slot":     p["slot"],
                    "Qty":      p["quantity"],
                    "Unit":     p["unit"],
                    "MRP(₹)":   p["mrp"],
                    "Status":   "🔴 LOW" if p["quantity"] < LOW_STOCK_ALERT else "🟢 OK",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No products yet.")

    with tab2:
        st.markdown("#### Add New Product Manually")
        master_products = get_all_master_products()
        master_opts = ["-- Custom Entry --"] + [p["name"] for p in master_products]
        
        sel_master = st.selectbox("Select from Master Database (Optional)", master_opts, help="Select a product to auto-fill its details.")
        
        auto_name = ""
        auto_hsn = ""
        auto_gst = DEFAULT_GST_LABEL
        
        if sel_master != "-- Custom Entry --":
            prod = next(p for p in master_products if p["name"] == sel_master)
            auto_name = prod["name"]
            auto_hsn = prod["hsn_code"]
            # Find closest matching GST rate label
            for label, rate in GST_RATES.items():
                if abs(rate - prod["gst_rate"]) < 0.01:
                    auto_gst = label
                    break

        with st.form("add_product_form"):
            c1, c2 = st.columns(2)
            p_barcode = c1.text_input("QR Code (scan or type)", placeholder="Leave blank if no QR code")
            
            p_name    = c2.text_input("Product Name *", value=auto_name)
            
            p_hsn     = c1.text_input("HSN Code *", value=auto_hsn)
            p_section = c2.selectbox("Section", [
                "Chemical Section","Organic Section","Micro-Nutrient",
                "Mineral Section","Pesticide Section","Other"])
            p_row  = c1.text_input("Row No (e.g. Row 1)")
            p_slot = c2.text_input("Slot (e.g. AA)")
            p_unit = c1.selectbox("Unit", ["Kg","Bag","Litre","Gram","Nos"])
            p_qty  = c2.number_input("Opening Stock Qty", min_value=0.0, step=0.5)
            p_mrp  = c1.number_input("MRP per Unit (₹)", min_value=0.0, step=0.5)
            p_cost = c2.number_input("Cost Price per Unit (₹)", min_value=0.0, step=0.5)
            p_gst_label = c1.selectbox("GST Rate *", list(GST_RATES.keys()),
                          index=list(GST_RATES.keys()).index(auto_gst))

            if st.form_submit_button("➕ Add Product", type="primary"):
                if p_name and p_hsn and p_row and p_slot:
                    try:
                        conn.execute("""
                            INSERT INTO inventory
                                (qr_code,name,hsn_code,section,row_no,slot,
                                 unit,quantity,mrp,cost_price,gst_rate)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)
                        """, (p_barcode.strip() or None, p_name, p_hsn, p_section,
                              p_row, p_slot, p_unit, p_qty, p_mrp, p_cost,
                              GST_RATES[p_gst_label]))
                        conn.commit()
                        if p_barcode.strip():
                            pid = conn.execute(
                                "SELECT id FROM inventory WHERE qr_code=?",
                                (p_barcode.strip(),)
                            ).fetchone()["id"]
                            register_barcode_scan(p_barcode.strip(), pid, p_name)
                        st.success(f"✅ '{p_name}' added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ QR code already registered for another product!")
                else:
                    st.error("Fill all required (*) fields.")

        st.markdown("---")
        st.markdown("#### 🔄 Restock a Product")
        all_prods = conn.execute(
            "SELECT id,name,quantity,unit FROM inventory ORDER BY name"
        ).fetchall()
        prod_opts = {f"{p['name']} (Stock: {p['quantity']} {p['unit']})": p["id"]
                     for p in all_prods}
        if prod_opts:
            sel     = st.selectbox("Select Product", list(prod_opts.keys()))
            add_qty = st.number_input("Add Quantity", min_value=0.0, step=0.5)
            if st.button("✅ Update Stock"):
                conn.execute("UPDATE inventory SET quantity=quantity+? WHERE id=?",
                             (add_qty, prod_opts[sel]))
                conn.commit()
                st.success("Stock updated!")
                st.rerun()
