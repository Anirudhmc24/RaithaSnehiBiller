import streamlit as st
import datetime
import pandas as pd
from database.db_main import get_conn
from services.excel_generator import generate_excel_report

def page_reports():
    st.subheader("📊 CA-Ready Sales Reports — GSTR-1")
    conn = get_conn()
    today      = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())

    daily_total   = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM invoices WHERE DATE(invoice_date)=?",
        (today.isoformat(),)).fetchone()[0]
    weekly_total  = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM invoices WHERE DATE(invoice_date) BETWEEN ? AND ?",
        (week_start.isoformat(), (week_start + datetime.timedelta(days=6)).isoformat())).fetchone()[0]
    monthly_total = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM invoices WHERE strftime('%Y-%m',invoice_date)=?",
        (today.strftime("%Y-%m"),)).fetchone()[0]
    inv_count     = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]

    mc1,mc2,mc3,mc4 = st.columns(4)
    mc1.metric("Today",          f"₹ {daily_total:,.2f}")
    mc2.metric("This Week",      f"₹ {weekly_total:,.2f}")
    mc3.metric("This Month",     f"₹ {monthly_total:,.2f}")
    mc4.metric("Total Invoices", inv_count)

    st.markdown("---")
    if st.button("📥 Generate GSTR-1 Excel Report", type="primary"):
        with st.spinner("Generating..."):
            excel_bytes = generate_excel_report()
        st.download_button(
            "⬇️ Download Excel (Daily | Weekly | Monthly)",
            data=excel_bytes,
            file_name=f"SLV_Sales_{today.strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("✅ Share this with your CA for GSTR-1 filing.")

    st.markdown("---")
    st.markdown("#### 🗂️ Invoice History")
    search_inv = st.text_input("🔍 Search by Invoice No or Customer")
    q  = """SELECT invoice_no,invoice_date,customer_name,
                   taxable_value,cgst_amount,sgst_amount,total_amount
            FROM invoices"""
    p  = ()
    if search_inv:
        q += " WHERE invoice_no LIKE ? OR customer_name LIKE ?"
        p  = (f"%{search_inv}%", f"%{search_inv}%")
    q += " ORDER BY id DESC LIMIT 50"
    rows = conn.execute(q, p).fetchall()
    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        df.columns = ["Invoice No","Date","Customer","Taxable(₹)","CGST(₹)","SGST(₹)","Total(₹)"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No invoices found.")
