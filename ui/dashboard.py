import streamlit as st
import json
from config.settings import MONTHS, MON_ABBR, GSTIN
from utils.helpers import fmtc, parse_mk
from services.gst_calculator import get_voucher_start, build_daily_sales
from services.billing_service import bills_summary, derive_sales_totals, ok_bills, make_gstr1_json
from services.excel_generator import make_sales_xlsx, make_purchase_xlsx

def page_dashboard():
    st.markdown("## 🏠 Dashboard")
    st.caption("Enter purchase bills for each month → sales auto-derive → download all 3 documents per month")
    st.markdown("---")

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
    st.markdown("### Download all documents")
    st.caption("Click a month tab at the top to enter purchase bills. Once bills are entered, download buttons appear below.")

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
        st.info("No months have purchase bills yet. Click a month tab at the top to get started.")
