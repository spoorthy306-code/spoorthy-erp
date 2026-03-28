"""
pdf_invoice.py — GST Tax Invoice PDF generator for SPOORTHY ERP
Generates professional A4 invoices with ReportLab.
Usage:
    from pdf_invoice import generate_invoice_pdf
    pdf_bytes = generate_invoice_pdf(invoice_data)
    st.download_button("Download PDF", pdf_bytes, "invoice.pdf", "application/pdf")
"""

from io import BytesIO
from datetime import date, datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, KeepTogether
)
from reportlab.pdfbase.pdfmetrics import stringWidth


# ── Colours ───────────────────────────────────────────────────────────────────
DARK   = colors.HexColor("#0f172a")
BLUE   = colors.HexColor("#1d4ed8")
GREY   = colors.HexColor("#64748b")
LGREY  = colors.HexColor("#f1f5f9")
WHITE  = colors.white
GREEN  = colors.HexColor("#166534")
GREEN_BG = colors.HexColor("#dcfce7")


def _num_to_words(n: float) -> str:
    """Convert a number to Indian-English words (up to crores)."""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven",
            "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen",
            "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty",
            "Sixty", "Seventy", "Eighty", "Ninety"]

    def _two(n):
        if n < 20:
            return ones[n]
        return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")

    def _three(n):
        if n >= 100:
            return ones[n // 100] + " Hundred" + (" and " + _two(n % 100) if n % 100 else "")
        return _two(n)

    rupees = int(n)
    paise  = round((n - rupees) * 100)

    parts = []
    if rupees >= 10_000_000:
        parts.append(_three(rupees // 10_000_000) + " Crore")
        rupees %= 10_000_000
    if rupees >= 100_000:
        parts.append(_three(rupees // 100_000) + " Lakh")
        rupees %= 100_000
    if rupees >= 1_000:
        parts.append(_three(rupees // 1_000) + " Thousand")
        rupees %= 1_000
    if rupees:
        parts.append(_three(rupees))

    result = " ".join(parts).strip() if parts else "Zero"
    if paise:
        result += f" and {_two(paise)} Paise"
    return result + " Only"


def generate_invoice_pdf(invoice_data: dict) -> bytes:
    """
    Generate a professional GST Tax Invoice PDF.

    invoice_data keys:
        invoice_no, invoice_date, due_date, po_ref
        seller_name, seller_address, seller_gstin, seller_pan, seller_phone, seller_email
        seller_bank_name, seller_account_no, seller_ifsc, seller_branch
        buyer_name, buyer_address, buyer_gstin
        ship_to_name, ship_to_address (optional)
        line_items: list of dicts:
            {description, sac, qty, unit, rate, gst_pct, is_igst (bool)}
        narration (optional)
        place_of_supply (optional, default "Telangana")

    Returns raw PDF bytes.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm, bottomMargin=12*mm,
    )

    W = A4[0] - 30*mm   # usable width
    styles = getSampleStyleSheet()

    def P(text, size=8, bold=False, color=colors.black, align=TA_LEFT):
        st = ParagraphStyle(
            "x", fontSize=size, leading=size*1.35,
            textColor=color, alignment=align,
            fontName="Helvetica-Bold" if bold else "Helvetica",
        )
        return Paragraph(text, st)

    elems = []

    # ── HEADER BAR ────────────────────────────────────────────────────────────
    inv_no   = invoice_data.get("invoice_no", "")
    inv_date = invoice_data.get("invoice_date", date.today())
    due_date = invoice_data.get("due_date", "")
    po_ref   = invoice_data.get("po_ref", "")

    if isinstance(inv_date, str):
        try: inv_date = datetime.strptime(inv_date[:10], "%Y-%m-%d").date()
        except: pass
    if isinstance(due_date, str) and due_date:
        try: due_date = datetime.strptime(due_date[:10], "%Y-%m-%d").date()
        except: pass

    inv_date_str = inv_date.strftime("%d-%m-%Y") if hasattr(inv_date, "strftime") else str(inv_date)
    due_date_str = due_date.strftime("%d-%m-%Y") if hasattr(due_date, "strftime") else str(due_date)

    seller_name = invoice_data.get("seller_name", "")
    hdr_data = [[
        P(f"<b>{seller_name}</b>", size=14, bold=True, color=WHITE),
        P("<b>TAX INVOICE</b>", size=16, bold=True, color=WHITE, align=TA_RIGHT),
    ]]
    hdr_table = Table(hdr_data, colWidths=[W*0.6, W*0.4])
    hdr_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING", (0,0), (0,-1), 12),
        ("RIGHTPADDING",(1,0),(-1,-1), 12),
    ]))
    elems.append(hdr_table)
    elems.append(Spacer(1, 4*mm))

    # ── SELLER + META ─────────────────────────────────────────────────────────
    seller_addr  = invoice_data.get("seller_address", "")
    seller_gstin = invoice_data.get("seller_gstin", "")
    seller_pan   = invoice_data.get("seller_pan", "")
    seller_phone = invoice_data.get("seller_phone", "")
    seller_email = invoice_data.get("seller_email", "")

    meta_rows = [
        [P("<b>Invoice No:</b>", 8, True), P(inv_no, 8), P("<b>Invoice Date:</b>", 8, True), P(inv_date_str, 8)],
        [P("<b>Due Date:</b>", 8, True),   P(due_date_str, 8), P("<b>PO Ref:</b>", 8, True), P(po_ref, 8)],
    ]
    meta_table = Table(meta_rows, colWidths=[W*0.15, W*0.35, W*0.15, W*0.35])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LGREY),
        ("TOPPADDING",  (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))

    seller_block = [
        P(f"<b>{seller_name}</b>", 9, True, DARK),
        P(seller_addr, 8, color=GREY),
        Spacer(1, 2),
        P(f"GSTIN: <b>{seller_gstin}</b>  |  PAN: <b>{seller_pan}</b>", 8),
        P(f"Ph: {seller_phone}  |  Email: {seller_email}", 8, color=GREY),
    ]

    top_data = [[seller_block, meta_table]]
    top_table = Table(top_data, colWidths=[W*0.5, W*0.5])
    top_table.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",(0,0),(0,-1), 0),
        ("RIGHTPADDING",(-1,0),(-1,-1), 0),
    ]))
    elems.append(top_table)
    elems.append(Spacer(1, 3*mm))

    # ── BILLED TO / SHIPPED TO ────────────────────────────────────────────────
    buyer_name    = invoice_data.get("buyer_name", "")
    buyer_addr    = invoice_data.get("buyer_address", "")
    buyer_gstin   = invoice_data.get("buyer_gstin", "")
    ship_name     = invoice_data.get("ship_to_name", buyer_name)
    ship_addr     = invoice_data.get("ship_to_address", buyer_addr)
    pos           = invoice_data.get("place_of_supply", "Telangana")

    bill_data = [[
        [P("<b>Billed To</b>", 8, True, BLUE),
         P(f"<b>{buyer_name}</b>", 9, True),
         P(buyer_addr, 8, color=GREY),
         P(f"GSTIN: {buyer_gstin}", 8)],
        [P("<b>Shipped To</b>", 8, True, BLUE),
         P(f"<b>{ship_name}</b>", 9, True),
         P(ship_addr, 8, color=GREY)],
        [P("<b>Place of Supply</b>", 8, True, BLUE),
         P(pos, 9)],
    ]]
    bill_table = Table(bill_data, colWidths=[W*0.4, W*0.35, W*0.25])
    bill_table.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("BOX",    (0,0),(-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ("GRID",   (0,0),(-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND",(0,0),(-1,0), LGREY),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
    ]))
    elems.append(bill_table)
    elems.append(Spacer(1, 4*mm))

    # ── LINE ITEMS ────────────────────────────────────────────────────────────
    items = invoice_data.get("line_items", [])
    col_w = [8*mm, W*0.32, 14*mm, 14*mm, 22*mm, 22*mm, 14*mm, 18*mm, 18*mm, 20*mm]

    item_header = [
        P("<b>#</b>",8,True,WHITE,TA_CENTER),
        P("<b>Description / SAC</b>",8,True,WHITE),
        P("<b>Qty</b>",8,True,WHITE,TA_CENTER),
        P("<b>Unit</b>",8,True,WHITE,TA_CENTER),
        P("<b>Rate (₹)</b>",8,True,WHITE,TA_RIGHT),
        P("<b>Taxable (₹)</b>",8,True,WHITE,TA_RIGHT),
        P("<b>GST%</b>",8,True,WHITE,TA_CENTER),
        P("<b>CGST (₹)</b>",8,True,WHITE,TA_RIGHT),
        P("<b>SGST (₹)</b>",8,True,WHITE,TA_RIGHT),
        P("<b>Total (₹)</b>",8,True,WHITE,TA_RIGHT),
    ]

    item_rows = [item_header]
    total_taxable = 0.0
    total_cgst    = 0.0
    total_sgst    = 0.0
    total_igst    = 0.0
    is_igst_inv   = False

    for i, itm in enumerate(items, 1):
        desc    = itm.get("description", "")
        sac     = itm.get("sac", "")
        qty     = float(itm.get("qty", 1))
        unit    = itm.get("unit", "Nos")
        rate    = float(itm.get("rate", 0))
        gst_pct = float(itm.get("gst_pct", 18))
        is_igst = itm.get("is_igst", False)
        is_igst_inv = is_igst_inv or is_igst

        taxable = round(qty * rate, 2)
        half    = gst_pct / 2
        cgst    = round(taxable * half / 100, 2)
        sgst    = cgst
        igst    = round(taxable * gst_pct / 100, 2)
        line_total = taxable + (igst if is_igst else cgst + sgst)

        total_taxable += taxable
        if is_igst:
            total_igst += igst
        else:
            total_cgst += cgst
            total_sgst += sgst

        desc_cell = [P(f"<b>{desc}</b>", 8), P(f"SAC: {sac}", 7, color=GREY)]
        if is_igst:
            tax_cells = [P(f"{gst_pct}%",8,align=TA_CENTER),
                         P(f"{igst:,.2f}",8,align=TA_RIGHT),
                         P("—",8,align=TA_RIGHT),
                         P(f"{line_total:,.2f}",8,bold=True,align=TA_RIGHT)]
        else:
            tax_cells = [P(f"{gst_pct}%",8,align=TA_CENTER),
                         P(f"{cgst:,.2f}",8,align=TA_RIGHT),
                         P(f"{sgst:,.2f}",8,align=TA_RIGHT),
                         P(f"{line_total:,.2f}",8,bold=True,align=TA_RIGHT)]

        row = [
            P(str(i), 8, align=TA_CENTER),
            desc_cell,
            P(f"{qty:g}", 8, align=TA_CENTER),
            P(unit, 8, align=TA_CENTER),
            P(f"{rate:,.2f}", 8, align=TA_RIGHT),
            P(f"{taxable:,.2f}", 8, align=TA_RIGHT),
        ] + tax_cells
        item_rows.append(row)

    # Sub-total row
    grand_total = total_taxable + total_cgst + total_sgst + total_igst
    sub_row = [
        P("", 8), P("<b>Sub Total</b>", 8, True), P("", 8), P("", 8),
        P("", 8),
        P(f"{total_taxable:,.2f}", 8, True, align=TA_RIGHT),
        P("", 8),
        P(f"{total_cgst:,.2f}" if not is_igst_inv else f"{total_igst:,.2f}", 8, True, align=TA_RIGHT),
        P(f"{total_sgst:,.2f}" if not is_igst_inv else "—", 8, True, align=TA_RIGHT),
        P(f"{grand_total:,.2f}", 8, True, align=TA_RIGHT),
    ]
    item_rows.append(sub_row)

    items_table = Table(item_rows, colWidths=col_w, repeatRows=1)
    items_ts = TableStyle([
        # Header
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("TOPPADDING", (0,0), (-1,0), 6),
        ("BOTTOMPADDING",(0,0),(-1,0), 6),
        # Rows
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,1), (-1,-2), 4),
        ("BOTTOMPADDING",(0,1),(-1,-2), 4),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID",   (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        # Alternating rows
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [WHITE, LGREY]),
        # Sub-total row
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#dbeafe")),
        ("FONTNAME",   (0,-1), (-1,-1), "Helvetica-Bold"),
        ("TOPPADDING", (0,-1), (-1,-1), 6),
        ("BOTTOMPADDING",(0,-1),(-1,-1), 6),
    ])
    items_table.setStyle(items_ts)
    elems.append(items_table)
    elems.append(Spacer(1, 4*mm))

    # ── TOTALS + BANK DETAILS ─────────────────────────────────────────────────
    bank_name = invoice_data.get("seller_bank_name", "")
    bank_acc  = invoice_data.get("seller_account_no", "")
    bank_ifsc = invoice_data.get("seller_ifsc", "")
    bank_branch = invoice_data.get("seller_branch", "")

    in_words = _num_to_words(grand_total)

    totals_data = [
        [P("<b>Taxable Amount</b>", 8, True), P(f"₹{total_taxable:,.2f}", 8, bold=True, align=TA_RIGHT)],
        [P("CGST" if not is_igst_inv else "IGST", 8), P(f"₹{total_cgst if not is_igst_inv else total_igst:,.2f}", 8, align=TA_RIGHT)],
    ]
    if not is_igst_inv:
        totals_data.append([P("SGST", 8), P(f"₹{total_sgst:,.2f}", 8, align=TA_RIGHT)])
    totals_data.append([
        P("<b>Grand Total</b>", 10, True, DARK),
        P(f"<b>₹{grand_total:,.2f}</b>", 10, True, DARK, TA_RIGHT)
    ])

    totals_table = Table(totals_data, colWidths=[W*0.6, W*0.4])
    totals_table.setStyle(TableStyle([
        ("TOPPADDING",  (0,0),(-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING", (0,0),(0,-1), 6),
        ("RIGHTPADDING",(1,0),(-1,-1), 6),
        ("LINEABOVE", (0,-1), (-1,-1), 1, DARK),
        ("BACKGROUND", (0,-1),(-1,-1), LGREY),
        ("BOX", (0,0),(-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))

    bank_lines = [
        P("<b>Bank Details</b>", 8, True, BLUE),
        P(f"Bank: <b>{bank_name}</b>", 8),
        P(f"A/C No: <b>{bank_acc}</b>", 8),
        P(f"IFSC: <b>{bank_ifsc}</b>  |  Branch: {bank_branch}", 8),
        Spacer(1, 4),
        P(f"<b>Amount in Words:</b>", 8, True),
        P(f"Indian Rupees {in_words}", 8, color=GREY),
    ]

    sign_lines = [
        Spacer(1, 20),
        HRFlowable(width=60*mm, thickness=0.5, color=DARK),
        P("<b>Authorised Signatory</b>", 8, True),
        P(seller_name, 8, color=GREY),
    ]

    bottom_data = [[bank_lines, totals_table, sign_lines]]
    bottom_table = Table(bottom_data, colWidths=[W*0.36, W*0.38, W*0.26])
    bottom_table.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",(0,0),(0,-1), 0),
        ("RIGHTPADDING",(-1,0),(-1,-1), 0),
    ]))
    elems.append(bottom_table)

    # ── NARRATION ─────────────────────────────────────────────────────────────
    narration = invoice_data.get("narration", "")
    if narration:
        elems.append(Spacer(1, 3*mm))
        elems.append(P(f"<i>Note: {narration}</i>", 8, color=GREY))

    elems.append(Spacer(1, 4*mm))

    # ── FOOTER BAR ────────────────────────────────────────────────────────────
    footer_text = invoice_data.get("footer_text", "")
    if not footer_text:
        footer_text = (
            f"{seller_name} | GSTIN: {seller_gstin} | PAN: {seller_pan} | "
            f"Ph: {seller_phone} | {seller_email}"
        )
    ftr_data = [[P(footer_text, 7, color=WHITE, align=TA_CENTER)]]
    ftr_table = Table(ftr_data, colWidths=[W])
    ftr_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), DARK),
        ("TOPPADDING", (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    elems.append(ftr_table)

    doc.build(elems)
    return buf.getvalue()
