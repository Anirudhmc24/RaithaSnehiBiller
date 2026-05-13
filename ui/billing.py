import streamlit as st
import datetime
import pandas as pd
from database.db_main import get_conn, lookup_barcode, generate_invoice_no
from services.gst_calculator import calculate_gst
from services.pdf_generator import generate_pdf_invoice
from config.settings import LOW_STOCK_ALERT

def page_billing():
    conn = get_conn()
    for k, v in {"bill_cust_name":"","bill_cust_phone":"","bill_cust_gstin":""}.items():
        if k not in st.session_state:
            st.session_state[k] = v

    st.markdown("""
    <div style="background:#1a3c5e;border-radius:12px;padding:18px 22px;margin-bottom:18px;">
        <h2 style="color:white;margin:0 0 4px 0;font-size:1.4rem;">📱 Step 1 — Scan Product</h2>
        <p style="color:#c8e6c9;margin:0;font-size:0.9rem;">
            Click the box below → point scanner at QR code → item added instantly
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("bill_qr_form", clear_on_submit=True):
        bill_qr = st.text_input(
            "Scan QR Code",
            placeholder="👆 Click here first, then scan the product QR code...",
            label_visibility="collapsed"
        )
        scan_submitted = st.form_submit_button(
            "➕  ADD TO CART",
            type="primary",
            use_container_width=True
        )

    if scan_submitted and bill_qr.strip():
        bc = bill_qr.strip()
        product, is_new = lookup_barcode(bc)

        if is_new or product is None:
            st.error(f"❌  QR code not recognised. Register this product in 🔬 QR Scanner first.")
        elif product["quantity"] <= 0:
            st.error(f"❌  {product['name']} is OUT OF STOCK.")
        else:
            gst_rate = product.get("gst_rate") if product.get("gst_rate") is not None else 0.05
            existing = next((i for i,c in enumerate(st.session_state.cart)
                             if c["product_id"] == product["id"]), None)
            if existing is not None:
                new_qty = st.session_state.cart[existing]["quantity"] + 1
                if new_qty > product["quantity"]:
                    st.error(f"❌  Only {product['quantity']} {product['unit']} in stock!")
                else:
                    st.session_state.cart[existing]["quantity"] = new_qty
                    new_tax = round(product["mrp"] * new_qty, 2)
                    (st.session_state.cart[existing]["taxable_value"],
                     st.session_state.cart[existing]["cgst_amount"],
                     st.session_state.cart[existing]["sgst_amount"],
                     st.session_state.cart[existing]["line_total"]) = (
                        new_tax, *calculate_gst(new_tax, gst_rate))
                    st.toast(f"✅  {product['name']}  ×{new_qty}", icon="🛒")
            else:
                taxable = round(product["mrp"], 2)
                cgst, sgst, total = calculate_gst(taxable, gst_rate)
                st.session_state.cart.append({
                    "product_id":    product["id"],
                    "product_name":  product["name"],
                    "hsn_code":      product["hsn_code"],
                    "gst_rate":      gst_rate,
                    "quantity":      1.0,
                    "unit":          product["unit"],
                    "unit_price":    product["mrp"],
                    "taxable_value": taxable,
                    "cgst_amount":   cgst,
                    "sgst_amount":   sgst,
                    "line_total":    total,
                })
                st.toast(f"✅  {product['name']}  added  ₹{product['mrp']:.2f}", icon="🛒")
            st.rerun()

    with st.expander("⌨️  Add item manually (product has no QR code)"):
        all_prods = conn.execute(
            "SELECT id,name,hsn_code,unit,quantity,mrp,gst_rate FROM inventory ORDER BY name"
        ).fetchall()
        prod_map  = {p["name"]: dict(p) for p in all_prods}
        sel_name  = st.selectbox("Product", ["-- select --"] + list(prod_map.keys()))
        man_qty   = st.number_input("Qty", min_value=0.1, step=0.5, value=1.0)
        if st.button("➕ Add", key="manual_add"):
            if sel_name != "-- select --":
                prod     = prod_map[sel_name]
                gst_rate = prod.get("gst_rate") if prod.get("gst_rate") is not None else 0.05
                if man_qty > prod["quantity"]:
                    st.error(f"❌  Only {prod['quantity']} {prod['unit']} available!")
                else:
                    taxable = round(prod["mrp"] * man_qty, 2)
                    cgst, sgst, total = calculate_gst(taxable, gst_rate)
                    existing = next((i for i,c in enumerate(st.session_state.cart)
                                     if c["product_id"] == prod["id"]), None)
                    if existing is not None:
                        st.session_state.cart[existing]["quantity"] += man_qty
                        c_ = st.session_state.cart[existing]
                        new_tax = round(c_["unit_price"] * c_["quantity"], 2)
                        (c_["taxable_value"], c_["cgst_amount"],
                         c_["sgst_amount"],   c_["line_total"]) = (
                            new_tax, *calculate_gst(new_tax, gst_rate))
                    else:
                        st.session_state.cart.append({
                            "product_id":    prod["id"],
                            "product_name":  prod["name"],
                            "hsn_code":      prod["hsn_code"],
                            "gst_rate":      gst_rate,
                            "quantity":      man_qty,
                            "unit":          prod["unit"],
                            "unit_price":    prod["mrp"],
                            "taxable_value": taxable,
                            "cgst_amount":   cgst,
                            "sgst_amount":   sgst,
                            "line_total":    total,
                        })
                    st.rerun()

    st.markdown("""
    <div style="background:#2e7d32;border-radius:12px;padding:14px 22px;margin:18px 0 12px 0;">
        <h2 style="color:white;margin:0;font-size:1.3rem;">🛒 Step 2 — Items in Cart</h2>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.cart:
        cart_display = []
        for item in st.session_state.cart:
            cart_display.append({
                "Product":   item["product_name"],
                "Qty":       item["quantity"],
                "Unit":      item["unit"],
                "MRP (₹)":   f"{item['unit_price']:.2f}",
                "Sale Rate": f"{item.get('sale_price', item['unit_price']):.2f}",
                "Total (₹)": f"{item['line_total']:.2f}",
            })
        st.dataframe(pd.DataFrame(cart_display), use_container_width=True, hide_index=True)

        st.caption("Tap ✖ to remove an item:")
        cols = st.columns(min(len(st.session_state.cart), 4))
        for i, item in enumerate(st.session_state.cart):
            if cols[i % 4].button(f"✖ {item['product_name'][:18]}", key=f"del_{i}", use_container_width=True):
                st.session_state.cart.pop(i)
                st.rerun()

        sub_taxable = sum(c["taxable_value"] for c in st.session_state.cart)
        sub_cgst    = sum(c["cgst_amount"]   for c in st.session_state.cart)
        sub_sgst    = sum(c["sgst_amount"]   for c in st.session_state.cart)
        sub_total   = sum(c["line_total"]    for c in st.session_state.cart)

        st.markdown("""
        <div style="background:#f3e5f5;border-left:5px solid #7b1fa2;
                    border-radius:8px;padding:12px 18px;margin:12px 0 8px 0;">
            <b>🏷️ Discount (Optional)</b> — Leave at 0 if no discount
        </div>
        """, unsafe_allow_html=True)

        disc_col1, disc_col2 = st.columns(2)
        disc_type = disc_col1.radio("Discount Type", ["₹ Fixed Amount", "% Percentage"], horizontal=True, label_visibility="collapsed")
        disc_val = disc_col2.number_input("Discount value", min_value=0.0, max_value=sub_total if disc_type == "₹ Fixed Amount" else 100.0, step=0.5, value=0.0, label_visibility="collapsed", format="%.2f")

        if disc_type == "% Percentage":
            discount_amt = round(sub_total * disc_val / 100, 2)
        else:
            discount_amt = round(min(disc_val, sub_total), 2)

        grand_total   = round(sub_total   - discount_amt, 2)
        ratio         = grand_total / sub_total if sub_total > 0 else 1
        grand_taxable = round(sub_taxable * ratio, 2)
        grand_cgst    = round(sub_cgst    * ratio, 2)
        grand_sgst    = round(sub_sgst    * ratio, 2)

        if discount_amt > 0:
            st.markdown(f"""
            <div style="background:#fff8e1;border:2px solid #f9a825;border-radius:12px;
                        padding:16px 24px;margin:12px 0;text-align:center;">
                <p style="margin:0;color:#555;font-size:0.9rem;">
                    Subtotal &nbsp;₹{sub_total:.2f}
                    &nbsp; — &nbsp;
                    <span style="color:#c62828;font-weight:bold;">
                        Discount&nbsp;
                        {"(" + str(disc_val) + "%)" if disc_type == "% Percentage" else ""}
                        &nbsp;₹{discount_amt:.2f}
                    </span>
                </p>
                <h1 style="margin:6px 0 0 0;color:#1a3c5e;font-size:2.2rem;">
                    TOTAL &nbsp; ₹ {grand_total:.2f}
                </h1>
                <p style="margin:4px 0 0 0;color:#777;font-size:0.8rem;">
                    Taxable ₹{grand_taxable:.2f} + CGST ₹{grand_cgst:.2f} + SGST ₹{grand_sgst:.2f}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#fff8e1;border:2px solid #f9a825;border-radius:12px;
                        padding:16px 24px;margin:12px 0;text-align:center;">
                <p style="margin:0;color:#555;font-size:0.9rem;">
                    Taxable ₹{grand_taxable:.2f} &nbsp;+&nbsp;
                    CGST ₹{grand_cgst:.2f} &nbsp;+&nbsp;
                    SGST ₹{grand_sgst:.2f}
                </p>
                <h1 style="margin:4px 0 0 0;color:#1a3c5e;font-size:2.2rem;">
                    TOTAL &nbsp; ₹ {grand_total:.2f}
                </h1>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#e8f5e9;border-radius:12px;padding:14px 22px;margin-bottom:12px;">
            <h2 style="color:#1b5e20;margin:0;font-size:1.3rem;">🖨️ Step 3 — Generate Bill</h2>
            <p style="color:#555;margin:4px 0 0 0;font-size:0.85rem;">
                Optional: enter customer name below. Then press the green button.
            </p>
        </div>
        """, unsafe_allow_html=True)

        cust_name_input = st.text_input("Customer Name (optional)", value=st.session_state.bill_cust_name, placeholder="Leave empty for Cash Sale")
        if cust_name_input:
            st.session_state.bill_cust_name = cust_name_input

        if st.button("✅   GENERATE BILL & DOWNLOAD PDF", type="primary", use_container_width=True):
            inv_no   = generate_invoice_no()
            inv_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c_name   = st.session_state.bill_cust_name or "Cash Customer"

            conn.execute("""
                INSERT INTO invoices
                    (invoice_no,customer_name,customer_phone,customer_gstin,
                     invoice_date,taxable_value,cgst_amount,sgst_amount,total_amount)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (inv_no, c_name, "", "", inv_date, grand_taxable, grand_cgst, grand_sgst, grand_total))

            for item in st.session_state.cart:
                conn.execute("""
                    INSERT INTO invoice_items
                        (invoice_no,product_id,product_name,hsn_code,
                         quantity,unit,unit_price,gst_rate,
                         taxable_value,cgst_amount,sgst_amount,line_total)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (inv_no, item["product_id"], item["product_name"],
                      item["hsn_code"], item["quantity"], item["unit"],
                      item["unit_price"], item.get("gst_rate", 0.05),
                      item["taxable_value"], item["cgst_amount"],
                      item["sgst_amount"], item["line_total"]))
                conn.execute("UPDATE inventory SET quantity=quantity-? WHERE id=?", (item["quantity"], item["product_id"]))
                rem = conn.execute("SELECT quantity,name FROM inventory WHERE id=?", (item["product_id"],)).fetchone()
                if rem and rem["quantity"] < LOW_STOCK_ALERT:
                    st.warning(f"⚠️  Low stock: {rem['name']} → {rem['quantity']} left")

            conn.commit()

            cart_snapshot = list(st.session_state.cart)
            pdf_bytes = generate_pdf_invoice({
                "invoice_no":    inv_no,
                "invoice_date":  inv_date,
                "customer_name": c_name,
                "customer_phone":"",
                "customer_gstin":"",
                "taxable_value": grand_taxable,
                "cgst_amount":   grand_cgst,
                "sgst_amount":   grand_sgst,
                "total_amount":  grand_total,
                "discount_amt":  discount_amt,
                "sub_total":     sub_total,
            }, cart_snapshot)

            st.session_state.cart           = []
            st.session_state.bill_cust_name = ""

            st.success(f"✅  Invoice {inv_no} saved!  Total ₹{grand_total:.2f}" + (f"  (Discount ₹{discount_amt:.2f})" if discount_amt > 0 else ""))
            st.download_button(label="⬇️   DOWNLOAD PDF BILL", data=pdf_bytes, file_name=f"Bill_{inv_no}.pdf", mime="application/pdf", use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️  Clear cart and start over", use_container_width=False):
            st.session_state.cart           = []
            st.session_state.bill_cust_name = ""
            st.rerun()

    else:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;background:#f9f9f9;
                    border-radius:12px;border:2px dashed #ccc;margin-top:10px;">
            <div style="font-size:3rem;">📱</div>
            <h3 style="color:#1a3c5e;">No items yet</h3>
            <p style="color:#777;font-size:1rem;">
                Click the scan box at the top<br>
                and scan a product QR code to begin.
            </p>
        </div>
        """, unsafe_allow_html=True)
