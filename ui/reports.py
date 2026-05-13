import streamlit as st
import datetime
import pandas as pd
import json
from database.db_main import get_conn
from services.excel_generator import generate_excel_report, make_sales_xlsx, make_purchase_xlsx
from config.settings import MONTHS, MON_ABBR, GSTIN
from utils.helpers import fmtc, parse_mk
from services.gst_calculator import get_voucher_start, build_daily_sales
from services.billing_service import bills_summary, derive_sales_totals, ok_bills, make_gstr1_json

def page_reports():
    st.markdown("## 📊 Reports & Documents")
    st.caption("Download GST documents and view invoice history.")
    
    st.markdown("---")
    st.markdown("### 📥 Download GST Documents")
    st.caption("Once purchase bills are entered for a month, download buttons appear below.")

    any_ready=False
    for mk,lbl in MONTHS:
        bs=bills_summary(mk)
        if bs["count"]==0: continue
        any_ready=True
        st.markdown(f"**{lbl}** — {bs['count']} purchase bills · Est. sales {fmtc(sum(derive_sales_totals(mk).values()))}")
        c1,c2,c3=st.columns(3)
        start_vno=get_voucher_start(mk)
        overrides = st.session_state.sales_override.get(mk, {})
        totals = derive_sales_totals(mk)
        entries = build_daily_sales(mk, totals, overrides)
        purchases=ok_bills(mk)
        sales_xls,sales_g,last_vno=make_sales_xlsx(mk,entries,start_vno)
        pur_xls,_=make_purchase_xlsx(mk,purchases)
        gstr1=make_gstr1_json(mk,sales_g,start_vno,last_vno,last_vno-start_vno+1)
        m2,y2=parse_mk(mk); mname=lbl.replace(" ","_")
        c1.download_button("⬇ Sales Register .xlsx",data=sales_xls,
            file_name=f"Sales_Register_{mname}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dd_s_{mk}")
        c2.download_button("⬇ Purchase Register .xlsx",data=pur_xls,
            file_name=f"Purchase_Register_{mname}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dd_p_{mk}")
        c3.download_button(f"⬇ GSTR-1 JSON",data=json.dumps(gstr1,indent=2).encode(),
            file_name=f"{GSTIN}_GSTR1_{MON_ABBR[m2]}{y2}.json",
            mime="application/json",key=f"dd_g_{mk}")
        st.markdown("")

    if not any_ready:
        st.info("No months have purchase bills yet. Go to GST Registers to enter data.")

    st.markdown("---")
    st.markdown("### 📥 Generic Sales Excel")
    if st.button("Generate Generic GSTR-1 Excel Report", type="secondary"):
        with st.spinner("Generating..."):
            excel_bytes = generate_excel_report()
        today = datetime.date.today()
        shop_prefix = st.session_state.get("invoice_prefix", "RS")
        st.download_button(
            "⬇️ Download Excel (Daily | Weekly | Monthly)",
            data=excel_bytes,
            file_name=f"{shop_prefix}_Sales_{today.strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("✅ Share this with your CA for GSTR-1 filing.")

    st.markdown("---")
    st.markdown("#### 🗂️ Invoice History")
    conn = get_conn()
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
