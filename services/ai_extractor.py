import base64
import json
import re
import datetime
import requests

EXTRACT_PROMPT = """Extract all fields from this Indian GST purchase invoice.
Return ONLY valid JSON — no markdown, no explanation.
{
  "supplier":"full company name","gstin":"15-char GSTIN",
  "invno":"invoice number","inv_date":"DD-MM-YYYY",
  "val18":taxable@18% (number),"cgst9":CGST9% (number),"sgst9":SGST9% (number),
  "val5":taxable@5% (number),"cgst25":CGST2.5% (number),"sgst25":SGST2.5% (number),
  "val12":taxable@12% (number),"exempt":exempt value (number),
  "gross":total invoice amount (number),"round_off":rounding (number),"discount":cash discount (number)
}
All numbers plain — no commas, no symbols. Use 0 if not present."""

def extract_bill_ai(image_bytes, mime_type, api_key):
    b64 = base64.b64encode(image_bytes).decode()
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        headers={"content-type":"application/json"},
        json={"contents":[{"parts":[{"inline_data":{"mime_type":mime_type,"data":b64}},
            {"text":EXTRACT_PROMPT}]}],
            "generationConfig":{"maxOutputTokens":500,"temperature":0}},
        timeout=30)
    resp.raise_for_status()
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"```[a-z]*","",text).strip()
    data = json.loads(text)
    try:
        pts = str(data.get("inv_date","")).split("-")
        data["inv_date_obj"] = datetime.date(int(pts[2]),int(pts[1]),int(pts[0]))
    except: data["inv_date_obj"] = None
    for f in ["val18","cgst9","sgst9","val5","cgst25","sgst25","val12",
              "exempt","gross","round_off","discount"]:
        try:    data[f] = float(data.get(f) or 0)
        except: data[f] = 0.0
    return data
