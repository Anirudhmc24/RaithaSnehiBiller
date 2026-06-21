import streamlit as st
import pandas as pd
from database.db_main import get_conn
from config.settings import LOW_STOCK_ALERT

def page_search():
    st.subheader("🔍 Product Location Search")
    search_query = st.text_input(
        "Search by product name or QR code...",
        placeholder="e.g. Urea, DAP, Zinc, or type/scan a barcode"
    )
    conn = get_conn()
    if search_query.strip():
        results = conn.execute("""
            SELECT name,qr_code,hsn_code,section,row_no,slot,quantity,unit,mrp,gst_rate
            FROM inventory
            WHERE name LIKE ? OR qr_code LIKE ?
            ORDER BY section,row_no,slot
        """, (f"%{search_query}%", f"%{search_query}%")).fetchall()

        if results:
            st.markdown(f"**{len(results)} result(s) found:**")
            for prod in results:
                sc      = "🔴" if prod["quantity"] < LOW_STOCK_ALERT else "🟢"
                gst_pct = (prod["gst_rate"] or 0) * 100
                st.markdown(f"""
                <div class="scan-found" style="background:#ffffff;border:1px solid rgba(226,232,240,0.8);border-left:6px solid #2e7d32;padding:20px;border-radius:12px;margin-bottom:12px;box-shadow:0 4px 12px rgba(15,23,42,0.03);">
                    <h4 style="margin:0 0 8px 0;color:#0f172a;font-size:1.15rem;font-weight:700;">🌱 {prod['name']}</h4>
                    <div class="detail-row">
                        <span class="detail-pill">HSN: <b>{prod['hsn_code']}</b></span>
                        <span class="detail-pill">QR: <b>{prod['qr_code'] or '—'}</b></span>
                        <span class="detail-pill">GST Rate: <b>{gst_pct:.0f}%</b></span>
                    </div>
                    <div class="detail-row" style="margin-top: 6px;">
                        <span class="detail-pill">📍 Location: <b>{prod['section']} &nbsp;›&nbsp; {prod['row_no']} &nbsp;›&nbsp; Slot {prod['slot']}</b></span>
                        <span class="detail-pill">{sc} Stock: <b>{prod['quantity']} {prod['unit']}</b></span>
                        <span class="detail-pill">💰 MRP: <b>₹ {prod['mrp']:.2f} / {prod['unit']}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"No products found for **'{search_query}'**.")
    else:
        st.info("Start typing a product name or QR code to search.")
        st.markdown("---")
        st.markdown("#### 🗺️ Shop Layout Overview")
        sections = conn.execute(
            "SELECT section,COUNT(*) as cnt FROM inventory GROUP BY section ORDER BY section"
        ).fetchall()
        for sec in sections:
            prods = conn.execute(
                """SELECT name,qr_code,row_no,slot,quantity,unit
                   FROM inventory WHERE section=? ORDER BY row_no,slot""",
                (sec["section"],)
            ).fetchall()
            with st.expander(f"📦 {sec['section']} ({sec['cnt']} products)"):
                for p in prods:
                    badge   = "🔴 LOW" if p["quantity"] < LOW_STOCK_ALERT else "🟢"
                    barcode = f"| 📱 QR: `{p['qr_code']}`" if p["qr_code"] else ""
                    st.markdown(
                        f"• **{p['name']}** — {p['row_no']}, Slot {p['slot']} "
                        f"| Stock: {p['quantity']} {p['unit']} {badge} {barcode}"
                    )
