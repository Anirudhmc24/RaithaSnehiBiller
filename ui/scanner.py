import streamlit as st
import sqlite3
from database.db_main import get_conn, lookup_barcode, register_barcode_scan
from services.gst_calculator import calculate_gst
from config.settings import LOW_STOCK_ALERT, GST_RATES, DEFAULT_GST_LABEL

def page_scanner():
    st.subheader("🔬 USB QR Code Scanner — Inventory & Billing")

    st.markdown("""
    <div style="background:#e3f2fd;border-left:5px solid #1565c0;
                padding:12px 16px;border-radius:8px;margin-bottom:16px;">
        <b>📡 How to use your USB QR Code Scanner:</b><br>
        1. Plug the USB QR scanner into your PC — it works like a keyboard, no drivers needed<br>
        2. Select the <b>mode</b> below (Receive Stock or Billing)<br>
        3. Click inside the <b>"Scan QR Code Here"</b> box<br>
        4. Point the scanner at any product QR code and pull the trigger<br>
        5. The scanner reads the QR and types the code automatically<br><br>
        <b>✅ Known product</b> → Shows details + restock/billing form instantly<br>
        <b>🆕 New product</b> → Prompts you to fill product details and register it
    </div>
    """, unsafe_allow_html=True)

    scan_mode = st.radio(
        "Scanner Mode",
        ["📥 Receive Stock (Add to Inventory)", "🧾 Billing (Add to Cart)"],
        horizontal=True
    )
    st.markdown("---")

    with st.form("qr_form", clear_on_submit=True):
        scanned = st.text_input(
            "🔍 Scan QR Code Here",
            placeholder="Click here, then scan product QR code with USB scanner...",
            help="The USB QR scanner acts as a keyboard — it reads and types the QR code automatically"
        )
        col_scan, col_manual = st.columns([1, 3])
        submitted = col_scan.form_submit_button("🔎 Lookup", type="primary")
        col_manual.caption("💡 Tip: Scanner auto-submits on Enter. Manual lookup button is a backup.")

    if submitted and scanned.strip():
        barcode = scanned.strip()
        product, is_new = lookup_barcode(barcode)
        st.session_state.qr_result    = product
        st.session_state.qr_is_new    = is_new
        st.session_state.last_qr_code = barcode

    barcode = st.session_state.get("last_qr_code")
    product = st.session_state.get("qr_result")
    is_new  = st.session_state.get("qr_is_new")

    conn = get_conn()

    if barcode:
        if not is_new and product:
            gst_pct     = (product.get("gst_rate") or 0.05) * 100
            stock_color = "🔴" if product["quantity"] < LOW_STOCK_ALERT else "🟢"

            st.markdown(f"""
            <div class="scan-found">
                <h3>✅ Product Found in Inventory!</h3>
                <div class="detail-row">
                    <span class="detail-pill">📦 <b>{product['name']}</b></span>
                    <span class="detail-pill">📱 QR Code: <b>{barcode}</b></span>
                    <span class="detail-pill">HSN: {product['hsn_code']}</span>
                    <span class="detail-pill">GST: {gst_pct:.0f}%</span>
                </div>
                <div class="detail-row">
                    <span class="detail-pill">📍 {product['location_path']}</span>
                    <span class="detail-pill">{stock_color} Stock: <b>{product['quantity']} {product['unit']}</b></span>
                    <span class="detail-pill">💰 MRP: ₹{product['mrp']:.2f}/{product['unit']}</span>
                    <span class="detail-pill">🏭 Cost: ₹{product['cost_price']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if product["quantity"] < LOW_STOCK_ALERT:
                st.warning(f"⚠️ Low Stock Alert! Only **{product['quantity']} {product['unit']}** remaining.")

            register_barcode_scan(barcode, product["id"], product["name"])

            if "Receive Stock" in scan_mode:
                st.markdown("#### 📥 Update Stock for this Product")
                with st.form("restock_form"):
                    rc1, rc2, rc3 = st.columns(3)
                    r_qty  = rc1.number_input("Quantity Received",   min_value=0.1, step=0.5, value=1.0)
                    r_cost = rc2.number_input("Updated Cost (₹/unit)", min_value=0.0, step=0.5, value=float(product["cost_price"]))
                    r_mrp  = rc3.number_input("Updated MRP (₹/unit)",  min_value=0.0, step=0.5, value=float(product["mrp"]))
                    if st.form_submit_button("✅ Confirm Stock Receipt", type="primary"):
                        conn.execute("""
                            UPDATE inventory
                            SET quantity=quantity+?, cost_price=?, mrp=?
                            WHERE id=?
                        """, (r_qty, r_cost, r_mrp, product["id"]))
                        conn.commit()
                        new_qty = product["quantity"] + r_qty
                        st.success(f"✅ Stock updated! **{product['name']}** → **{new_qty} {product['unit']}** now in stock.")
                        st.session_state.last_qr_code   = ""
                        st.session_state.qr_result      = None
                        st.rerun()

            else:
                st.markdown("#### 🧾 Add this Product to Bill")
                with st.form("scan_bill_form"):
                    b_qty = st.number_input(f"Quantity to Bill (Available: {product['quantity']} {product['unit']})", min_value=0.1, step=0.5, value=1.0)
                    gst_rate = product.get("gst_rate") or 0.05
                    taxable  = round(product["mrp"] * b_qty, 2)
                    cgst_prev, sgst_prev, total_prev = calculate_gst(taxable, gst_rate)
                    pc1,pc2,pc3,pc4 = st.columns(4)
                    pc1.metric("Taxable",  f"₹ {taxable:.2f}")
                    pc2.metric(f"CGST ({gst_rate/2*100:.1f}%)", f"₹ {cgst_prev:.2f}")
                    pc3.metric(f"SGST ({gst_rate/2*100:.1f}%)", f"₹ {sgst_prev:.2f}")
                    pc4.metric("Line Total", f"₹ {total_prev:.2f}")

                    if st.form_submit_button("➕ Add to Cart", type="primary"):
                        if b_qty > product["quantity"]:
                            st.error(f"❌ Only {product['quantity']} {product['unit']} in stock!")
                        else:
                            cgst, sgst, total = calculate_gst(round(product["mrp"] * b_qty, 2), gst_rate)
                            existing = next((i for i, c in enumerate(st.session_state.cart) if c["product_id"] == product["id"]), None)
                            if existing is not None:
                                st.session_state.cart[existing]["quantity"] += b_qty
                                c_ = st.session_state.cart[existing]
                                new_tax = round(c_["unit_price"] * c_["quantity"], 2)
                                c_["taxable_value"], c_["cgst_amount"], c_["sgst_amount"], c_["line_total"] = new_tax, *calculate_gst(new_tax, gst_rate)
                            else:
                                st.session_state.cart.append({
                                    "product_id":    product["id"],
                                    "product_name":  product["name"],
                                    "hsn_code":      product["hsn_code"],
                                    "gst_rate":      gst_rate,
                                    "quantity":      b_qty,
                                    "unit":          product["unit"],
                                    "unit_price":    product["mrp"],
                                    "taxable_value": round(product["mrp"] * b_qty, 2),
                                    "cgst_amount":   cgst,
                                    "sgst_amount":   sgst,
                                    "line_total":    total,
                                })
                            st.success(f"✅ **{product['name']}** × {b_qty} added to cart! Go to 🧾 New Bill to complete the invoice.")
                            st.session_state.last_qr_code   = ""
                            st.session_state.qr_result      = None
                            st.rerun()

        elif is_new:
            st.markdown(f"""
            <div class="scan-new">
                <h3>🆕 New Product Detected — First Time Scan!</h3>
                <p>
                    QR Code <b>{barcode}</b> is <b>not yet registered</b> in your inventory.<br>
                    This is the <b>first time</b> this product is being added to Sri Lakshmi Venkateshwara Traders.<br>
                    Fill in the details below and click <b>Register Product</b> to save it permanently.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📋 Register New Product Details")
            st.info(f"📱 QR Code **`{barcode}`** will be linked to this product automatically.")

            with st.form("new_product_scan_form"):
                fc1, fc2 = st.columns(2)
                np_name    = fc1.text_input("Product Name *", placeholder="e.g. Urea (46% N)")
                np_hsn     = fc2.text_input("HSN Code *", placeholder="e.g. 31021010", help="Find HSN on your purchase bill or GST portal")
                
                from ui.components import render_location_selector
                from database.db_main import get_shop_layout
                layout_tree = get_shop_layout()
                np_location_path = render_location_selector(layout_tree, "scan_new")
                
                np_unit    = fc2.selectbox("Unit", ["Kg","Bag","Litre","Gram","Nos"])
                np_qty     = fc1.number_input("Opening Stock Qty",    min_value=0.0, step=0.5)
                np_mrp     = fc2.number_input("MRP per Unit (₹)",     min_value=0.0, step=0.5)
                np_cost    = fc1.number_input("Cost Price per Unit (₹)", min_value=0.0, step=0.5)
                np_gst     = fc2.selectbox("GST Rate *", list(GST_RATES.keys()), index=list(GST_RATES.keys()).index(DEFAULT_GST_LABEL))

                st.markdown("---")
                st.markdown("**📊 GST Preview for this Product**")
                if np_mrp > 0 and np_qty > 0:
                    rate      = GST_RATES[np_gst]
                    taxable   = round(np_mrp * np_qty, 2)
                    cgst_p, sgst_p, total_p = calculate_gst(taxable, rate)
                    pv1,pv2,pv3,pv4,pv5 = st.columns(5)
                    pv1.metric("MRP × Qty",       f"₹ {taxable:.2f}")
                    pv2.metric(f"CGST ({rate/2*100:.1f}%)", f"₹ {cgst_p:.2f}")
                    pv3.metric(f"SGST ({rate/2*100:.1f}%)", f"₹ {sgst_p:.2f}")
                    pv4.metric("Total GST",        f"₹ {cgst_p+sgst_p:.2f}")
                    pv5.metric("Invoice Value",    f"₹ {total_p:.2f}")
                else:
                    st.caption("Enter MRP and Opening Qty above to see GST preview.")

                st.markdown("---")
                if st.form_submit_button("✅ Register Product & Save to Inventory", type="primary"):
                    if np_name and np_hsn and np_location_path:
                        try:
                            conn.execute("""
                                INSERT INTO inventory
                                    (qr_code,name,hsn_code,location_path,section,row_no,slot,
                                     unit,quantity,mrp,cost_price,gst_rate)
                                VALUES (?,?,?,?,'','','',?,?,?,?,?)
                            """, (barcode, np_name, np_hsn, np_location_path,
                                  np_unit, np_qty,
                                  np_mrp, np_cost, GST_RATES[np_gst]))
                            conn.commit()

                            new_id = conn.execute(
                                "SELECT id FROM inventory WHERE qr_code=?", (barcode,)
                            ).fetchone()["id"]
                            register_barcode_scan(barcode, new_id, np_name)

                            rate    = GST_RATES[np_gst]
                            st.success("✅ Product successfully registered in inventory!")
                            st.markdown(f"""
                            | Field | Value |
                            |---|---|
                            | **Product Name** | {np_name} |
                            | **QR Code** | `{barcode}` |
                            | **HSN Code** | {np_hsn} |
                            | **Location** | {np_location_path} |
                            | **Opening Stock** | {np_qty} {np_unit} |
                            | **MRP** | ₹ {np_mrp:.2f} / {np_unit} |
                            | **Cost Price** | ₹ {np_cost:.2f} / {np_unit} |
                            | **GST Rate** | {rate*100:.0f}% (CGST {rate/2*100:.1f}% + SGST {rate/2*100:.1f}%) |
                            | **Stock Value (MRP)** | ₹ {np_mrp * np_qty:,.2f} |
                            """)

                            st.session_state.last_qr_code   = ""
                            st.session_state.qr_result      = None
                            st.session_state.qr_is_new      = False
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("❌ This QR code is already registered!")
                    else:
                        st.error("Please fill all required (*) fields.")

    st.markdown("---")
    st.markdown("#### 📜 Scan History (Last 20)")
    import pandas as pd
    history = conn.execute("""
        SELECT br.qr_code, br.product_name, br.first_scanned, br.scan_count,
               i.location_path, i.quantity, i.unit
        FROM qr_registry br
        LEFT JOIN inventory i ON br.product_id = i.id
        ORDER BY br.first_scanned DESC LIMIT 20
    """).fetchall()
    if history:
        df = pd.DataFrame([dict(r) for r in history])
        df.columns = ["QR Code","Product","First Scanned","Times Scanned","Location","Current Qty","Unit"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No scan history yet. Start scanning products!")
