import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from config.settings import (
    SHOP_NAME, SHOP_ADDRESS1, SHOP_ADDRESS2, SHOP_ADDRESS3,
    SHOP_PHONE, SHOP_EMAIL, GSTIN, STATE_CODE
)

def generate_pdf_invoice(invoice_data: dict, items: list) -> bytes:
    buffer     = io.BytesIO()
    doc        = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=12*mm, rightMargin=12*mm,
        topMargin=8*mm,   bottomMargin=12*mm
    )

    brand_blue  = colors.HexColor("#1a3c5e")
    brand_green = colors.HexColor("#2e7d32")
    light_grey  = colors.HexColor("#f5f5f5")
    mid_grey    = colors.HexColor("#e0e0e0")
    white       = colors.white

    s_shop  = ParagraphStyle("shop",  fontSize=16, textColor=white, alignment=TA_CENTER, fontName="Helvetica-Bold", leading=20)
    s_addr  = ParagraphStyle("addr",  fontSize=8,  textColor=colors.HexColor("#c8e6c9"), alignment=TA_CENTER, fontName="Helvetica", leading=12)
    s_label = ParagraphStyle("lbl",   fontSize=8,  textColor=brand_blue, fontName="Helvetica-Bold")
    s_val   = ParagraphStyle("val",   fontSize=8,  fontName="Helvetica")
    s_foot  = ParagraphStyle("ft",    fontSize=7,  textColor=colors.grey, alignment=TA_CENTER, fontName="Helvetica-Oblique")
    s_ti    = ParagraphStyle("ti",    fontSize=9,  textColor=white, alignment=TA_CENTER, fontName="Helvetica-Bold", leading=14)

    story = []
    inv   = invoice_data

    header_content = [
        [Paragraph(SHOP_NAME, s_shop)],
        [Paragraph(SHOP_ADDRESS1, s_addr)],
        [Paragraph(SHOP_ADDRESS2, s_addr)],
        [Paragraph(SHOP_ADDRESS3, s_addr)],
        [Paragraph(f"📞 {SHOP_PHONE}   |   ✉ {SHOP_EMAIL}   |   GSTIN: {GSTIN}", s_addr)],
    ]
    t_banner = Table(header_content, colWidths=[186*mm])
    t_banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), brand_blue),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 2*mm))

    t_title = Table([[
        Paragraph("TAX INVOICE", s_ti),
        Paragraph(f"Invoice No: <b>{inv['invoice_no']}</b>", s_val),
        Paragraph(f"Date: <b>{inv['invoice_date'][:10]}</b>", s_val),
    ]], colWidths=[80*mm, 60*mm, 46*mm])
    t_title.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), brand_green),
        ("BACKGROUND",    (1,0),(2,0), light_grey),
        ("ALIGN",         (0,0),(0,0), "CENTER"),
        ("ALIGN",         (1,0),(2,0), "LEFT"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("BOX",           (0,0),(-1,-1), 0.5, mid_grey),
        ("LINEAFTER",     (0,0),(1,0),   0.5, mid_grey),
    ]))
    story.append(t_title)
    story.append(Spacer(1, 3*mm))

    def cell(label, value):
        return Paragraph(f"<b>{label}:</b> {value}", s_val)

    seller_rows = [
        [Paragraph("<b>Sold By</b>", s_label)],
        [cell("Name",  SHOP_NAME)],
        [cell("Addr",  f"{SHOP_ADDRESS1}, {SHOP_ADDRESS2}")],
        [cell("",      SHOP_ADDRESS3)],
        [cell("GSTIN", GSTIN)],
        [cell("State", f"Karnataka ({STATE_CODE})")],
    ]
    buyer_name  = inv.get("customer_name")  or "Cash Customer"
    buyer_phone = inv.get("customer_phone") or "—"
    buyer_gstin = inv.get("customer_gstin") or "Unregistered"
    buyer_rows  = [
        [Paragraph("<b>Bill To</b>", s_label)],
        [cell("Name",  buyer_name)],
        [cell("Phone", buyer_phone)],
        [cell("GSTIN", buyer_gstin)],
    ]

    t_seller = Table(seller_rows, colWidths=[88*mm])
    t_seller.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), light_grey),
        ("BOX",           (0,0),(-1,-1), 0.5, mid_grey),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
    ]))

    t_buyer = Table(buyer_rows, colWidths=[88*mm])
    t_buyer.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), light_grey),
        ("BOX",           (0,0),(-1,-1), 0.5, mid_grey),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
    ]))

    t_parties = Table([[t_seller, Spacer(10*mm,1), t_buyer]], colWidths=[88*mm, 10*mm, 88*mm])
    t_parties.setStyle(TableStyle([("VALIGN", (0,0),(-1,-1), "TOP")]))
    story.append(t_parties)
    story.append(Spacer(1, 4*mm))

    col_w   = [6*mm, 46*mm, 14*mm, 9*mm, 9*mm, 9*mm, 16*mm, 18*mm, 16*mm, 16*mm, 17*mm]
    headers = ["#", "Product", "HSN", "GST%", "Qty", "Unit", "Rate(₹)", "Taxable(₹)", "CGST(₹)", "SGST(₹)", "Total(₹)"]
    table_data = [headers]
    for i, item in enumerate(items, 1):
        gp   = (item.get("gst_rate", 0.05) or 0) * 100
        table_data.append([
            str(i),
            Paragraph(item["product_name"], ParagraphStyle("pn", fontSize=7, fontName="Helvetica", leading=9, wordWrap="LTR")),
            item["hsn_code"],
            f"{gp:.0f}%",
            str(int(item["quantity"]) if item["quantity"] == int(item["quantity"]) else item["quantity"]),
            item["unit"],
            f"{item['unit_price']:.2f}",
            f"{item['taxable_value']:.2f}",
            f"{item['cgst_amount']:.2f}",
            f"{item['sgst_amount']:.2f}",
            f"{item['line_total']:.2f}",
        ])

    t_items = Table(table_data, colWidths=col_w, repeatRows=1)
    t_items.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  brand_blue),
        ("TEXTCOLOR",     (0,0),(-1,0),  white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 7),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("ALIGN",         (1,1),(1,-1),  "LEFT"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [white, light_grey]),
        ("GRID",          (0,0),(-1,-1), 0.25, mid_grey),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 3),
        ("RIGHTPADDING",  (0,0),(-1,-1), 3),
    ]))
    story.append(t_items)
    story.append(Spacer(1, 3*mm))

    tv   = inv["taxable_value"]
    cgst = inv["cgst_amount"]
    sgst = inv["sgst_amount"]
    tot  = inv["total_amount"]

    s_tot_lbl = ParagraphStyle("tl", fontSize=8,  fontName="Helvetica", alignment=TA_RIGHT)
    s_tot_val = ParagraphStyle("tv", fontSize=8,  fontName="Helvetica", alignment=TA_RIGHT)
    s_grand   = ParagraphStyle("gv", fontSize=11, fontName="Helvetica-Bold", alignment=TA_RIGHT, textColor=brand_blue)

    discount_amt = inv.get("discount_amt", 0) or 0
    sub_total    = inv.get("sub_total", tot)   or tot

    totals_rows = [
        [Paragraph("Taxable Value", s_tot_lbl), Paragraph(f"₹ {tv:.2f}",   s_tot_val)],
        [Paragraph("CGST",          s_tot_lbl), Paragraph(f"₹ {cgst:.2f}", s_tot_val)],
        [Paragraph("SGST",          s_tot_lbl), Paragraph(f"₹ {sgst:.2f}", s_tot_val)],
    ]
    if discount_amt > 0:
        totals_rows.append([Paragraph("Subtotal", s_tot_lbl), Paragraph(f"₹ {sub_total:.2f}", s_tot_val)])
        s_disc = ParagraphStyle("disc", fontSize=8, fontName="Helvetica-Bold", alignment=TA_RIGHT, textColor=colors.HexColor("#c62828"))
        totals_rows.append([Paragraph("Discount", s_disc), Paragraph(f"- ₹ {discount_amt:.2f}", s_disc)])
    
    totals_rows.append([Paragraph("<b>GRAND TOTAL</b>", s_grand), Paragraph(f"<b>₹ {tot:.2f}</b>", s_grand)])

    t_totals = Table(totals_rows, colWidths=[120*mm, 66*mm])
    style_cmds = [
        ("ALIGN",         (0,0),(-1,-1), "RIGHT"),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LINEABOVE",     (0,-1),(-1,-1), 1, brand_blue),
        ("LINEBELOW",     (0,-1),(-1,-1), 1, brand_blue),
        ("BACKGROUND",    (0,-1),(-1,-1), light_grey),
    ]
    t_totals.setStyle(TableStyle(style_cmds))
    story.append(t_totals)
    story.append(Spacer(1, 5*mm))

    t_footer = Table([[
        Paragraph("This is a computer-generated invoice. No signature required.", s_foot),
        Paragraph("<b>Authorised Signatory</b><br/>" + SHOP_NAME, ParagraphStyle("sig", fontSize=8, fontName="Helvetica", alignment=TA_RIGHT, leading=12)),
    ]], colWidths=[120*mm, 66*mm])
    t_footer.setStyle(TableStyle([
        ("VALIGN",     (0,0),(-1,-1), "BOTTOM"),
        ("LINEABOVE",  (1,0),(1,0),   0.5, mid_grey),
        ("TOPPADDING", (0,0),(-1,-1), 4),
    ]))
    story.append(t_footer)

    doc.build(story)
    return buffer.getvalue()
