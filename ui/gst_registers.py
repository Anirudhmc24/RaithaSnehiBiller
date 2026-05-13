import streamlit as st
import json
import datetime
from config.settings import MONTHS, MON_ABBR, GSTIN, LOW_STOCK_ALERT
from utils.helpers import fmtc, parse_mk, r2, ld
from services.gst_calculator import get_voucher_start, get_purchase_voucher_start, build_daily_sales, distribute_target_sales, calculate_gst
from services.billing_service import bills_summary, derive_sales_totals, ok_bills, make_gstr1_json, FILED_HSN, aggregate_hsn_from_bills
from services.excel_generator import make_sales_xlsx, make_purchase_xlsx
from services.ai_extractor import extract_bill_ai
from database.db_gst import db_save_bills, db_save_override, db_delete_overrides, db_load_target, db_save_hsn, db_load_bills, db_load_overrides, db_load_suppliers, db_save_supplier, db_load_hsn
from database.db_main import get_conn

def gst_ss_init():
    # 1. Initialize core dicts if missing
    for k in ["gst_bills", "gst_overrides", "hsn_entries"]:
        if k not in st.session_state:
            st.session_state[k] = {}
        
        # 2. Ensure ALL months in MONTHS are present (fixes KeyError after adding next month)
        for m, _ in MONTHS:
            if m not in st.session_state[k]:
                if k == "gst_bills":
                    st.session_state[k][m] = db_load_bills(m)
                elif k == "gst_overrides":
                    st.session_state[k][m] = db_load_overrides(m)
                elif k == "hsn_entries":
                    from_db = db_load_hsn(m)
                    if from_db:
                        st.session_state[k][m] = from_db
                    elif m in FILED_HSN:
                        # Seed pre-filed months from the hardcoded table
                        st.session_state[k][m] = list(FILED_HSN[m])
                    else:
                        st.session_state[k][m] = []

    # 3. Suppliers (Flat Dictionary, not month-keyed)
    if "gst_suppliers" not in st.session_state:
        st.session_state["gst_suppliers"] = db_load_suppliers()

    # 4. Miscellaneous keys
    if "gst_sub_page" not in st.session_state:
        st.session_state.gst_sub_page = "dashboard"
    if "gemini_key" not in st.session_state:
        st.session_state.gemini_key = ""

def supplier_selectbox(key_prefix, current_name="", current_gstin=""):
    """Plain text inputs — type supplier name and GSTIN freely."""
    nn_key = f"{key_prefix}_ntxt"
    ng_key = f"{key_prefix}_gtxt"
    if nn_key not in st.session_state:
        st.session_state[nn_key] = current_name
    if ng_key not in st.session_state:
        st.session_state[ng_key] = current_gstin
    ca, cb = st.columns(2)
    ca.text_input("Supplier name",  key=nn_key, placeholder="e.g. Rallis India Ltd")
    cb.text_input("Supplier GSTIN", key=ng_key, placeholder="e.g. 29AABCR2657NIZU")
    return st.session_state[nn_key].strip(), st.session_state[ng_key].strip()

def bill_fields(bill, kp):
    """Render editable fields for a bill. Returns updated dict."""
    updated = dict(bill)

    c_sup, c_inv, c_dt = st.columns([2,1,1])
    with c_sup:
        updated["supplier"], updated["gstin"] = supplier_selectbox(
            f"{kp}s", current_name=bill.get("supplier",""), current_gstin=bill.get("gstin",""))
    updated["invno"]   = c_inv.text_input("Supplier Invoice no.", value=bill.get("invno",""),    key=f"{kp}inv")
    updated["inv_date"]= c_dt.text_input( "Date DD-MM-YYYY",      value=bill.get("inv_date",""), key=f"{kp}dt")
    updated["pur_vno"] = st.number_input("Voucher No. (Tally)",
                             min_value=1, value=int(bill.get("pur_vno") or 1),
                             step=1, key=f"{kp}pvno")

    _def = bill

    st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>18% slab</div>", unsafe_allow_html=True)
    ea1,ea2,ea3 = st.columns(3)
    updated["val18"] = ea1.number_input("Taxable value", value=float(_def.get("val18") or 0), min_value=0.0, step=1.0, format="%.2f", key=f"{kp}v18")
    updated["cgst9"] = ea2.number_input("CGST 9%",       value=float(_def.get("cgst9") or r2(updated["val18"]*0.09)), min_value=0.0, step=0.01, format="%.2f", key=f"{kp}c9")
    updated["sgst9"] = ea3.number_input("SGST 9%",       value=float(_def.get("sgst9") or r2(updated["val18"]*0.09)), min_value=0.0, step=0.01, format="%.2f", key=f"{kp}s9")

    st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>5% slab</div>", unsafe_allow_html=True)
    eb1,eb2,eb3 = st.columns(3)
    updated["val5"]   = eb1.number_input("Taxable value", value=float(_def.get("val5")   or 0), min_value=0.0, step=1.0,  format="%.2f", key=f"{kp}v5")
    updated["cgst25"] = eb2.number_input("CGST 2.5%",     value=float(_def.get("cgst25") or r2(updated["val5"]*0.025)), min_value=0.0, step=0.01, format="%.2f", key=f"{kp}c25")
    updated["sgst25"] = eb3.number_input("SGST 2.5%",     value=float(_def.get("sgst25") or r2(updated["val5"]*0.025)), min_value=0.0, step=0.01, format="%.2f", key=f"{kp}s25")

    st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>12% slab</div>", unsafe_allow_html=True)
    ec1,ec2,ec3 = st.columns(3)
    updated["val12"] = ec1.number_input("Taxable value", value=float(_def.get("val12") or 0), min_value=0.0, step=1.0,  format="%.2f", key=f"{kp}v12")
    updated["cgst6"] = ec2.number_input("CGST 6%",       value=float(_def.get("cgst6") or r2(updated["val12"]*0.06)), min_value=0.0, step=0.01, format="%.2f", key=f"{kp}c6")
    updated["sgst6"] = ec3.number_input("SGST 6%",       value=float(_def.get("sgst6") or r2(updated["val12"]*0.06)), min_value=0.0, step=0.01, format="%.2f", key=f"{kp}s6")

    st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>Other</div>", unsafe_allow_html=True)
    ed1,ed2,ed3,ed4 = st.columns(4)
    updated["exempt"]    = ed1.number_input("Exempt/Nil",    value=float(_def.get("exempt")    or 0), min_value=0.0, step=1.0,  format="%.2f", key=f"{kp}ex")
    updated["round_off"] = ed2.number_input("Round off",     value=float(_def.get("round_off") or 0), step=0.01,               format="%.2f", key=f"{kp}ro")
    updated["discount"]  = ed3.number_input("Cash discount", value=float(_def.get("discount")  or 0), min_value=0.0, step=1.0,  format="%.2f", key=f"{kp}dc")

    total_gst = r2(updated["cgst9"]+updated["sgst9"]+updated["cgst25"]+updated["sgst25"]+updated["cgst6"]+updated["sgst6"])
    auto_gross = r2(updated["val18"]+updated["val5"]+updated["val12"]+updated["exempt"]+total_gst+updated["round_off"]-updated["discount"])
    updated["gross"] = ed4.number_input("Gross total", value=float(_def.get("gross") or auto_gross), min_value=0.0, step=1.0, format="%.2f", key=f"{kp}gr")

    itc = r2(updated["cgst9"]+updated["sgst9"]+updated["cgst25"]+updated["sgst25"])
    st.markdown(
        f"<div style='background:#eaf2e8;border-radius:5px;padding:7px 12px;font-size:12px;color:#1a3c1a;margin-top:6px'>"
        f"Total GST: <strong>{fmtc(total_gst)}</strong> &nbsp;|&nbsp; ITC: <strong>{fmtc(itc)}</strong> &nbsp;|&nbsp; Gross: <strong>{fmtc(updated['gross'])}</strong>"
        f"</div>", unsafe_allow_html=True)
    
    try:
        pts = updated["inv_date"].split("-")
        updated["inv_date_obj"] = datetime.date(int(pts[2]),int(pts[1]),int(pts[0]))
    except: updated["inv_date_obj"] = None

    return updated

def page_month(mk):
    lbl=dict(MONTHS).get(mk,mk); m,y=parse_mk(mk)
    st.markdown(f"## 📅 {lbl}")
    tab_pur,tab_sales,tab_hsn,tab_docs=st.tabs(
        ["📥 Purchase Bills","📊 Sales (derived)","🔢 HSN Summary","📤 Download Documents"])

    # ── TAB 1: PURCHASE BILLS ─────────────────────────────────────────────────
    with tab_pur:
        st.caption("Enter all purchase bills for this month. Sales registers are auto-generated from these.")

        st.markdown("### ✏️ Add bill manually")

        with st.form(f"addbill_{mk}", clear_on_submit=False):
            nb = {}
            st.markdown("**Supplier**")
            nb["supplier"], nb["gstin"] = supplier_selectbox(f"add{mk}")
            c3f, c4f, c5f = st.columns(3)
            nb["invno"]   = c3f.text_input("Supplier Invoice no. *", placeholder="INV-001",                    key=f"ninv{mk}")
            nb["inv_date"]= c4f.text_input("Date DD-MM-YYYY *",      placeholder=f"10-{str(m).zfill(2)}-{y}", key=f"ndt{mk}")
            _next_pur_vno = get_purchase_voucher_start(mk, ok_bills) + len(ok_bills(mk))
            nb["pur_vno"] = c5f.number_input("Voucher No. (Tally)", min_value=1,
                                              value=_next_pur_vno, step=1, key=f"npvno{mk}")

            st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>18% slab</div>", unsafe_allow_html=True)
            fa1,fa2,fa3 = st.columns(3)
            nb["val18"] = fa1.number_input("Taxable value", min_value=0.0,value=0.0,step=1.0,format="%.2f",key=f"nv18{mk}")
            nb["cgst9"] = fa2.number_input("CGST 9%  (auto-fills)",  min_value=0.0,value=r2(nb["val18"]*0.09), step=0.01,format="%.2f",key=f"nc9{mk}")
            nb["sgst9"] = fa3.number_input("SGST 9%  (auto-fills)",  min_value=0.0,value=r2(nb["val18"]*0.09), step=0.01,format="%.2f",key=f"ns9{mk}")

            st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>5% slab</div>", unsafe_allow_html=True)
            fb1,fb2,fb3 = st.columns(3)
            nb["val5"]   = fb1.number_input("Taxable value", min_value=0.0,value=0.0,step=1.0,format="%.2f",key=f"nv5{mk}")
            nb["cgst25"] = fb2.number_input("CGST 2.5% (auto-fills)",min_value=0.0,value=r2(nb["val5"]*0.025),step=0.01,format="%.2f",key=f"nc25{mk}")
            nb["sgst25"] = fb3.number_input("SGST 2.5% (auto-fills)",min_value=0.0,value=r2(nb["val5"]*0.025),step=0.01,format="%.2f",key=f"ns25{mk}")

            st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>12% slab</div>", unsafe_allow_html=True)
            fc1,fc2,fc3 = st.columns(3)
            nb["val12"] = fc1.number_input("Taxable value", min_value=0.0,value=0.0,step=1.0,format="%.2f",key=f"nv12{mk}")
            nb["cgst6"] = fc2.number_input("CGST 6%  (auto-fills)",  min_value=0.0,value=r2(nb["val12"]*0.06),step=0.01,format="%.2f",key=f"nc6{mk}")
            nb["sgst6"] = fc3.number_input("SGST 6%  (auto-fills)",  min_value=0.0,value=r2(nb["val12"]*0.06),step=0.01,format="%.2f",key=f"ns6{mk}")

            st.markdown("<div style='font-size:11px;font-weight:600;color:#4a7a47;text-transform:uppercase;letter-spacing:.4px;margin:8px 0 3px'>Other</div>", unsafe_allow_html=True)
            fd1,fd2,fd3,fd4 = st.columns(4)
            nb["exempt"]    = fd1.number_input("Exempt/Nil",   min_value=0.0,value=0.0,step=1.0,format="%.2f",key=f"nex{mk}")
            nb["round_off"] = fd2.number_input("Round off",    value=0.0,step=0.01,format="%.2f",key=f"nro{mk}")
            nb["discount"]  = fd3.number_input("Cash discount",min_value=0.0,value=0.0,step=1.0,format="%.2f",key=f"ndc{mk}")
            _auto_gross = r2(nb["val18"]+nb["val5"]+nb["val12"]+nb["exempt"]+nb["cgst9"]+nb["sgst9"]+nb["cgst25"]+nb["sgst25"]+nb["cgst6"]+nb["sgst6"]+nb["round_off"]-nb["discount"])
            nb["gross"]     = fd4.number_input("Gross total",  min_value=0.0,value=_auto_gross,step=1.0,format="%.2f",key=f"ngr{mk}")
            photo = st.file_uploader("Photo (optional)", type=["jpg","jpeg","png","webp"], key=f"nph{mk}")

            calc_clicked = st.form_submit_button("🧮  Calculate — preview before adding", use_container_width=True)
            if calc_clicked:
                st.session_state[f"calc_{mk}"] = dict(nb)
                st.session_state[f"calc_photo_{mk}"] = photo.name if photo else None

        prev = st.session_state.get(f"calc_{mk}")
        if prev:
            p = dict(prev)
            _tgst = r2((p.get("cgst9") or 0)+(p.get("sgst9") or 0)+
                       (p.get("cgst25") or 0)+(p.get("sgst25") or 0)+
                       (p.get("cgst6") or 0)+(p.get("sgst6") or 0))
            if not p.get("gross"):
                p["gross"] = r2((p.get("val18") or 0)+(p.get("val5") or 0)+
                                (p.get("val12") or 0)+(p.get("exempt") or 0)+
                                _tgst+(p.get("round_off") or 0)-(p.get("discount") or 0))
            _itc = r2((p.get("cgst9") or 0)+(p.get("sgst9") or 0)+
                      (p.get("cgst25") or 0)+(p.get("sgst25") or 0))

            st.markdown("---")
            st.markdown("#### 🧾 Bill preview — verify before adding")

            hc1,hc2,hc3,hc4,hc5 = st.columns(5)
            hc1.markdown(f"**Supplier**<br>{p.get('supplier','—')}", unsafe_allow_html=True)
            hc2.markdown(f"**GSTIN**<br>{p.get('gstin','—')}", unsafe_allow_html=True)
            hc3.markdown(f"**Supplier Invoice no.**<br>{p.get('invno','—')}", unsafe_allow_html=True)
            hc4.markdown(f"**Date**<br>{p.get('inv_date','—')}", unsafe_allow_html=True)
            hc5.markdown(f"**Voucher No.**<br>{p.get('pur_vno','—')}", unsafe_allow_html=True)

            st.markdown("")
            rows = []
            if p["val18"]: rows.append({"Slab":"18%","Taxable":fmtc(p["val18"]),"CGST":fmtc(p["cgst9"]), "SGST":fmtc(p["sgst9"]), "Total GST":fmtc(p["cgst9"]+p["sgst9"])})
            if p["val5"]:  rows.append({"Slab":"5%", "Taxable":fmtc(p["val5"]), "CGST":fmtc(p["cgst25"]),"SGST":fmtc(p["sgst25"]),"Total GST":fmtc(p["cgst25"]+p["sgst25"])})
            if p["val12"]: rows.append({"Slab":"12%","Taxable":fmtc(p["val12"]),"CGST":fmtc(p["cgst6"]), "SGST":fmtc(p["sgst6"]), "Total GST":fmtc(p["cgst6"]+p["sgst6"])})
            if p["exempt"]:rows.append({"Slab":"Exempt","Taxable":fmtc(p["exempt"]),"CGST":"—","SGST":"—","Total GST":"—"})
            if rows:
                st.dataframe(rows, use_container_width=True, hide_index=True)

            sc1,sc2,sc3,sc4,sc5 = st.columns(5)
            sc1.metric("Total taxable", fmtc(p["val18"]+p["val5"]+p["val12"]+p["exempt"]))
            sc2.metric("Total GST",     fmtc(_tgst))
            sc3.metric("ITC",           fmtc(_itc))
            sc4.metric("Round off",     fmtc(p.get("round_off") or 0))
            sc5.metric("Gross total",   fmtc(p["gross"]))

            ac1, ac2 = st.columns(2)
            if ac1.button("✅  Add bill to register", type="primary", use_container_width=True, key=f"confirm_{mk}"):
                if not p.get("supplier") or not p.get("invno") or not p.get("inv_date"):
                    st.error("Supplier, Invoice no., and Date are required.")
                elif (p["val18"]+p["val5"]+p["val12"]+p["exempt"])==0:
                    st.error("Enter at least one taxable/exempt amount.")
                else:
                    try:
                        pts = p["inv_date"].split("-")
                        p["inv_date_obj"] = datetime.date(int(pts[2]),int(pts[1]),int(pts[0]))
                    except: p["inv_date_obj"] = None
                    p["filename"] = st.session_state.get(f"calc_photo_{mk}") or f"manual_{p['invno']}"
                    p["status"] = "ok"; p["source"] = "manual"
                    if p.get("supplier") and p.get("gstin"):
                        if p["supplier"] not in st.session_state.suppliers:
                            st.session_state.suppliers[p["supplier"]] = p["gstin"]
                            db_save_supplier(p["supplier"], p["gstin"])
                    for _k in [k for k in st.session_state if k.endswith("_nn_val") or k.endswith("_ng_val")]:
                        del st.session_state[_k]
                    st.session_state.bills[mk].append(p)
                    db_save_bills(mk, st.session_state.bills[mk])
                    del st.session_state[f"calc_{mk}"]
                    st.success(f"✓ Added: {p['supplier']} — {p['invno']}"); st.rerun()
            if ac2.button("✏️  Edit — go back", use_container_width=True, key=f"discard_{mk}"):
                del st.session_state[f"calc_{mk}"]; st.rerun()

        st.markdown("---")
        st.markdown("### 📷 Scan from photos (Gemini AI)")
        if not st.session_state.get("gemini_key"):
            st.warning("Enter Gemini API key in sidebar to use AI scanning.")
        else:
            uploaded=st.file_uploader("Upload bill photos — multiple OK",
                type=["jpg","jpeg","png","webp"],accept_multiple_files=True,key=f"scan{mk}")
            if uploaded:
                existing={b.get("filename") for b in st.session_state.bills[mk]}
                new_files=[f for f in uploaded if f.name not in existing]
                if new_files:
                    prog=st.progress(0,text="Reading bills…")
                    for i,f in enumerate(new_files):
                        prog.progress(i/len(new_files),text=f"Reading {f.name} ({i+1}/{len(new_files)})")
                        try:
                            data=extract_bill_ai(f.read(),f.type,st.session_state.gemini_key)
                            data["filename"]=f.name; data["status"]="ok"; data["source"]="ai"
                        except Exception as e:
                            data={"filename":f.name,"status":"error","error":str(e),"source":"ai"}
                        st.session_state.bills[mk].append(data)
                    db_save_bills(mk, st.session_state.bills[mk])
                    prog.progress(1.0,text=f"✓ Done — {len(new_files)} bill(s). Review below.")
                    st.rerun()

        bills_list=st.session_state.bills.get(mk,[])
        ok_list =[b for b in bills_list if b.get("status")=="ok"]
        err_list=[b for b in bills_list if b.get("status")=="error"]
        for b in err_list:
            st.error(f"❌ {b['filename']}: {b.get('error','unknown')}")

        if ok_list:
            st.markdown("---")
            bs=bills_summary(mk)

            c1,c2,c3,c4=st.columns(4)
            c1.metric("Bills entered",    bs["count"])
            c2.metric("Total taxable",    fmtc(bs["p18"]+bs["p5"]+bs["p12"]))
            c3.metric("ITC available",    fmtc(bs["itc"]))
            c4.metric("Gross total",      fmtc(bs["gross"]))

            st.markdown(f"### 📋 Bills added — {len(ok_list)} total")
            tbl_rows = []
            for i, bill in enumerate([b for b in bills_list if b.get("status")=="ok"]):
                itc_b = r2((bill.get("cgst9") or 0)+(bill.get("sgst9") or 0)+
                           (bill.get("cgst25") or 0)+(bill.get("sgst25") or 0))
                tbl_rows.append({
                    "#":            i+1,
                    "Voucher No.":  bill.get("pur_vno","—"),
                    "Supplier":     bill.get("supplier","?"),
                    "GSTIN":        bill.get("gstin","—"),
                    "Supplier Inv.":bill.get("invno","—"),
                    "Date":         bill.get("inv_date","—"),
                    "@18%":         fmtc(bill.get("val18") or 0) if (bill.get("val18") or 0)>0 else "—",
                    "@5%":          fmtc(bill.get("val5")  or 0) if (bill.get("val5")  or 0)>0 else "—",
                    "@12%":         fmtc(bill.get("val12") or 0) if (bill.get("val12") or 0)>0 else "—",
                    "Exempt":       fmtc(bill.get("exempt")or 0) if (bill.get("exempt")or 0)>0 else "—",
                    "Gross":        fmtc(bill.get("gross") or 0),
                    "ITC":          fmtc(itc_b),
                    "Source":       "✏️ Manual" if bill.get("source")=="manual" else "🤖 AI",
                })
            st.dataframe(tbl_rows, use_container_width=True, hide_index=True)

            st.markdown("**Edit or remove a bill:**")
            to_del   = None
            to_save  = None
            to_hsn_add = None   # (bill_idx, item_dict)
            to_hsn_del = None   # (bill_idx, item_idx)
            for idx, bill in enumerate(st.session_state.bills[mk]):
                if bill.get("status") != "ok": continue
                src_icon = "✏️" if bill.get("source") == "manual" else "🤖"
                hsn_count = len(bill.get("hsn_items") or [])
                hsn_badge = f" · 📦 {hsn_count} HSN item{'s' if hsn_count!=1 else ''}" if hsn_count else ""
                lbl2 = (f"{src_icon} #{idx+1} · **{bill.get('supplier','?')}** "
                    f"· {bill.get('invno','?')} · {bill.get('inv_date','?')} "
                    f"· {fmtc(bill.get('gross',0))}{hsn_badge}")
                with st.expander(lbl2, expanded=False):
                    updated = bill_fields(bill, f"ef{mk}{idx}")
                    bc1, bc2 = st.columns(2)
                    if bc1.button("💾  Save changes", key=f"sav{mk}{idx}", type="primary", use_container_width=True):
                        to_save = (idx, updated)
                    if bc2.button("🗑  Remove this bill", key=f"del{mk}{idx}", use_container_width=True):
                        to_del = idx

                    # ── HSN LINE ITEMS ──────────────────────────────────
                    st.markdown("---")
                    st.markdown("📦 **HSN Line Items** — enter product-wise HSN details from this invoice")
                    cur_items = list(bill.get("hsn_items") or [])

                    if cur_items:
                        item_tbl = [{
                            "#":        i+1,
                            "HSN Code": it.get("hsn_sc",""),
                            "UQC":      it.get("uqc",""),
                            "Qty":      it.get("qty",0),
                            "Rate %":   it.get("rt",0),
                            "Taxable":  fmtc(it.get("txval",0)),
                            "CGST":     fmtc(it.get("camt",0)),
                            "SGST":     fmtc(it.get("samt",0)),
                        } for i, it in enumerate(cur_items)]
                        st.dataframe(item_tbl, use_container_width=True, hide_index=True)
                        for ii, it in enumerate(cur_items):
                            if st.button(
                                f"🗑 Remove #{ii+1} · {it.get('hsn_sc','')} · {it.get('uqc','')} · @{it.get('rt',0)}%",
                                key=f"hsnidel_{mk}{idx}{ii}", use_container_width=True):
                                to_hsn_del = (idx, ii)

                    _UQC = ["PCS","PAC","KGS","LTR","NOS","BAG","BOX","MTR","OTH"]
                    _RT  = [0, 5, 12, 18, 28]
                    with st.form(f"hsniadd_{mk}{idx}", clear_on_submit=True):
                        st.caption("➕ Add a product HSN line from this invoice")
                        hi1,hi2,hi3,hi4 = st.columns([2,1,1,1])
                        nh = hi1.text_input("HSN code", placeholder="e.g. 38089290", key=f"nhc_{mk}{idx}")
                        nu = hi2.selectbox("UQC",        _UQC,                       key=f"nhu_{mk}{idx}")
                        nr = hi3.selectbox("GST %",      _RT,                        key=f"nhr_{mk}{idx}")
                        nq = hi4.number_input("Qty", min_value=0, value=0, step=1,   key=f"nhq_{mk}{idx}")
                        ntv = st.number_input("Taxable value (₹)", min_value=0.0, value=0.0,
                                              step=1.0, format="%.2f",               key=f"nhtv_{mk}{idx}")
                        if st.form_submit_button("➕ Add HSN item", use_container_width=True):
                            if not nh.strip():
                                st.error("HSN code is required.")
                            elif ntv <= 0:
                                st.error("Taxable value must be > 0.")
                            else:
                                _rf = nr / 100 / 2
                                to_hsn_add = (idx, {
                                    "hsn_sc": nh.strip(), "uqc": nu, "rt": nr,
                                    "qty": nq, "txval": ntv,
                                    "camt": r2(ntv * _rf), "samt": r2(ntv * _rf),
                                })

            # ── Deferred mutations (must be outside the expander loop) ────────
            if to_hsn_add is not None:
                bidx, item = to_hsn_add
                _b = st.session_state.bills[mk][bidx]
                _items = list(_b.get("hsn_items") or [])
                _items.append(item)
                _b["hsn_items"] = _items
                db_save_bills(mk, st.session_state.bills[mk])
                st.success(f"✓ HSN item ({item['hsn_sc']}) added to bill #{bidx+1}.")
                st.rerun()
            if to_hsn_del is not None:
                bidx, iidx = to_hsn_del
                _b = st.session_state.bills[mk][bidx]
                _items = list(_b.get("hsn_items") or [])
                _items.pop(iidx)
                _b["hsn_items"] = _items
                db_save_bills(mk, st.session_state.bills[mk])
                st.rerun()

            if to_save is not None:
                sidx, supdated = to_save
                supdated["status"] = "ok"
                st.session_state.bills[mk][sidx] = supdated
                db_save_bills(mk, st.session_state.bills[mk])
                st.success(f"✓ Bill #{sidx+1} updated."); st.rerun()
            if to_del is not None:
                st.session_state.bills[mk].pop(to_del)
                db_save_bills(mk, st.session_state.bills[mk])
                st.rerun()

            st.markdown("")
            if st.button("🗑 Clear ALL bills for this month", key=f"clr{mk}"):
                st.session_state.bills[mk] = []
                db_save_bills(mk, [])
                st.rerun()
        else:
            st.info("No bills yet. Use the form above or upload photos.")

    # ── TAB 2: DERIVED SALES ──────────────────────────────────────────────────
    with tab_sales:
        bs=bills_summary(mk)
        if bs["count"]==0:
            st.info("Enter purchase bills in the Purchase Bills tab first."); return

        totals=derive_sales_totals(mk)
        st.markdown("Sales are auto-derived from your purchase data.")

        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric("Est. total sales",fmtc(sum(totals.values())))
        c2.metric("@18%",fmtc(totals["v18"])); c3.metric("@5%",fmtc(totals["v5"]))
        c4.metric("@12%",fmtc(totals["v12"])); c5.metric("Exempt",fmtc(totals["vex"]))

        st.markdown("---")
        st.markdown("**Daily breakdown**")
        overrides = st.session_state.sales_override.get(mk, {})
        entries=build_daily_sales(mk, totals, overrides)
        rows=[{"Date":e["date"].strftime("%d %b"),"Day":e["date"].strftime("%a"),
            "@18%":fmtc(e["v18"]) if e["v18"] else "—",
            "@5%": fmtc(e["v5"])  if e["v5"]  else "—",
            "@12%":fmtc(e["v12"]) if e["v12"] else "—",
            "Exempt":fmtc(e["vex"]) if e["vex"] else "—",
            "Total":fmtc(e["v18"]+e["v5"]+e["v12"]+e["vex"]),
            "Bills":e["nbills"]} for e in entries]
        st.dataframe(rows,use_container_width=True,hide_index=True,height=400)

        st.markdown("---")
        with st.expander("✏️ Override a specific day"):
            days=ld(m,y)
            ov_d=st.number_input("Day", min_value=1, max_value=days, value=1, step=1, key=f"ovd{mk}")
            oc1,oc2,oc3,oc4,oc5=st.columns(5)
            ov18=oc1.number_input("@18%", 0.0,step=50.0,format="%.2f",key=f"ov18{mk}")
            ov5 =oc2.number_input("@5%",  0.0,step=10.0,format="%.2f",key=f"ov5{mk}")
            ov12=oc3.number_input("@12%", 0.0,step=10.0,format="%.2f",key=f"ov12{mk}")
            ovex=oc4.number_input("Exempt",0.0,step=50.0,format="%.2f",key=f"ovex{mk}")
            ovnb=oc5.number_input("Bills", min_value=1, max_value=30, value=4, step=1, key=f"ovnb{mk}")
            if st.button("Save override",key=f"ovsave{mk}"):
                ov_data = {"v18":ov18,"v5":ov5,"v12":ov12,"vex":ovex,"nbills":int(ovnb)}
                st.session_state.sales_override[mk][int(ov_d)] = ov_data
                db_save_override(mk, int(ov_d), ov_data)
                st.success(f"Saved for day {ov_d}"); st.rerun()
            ovs=st.session_state.sales_override.get(mk,{})
            if ovs:
                st.caption(f"{len(ovs)} day(s) overridden: {sorted(ovs.keys())}")
                if st.button("Clear all overrides",key=f"ovclr{mk}"):
                    st.session_state.sales_override[mk]={}
                    db_delete_overrides(mk)
                    st.rerun()

        st.markdown("---")
        st.markdown("### 🎯 Smart Sales Override")
        
        _saved_target = db_load_target(mk)
        _default_target = float(_saved_target) if _saved_target else 1600000.0

        _target_col, _btn_col = st.columns([3, 1])
        smart_target = _target_col.number_input(
            "Desired Total Sales (₹)", min_value=10000.0, max_value=50000000.0,
            value=_default_target, step=10000.0, format="%.2f", key=f"smart_target_{mk}")

        _rev18 = smart_target * 0.75
        _rev5  = smart_target - _rev18
        _tx18  = _rev18 / 1.18
        _tx5   = _rev5  / 1.05
        st.markdown(f"<div style='background:#eaf7ea;border-radius:6px;padding:8px 14px;font-size:12px;color:#1a3c1a;margin:4px 0 8px 0'>Split preview → <b>18% slab (75%):</b> taxable {fmtc(_tx18)} + GST {fmtc(_tx18*0.18)} = {fmtc(_rev18)} &nbsp;|&nbsp; <b>5% slab (25%):</b> taxable {fmtc(_tx5)} + GST {fmtc(_tx5*0.05)} = {fmtc(_rev5)} &nbsp;|&nbsp; <b>Grand total gross: {fmtc(smart_target)}</b></div>", unsafe_allow_html=True)

        if _btn_col.button("🚀 Generate Smart Override", key=f"smart_gen_{mk}", type="primary", use_container_width=True):
            with st.spinner(f"Distributing ₹{smart_target:,.0f} across {ld(m,y)} days…"):
                distribute_target_sales(mk, smart_target)
            st.success("✅ Smart override applied!"); st.rerun()

        if _saved_target:
            st.caption(f"Last saved target for this month: **{fmtc(_saved_target)}**")

    # ── TAB 3: HSN SUMMARY ────────────────────────────────────────────────────
    with tab_hsn:
        st.caption("HSN-wise summary included in the GSTR-1 JSON. Auto-compute from purchases or add rows manually.")

        cur_hsn = list(st.session_state.hsn_entries.get(mk, []))

        # ── Auto-compute button ────────────────────────────────────────────
        st.markdown("### ⚡ Auto-compute from Purchase Bills")
        st.info("This aggregates HSN + UQC + qty + taxable value from your purchase register "
                "and computes output GST using sales ratios. Use as a starting point then fine-tune manually.")

        if st.button("🔄 Auto-compute HSN rows from bills", key=f"hsnauto_{mk}", type="primary"):
            rows_auto = aggregate_hsn_from_bills(mk)
            if rows_auto:
                st.session_state.hsn_entries[mk] = rows_auto
                db_save_hsn(mk, rows_auto)
                st.success(f"✓ Generated {len(rows_auto)} HSN rows from purchase bill items.")
                st.rerun()
            else:
                st.warning(
                    "⚠️ No HSN item data found in purchase bills. "
                    "Open each bill in the Purchase Bills tab, expand it, and add HSN line items from the invoice.")


        st.markdown("---")
        st.markdown("### ➕ Add / Edit HSN Rows")

        UQC_OPTIONS = ["PCS","PAC","KGS","LTR","NOS","BAG","BOX","MTR","OTH"]
        RT_OPTIONS  = [0, 5, 12, 18, 28]

        # ── Add new row form ───────────────────────────────────────────────
        with st.form(f"hsnadd_{mk}", clear_on_submit=True):
            st.markdown("**New HSN row**")
            ha1,ha2,ha3,ha4 = st.columns([2,1,1,1])
            new_hsn  = ha1.text_input("HSN code",       placeholder="e.g. 38089290", key=f"nhsn_{mk}")
            new_uqc  = ha2.selectbox("UQC",             UQC_OPTIONS,                key=f"nuqc_{mk}")
            new_rt   = ha3.selectbox("GST Rate (%)",    RT_OPTIONS,                 key=f"nrt_{mk}")
            new_qty  = ha4.number_input("Qty",  min_value=0, value=0, step=1,       key=f"nqty_{mk}")
            hb1,hb2,hb3,hb4 = st.columns(4)
            new_txval= hb1.number_input("Taxable value", min_value=0.0, value=0.0, step=1.0, format="%.2f", key=f"ntxv_{mk}")
            _rf      = new_rt/100/2
            new_camt = hb2.number_input("CGST amt",      min_value=0.0, value=r2(new_txval*_rf), step=0.01, format="%.2f", key=f"nca_{mk}")
            new_samt = hb3.number_input("SGST amt",      min_value=0.0, value=r2(new_txval*_rf), step=0.01, format="%.2f", key=f"nsa_{mk}")
            new_csamt= hb4.number_input("Cess amt",      min_value=0.0, value=0.0, step=0.01, format="%.2f", key=f"ncs_{mk}")
            if st.form_submit_button("➕ Add HSN row", use_container_width=True):
                if not new_hsn.strip():
                    st.error("HSN code is required.")
                elif new_txval <= 0:
                    st.error("Taxable value must be > 0.")
                else:
                    next_num = max((r.get("num",0) for r in cur_hsn), default=0) + 1
                    cur_hsn.append({
                        "num":next_num,"hsn_sc":new_hsn.strip(),"desc":"","user_desc":"",
                        "uqc":new_uqc,"qty":new_qty,"rt":new_rt,"txval":new_txval,
                        "iamt":0,"camt":new_camt,"samt":new_samt,"csamt":new_csamt
                    })
                    st.session_state.hsn_entries[mk] = cur_hsn
                    db_save_hsn(mk, cur_hsn)
                    st.success(f"✓ HSN row added ({new_hsn})"); st.rerun()

        # ── Existing rows table ────────────────────────────────────────────
        if cur_hsn:
            st.markdown(f"**{len(cur_hsn)} HSN rows saved for this month:**")
            preview = [{
                "#":          r.get("num",i+1),
                "HSN Code":   r.get("hsn_sc",""),
                "UQC":        r.get("uqc",""),
                "Qty":        r.get("qty",0),
                "Rate %":     r.get("rt",0),
                "Taxable":    fmtc(r.get("txval",0)),
                "CGST":       fmtc(r.get("camt",0)),
                "SGST":       fmtc(r.get("samt",0)),
            } for i,r in enumerate(cur_hsn)]
            st.dataframe(preview, use_container_width=True, hide_index=True)

            # Edit/delete individual rows
            to_del_hsn = None
            for i, hr in enumerate(cur_hsn):
                lbl_h = f"#{hr.get('num',i+1)} · {hr.get('hsn_sc','')} · {hr.get('uqc','')} · @{hr.get('rt',0)}% · txval {fmtc(hr.get('txval',0))}"
                with st.expander(lbl_h, expanded=False):
                    hc1,hc2,hc3,hc4 = st.columns([2,1,1,1])
                    e_hsn  = hc1.text_input("HSN code",     value=hr.get("hsn_sc",""), key=f"ehsn_{mk}{i}")
                    e_uqc  = hc2.selectbox("UQC",           UQC_OPTIONS, index=UQC_OPTIONS.index(hr.get("uqc","PCS")) if hr.get("uqc","PCS") in UQC_OPTIONS else 0, key=f"euqc_{mk}{i}")
                    e_rt   = hc3.selectbox("Rate %",        RT_OPTIONS,  index=RT_OPTIONS.index(hr.get("rt",0)) if hr.get("rt",0) in RT_OPTIONS else 0, key=f"ert_{mk}{i}")
                    e_qty  = hc4.number_input("Qty",        value=int(hr.get("qty",0)), min_value=0, step=1, key=f"eqty_{mk}{i}")
                    hd1,hd2,hd3,hd4 = st.columns(4)
                    e_txval= hd1.number_input("Taxable",    value=float(hr.get("txval",0)), min_value=0.0, step=1.0, format="%.2f", key=f"etxv_{mk}{i}")
                    _erf   = e_rt/100/2
                    e_camt = hd2.number_input("CGST amt",   value=float(hr.get("camt",0)), min_value=0.0, step=0.01, format="%.2f", key=f"eca_{mk}{i}")
                    e_samt = hd3.number_input("SGST amt",   value=float(hr.get("samt",0)), min_value=0.0, step=0.01, format="%.2f", key=f"esa_{mk}{i}")
                    e_csamt= hd4.number_input("Cess amt",   value=float(hr.get("csamt",0)), min_value=0.0, step=0.01, format="%.2f", key=f"ecs_{mk}{i}")
                    ec1,ec2 = st.columns(2)
                    if ec1.button("💾 Save row", key=f"ehsave_{mk}{i}", type="primary", use_container_width=True):
                        cur_hsn[i] = dict(cur_hsn[i])
                        cur_hsn[i].update({"hsn_sc":e_hsn,"uqc":e_uqc,"rt":e_rt,"qty":e_qty,
                                           "txval":e_txval,"camt":e_camt,"samt":e_samt,"csamt":e_csamt})
                        st.session_state.hsn_entries[mk] = cur_hsn
                        db_save_hsn(mk, cur_hsn)
                        st.success(f"✓ Row #{hr.get('num',i+1)} updated."); st.rerun()
                    if ec2.button("🗑 Delete row", key=f"ehdel_{mk}{i}", use_container_width=True):
                        to_del_hsn = i
            if to_del_hsn is not None:
                cur_hsn.pop(to_del_hsn)
                # Renumber
                for n, r in enumerate(cur_hsn):
                    r["num"] = n + 1
                st.session_state.hsn_entries[mk] = cur_hsn
                db_save_hsn(mk, cur_hsn)
                st.rerun()

            if st.button("🗑 Clear ALL HSN rows for this month", key=f"hsnclr_{mk}"):
                st.session_state.hsn_entries[mk] = []
                db_save_hsn(mk, [])
                st.rerun()
        else:
            st.info("No HSN rows yet. Use Auto-compute or add rows manually above.")

    # ── TAB 4: DOWNLOAD DOCUMENTS ─────────────────────────────────────────────
    with tab_docs:
        bs=bills_summary(mk)
        if bs["count"]==0:
            st.info("Enter purchase bills first."); return

        start_vno=get_voucher_start(mk)
        overrides = st.session_state.sales_override.get(mk, {})
        entries  =build_daily_sales(mk, derive_sales_totals(mk), overrides)
        purchases=ok_bills(mk)
        sales_xls,sales_g,last_vno=make_sales_xlsx(mk,entries,start_vno)
        pur_xls,_ =make_purchase_xlsx(mk,purchases)
        gstr1_dict=make_gstr1_json(mk,sales_g,start_vno,last_vno,last_vno-start_vno+1)
        gstr1_json=json.dumps(gstr1_dict,indent=2)
        m2,y2=parse_mk(mk); mname=lbl.replace(" ","_")

        st.markdown(f"### Summary — {lbl}")
        out_gst=r2(sales_g["c9"]+sales_g["s9"]+sales_g["c25"]+sales_g["s25"]+sales_g["c6"]+sales_g["s6"])
        net_pay=r2(max(0, out_gst - bs["itc"]))
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Total sales",     fmtc(sales_g["val"]))
        c2.metric("Output GST",      fmtc(out_gst))
        c3.metric("ITC (purchases)", fmtc(bs["itc"]))
        c4.metric("Net GST payable", fmtc(net_pay))

        st.markdown("---")
        st.markdown("### Download all 3 documents")

        st.download_button(f"⬇  Sales_Register_{mname}.xlsx",data=sales_xls,
            file_name=f"Sales_Register_{mname}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",use_container_width=True,key=f"dl_s_{mk}")

        st.download_button(f"⬇  Purchase_Register_{mname}.xlsx",data=pur_xls,
            file_name=f"Purchase_Register_{mname}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",use_container_width=True,key=f"dl_p_{mk}")

        st.download_button(f"⬇  {GSTIN}_GSTR1_{MON_ABBR[m2]}{y2}.json",
            data=gstr1_json.encode(),
            file_name=f"{GSTIN}_GSTR1_{MON_ABBR[m2]}{y2}.json",
            mime="application/json",
            type="primary",use_container_width=True,key=f"dl_g_{mk}")

        st.info(f"Vouchers: **{start_vno}** → **{last_vno}** ({last_vno-start_vno+1} bills) · Next month starts at **{last_vno+1}**")
