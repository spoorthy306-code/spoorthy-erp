import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from sqlalchemy import select

from backend.app.models.company import CompanyProfile
from backend.db.session import SessionLocal


class InvoiceService:
    @staticmethod
    def generate_pdf(order, filename: str = None):
        os.makedirs("invoices", exist_ok=True)
        filename = filename or f"invoice_{order.id}.pdf"
        filepath = os.path.join("invoices", filename)

        # Load company profile (first available)
        db = SessionLocal()
        company = db.execute(select(CompanyProfile)).scalars().first()
        db.close()

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # Company header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(
            1 * cm, height - 2 * cm, company.name if company else "SPOORTHY ERP"
        )
        c.setFont("Helvetica", 10)
        address = company.address if company else "123 Business Road, Hyderabad, TG"
        gstin = company.gstin if company else "36AAAAA0000A1Z5"
        c.drawString(1 * cm, height - 2.6 * cm, address)
        c.drawString(1 * cm, height - 3.1 * cm, f"GSTIN: {gstin}")

        if company and company.logo_path and os.path.exists(company.logo_path):
            c.drawImage(
                company.logo_path,
                width - 4.5 * cm,
                height - 4.5 * cm,
                width=3 * cm,
                preserveAspectRatio=True,
            )

        # Invoice metadata
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(width - 1 * cm, height - 2 * cm, f"INVOICE: INV-{order.id}")
        c.setFont("Helvetica", 10)
        c.drawRightString(
            width - 1 * cm,
            height - 2.6 * cm,
            f"Date: {order.created_at.strftime('%Y-%m-%d')}",
        )

        # Table header
        y = height - 4 * cm
        c.line(1 * cm, y, width - 1 * cm, y)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5 * cm, y - 0.5 * cm, "Description")
        c.drawString(10 * cm, y - 0.5 * cm, "Qty")
        c.drawString(12 * cm, y - 0.5 * cm, "Rate")
        c.drawString(15 * cm, y - 0.5 * cm, "Tax")
        c.drawRightString(width - 1.5 * cm, y - 0.5 * cm, "Amount")
        c.line(1 * cm, y - 0.8 * cm, width - 1 * cm, y - 0.8 * cm)

        # Item row
        c.setFont("Helvetica", 10)
        desc = order.item_description or f"Order Item (Order ID: {order.id})"
        c.drawString(1.5 * cm, y - 1.5 * cm, desc)
        c.drawString(9.5 * cm, y - 1.5 * cm, f"{order.hsn_code or '-'}")
        c.drawString(10.5 * cm, y - 1.5 * cm, f"{float(order.quantity):.2f}")
        c.drawString(12.5 * cm, y - 1.5 * cm, f"{float(order.unit_price):.2f}")
        c.drawString(15 * cm, y - 1.5 * cm, f"{float(order.tax_amount):.2f}")
        c.drawRightString(
            width - 1.5 * cm, y - 1.5 * cm, f"{float(order.total_amount):.2f}"
        )

        # Totals
        c.line(1 * cm, y - 2.4 * cm, width - 1 * cm, y - 2.4 * cm)
        c.drawString(12 * cm, y - 3.0 * cm, "Subtotal:")
        c.drawRightString(
            width - 1.5 * cm, y - 3.0 * cm, f"{float(order.subtotal):.2f}"
        )
        c.drawString(12 * cm, y - 3.5 * cm, "Tax Amount:")
        c.drawRightString(
            width - 1.5 * cm, y - 3.5 * cm, f"{float(order.tax_amount):.2f}"
        )

        c.setFont("Helvetica-Bold", 12)
        c.drawString(12 * cm, y - 4.1 * cm, "GRAND TOTAL:")
        c.drawRightString(
            width - 1.5 * cm, y - 4.1 * cm, f"INR {float(order.total_amount):.2f}"
        )

        c.showPage()
        c.save()

        return filepath
