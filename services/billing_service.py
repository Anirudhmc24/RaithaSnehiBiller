import streamlit as st
from utils.helpers import r2
from config.settings import RATIO_18_TO_18, RATIO_18_TO_12, RATIO_5_TO_5, RATIO_EX_TO_EX, MONTH_FP, GSTIN

FILED_B2CS = {
    "10-2025": [
        {"typ":"OE","sply_ty":"INTRA","rt":5, "pos":"29","txval":10298.03,"camt":257.45, "samt":257.45, "csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":12,"pos":"29","txval":2175,    "camt":130.50, "samt":130.50, "csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":18,"pos":"29","txval":339490,  "camt":30554.10,"samt":30554.10,"csamt":0},
    ],
    "11-2025": [
        {"typ":"OE","sply_ty":"INTRA","rt":5, "pos":"29","txval":4830.599999999999,"camt":120.76,"samt":120.76,"csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":12,"pos":"29","txval":1374.5,           "camt":82.47, "samt":82.47, "csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":18,"pos":"29","txval":274300.0,         "camt":24687.0,"samt":24687.0,"csamt":0},
    ],
    "12-2025": [
        {"typ":"OE","sply_ty":"INTRA","rt":5, "pos":"29","txval":57400.97999999999,"camt":1435.02,"samt":1435.02,"csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":12,"pos":"29","txval":281.02,           "camt":16.86,  "samt":16.86,  "csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":18,"pos":"29","txval":112650.0,         "camt":10138.5,"samt":10138.5,"csamt":0},
    ],
    "01-2026": [
        {"typ":"OE","sply_ty":"INTRA","rt":5, "pos":"29","txval":56423.25,            "camt":1410.58,"samt":1410.58,"csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":12,"pos":"29","txval":798.7,               "camt":47.92,  "samt":47.92,  "csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":18,"pos":"29","txval":398700.00000000006,  "camt":35883.0,"samt":35883.0,"csamt":0},
    ],
    "02-2026": [
        {"typ":"OE","sply_ty":"INTRA","rt":5, "pos":"29","txval":144559.73999999996, "camt":3613.99,"samt":3613.99,"csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":12,"pos":"29","txval":123.72,             "camt":7.42,   "samt":7.42,   "csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":18,"pos":"29","txval":34650.0,            "camt":3118.5, "samt":3118.5, "csamt":0},
    ],
    "03-2026": [
        {"typ":"OE","sply_ty":"INTRA","rt":5, "pos":"29","txval":382857.13,"camt":9571.43, "samt":9571.43, "csamt":0},
        {"typ":"OE","sply_ty":"INTRA","rt":18,"pos":"29","txval":1022033.9,"camt":91983.05,"samt":91983.05,"csamt":0},
    ],
}

FILED_NIL = {
    "10-2025": {"inv":[{"sply_ty":"INTRAB2C","nil_amt":0,"expt_amt":11250,  "ngsup_amt":0}]},
    "11-2025": {"inv":[{"sply_ty":"INTRAB2C","nil_amt":0,"expt_amt":65740.0,"ngsup_amt":0}]},
    "12-2025": {"inv":[{"sply_ty":"INTRAB2C","nil_amt":0,"expt_amt":0.0,    "ngsup_amt":0}]},
    "01-2026": {"inv":[{"sply_ty":"INTRAB2C","nil_amt":0,"expt_amt":0.0,    "ngsup_amt":0}]},
    "02-2026": {"inv":[{"sply_ty":"INTRAB2C","nil_amt":0,"expt_amt":6920.0, "ngsup_amt":0}]},
    "03-2026": {"inv":[{"sply_ty":"INTRAB2C","nil_amt":0,"expt_amt":0.0,   "ngsup_amt":0}]},
}

FILED_DOC_ISSUE = {
    "10-2025": {"doc_det":[{"doc_num":1,"docs":[{"cancel":0,"from":"351","net_issue":124,"num":1,"to":"474","totnum":124}]}]},
    "11-2025": {"doc_det":[{"doc_num":1,"docs":[{"cancel":0,"from":"475","net_issue":117,"num":1,"to":"591","totnum":117}]}]},
    "12-2025": {"doc_det":[{"doc_num":1,"docs":[{"cancel":0,"from":"592","net_issue":119,"num":1,"to":"710","totnum":119}]}]},
    "01-2026": {"doc_det":[{"doc_num":1,"docs":[{"cancel":0,"from":"714","net_issue":117,"num":1,"to":"830","totnum":117}]}]},
    "02-2026": {"doc_det":[{"doc_num":1,"docs":[{"cancel":0,"from":"834","net_issue":106,"num":1,"to":"939","totnum":106}]}]},
    "03-2026": {"doc_det":[{"doc_num":1,"docs":[{"cancel":0,"from":"940","net_issue":131,"num":1,"to":"1070","totnum":131}]}]},
}

FILED_HSN = {
    "11-2025": [
        {"num":1,"hsn_sc":"10063010","desc":"","user_desc":"","uqc":"PAC","qty":9,"rt":0,"txval":65740.0,"iamt":0,"camt":0.0,"samt":0.0,"csamt":0},
        {"num":2,"hsn_sc":"31059010","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":5,"txval":1850.12,"iamt":0,"camt":46.25,"samt":46.25,"csamt":0},
        {"num":3,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":5,"txval":1526.47,"iamt":0,"camt":38.16,"samt":38.16,"csamt":0},
        {"num":4,"hsn_sc":"38089349","desc":"","user_desc":"","uqc":"PAC","qty":1,"rt":5,"txval":1454.01,"iamt":0,"camt":36.35,"samt":36.35,"csamt":0},
        {"num":5,"hsn_sc":"28331990","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":12,"txval":1374.5,"iamt":0,"camt":82.47,"samt":82.47,"csamt":0},
        {"num":6,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":686,"rt":18,"txval":168968.8,"iamt":0,"camt":15207.19,"samt":15207.19,"csamt":0},
        {"num":7,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PCS","qty":165,"rt":18,"txval":27430.0,"iamt":0,"camt":2468.7,"samt":2468.7,"csamt":0},
        {"num":8,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PAC","qty":52,"rt":18,"txval":14537.9,"iamt":0,"camt":1308.41,"samt":1308.41,"csamt":0},
        {"num":9,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":96,"rt":18,"txval":23864.1,"iamt":0,"camt":2147.77,"samt":2147.77,"csamt":0},
        {"num":10,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PAC","qty":5,"rt":18,"txval":7954.7,"iamt":0,"camt":715.92,"samt":715.92,"csamt":0},
        {"num":11,"hsn_sc":"39201012","desc":"","user_desc":"","uqc":"PCS","qty":19,"rt":18,"txval":12617.8,"iamt":0,"camt":1135.6,"samt":1135.6,"csamt":0},
        {"num":12,"hsn_sc":"38089350","desc":"","user_desc":"","uqc":"PCS","qty":27,"rt":18,"txval":6583.2,"iamt":0,"camt":592.49,"samt":592.49,"csamt":0},
        {"num":13,"hsn_sc":"34029099","desc":"","user_desc":"","uqc":"PCS","qty":58,"rt":18,"txval":5760.3,"iamt":0,"camt":518.43,"samt":518.43,"csamt":0},
        {"num":14,"hsn_sc":"38081091","desc":"","user_desc":"","uqc":"PCS","qty":19,"rt":18,"txval":3840.2,"iamt":0,"camt":345.62,"samt":345.62,"csamt":0},
        {"num":15,"hsn_sc":"38089910","desc":"","user_desc":"","uqc":"PCS","qty":3,"rt":18,"txval":1920.1,"iamt":0,"camt":172.81,"samt":172.81,"csamt":0},
        {"num":16,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":14,"rt":18,"txval":1097.2,"iamt":0,"camt":98.75,"samt":98.75,"csamt":0},
    ],
    "12-2025": [
        {"num":1,"hsn_sc":"31059010","desc":"","user_desc":"","uqc":"PCS","qty":12,"rt":5,"txval":21984.58,"iamt":0,"camt":549.61,"samt":549.61,"csamt":0},
        {"num":2,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":3,"rt":5,"txval":18138.71,"iamt":0,"camt":453.47,"samt":453.47,"csamt":0},
        {"num":3,"hsn_sc":"38089349","desc":"","user_desc":"","uqc":"PAC","qty":12,"rt":5,"txval":17277.69,"iamt":0,"camt":431.94,"samt":431.94,"csamt":0},
        {"num":4,"hsn_sc":"28331990","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":12,"txval":281.02,"iamt":0,"camt":16.86,"samt":16.86,"csamt":0},
        {"num":5,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":282,"rt":18,"txval":69392.4,"iamt":0,"camt":6245.32,"samt":6245.32,"csamt":0},
        {"num":6,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PCS","qty":68,"rt":18,"txval":11265.0,"iamt":0,"camt":1013.85,"samt":1013.85,"csamt":0},
        {"num":7,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PAC","qty":21,"rt":18,"txval":5970.45,"iamt":0,"camt":537.34,"samt":537.34,"csamt":0},
        {"num":8,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":39,"rt":18,"txval":9800.55,"iamt":0,"camt":882.05,"samt":882.05,"csamt":0},
        {"num":9,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PAC","qty":2,"rt":18,"txval":3266.85,"iamt":0,"camt":294.02,"samt":294.02,"csamt":0},
        {"num":10,"hsn_sc":"39201012","desc":"","user_desc":"","uqc":"PCS","qty":8,"rt":18,"txval":5181.9,"iamt":0,"camt":466.37,"samt":466.37,"csamt":0},
        {"num":11,"hsn_sc":"38089350","desc":"","user_desc":"","uqc":"PCS","qty":11,"rt":18,"txval":2703.6,"iamt":0,"camt":243.32,"samt":243.32,"csamt":0},
        {"num":12,"hsn_sc":"34029099","desc":"","user_desc":"","uqc":"PCS","qty":24,"rt":18,"txval":2365.65,"iamt":0,"camt":212.91,"samt":212.91,"csamt":0},
        {"num":13,"hsn_sc":"38081091","desc":"","user_desc":"","uqc":"PCS","qty":8,"rt":18,"txval":1577.1,"iamt":0,"camt":141.94,"samt":141.94,"csamt":0},
        {"num":14,"hsn_sc":"38089910","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":18,"txval":788.55,"iamt":0,"camt":70.97,"samt":70.97,"csamt":0},
        {"num":15,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":6,"rt":18,"txval":450.6,"iamt":0,"camt":40.55,"samt":40.55,"csamt":0},
    ],
    "01-2026": [
        {"num":1,"hsn_sc":"31059010","desc":"","user_desc":"","uqc":"PCS","qty":12,"rt":5,"txval":21610.1,"iamt":0,"camt":540.25,"samt":540.25,"csamt":0},
        {"num":2,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":3,"rt":5,"txval":17829.75,"iamt":0,"camt":445.74,"samt":445.74,"csamt":0},
        {"num":3,"hsn_sc":"38089349","desc":"","user_desc":"","uqc":"PAC","qty":12,"rt":5,"txval":16983.4,"iamt":0,"camt":424.58,"samt":424.58,"csamt":0},
        {"num":4,"hsn_sc":"28331990","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":12,"txval":798.7,"iamt":0,"camt":47.92,"samt":47.92,"csamt":0},
        {"num":5,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":997,"rt":18,"txval":245599.2,"iamt":0,"camt":22103.93,"samt":22103.93,"csamt":0},
        {"num":6,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PCS","qty":239,"rt":18,"txval":39870.0,"iamt":0,"camt":3588.3,"samt":3588.3,"csamt":0},
        {"num":7,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PAC","qty":76,"rt":18,"txval":21131.1,"iamt":0,"camt":1901.8,"samt":1901.8,"csamt":0},
        {"num":8,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":140,"rt":18,"txval":34686.9,"iamt":0,"camt":3121.82,"samt":3121.82,"csamt":0},
        {"num":9,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PAC","qty":8,"rt":18,"txval":11562.3,"iamt":0,"camt":1040.61,"samt":1040.61,"csamt":0},
        {"num":10,"hsn_sc":"39201012","desc":"","user_desc":"","uqc":"PCS","qty":28,"rt":18,"txval":18340.2,"iamt":0,"camt":1650.62,"samt":1650.62,"csamt":0},
        {"num":11,"hsn_sc":"38089350","desc":"","user_desc":"","uqc":"PCS","qty":40,"rt":18,"txval":9568.8,"iamt":0,"camt":861.19,"samt":861.19,"csamt":0},
        {"num":12,"hsn_sc":"34029099","desc":"","user_desc":"","uqc":"PCS","qty":84,"rt":18,"txval":8372.7,"iamt":0,"camt":753.54,"samt":753.54,"csamt":0},
        {"num":13,"hsn_sc":"38081091","desc":"","user_desc":"","uqc":"PCS","qty":28,"rt":18,"txval":5581.8,"iamt":0,"camt":502.36,"samt":502.36,"csamt":0},
        {"num":14,"hsn_sc":"38089910","desc":"","user_desc":"","uqc":"PCS","qty":4,"rt":18,"txval":2790.9,"iamt":0,"camt":251.18,"samt":251.18,"csamt":0},
        {"num":15,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":20,"rt":18,"txval":1594.8,"iamt":0,"camt":143.53,"samt":143.53,"csamt":0},
    ],
    "02-2026": [
        {"num":1,"hsn_sc":"10063010","desc":"","user_desc":"","uqc":"PAC","qty":1,"rt":0,"txval":6920.0,"iamt":0,"camt":0.0,"samt":0.0,"csamt":0},
        {"num":2,"hsn_sc":"31059010","desc":"","user_desc":"","uqc":"PCS","qty":30,"rt":5,"txval":55366.38,"iamt":0,"camt":1384.16,"samt":1384.16,"csamt":0},
        {"num":3,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":7,"rt":5,"txval":45680.88,"iamt":0,"camt":1142.02,"samt":1142.02,"csamt":0},
        {"num":4,"hsn_sc":"38089349","desc":"","user_desc":"","uqc":"PAC","qty":30,"rt":5,"txval":43512.48,"iamt":0,"camt":1087.81,"samt":1087.81,"csamt":0},
        {"num":5,"hsn_sc":"28331990","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":12,"txval":123.72,"iamt":0,"camt":7.42,"samt":7.42,"csamt":0},
        {"num":6,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":87,"rt":18,"txval":21344.4,"iamt":0,"camt":1921.0,"samt":1921.0,"csamt":0},
        {"num":7,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PCS","qty":21,"rt":18,"txval":3465.0,"iamt":0,"camt":311.85,"samt":311.85,"csamt":0},
        {"num":8,"hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PAC","qty":7,"rt":18,"txval":1836.45,"iamt":0,"camt":165.28,"samt":165.28,"csamt":0},
        {"num":9,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":12,"rt":18,"txval":3014.55,"iamt":0,"camt":271.31,"samt":271.31,"csamt":0},
        {"num":10,"hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PAC","qty":1,"rt":18,"txval":1004.85,"iamt":0,"camt":90.44,"samt":90.44,"csamt":0},
        {"num":11,"hsn_sc":"39201012","desc":"","user_desc":"","uqc":"PCS","qty":2,"rt":18,"txval":1593.9,"iamt":0,"camt":143.45,"samt":143.45,"csamt":0},
        {"num":12,"hsn_sc":"38089350","desc":"","user_desc":"","uqc":"PCS","qty":3,"rt":18,"txval":831.6,"iamt":0,"camt":74.84,"samt":74.84,"csamt":0},
        {"num":13,"hsn_sc":"34029099","desc":"","user_desc":"","uqc":"PCS","qty":7,"rt":18,"txval":727.65,"iamt":0,"camt":65.49,"samt":65.49,"csamt":0},
        {"num":14,"hsn_sc":"38081091","desc":"","user_desc":"","uqc":"PCS","qty":2,"rt":18,"txval":485.1,"iamt":0,"camt":43.66,"samt":43.66,"csamt":0},
        {"num":15,"hsn_sc":"38089910","desc":"","user_desc":"","uqc":"PCS","qty":1,"rt":18,"txval":242.55,"iamt":0,"camt":21.83,"samt":21.83,"csamt":0},
        {"num":16,"hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":2,"rt":18,"txval":138.6,"iamt":0,"camt":12.47,"samt":12.47,"csamt":0},
    ],
    "03-2026": [
        {"num":1, "hsn_sc":"31059010","desc":"","user_desc":"","uqc":"PCS","qty":79,  "rt":5, "txval":146634.28,"iamt":0,"camt":3665.86,"samt":3665.86,"csamt":0},
        {"num":2, "hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":19,  "rt":5, "txval":120982.86,"iamt":0,"camt":3024.57,"samt":3024.57,"csamt":0},
        {"num":3, "hsn_sc":"38089349","desc":"","user_desc":"","uqc":"PAC","qty":79,  "rt":5, "txval":115239.99,"iamt":0,"camt":2881.00,"samt":2881.00,"csamt":0},
        {"num":4, "hsn_sc":"38089290","desc":"","user_desc":"","uqc":"PCS","qty":2566,"rt":18,"txval":629572.88,"iamt":0,"camt":56661.56,"samt":56661.56,"csamt":0},
        {"num":5, "hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PCS","qty":619, "rt":18,"txval":102203.39,"iamt":0,"camt":9198.31,"samt":9198.31,"csamt":0},
        {"num":6, "hsn_sc":"38089390","desc":"","user_desc":"","uqc":"PAC","qty":206, "rt":18,"txval":54167.80, "iamt":0,"camt":4875.10,"samt":4875.10,"csamt":0},
        {"num":7, "hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PCS","qty":354, "rt":18,"txval":88916.95, "iamt":0,"camt":8002.53,"samt":8002.53,"csamt":0},
        {"num":8, "hsn_sc":"38089199","desc":"","user_desc":"","uqc":"PAC","qty":29,  "rt":18,"txval":29638.98, "iamt":0,"camt":2667.51,"samt":2667.51,"csamt":0},
        {"num":9, "hsn_sc":"39201012","desc":"","user_desc":"","uqc":"PCS","qty":59,  "rt":18,"txval":47013.56, "iamt":0,"camt":4231.22,"samt":4231.22,"csamt":0},
        {"num":10,"hsn_sc":"38089350","desc":"","user_desc":"","uqc":"PCS","qty":88,  "rt":18,"txval":24528.81, "iamt":0,"camt":2207.59,"samt":2207.59,"csamt":0},
        {"num":11,"hsn_sc":"34029099","desc":"","user_desc":"","uqc":"PCS","qty":206, "rt":18,"txval":21462.71, "iamt":0,"camt":1931.64,"samt":1931.64,"csamt":0},
        {"num":12,"hsn_sc":"38081091", "desc":"","user_desc":"","uqc":"PCS","qty":59,  "rt":18,"txval":14308.47, "iamt":0,"camt":1287.76,"samt":1287.76,"csamt":0},
        {"num":13,"hsn_sc":"38089910","desc":"","user_desc":"","uqc":"PCS","qty":29,  "rt":18,"txval":7154.24,  "iamt":0,"camt":643.88, "samt":643.88, "csamt":0},
        {"num":14,"hsn_sc":"38089290", "desc":"","user_desc":"","uqc":"PCS","qty":44,  "rt":18,"txval":3066.11,  "iamt":0,"camt":275.95, "samt":275.95, "csamt":0},
    ],
}

def ok_bills(mk):
    bills_dict = st.session_state.get("bills", {})
    if not isinstance(bills_dict, dict): return []
    return [b for b in bills_dict.get(mk,[]) if b.get("status")=="ok"]

def bills_summary(mk):
    bills = ok_bills(mk)
    p18  = sum(b.get("val18") or 0 for b in bills)
    p5   = sum(b.get("val5")  or 0 for b in bills)
    p12  = sum(b.get("val12") or 0 for b in bills)
    pex  = sum(b.get("exempt")or 0 for b in bills)
    itc  = sum((float(b.get("cgst9") or 0))+(float(b.get("sgst9") or 0))+
               (float(b.get("cgst25")or 0))+(float(b.get("sgst25")or 0)) for b in bills)
    gross= sum(float(b.get("gross") or 0) for b in bills)
    return {"p18":r2(p18),"p5":r2(p5),"p12":r2(p12),"pex":r2(pex),
            "itc":r2(itc),"gross":r2(gross),"count":len(bills)}

def derive_sales_totals(mk):
    bs = bills_summary(mk)
    return {
        "v18": r2(bs["p18"]*RATIO_18_TO_18),
        "v5":  r2(bs["p5"] *RATIO_5_TO_5),
        "v12": r2(bs["p18"]*RATIO_18_TO_12),
        "vex": r2(bs["pex"]*RATIO_EX_TO_EX),
    }

def make_gstr1_json(mk, sales_g, vno_from, vno_to, vno_count):
    fp = MONTH_FP.get(mk, mk.replace("-",""))

    if mk in FILED_B2CS:
        b2cs      = FILED_B2CS[mk]
        nil       = FILED_NIL[mk]
        doc_issue = FILED_DOC_ISSUE[mk]
    else:
        v18=sales_g["v18"]; v5=sales_g["v5"]; v12=sales_g["v12"]; vex=sales_g["ex"]
        b2cs=[]
        for rt,txval in [(5,v5),(12,v12),(18,v18)]:
            if txval>0:
                rf=rt/100/2
                b2cs.append({"typ":"OE","sply_ty":"INTRA","rt":rt,"pos":"29",
                    "txval":r2(txval),"camt":r2(txval*rf),"samt":r2(txval*rf),"csamt":0})
        nil={"inv":[{"sply_ty":"INTRAB2C","nil_amt":0,"expt_amt":vex,"ngsup_amt":0}]}
        doc_issue={"doc_det":[{"doc_num":1,"docs":[{
            "cancel":0,"from":str(vno_from),"net_issue":vno_count,
            "num":1,"to":str(vno_to),"totnum":vno_count}]}]}

    result = {"gstin":GSTIN,"fp":fp,"b2cs":b2cs,"nil":nil,"doc_issue":doc_issue}

    HSN_KEY_ORDER = ["num","hsn_sc","txval","iamt","camt","samt","csamt","desc","user_desc","uqc","qty","rt"]
    
    # 1. Check session state first (manually curated in HSN Summary tab)
    hsn_rows = st.session_state.get("hsn_entries", {}).get(mk, [])

    # 2. Fall back to FILED_HSN for pre-filed months
    if not hsn_rows and mk in FILED_HSN:
        hsn_rows = FILED_HSN[mk]

    # 3. Aggregate from purchase bills' HSN line items (accurate — entered per invoice)
    if not hsn_rows:
        hsn_rows = aggregate_hsn_from_bills(mk)

    # 4. Last resort: proportional estimate from March 2026 product-mix
    if not hsn_rows:
        hsn_rows = derive_hsn_from_sales(sales_g)

    if hsn_rows:
        ordered_rows = [
            {k: row.get(k, 0 if k not in ("desc","user_desc","hsn_sc","uqc") else "")
             for k in HSN_KEY_ORDER}
            for row in hsn_rows
        ]
        result["hsn"] = {"hsn_b2c": ordered_rows}

    return result


# ─────────────────────────────────────────────────────────────────────────────
# HSN FROM PURCHASE BILLS  (accurate — aggregated directly from invoices)
# ─────────────────────────────────────────────────────────────────────────────

def aggregate_hsn_from_bills(mk):
    """
    Aggregate HSN line items from all OK purchase bills for a month.
    Groups by (hsn_sc, uqc, rt), sums qty + taxable value, and returns
    numbered GSTR-1 HSN rows.

    Returns [] if no bill has hsn_items data.
    """
    bills = ok_bills(mk)
    agg   = {}   # (hsn_sc, uqc, rt) → {qty, txval}
    for b in bills:
        for it in (b.get("hsn_items") or []):
            key = (it.get("hsn_sc", ""), it.get("uqc", "PCS"), it.get("rt", 0))
            if key not in agg:
                agg[key] = {"qty": 0, "txval": 0.0}
            agg[key]["qty"]   += it.get("qty",   0)
            agg[key]["txval"] += it.get("txval", 0.0)
    if not agg:
        return []
    rows = []
    num  = 1
    for (hsn_sc, uqc, rt), v in sorted(agg.items(), key=lambda x: x[0][2]):
        txval = r2(v["txval"])
        rf    = rt / 100 / 2
        rows.append({
            "num": num, "hsn_sc": hsn_sc, "desc": "", "user_desc": "",
            "uqc": uqc, "qty": v["qty"], "rt": rt, "txval": txval,
            "iamt": 0, "camt": r2(txval * rf), "samt": r2(txval * rf), "csamt": 0,
        })
        num += 1
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# HSN AUTO-DERIVATION (proportional fallback)
# Proportions derived from March 2026 (most recent complete filed month).
# For unfiled months, these ratios are applied to the computed v5 / v18
# sales totals so the JSON always contains a valid HSN summary.
# ─────────────────────────────────────────────────────────────────────────────

# (hsn_sc, uqc, rt, txval_fraction_of_slab, qty_per_rupee_of_txval)
# Fractions sum to 1.0 within each slab.
_HSN_DIST_5 = [
    ("31059010", "PCS", 5,  0.3829, 0.000539),   # NPK fertilizers
    ("38089199", "PCS", 5,  0.3160, 0.000157),   # Insecticide 5% PCS
    ("38089349", "PAC", 5,  0.3011, 0.000685),   # Insecticide 5% pack
]

_HSN_DIST_18 = [
    # hsn_sc,   uqc,   rt,  txval_frac,  qty/₹
    ("38089290", "PCS", 18, 0.6190, 0.004127),   # Fungicide PCS (dominant)
    ("38089390", "PCS", 18, 0.1000, 0.006057),   # Herbicide PCS
    ("38089199", "PCS", 18, 0.0870, 0.003983),   # Insecticide 18% PCS
    ("38089390", "PAC", 18, 0.0530, 0.003802),   # Herbicide PAC
    ("39201012", "PCS", 18, 0.0460, 0.001254),   # Mulch film / plastic sheet
    ("38089199", "PAC", 18, 0.0290, 0.000978),   # Insecticide 18% PAC
    ("38089350", "PCS", 18, 0.0240, 0.003587),   # Rodenticide
    ("34029099", "PCS", 18, 0.0210, 0.009599),   # Surfactant / wetting agent
    ("38081091", "PCS", 18, 0.0140, 0.004123),   # Chlorpyrifos / insecticide
    ("38089910", "PCS", 18, 0.0070, 0.004053),   # Other pesticide formulation
]

def derive_hsn_from_sales(sales_g):
    """
    Auto-generate HSN summary rows for an unfiled month by distributing
    the sales taxable values (v5, v18) across HSN codes using the
    product-mix proportions of March 2026.

    Returns a list of HSN row dicts ready for the GSTR-1 JSON.
    """
    v5  = sales_g.get("v5",  0) or 0
    v18 = sales_g.get("v18", 0) or 0

    rows = []
    num  = 1

    for hsn_sc, uqc, rt, frac, qty_per_rupee in _HSN_DIST_5:
        txval = r2(v5 * frac)
        if txval <= 0:
            continue
        qty  = max(1, round(txval * qty_per_rupee))
        rf   = rt / 100 / 2
        rows.append({
            "num": num, "hsn_sc": hsn_sc, "desc": "", "user_desc": "",
            "uqc": uqc, "qty": qty, "rt": rt, "txval": txval,
            "iamt": 0, "camt": r2(txval * rf), "samt": r2(txval * rf), "csamt": 0,
        })
        num += 1

    for hsn_sc, uqc, rt, frac, qty_per_rupee in _HSN_DIST_18:
        txval = r2(v18 * frac)
        if txval <= 0:
            continue
        qty  = max(1, round(txval * qty_per_rupee))
        rf   = rt / 100 / 2
        rows.append({
            "num": num, "hsn_sc": hsn_sc, "desc": "", "user_desc": "",
            "uqc": uqc, "qty": qty, "rt": rt, "txval": txval,
            "iamt": 0, "camt": r2(txval * rf), "samt": r2(txval * rf), "csamt": 0,
        })
        num += 1

    return rows
