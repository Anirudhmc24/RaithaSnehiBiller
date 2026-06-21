import streamlit as st
import datetime
from database.db_main import get_conn
from config.settings import MONTHS
from utils.helpers import fmtc
from services.billing_service import bills_summary, derive_sales_totals

def page_dashboard():
    st.markdown("## 🏠 Dashboard")
    st.caption("Overview of your shop's performance.")
    
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

    from ui.components import render_metric_card
    
    mc1,mc2,mc3,mc4 = st.columns(4)
    with mc1:
        render_metric_card("Today's Sales", f"₹ {daily_total:,.2f}", "📅")
    with mc2:
        render_metric_card("Weekly Sales", f"₹ {weekly_total:,.2f}", "📊")
    with mc3:
        render_metric_card("Monthly Sales", f"₹ {monthly_total:,.2f}", "🌱")
    with mc4:
        render_metric_card("Total Invoices", f"{inv_count}", "🧾")
    
    # Dashboard Hero Quick Action Card
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    hc1, hc2 = st.columns([3.2, 1])
    with hc1:
        st.markdown("""
        <h3 style="margin: 0 0 6px 0; color: #1b5e20; font-size: 1.35rem; font-weight: 700;">🌱 Create New GST Invoice</h3>
        <p style="margin: 0; color: #334155; font-size: 0.95rem; line-height: 1.5; font-weight: 500;">
            Issue professional bills with automated tax calculations for fertilizers, pesticides, and seeds. Full barcode/QR scanner support included.
        </p>
        """, unsafe_allow_html=True)
    with hc2:
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
        if st.button("🧾 Start Billing", key="dash_new_bill_btn", type="primary", use_container_width=True):
            st.session_state.active_page = "🧾 New Bill"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    
    st.markdown("---")
    st.markdown("### Month-by-Month GST Summary")
    rows=[]
    for mk,lbl in MONTHS:
        bs=bills_summary(mk)
        st_txt="✅ Ready" if bs["count"]>0 else "⏳ Awaiting bills"
        rows.append({"Month":lbl,"Bills entered":bs["count"],
            "Purchase value":fmtc(bs["p18"]+bs["p5"]+bs["pex"]),
            "ITC available":fmtc(bs["itc"]),
            "Estimated sales":fmtc(sum(derive_sales_totals(mk).values())),
            "Status":st_txt})
    st.dataframe(rows,use_container_width=True,hide_index=True)
    
    st.markdown("---")
    st.markdown("### Advanced Options")
    if st.button("➕ Create Next Month", help="Generate the tab and configuration for the next sequential month."):
        from utils.helpers import add_next_month
        add_next_month()
        st.success("Next month created successfully! Streamlit will reload automatically.")
        st.rerun()
