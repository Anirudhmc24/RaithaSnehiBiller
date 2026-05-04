import random
import datetime
import streamlit as st
from utils.helpers import parse_mk, ld, r2
from config.settings import MONTHS, VOUCHER_START, OCT_LAST_VNO, OCT_LAST_PUR_VNO
from database.db_gst import db_delete_overrides, db_save_override, db_save_target

def calculate_gst(taxable_value: float, gst_rate: float = 0.05):
    """
    Intra-state GST: total rate split 50:50 → CGST + SGST
    """
    half  = gst_rate / 2
    cgst  = round(taxable_value * half, 2)
    sgst  = round(taxable_value * half, 2)
    total = round(taxable_value + cgst + sgst, 2)
    return cgst, sgst, total

def get_voucher_start(mk):
    return VOUCHER_START.get(mk, OCT_LAST_VNO + 1)

def get_purchase_voucher_start(mk, ok_bills_func):
    mk_list = [m for m,_ in MONTHS]
    idx = mk_list.index(mk)
    vno = OCT_LAST_PUR_VNO + 1
    for i in range(idx):
        prev_mk = mk_list[i]
        vno += len(ok_bills_func(prev_mk))
    return vno

def build_daily_sales(mk, totals, overrides):
    m, y    = parse_mk(mk)
    days    = ld(m, y)
    random.seed(m*1000+y)

    all_days = list(range(1, days))
    random.shuffle(all_days)
    only5  = set(all_days[:3])
    mixed  = set(all_days[3:6])
    has12  = set(random.sample(all_days[6:], min(2, max(0,len(all_days)-6))))

    running = {"v18":0.0,"v5":0.0,"v12":0.0}
    entries = []

    for d in range(1, days+1):
        if d in overrides:
            ov = overrides[d]
            entries.append({"date":datetime.date(y,m,d),
                "v18":ov.get("v18",0),"v5":ov.get("v5",0),
                "v12":ov.get("v12",0),"vex":ov.get("vex",0),
                "nbills":ov.get("nbills",4)})
            for k in ("v18","v5","v12"):
                running[k] += ov.get(k,0)
            continue

        is_last = (d == days)
        if is_last:
            vex = max(0, r2(totals["vex"] - sum(e["vex"] for e in entries)))
            entries.append({"date":datetime.date(y,m,d),
                "v18":0,"v5":0,"v12":0,"vex":vex,
                "nbills":random.randint(2,4)})
            continue

        rem_days  = days - d
        rem18 = max(0, totals["v18"] - running["v18"])
        rem5  = max(0, totals["v5"]  - running["v5"])
        rem12 = max(0, totals["v12"] - running["v12"])
        avg18 = rem18 / max(rem_days,1)
        avg5  = rem5  / max(rem_days,1)
        avg12 = rem12 / max(rem_days,1)
        dm    = min(max(random.lognormvariate(0, 0.75), 0.08), 3.5)

        if d in only5:
            v18=0; v5=r2(min(avg5*random.uniform(2,3.5), rem5)); v12=0; nb=random.randint(2,4)
        elif d in mixed:
            v18=r2(min(avg18*dm*0.8, rem18)); v5=r2(min(avg5*random.uniform(1.5,3), rem5)); v12=0; nb=random.randint(3,6)
        elif d in has12:
            v18=r2(min(avg18*dm*0.95, rem18)); v12=r2(min(avg12*random.uniform(1.5,2.5), rem12)); v5=0; nb=random.randint(4,7)
        else:
            v18=r2(min(avg18*dm, rem18)); v5=0; v12=0; nb=random.randint(2,6)

        if v18 > 0:
            v18 = float(round(v18/50)*50)
        v18=max(0,v18); v5=max(0,v5); v12=max(0,v12)

        entries.append({"date":datetime.date(y,m,d),"v18":v18,"v5":v5,"v12":v12,"vex":0,"nbills":nb})
        running["v18"]+=v18; running["v5"]+=v5; running["v12"]+=v12

    return entries

def distribute_target_sales(mk, target_val):
    """Smart Sales Override: generates daily sales data based on a log-normal distribution."""
    m, y  = parse_mk(mk)
    days  = ld(m, y)

    rev18 = r2(target_val * 0.75)
    rev5  = r2(target_val - rev18)

    total18 = r2(rev18 / 1.18)
    total5  = r2(rev5  / 1.05)

    random.seed(mk + "_smart")
    raw_weights = [max(0.4, min(random.lognormvariate(0, 0.30), 1.8))
                   for _ in range(days)]
    wsum = sum(raw_weights)
    weights = [w / wsum for w in raw_weights]

    db_delete_overrides(mk)
    st.session_state.sales_override[mk] = {}

    running18 = 0.0
    running5  = 0.0
    running_gross = 0.0

    for d in range(1, days + 1):
        w       = weights[d - 1]
        is_last = (d == days)

        if is_last:
            v18 = r2(max(0, total18 - running18))
            v5  = r2(max(0, total5  - running5))
            expected_gross = r2(v18 * 1.18 + v5 * 1.05)
            remainder = r2(target_val - running_gross - expected_gross)
            if remainder != 0:
                v5 = r2(v5 + remainder / 1.05)
        else:
            v18 = r2(total18 * w)
            v5  = r2(total5  * w)

        nbills  = random.randint(2, 6)
        ov_data = {"v18": v18, "v5": v5, "v12": 0.0, "vex": 0.0, "nbills": nbills}

        st.session_state.sales_override[mk][d] = ov_data
        db_save_override(mk, d, ov_data)

        running18 += v18
        running5  += v5
        running_gross += r2(v18 * 1.18 + v5 * 1.05)

    db_save_target(mk, target_val)
