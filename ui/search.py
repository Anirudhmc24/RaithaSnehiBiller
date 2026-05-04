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
                <div style="background:#f8fffe;border:1px solid #a5d6a7;
                            border-left:5px solid #2e7d32;padding:12px 16px;
                            border-radius:8px;margin-bottom:10px;">
                    <h4 style="margin:0;color:#1a3c5e;">🌱 {prod['name']}</h4>
                    <p style="margin:4px 0;color:#555;">
                        HSN: <b>{prod['hsn_code']}</b> &nbsp;|&nbsp;
                        QR Code: <b>{prod['qr_code'] or '—'}</b> &nbsp;|&nbsp;
                        GST: <b>{gst_pct:.0f}%</b>
                    </p>
                    <p style="margin:4px 0;">
                        📍 <b>Location:</b>
                        {prod['section']} &nbsp;›&nbsp; {prod['row_no']} &nbsp;›&nbsp;
                        <b>Slot {prod['slot']}</b>
                    </p>
                    <p style="margin:4px 0;">
                        {sc} <b>Stock:</b> {prod['quantity']} {prod['unit']}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        💰 <b>MRP:</b> ₹ {prod['mrp']:.2f} / {prod['unit']}
                    </p>
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
