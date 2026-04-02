# ════════════════════════════════════════════════════════════════════════════════
# SPOORTHY ERP
# ui/app.py — Complete Streamlit Web Application
# ════════════════════════════════════════════════════════════════════════════════
# Run with:  streamlit run ui/app.py
# ════════════════════════════════════════════════════════════════════════════════
# Pages:
#   1. Dashboard          — KPI cards, charts
#   2. Voucher Entry      — All 16 voucher types
#   3. PDF / DMS Upload   — Upload invoice, auto-extract
#   4. Masters            — Ledgers, Parties, Stock Items
#   5. Reports            — Trial Balance, P&L, BS, GST
#   6. Bank Reconciliation
#   7. Fixed Assets
#   8. Payroll
# ════════════════════════════════════════════════════════════════════════════════

import sys, os, json, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

from db.schema  import SessionLocal, Ledger, AccountGroup, Voucher, Transaction, \
                        VoucherType, Party, Document, StockItem, StockUnit, \
                        Currency, BankReconciliation, FixedAsset, Employee, SystemConfig, \
                        Company, Role, AppUser
from db.seed    import seed_all
from quantum_ui   import render_quantum_accounting, render_quantum_finance
from settings_ui  import render_settings_page
from payroll_ui   import render_payroll_page

# backend with reusable invoice generation may rely on backend models and heavy imports.
# Import safely to avoid total app failure in development or when package dependencies are incomplete.
try:
    from backend.app.services.invoice_service import InvoiceService
except Exception as _exc:
    InvoiceService = None
    print(f"⚠️ Warning: backend InvoiceService import failed: {_exc}")

try:
    from backend.app.models.order import Order, OrderStatus
except Exception as _exc:
    Order = None
    OrderStatus = None
    print(f"⚠️ Warning: backend Order model import failed: {_exc}")

try:
    from backend.app.models.company import CompanyProfile
except Exception as _exc:
    CompanyProfile = None
    print(f"⚠️ Warning: backend CompanyProfile model import failed: {_exc}")

import hashlib
from typing import Any


def _f(v: Any) -> float:
    """Cast any SQLAlchemy Numeric/Decimal column value to float; returns 0.0 for None."""
    return 0.0 if v is None else float(v)


def generate_invoice_pdf(data: dict) -> bytes:
    """Fallback invoice PDF — returns a minimal valid PDF with placeholder content."""
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    out.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    out.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n")
    out.write(b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 72 720 Td (Invoice PDF placeholder) Tj ET\nendstream\nendobj\n")
    out.write(b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000118 00000 n \n0000000191 00000 n \ntrailer\n<< /Root 1 0 R /Size 5 >>\nstartxref\n268\n%%EOF")
    return out.getvalue()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPOORTHY ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apple-style CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Helvetica Neue', Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ── Sidebar Apple-style ── */
    [data-testid="stSidebar"] {
        background: #f5f5f7 !important;
        border-right: 1px solid #d2d2d7;
    }
    [data-testid="stSidebar"] .stMarkdown p { color: #1d1d1f; }

    /* Nav button style — Apple SF Symbols look */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
        padding: 10px 14px;
        border-radius: 10px;
        cursor: pointer;
        font-size: 0.92rem;
        font-weight: 500;
        color: #1d1d1f;
        background: transparent;
        border: none;
        margin-bottom: 2px;
        transition: background 0.15s ease;
        text-align: left;
    }
    .nav-btn:hover { background: #e8e8ed; }
    .nav-btn.active {
        background: #ffffff;
        color: #007aff;
        box-shadow: 0 1px 4px rgba(0,0,0,0.10);
    }
    .nav-icon {
        font-size: 1.15rem;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 7px;
        flex-shrink: 0;
    }
    .nav-section-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 14px 14px 4px 14px;
    }

    /* ── Main content ── */
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1d1d1f;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #86868b;
        font-size: 0.88rem;
        font-weight: 400;
        margin-top: 2px;
    }

    /* ── Apple-style metric cards ── */
    .metric-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #e8e8ed;
    }
    .metric-label {
        font-size: 0.72rem;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1d1d1f;
        letter-spacing: -0.5px;
    }
    .metric-delta { font-size: 0.8rem; margin-top: 4px; font-weight: 500; }
    .positive { color: #34c759; }
    .negative { color: #ff3b30; }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1d1d1f;
        margin: 1.5rem 0 0.75rem 0;
    }

    /* ── Apple-style buttons ── */
    .stButton > button {
        background: #007aff;
        color: white;
        border: none;
        border-radius: 980px;
        padding: 0.5rem 1.4rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: #0071e3;
        border: none;
        transform: scale(1.01);
    }
    .stButton > button:active { transform: scale(0.98); }

    /* ── Streamlit tabs Apple-style ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #f5f5f7;
        border-radius: 12px;
        padding: 4px;
        gap: 2px;
        border: none;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        padding: 7px 16px;
        font-size: 0.87rem;
        font-weight: 500;
        color: #86868b;
        background: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #1d1d1f !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.12);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border-radius: 10px !important;
        border: 1.5px solid #d2d2d7 !important;
        font-size: 0.9rem;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #007aff !important;
        box-shadow: 0 0 0 3px rgba(0,122,255,0.15) !important;
    }

    /* ── Data tables ── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* ── Badges ── */
    .badge-posted   { background:#d1fae5; color:#065f46; padding:3px 10px; border-radius:980px; font-size:0.72rem; font-weight:600; }
    .badge-draft    { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:980px; font-size:0.72rem; font-weight:600; }
    .badge-reversed { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:980px; font-size:0.72rem; font-weight:600; }

    /* ── Dividers ── */
    hr { border-color: #e8e8ed !important; }

    /* Hide Streamlit default menu chrome */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ── Apple sidebar nav buttons ── */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #1d1d1f !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 9px 12px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        margin-bottom: 1px !important;
        box-shadow: none !important;
        transform: none !important;
        transition: background 0.12s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #e8e8ed !important;
        color: #1d1d1f !important;
        transform: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:focus,
    [data-testid="stSidebar"] .stButton > button:active {
        background: #dcdce0 !important;
        box-shadow: none !important;
        transform: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_resource
def init_db():
    try:
        seed_all()
    except Exception as e:
        # On first run, schema may be stale or incomplete; skip seed failure to keep UI available.
        st.warning(f"⚠️ Database seed error (non-blocking): {e}")
        print(f"⚠️ Database seed error (non-blocking): {e}")
    return True

init_db()


def get_db():
    return SessionLocal()


def fmt_inr(val):
    try:
        val = float(val)
        return f"₹{val:,.2f}"
    except:
        return "₹0.00"


def fmt_date(d) -> str:
    """Return date as DD-MM-YYYY string. Accepts date, datetime, or str."""
    if d is None:
        return ""
    if isinstance(d, str):
        # parse ISO yyyy-mm-dd
        try:
            d = datetime.strptime(d[:10], "%Y-%m-%d").date()
        except Exception:
            return d
    try:
        return d.strftime("%d-%m-%Y")
    except Exception:
        return str(d)


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_ledger_balance(db, ledger_code: str) -> float:
    led = db.query(Ledger).filter_by(code=ledger_code).first()
    if not led:
        return 0.0
    txns = db.query(Transaction).join(Voucher).filter(
        Transaction.ledger_id == led.id,
        Voucher.status == "POSTED"
    ).all()
    dr = sum(_f(t.debit) for t in txns)
    cr = sum(_f(t.credit) for t in txns)
    opening = _f(led.opening_balance)
    if led.nature == "Dr":
        return opening + dr - cr
    else:
        return opening + cr - dr


# ── Indian GST State Code Table ───────────────────────────────────────────────
GST_STATE_CODES = {
    "01":"Jammu & Kashmir",   "02":"Himachal Pradesh",  "03":"Punjab",
    "04":"Chandigarh",        "05":"Uttarakhand",        "06":"Haryana",
    "07":"Delhi",             "08":"Rajasthan",          "09":"Uttar Pradesh",
    "10":"Bihar",             "11":"Sikkim",             "12":"Arunachal Pradesh",
    "13":"Nagaland",          "14":"Manipur",            "15":"Mizoram",
    "16":"Tripura",           "17":"Meghalaya",          "18":"Assam",
    "19":"West Bengal",       "20":"Jharkhand",          "21":"Odisha",
    "22":"Chhattisgarh",      "23":"Madhya Pradesh",     "24":"Gujarat",
    "25":"Daman & Diu",       "26":"Dadra & Nagar Haveli","27":"Maharashtra",
    "28":"Andhra Pradesh (old)","29":"Karnataka",        "30":"Goa",
    "31":"Lakshadweep",       "32":"Kerala",             "33":"Tamil Nadu",
    "34":"Puducherry",        "35":"Andaman & Nicobar",  "36":"Telangana",
    "37":"Andhra Pradesh",    "38":"Ladakh",
}

_PAN_BIZ_TYPE = {
    "P":"Proprietorship", "F":"Firm / LLP", "C":"Company / Pvt Ltd",
    "H":"HUF",            "A":"AOP / BOI",   "T":"Trust",
    "B":"Body of Individuals", "L":"Local Authority",
    "J":"Artificial Juridical Person", "G":"Govt Department",
}


def lookup_gstin(gstin: str, api_key: str = "") -> dict:
    """
    Validate GSTIN and fetch taxpayer details.
    1. Offline decode (always available) — state, PAN, business type.
    2. If api_key supplied, call API Setu GSTIN endpoint for live details.
    """
    import re
    gstin = gstin.strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
    if not re.match(pattern, gstin):
        return {"error": "Invalid GSTIN — must be 15 chars, e.g. 36AABCS1234C1ZP"}

    state_code = gstin[:2]
    pan        = gstin[2:12]
    biz_type   = _PAN_BIZ_TYPE.get(pan[3], "Other")

    info = {
        "gstin":       gstin,
        "pan":         pan,
        "state_code":  state_code,
        "state":       GST_STATE_CODES.get(state_code, "Unknown"),
        "biz_type":    biz_type,
        "legal_name":  "",
        "trade_name":  "",
        "address":     "",
        "city":        "",
        "pincode":     "",
        "status":      "",
        "reg_date":    "",
        "source":      "Offline (GSTIN decode)",
    }

    if api_key:
        try:
            import requests as _req
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            url  = f"https://apisetu.gov.in/api/masterdata/gstin/{gstin}"
            resp = _req.get(url, headers={
                "X-APISETU-APIKEY": api_key,
                "Accept": "application/json",
            }, timeout=8, verify=True)
            if resp.status_code == 200:
                data = resp.json()
                addr = data.get("pradr", {}).get("addr", {})
                info.update({
                    "legal_name":  data.get("lgnm", ""),
                    "trade_name":  data.get("tradeNam", ""),
                    "status":      data.get("sts", ""),
                    "reg_date":    data.get("rgdt", ""),
                    "biz_type":    data.get("dty", biz_type),
                    "address":     data.get("pradr", {}).get("adr", ""),
                    "city":        addr.get("dst", addr.get("loc", "")),
                    "pincode":     addr.get("pncd", ""),
                    "source":      "GST Portal (API Setu)",
                })
            else:
                info["api_error"] = f"API returned {resp.status_code}: {resp.text[:120]}"
        except Exception as e:
            info["api_error"] = str(e)

    return info


def next_voucher_no(db, vtype_code: str) -> str:
    vt = db.query(VoucherType).filter_by(code=vtype_code).first()
    if not vt:
        return f"SPRY/{vtype_code}/000001"
    vt.current_seq = (vt.current_seq or 0) + 1
    db.flush()
    fy  = "2025-26"
    return f"SPRY/{vt.prefix}/{fy}/{vt.current_seq:06d}"


def post_double_entry(db, voucher_no: str, vtype_code: str, vdate: date,
                       narration: str, entries: list, party_id=None,
                       ref_no="", taxable=0.0, tax=0.0, total=0.0,
                       inter_state=False, doc_id=None) -> Voucher:
    """Core double-entry post function."""
    dr_total = sum(float(e.get("debit",  0)) for e in entries)
    cr_total = sum(float(e.get("credit", 0)) for e in entries)
    if round(dr_total, 2) != round(cr_total, 2):
        raise ValueError(f"Unbalanced: Dr={dr_total:.2f} Cr={cr_total:.2f}")

    vt    = db.query(VoucherType).filter_by(code=vtype_code).first()
    fy    = "2025-26"

    v = Voucher(
        voucher_no      = voucher_no,
        voucher_type_id = vt.id if vt else 1,
        voucher_date    = vdate,
        fiscal_year     = fy,
        party_id        = party_id,
        narration       = narration,
        ref_no          = ref_no,
        taxable_amount  = taxable,
        tax_amount      = tax,
        total_amount    = total or dr_total,
        status          = "POSTED",
        is_inter_state  = inter_state,
        doc_id          = doc_id,
    )
    db.add(v)
    db.flush()

    for e in entries:
        led = db.query(Ledger).filter_by(code=e["ledger_code"]).first()
        if not led:
            db.rollback()
            raise ValueError(f"Ledger not found: {e['ledger_code']}. Voucher not posted.")
        t = Transaction(
            voucher_id  = v.id,
            ledger_id   = led.id,
            debit       = float(e.get("debit",  0)),
            credit      = float(e.get("credit", 0)),
            narration   = e.get("narration", narration),
            cost_centre = e.get("cost_centre",""),
        )
        db.add(t)

    db.commit()
    return v


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # ── App logo / wordmark ──────────────────────────────────────────────────
    st.markdown("""
    <div style='padding: 1.2rem 0.5rem 0.8rem 0.5rem;'>
        <div style='display:flex; align-items:center; gap:10px;'>
            <div style='background:#007aff; border-radius:12px; width:38px; height:38px;
                        display:flex; align-items:center; justify-content:center;
                        font-size:1.3rem; flex-shrink:0;'>⚡</div>
            <div>
                <div style='font-size:1rem; font-weight:700; color:#1d1d1f; letter-spacing:-0.3px;'>SPOORTHY ERP</div>
                <div style='font-size:0.68rem; color:#86868b; font-weight:500;'>v2.0 · FY 2025-26</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px; background:#d2d2d7; margin:0 0 8px 0;"></div>', unsafe_allow_html=True)

    # ── Nav items definition ─────────────────────────────────────────────────
    _NAV = [
        ("OVERVIEW",    None),
        ("🏠", "Dashboard",              "Dashboard"),
        ("TRANSACTIONS", None),
        ("📝", "Voucher Entry",          "Voucher Entry"),
        ("📄", "DMS / PDF Upload",       "DMS / PDF Upload"),
        ("MASTERS",     None),
        ("🗄️", "Masters",               "Masters"),
        ("FINANCE",     None),
        ("📊", "Reports",               "Reports"),
        ("🏦", "Bank Reconciliation",   "Bank Reconciliation"),
        ("🏭", "Fixed Assets",          "Fixed Assets"),
        ("👥", "Payroll",               "Payroll"),
        ("ADVANCED",    None),
        ("⚛️", "Quantum Accounting",   "Quantum Accounting"),
        ("💹", "Quantum Finance",       "Quantum Finance"),
        ("SETTINGS",    None),
        ("⚙️", "Organisation Settings","Organisation Settings"),
    ]

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    for item in _NAV:
        if item[1] is None:
            # section label
            st.markdown(f'<div class="nav-section-label">{item[0]}</div>', unsafe_allow_html=True)
        else:
            icon, label, key = item
            is_active = st.session_state.page == key
            active_cls = "active" if is_active else ""
            icon_bg = "background:#e8f0fe;" if is_active else "background:#e8e8ed;"
            icon_color = "color:#007aff;" if is_active else "color:#1d1d1f;"
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
            ):
                st.session_state.page = key
                st.rerun()

    page = st.session_state.page

    # Highlight the active nav button via injected CSS targeting its key
    _active_key = f"nav_{page}"
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"][kind="secondary"]:has(+ * [key="{_active_key}"]),
    button[data-testid="baseButton-secondary"][aria-label*="{page}"] {{
        background: #ffffff !important;
        color: #007aff !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.10) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px; background:#d2d2d7; margin:12px 0 8px 0;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='padding:0 4px; font-size:0.72rem; color:#86868b;'>
        SPOORTHY Group · Hyderabad<br>© 2026 All rights reserved
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

if "Dashboard" in page:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    co_name = "Milvian Technologies Pvt Ltd"
    db = get_db()
    try:
        co = db.query(Company).first()
        if co: co_name = co.name
    except: pass
    finally:
        db.close()

    db = get_db()
    try:
        st.markdown(f'<div class="main-title">⚡ Financial Dashboard</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-title">{co_name} &nbsp;·&nbsp; FY 2025-26 &nbsp;·&nbsp; As on {fmt_date(date.today())}</div>', unsafe_allow_html=True)
        st.markdown("---")

        # ── Gather all ledger data ────────────────────────────────────────────
        def ledger_bal(code):
            return get_ledger_balance(db, code)

        cash_bal  = ledger_bal("CASH01") + ledger_bal("CASH02")
        bank_bal  = ledger_bal("BANK01") + ledger_bal("BANK02")
        debtors   = ledger_bal("SUN001")
        creditors = ledger_bal("SUP001")

        # Income / expense totals
        all_leds = db.query(Ledger).filter_by(is_active=True).all()
        total_income = total_expense = total_salaries = total_purchases = 0.0
        for led in all_leds:
            txns = db.query(Transaction).join(Voucher).filter(
                Transaction.ledger_id == led.id, Voucher.status == "POSTED"
            ).all()
            dr = sum(_f(t.debit) for t in txns)
            cr = sum(_f(t.credit) for t in txns)
            ob_dr = _f(led.opening_balance) if str(led.opening_type).upper() == "DR" else 0.0
            ob_cr = _f(led.opening_balance) if str(led.opening_type).upper() == "CR" else 0.0
            bal = abs((dr + ob_dr) - (cr + ob_cr))
            grp = db.query(AccountGroup).filter_by(id=led.group_id).first()
            if grp is None:
                continue
            grp_type = str(grp.group_type or "").upper()
            if grp_type == "INCOME":
                total_income += bal
            if grp_type == "EXPENSE":
                total_expense += bal
            if str(led.code) == "IE001":
                total_salaries = bal
            if str(led.code) == "PUR001":
                total_purchases = bal

        net_profit    = total_income - total_expense
        gross_profit  = total_income - total_purchases
        gst_payable   = ledger_bal("CGST_O_18") + ledger_bal("SGST_O_18") \
                      - ledger_bal("CGST_I_18") - ledger_bal("SGST_I_18")
        tds_payable   = abs(ledger_bal("TDS_192"))
        pf_payable    = abs(ledger_bal("PF_EMP"))
        total_emp     = db.query(Employee).filter_by(is_active=True).count()

        # ── ROW 1 — KPI cards ─────────────────────────────────────────────────
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("🏦 Bank Balance",    fmt_inr(bank_bal))
        k2.metric("💵 Cash",            fmt_inr(cash_bal))
        k3.metric("📤 Receivables",     fmt_inr(debtors),
                  delta="Due" if debtors > 0 else "NIL", delta_color="inverse" if debtors > 0 else "off")
        k4.metric("📥 Payables",        fmt_inr(creditors))
        k5.metric("📊 Revenue",         fmt_inr(total_income))
        k6.metric("👥 Employees",       str(total_emp))

        st.markdown("")

        k7, k8, k9, k10 = st.columns(4)
        k7.metric("Gross Profit",       fmt_inr(gross_profit),
                  delta=f"{gross_profit/total_income*100:.1f}% margin" if total_income else "—")
        k8.metric("Net Profit / Loss",  fmt_inr(abs(net_profit)),
                  delta="Loss" if net_profit < 0 else "Profit",
                  delta_color="inverse" if net_profit < 0 else "normal")
        k9.metric("GST Payable",        fmt_inr(gst_payable))
        k10.metric("TDS Payable",       fmt_inr(tds_payable))

        st.markdown("---")

        # ── ROW 2 — Revenue vs Expenses bar  +  Expense breakdown donut ──────
        c1, c2 = st.columns([3, 2])

        with c1:
            st.markdown("#### Revenue vs Expenses — FY 2025-26")

            # Month-wise from vouchers
            months_order = ["Apr-25","May-25","Jun-25","Jul-25","Aug-25","Sep-25",
                            "Oct-25","Nov-25","Dec-25","Jan-26","Feb-26","Mar-26"]
            rev_by_month  = {m: 0.0 for m in months_order}
            exp_by_month  = {m: 0.0 for m in months_order}

            for led in all_leds:
                grp = db.query(AccountGroup).filter_by(id=led.group_id).first()
                if not grp or grp.group_type not in ("INCOME","EXPENSE"): continue
                txns = db.query(Transaction).join(Voucher).filter(
                    Transaction.ledger_id == led.id,
                    Voucher.status == "POSTED"
                ).all()
                for t in txns:
                    v = db.query(Voucher).filter_by(id=t.voucher_id).first()
                    if not v: continue
                    vd = v.voucher_date
                    if hasattr(vd, "strftime"):
                        mkey = vd.strftime("%b-%y").capitalize()
                        # normalise to e.g. "Feb-26"
                        mkey = vd.strftime("%b") + "-" + vd.strftime("%y")
                    else:
                        continue
                    if mkey not in rev_by_month:
                        continue
                    grp_type = str(grp.group_type or "").upper()
                    credit_amount = _f(t.credit)
                    debit_amount = _f(t.debit)

                    if grp_type == "INCOME":
                        amt = credit_amount
                        rev_by_month[mkey] += amt
                    else:
                        amt = debit_amount
                        exp_by_month[mkey] += amt

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name="Revenue", x=months_order, y=[rev_by_month[m] for m in months_order],
                marker_color="#3b82f6", text=[f"₹{v/1e5:.1f}L" if v else "" for v in [rev_by_month[m] for m in months_order]],
                textposition="outside"
            ))
            fig_bar.add_trace(go.Bar(
                name="Expenses", x=months_order, y=[exp_by_month[m] for m in months_order],
                marker_color="#f87171", text=[f"₹{v/1e5:.1f}L" if v else "" for v in [exp_by_month[m] for m in months_order]],
                textposition="outside"
            ))
            fig_bar.update_layout(
                barmode="group", height=340,
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(tickformat=",.0f", gridcolor="#f1f5f9"),
                xaxis=dict(gridcolor="#f1f5f9"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.markdown("#### Expense Breakdown")

            exp_labels, exp_values, exp_colors = [], [], []
            color_palette = ["#3b82f6","#f87171","#fbbf24","#34d399","#a78bfa","#fb923c","#60a5fa"]
            for i, led in enumerate(all_leds):
                grp = db.query(AccountGroup).filter_by(id=led.group_id).first()
                grp_type = str(grp.group_type or "").upper() if grp else ""
                if grp is None or grp_type != "EXPENSE":
                    continue
                txns = db.query(Transaction).join(Voucher).filter(
                    Transaction.ledger_id == led.id, Voucher.status == "POSTED"
                ).all()
                amt = sum(_f(t.debit) for t in txns)
                if amt > 0.0:
                    exp_labels.append(led.name)
                    exp_values.append(amt)
                    exp_colors.append(color_palette[len(exp_labels) % len(color_palette)])

            if exp_values:
                fig_donut = go.Figure(go.Pie(
                    labels=exp_labels, values=exp_values,
                    hole=0.55,
                    marker_colors=exp_colors,
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
                ))
                fig_donut.add_annotation(
                    text=f"₹{total_expense/1e5:.1f}L<br>Total",
                    x=0.5, y=0.5, font_size=13, showarrow=False,
                )
                fig_donut.update_layout(
                    height=340, margin=dict(l=0, r=0, t=20, b=0),
                    showlegend=True,
                    legend=dict(orientation="v", font_size=10),
                    paper_bgcolor="white",
                )
                st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("---")

        # ── ROW 3 — Cash Flow waterfall  +  Statutory payables gauge ─────────
        c3, c4 = st.columns([3, 2])

        with c3:
            st.markdown("#### Cash Flow Waterfall")

            wf_labels  = ["Opening Balance", "Capital Infusion", "Sales Receipts",
                          "Payroll (Feb)", "Payroll (Mar)", "Asset Purchase", "Closing Balance"]
            wf_values  = [0, 5000000, 784700+240000+160000,
                          -get_ledger_balance(db, "BANK01") * 0,  # placeholder
                          0, 0, 0]

            # Build from actual bank transactions
            bank_led = db.query(Ledger).filter_by(code="BANK01").first()
            if bank_led:
                bank_txns = db.query(Transaction).join(Voucher).filter(
                    Transaction.ledger_id == bank_led.id,
                    Voucher.status == "POSTED"
                ).order_by(Voucher.voucher_date).all()

                # Group by voucher narration category
                inflows  = {}
                outflows = {}
                for t in bank_txns:
                    v = db.query(Voucher).filter_by(id=t.voucher_id).first()
                    narr = (v.narration or "Other") if v else "Other"
                    key = "Capital" if "capital" in narr.lower() or "Capital" in narr \
                          else "Sales / Receipts" if any(x in narr for x in ["Receipt","Sales","INV"]) \
                          else "Payroll" if "Payroll" in narr or "payroll" in narr \
                          else "Asset Purchase" if "Asset" in narr or "Computers" in narr \
                          else "Other"
                    dr = _f(t.debit)
                    cr = _f(t.credit)
                    if dr: inflows[key]  = inflows.get(key, 0)  + dr
                    if cr: outflows[key] = outflows.get(key, 0) + cr

                wf_x, wf_y, wf_measure, wf_text = ["Opening (01-Apr-25)"], [0], ["absolute"], ["₹0"]
                for k, v in inflows.items():
                    wf_x.append(f"+ {k}")
                    wf_y.append(v)
                    wf_measure.append("relative")
                    wf_text.append(f"₹{v/1e5:.1f}L")
                for k, v in outflows.items():
                    wf_x.append(f"- {k}")
                    wf_y.append(-v)
                    wf_measure.append("relative")
                    wf_text.append(f"₹{v/1e5:.1f}L")
                wf_x.append("Closing Balance")
                wf_y.append(sum(wf_y))
                wf_measure.append("total")
                wf_text.append(fmt_inr(bank_bal + cash_bal))

                fig_wf = go.Figure(go.Waterfall(
                    name="Cash Flow", orientation="v",
                    measure=wf_measure, x=wf_x, y=wf_y, text=wf_text,
                    textposition="outside",
                    increasing=dict(marker_color="#34d399"),
                    decreasing=dict(marker_color="#f87171"),
                    totals=dict(marker_color="#3b82f6"),
                    connector=dict(line=dict(color="#94a3b8", width=1, dash="dot")),
                ))
                fig_wf.update_layout(
                    height=340, margin=dict(l=0, r=0, t=20, b=40),
                    plot_bgcolor="white", paper_bgcolor="white",
                    yaxis=dict(tickformat=",.0f", gridcolor="#f1f5f9"),
                    showlegend=False,
                )
                st.plotly_chart(fig_wf, use_container_width=True)

        with c4:
            st.markdown("#### Statutory Payables")

            stat_labels = ["TDS u/s 192", "PF (Emp 12%)", "Output GST", "ESI", "TDS 194C"]
            stat_values = [
                abs(ledger_bal("TDS_192")),
                abs(ledger_bal("PF_EMP")),
                abs(ledger_bal("CGST_O_18")) + abs(ledger_bal("SGST_O_18")),
                abs(ledger_bal("ESI_EMP")),
                abs(ledger_bal("TDS_194C")),
            ]
            stat_colors = ["#f87171","#fbbf24","#3b82f6","#34d399","#a78bfa"]

            fig_stat = go.Figure(go.Bar(
                x=stat_values, y=stat_labels, orientation="h",
                marker_color=stat_colors,
                text=[fmt_inr(v) for v in stat_values],
                textposition="auto",
                hovertemplate="%{y}: ₹%{x:,.0f}<extra></extra>",
            ))
            fig_stat.update_layout(
                height=340, margin=dict(l=0, r=10, t=20, b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(tickformat=",.0f", gridcolor="#f1f5f9"),
                yaxis=dict(gridcolor="#f1f5f9"),
                showlegend=False,
            )
            st.plotly_chart(fig_stat, use_container_width=True)

        st.markdown("---")

        # ── ROW 4 — Recent vouchers  +  Payroll summary ───────────────────────
        c5, c6 = st.columns([3, 2])

        with c5:
            st.markdown("#### Recent Transactions")
            recent = db.query(Voucher).filter_by(status="POSTED")\
                       .order_by(Voucher.voucher_date.desc()).limit(12).all()
            if recent:
                rows = []
                for v in recent:
                    vt = db.query(VoucherType).filter_by(id=v.voucher_type_id).first()
                    tag = str(vt.code) if vt and vt.code is not None else "JV"
                    badge_color = {
                        "SINV":"#dcfce7","PINV":"#fef9c3","RV":"#dbeafe",
                        "PV":"#fee2e2","PYRL":"#f3e8ff","JV":"#f1f5f9"
                    }.get(tag, "#f1f5f9")
                    rows.append({
                        "Date":    fmt_date(v.voucher_date),
                        "Voucher": v.voucher_no,
                        "Type":    tag,
                        "Narration": (v.narration or "")[:45],
                        "Amount":  fmt_inr(v.total_amount),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True,
                             hide_index=True, height=320)

        with c6:
            st.markdown("#### Payroll Summary")
            payroll_vouchers = db.query(Voucher).filter(
                Voucher.voucher_no.like("%PYRL%"),
                Voucher.status == "POSTED"
            ).order_by(Voucher.voucher_date).all()

            if payroll_vouchers:
                pr_months = [v.narration.replace("Payroll — ","") for v in payroll_vouchers]
                pr_amounts = [_f(v.total_amount) for v in payroll_vouchers]

                fig_pr = go.Figure(go.Bar(
                    x=pr_months, y=pr_amounts,
                    marker_color=["#3b82f6","#6366f1"],
                    text=[fmt_inr(a) for a in pr_amounts],
                    textposition="outside",
                ))
                fig_pr.update_layout(
                    height=200, margin=dict(l=0, r=0, t=10, b=0),
                    plot_bgcolor="white", paper_bgcolor="white",
                    yaxis=dict(tickformat=",.0f", gridcolor="#f1f5f9", showticklabels=False),
                    showlegend=False,
                )
                st.plotly_chart(fig_pr, use_container_width=True)

                # Payroll KPIs
                total_pr = sum(pr_amounts)
                p1, p2 = st.columns(2)
                p1.metric("Total Payroll (FY)", fmt_inr(total_pr))
                p2.metric("Avg / Month", fmt_inr(total_pr / len(pr_amounts)))

                emp_count = db.query(Employee).filter(
                    Employee.is_active == True, Employee.gross_salary > 0
                ).count()
                p3, p4 = st.columns(2)
                p3.metric("Active Employees", str(total_emp))
                p4.metric("Payroll Months", str(len(payroll_vouchers)))

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VOUCHER ENTRY
# ═══════════════════════════════════════════════════════════════════════════════

elif "Voucher Entry" in page:
    st.markdown('<div class="main-title">📝 Voucher Entry</div>', unsafe_allow_html=True)
    st.markdown("---")

    db = get_db()
    try:
        all_ledgers = db.query(Ledger).filter_by(is_active=True).order_by(Ledger.name).all()
        led_options = {f"{l.code} — {l.name}": l.code for l in all_ledgers}

        vtype = st.selectbox("Voucher Type", [
            "Payment (PV)", "Receipt (RV)", "Journal (JV)", "Contra (CV)",
            "Purchase Invoice (PINV)", "Sales Invoice (SINV)",
            "Purchase Return (PCNV)", "Sales Return (SCNV)",
            "Debit Note (DN)", "Credit Note (CN)",
        ])

        col1, col2 = st.columns(2)
        with col1:
            vdate   = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        with col2:
            narration = st.text_input("Narration")

        ref_no = st.text_input("Reference No. (PO / Invoice No.)")

        # ── Payment / Receipt ────────────────────────────────────────────────
        if vtype in ("Payment (PV)", "Receipt (RV)"):
            col1, col2, col3 = st.columns(3)
            with col1:
                party_led = st.selectbox("Party / Expense Ledger", list(led_options.keys()), key="pr_party")
            with col2:
                bank_led  = st.selectbox("Bank / Cash Ledger",     list(led_options.keys()), key="pr_bank")
            with col3:
                amount    = st.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f")

            tds_col1, tds_col2 = st.columns(2)
            with tds_col1:
                tds_led = st.selectbox("TDS Ledger (optional)", ["— None —"] + list(led_options.keys()), key="pr_tds")
            with tds_col2:
                tds_amt = st.number_input("TDS Amount (₹)", min_value=0.0, step=10.0, format="%.2f")

            if st.button("✅ Post Voucher", use_container_width=True):
                try:
                    vcode = "PV" if "Payment" in vtype else "RV"
                    vno   = next_voucher_no(db, vcode)
                    net   = amount - tds_amt
                    p_code= led_options[party_led]
                    b_code= led_options[bank_led]

                    if "Payment" in vtype:
                        entries = [
                            {"ledger_code": p_code, "debit": amount, "credit": 0},
                            {"ledger_code": b_code, "debit": 0, "credit": net},
                        ]
                        if tds_amt > 0 and tds_led != "— None —":
                            entries.append({"ledger_code": led_options[tds_led], "debit": 0, "credit": tds_amt})
                    else:
                        entries = [
                            {"ledger_code": b_code, "debit": net,    "credit": 0},
                            {"ledger_code": p_code, "debit": 0,      "credit": amount},
                        ]
                        if tds_amt > 0 and tds_led != "— None —":
                            entries.insert(1, {"ledger_code": led_options[tds_led], "debit": tds_amt, "credit": 0})

                    post_double_entry(db, vno, vcode, vdate, narration, entries,
                                       ref_no=ref_no, total=amount)
                    st.success(f"✅ {vtype.split('(')[0].strip()} posted: **{vno}** | ₹{amount:,.2f}")
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── Journal Voucher ──────────────────────────────────────────────────
        elif vtype == "Journal (JV)":
            st.markdown("##### Journal Lines (add Dr / Cr entries)")
            n_rows = st.number_input("Number of lines", min_value=2, max_value=20, value=2)

            jv_entries = []
            for i in range(int(n_rows)):
                cols = st.columns([3,1,1])
                with cols[0]: led = st.selectbox(f"Ledger {i+1}", list(led_options.keys()), key=f"jv_led_{i}")
                with cols[1]: dr  = st.number_input("Debit",  min_value=0.0, step=100.0, format="%.2f", key=f"jv_dr_{i}")
                with cols[2]: cr  = st.number_input("Credit", min_value=0.0, step=100.0, format="%.2f", key=f"jv_cr_{i}")
                jv_entries.append({"ledger_code": led_options[led], "debit": dr, "credit": cr})

            total_dr = sum(e["debit"]  for e in jv_entries)
            total_cr = sum(e["credit"] for e in jv_entries)
            bal_diff = round(total_dr - total_cr, 2)
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Total Dr", fmt_inr(total_dr))
            col_b.metric("Total Cr", fmt_inr(total_cr))
            col_c.metric("Difference", fmt_inr(bal_diff), delta_color="off")

            if st.button("✅ Post Journal", use_container_width=True):
                if bal_diff != 0:
                    st.error(f"Journal is unbalanced by ₹{bal_diff:,.2f}. Please fix before posting.")
                else:
                    try:
                        vno = next_voucher_no(db, "JV")
                        post_double_entry(db, vno, "JV", vdate, narration, jv_entries,
                                           ref_no=ref_no, total=total_dr)
                        st.success(f"✅ Journal posted: **{vno}**")
                    except Exception as e:
                        st.error(f"Error: {e}")

        # ── Contra ──────────────────────────────────────────────────────────
        elif vtype == "Contra (CV)":
            col1, col2, col3 = st.columns(3)
            with col1: from_led = st.selectbox("From (Cash/Bank)", list(led_options.keys()), key="cv_from")
            with col2: to_led   = st.selectbox("To (Cash/Bank)",   list(led_options.keys()), key="cv_to")
            with col3: cv_amt   = st.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f")

            if st.button("✅ Post Contra", use_container_width=True):
                try:
                    vno = next_voucher_no(db, "CV")
                    entries = [
                        {"ledger_code": led_options[to_led],   "debit": cv_amt, "credit": 0},
                        {"ledger_code": led_options[from_led], "debit": 0,      "credit": cv_amt},
                    ]
                    post_double_entry(db, vno, "CV", vdate, narration, entries, total=cv_amt)
                    st.success(f"✅ Contra posted: **{vno}**")
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── Purchase / Sales Invoice ─────────────────────────────────────────
        elif vtype in ("Purchase Invoice (PINV)", "Sales Invoice (SINV)"):
            is_purchase = "Purchase" in vtype
            vcode       = "PINV" if is_purchase else "SINV"

            col1, col2, col3 = st.columns(3)
            with col1:
                party_led = st.selectbox(
                    "Supplier Ledger" if is_purchase else "Customer Ledger",
                    list(led_options.keys()), key="inv_party"
                )
            with col2:
                inter_state = st.checkbox("Inter-State Supply (IGST)", key="inv_inter")
            with col3:
                gst_rate = st.selectbox("GST Rate (%)", [0,5,12,18,28], index=3, key="inv_gst")

            # Purchase/Sales account
            acc_options = [k for k in led_options.keys()
                           if (("Purchase" in k or "PUR" in k) if is_purchase
                               else ("Sales" in k or "SAL" in k))]
            if not acc_options:
                acc_options = list(led_options.keys())

            account_led = st.selectbox(
                "Purchase Account" if is_purchase else "Sales Account",
                acc_options, key="inv_account"
            )
            taxable_val = st.number_input("Taxable Amount (₹)", min_value=0.0, step=100.0, format="%.2f")

            # Compute GST
            half = gst_rate / 2
            igst_amt = round(taxable_val * gst_rate / 100, 2)
            cgst_amt = round(taxable_val * half  / 100, 2)
            sgst_amt = cgst_amt
            total_v  = taxable_val + (igst_amt if inter_state else cgst_amt + sgst_amt)

            cols = st.columns(4)
            cols[0].metric("Taxable", fmt_inr(taxable_val))
            if inter_state:
                cols[1].metric(f"IGST {gst_rate}%", fmt_inr(igst_amt))
            else:
                cols[1].metric(f"CGST {half}%", fmt_inr(cgst_amt))
                cols[2].metric(f"SGST {half}%", fmt_inr(sgst_amt))
            cols[3].metric("Grand Total", fmt_inr(total_v))

            if st.button("✅ Post Invoice", use_container_width=True):
                try:
                    vno     = next_voucher_no(db, vcode)
                    acc_code= led_options[account_led]
                    p_code  = led_options[party_led]

                    entries = []
                    if is_purchase:
                        entries.append({"ledger_code": acc_code, "debit": taxable_val, "credit": 0})
                        if inter_state:
                            entries.append({"ledger_code": f"IGST_I_{gst_rate}", "debit": igst_amt, "credit": 0})
                        else:
                            entries.append({"ledger_code": f"CGST_I_{gst_rate}", "debit": cgst_amt, "credit": 0})
                            entries.append({"ledger_code": f"SGST_I_{gst_rate}", "debit": sgst_amt, "credit": 0})
                        entries.append({"ledger_code": p_code, "debit": 0, "credit": total_v})
                    else:
                        entries.append({"ledger_code": p_code, "debit": total_v, "credit": 0})
                        entries.append({"ledger_code": acc_code, "debit": 0, "credit": taxable_val})
                        if inter_state:
                            entries.append({"ledger_code": f"IGST_O_{gst_rate}", "debit": 0, "credit": igst_amt})
                        else:
                            entries.append({"ledger_code": f"CGST_O_{gst_rate}", "debit": 0, "credit": cgst_amt})
                            entries.append({"ledger_code": f"SGST_O_{gst_rate}", "debit": 0, "credit": sgst_amt})

                    post_double_entry(db, vno, vcode, vdate, narration, entries,
                                       ref_no=ref_no, taxable=taxable_val,
                                       tax=igst_amt if inter_state else cgst_amt+sgst_amt,
                                       total=total_v, inter_state=inter_state)
                    st.success(f"✅ {'Purchase' if is_purchase else 'Sales'} invoice posted: **{vno}** | {fmt_inr(total_v)}")
                except Exception as e:
                    st.error(f"Error: {e}")

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — DMS / PDF UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════

elif "DMS" in page or "PDF" in page:
    st.markdown('<div class="main-title">📄 Document Management & PDF Import</div>', unsafe_allow_html=True)
    st.markdown("---")

    db = get_db()
    try:
        tab1, tab2 = st.tabs(["📤 Upload & Extract", "📋 Document Library"])

        with tab1:
            st.markdown("#### Upload Invoice / Bill PDF")
            uploaded = st.file_uploader(
                "Drag & drop PDF, image, or Excel here",
                type=["pdf","png","jpg","jpeg","csv","xlsx","txt"],
                help="Supported: PDF, PNG, JPG, CSV, XLSX, TXT"
            )

            col1, col2 = st.columns(2)
            with col1:
                doc_category = st.selectbox("Category", [
                    "Invoice","Bill","Receipt","Bank Statement","Contract",
                    "Agreement","PO","GRN","Payslip","Tax Certificate","Other"
                ])
            with col2:
                doc_tags = st.text_input("Tags (comma separated)")

            auto_entry = st.checkbox("Auto-create voucher entry from extracted data", value=True)
            voucher_for= st.selectbox("Voucher Type", ["Purchase Invoice (PINV)","Sales Invoice (SINV)","Payment (PV)","Receipt (RV)"])

            if uploaded and st.button("🔍 Upload & Extract", use_container_width=True):
                # Save file
                upload_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, uploaded.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                st.info(f"📁 Saved: {uploaded.name} ({len(uploaded.getbuffer())/1024:.1f} KB)")

                # Extract text
                extracted = ""
                method    = "none"

                if uploaded.name.lower().endswith(".pdf"):
                    try:
                        import pdfplumber
                        with pdfplumber.open(file_path) as pdf:
                            extracted = "\n".join(p.extract_text() or "" for p in pdf.pages)
                        method = "pdfplumber"
                    except ImportError:
                        extracted = "[pdfplumber not installed — run: pip install pdfplumber]"

                elif uploaded.name.lower().endswith((".png",".jpg",".jpeg")):
                    try:
                        from PIL import Image
                        import pytesseract
                        img = Image.open(file_path)
                        extracted = pytesseract.image_to_string(img)
                        method = "OCR (pytesseract)"
                    except ImportError:
                        extracted = "[pytesseract not installed — run: pip install pytesseract]"

                elif uploaded.name.lower().endswith(".txt"):
                    with open(file_path) as f:
                        extracted = f.read()
                    method = "plaintext"

                elif uploaded.name.lower().endswith(".csv"):
                    df = pd.read_csv(file_path)
                    extracted = df.to_string()
                    method = "CSV"

                st.success(f"✅ Extracted {len(extracted)} chars via {method}")

                # Parse fields with regex

                def find(patterns, text):
                    for pat in patterns:
                        m = re.search(pat, text, re.IGNORECASE)
                        if m:
                            return m.group(1).strip()
                    return ""

                fields = {
                    "invoice_no":    find([r"invoice\s*no[.:\s]+([A-Z0-9\-/]+)", r"inv[.#:\s]+([A-Z0-9\-/]+)"], extracted),
                    "invoice_date":  find([r"(?:invoice\s*)?date[.:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"], extracted),
                    "seller_gstin":  find([r"GSTIN[.:\s]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z])"], extracted),
                    "vendor_name":   find([r"(?:from|vendor|supplier)[.:\s]+([A-Za-z0-9 ,&.]+)"], extracted),
                    "taxable_amount":find([r"taxable\s*(?:amount|value)[.:\s₹]*([\d,]+\.?\d*)"], extracted),
                    "cgst_amount":   find([r"CGST[.:\s@%\d]*[₹]?\s*([\d,]+\.?\d*)"], extracted),
                    "sgst_amount":   find([r"SGST[.:\s@%\d]*[₹]?\s*([\d,]+\.?\d*)"], extracted),
                    "igst_amount":   find([r"IGST[.:\s@%\d]*[₹]?\s*([\d,]+\.?\d*)"], extracted),
                    "total_amount":  find([r"(?:grand\s*total|total\s*amount|amount\s*payable)[.:\s₹]*([\d,]+\.?\d*)",
                                            r"TOTAL[.:\s₹]*([\d,]+\.?\d*)"], extracted),
                }

                # Convert numeric fields
                for k in ("taxable_amount","cgst_amount","sgst_amount","igst_amount","total_amount"):
                    try:
                        fields[k] = float(str(fields[k]).replace(",","")) if fields[k] else 0.0
                    except:
                        fields[k] = 0.0

                st.markdown("#### 🔍 Extracted Fields")
                field_df = pd.DataFrame([{"Field": k, "Value": v} for k,v in fields.items()])
                st.dataframe(field_df, use_container_width=True, hide_index=True)

                st.text_area("Raw Extracted Text", extracted[:3000] + ("..." if len(extracted) > 3000 else ""), height=200)

                # Store doc in DB
                with open(file_path,"rb") as f:
                    fhash = hashlib.md5(f.read()).hexdigest()

                existing_doc = db.query(Document).filter_by(file_hash=fhash).first()
                if not existing_doc:
                    doc = Document(
                        doc_ref          = f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        original_filename= uploaded.name,
                        stored_path      = file_path,
                        mime_type        = uploaded.type,
                        file_size_kb     = len(uploaded.getbuffer()) / 1024,
                        file_hash        = fhash,
                        category         = doc_category,
                        tags             = doc_tags,
                        extracted_text   = extracted,
                        parsed_fields    = json.dumps(fields),
                        status           = "EXTRACTED",
                        extraction_method= method,
                        uploaded_by      = "user",
                    )
                    db.add(doc)
                    db.commit()
                    st.success(f"📁 Document stored: {doc.doc_ref}")
                else:
                    st.info("Document already exists (duplicate hash).")

        with tab2:
            st.markdown("#### Document Library")
            docs = db.query(Document).order_by(Document.created_at.desc()).limit(50).all()
            if docs:
                rows = [{"Ref": d.doc_ref, "File": d.original_filename,
                          "Category": d.category, "Status": d.status,
                          "Uploaded": fmt_date(d.upload_date)}
                         for d in docs]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No documents uploaded yet.")

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — MASTERS
# ═══════════════════════════════════════════════════════════════════════════════

elif "Masters" in page:
    st.markdown('<div class="main-title">🗄️ Master Data</div>', unsafe_allow_html=True)
    st.markdown("---")

    db = get_db()
    try:
        tab1, tab2, tab3, tab4 = st.tabs(["📒 Ledgers", "👥 Parties", "📦 Stock Items", "🏦 Bank Accounts"])

        with tab1:
            st.markdown("#### Chart of Accounts")
            ledgers = db.query(Ledger).join(AccountGroup).order_by(AccountGroup.code, Ledger.code).all()
            if ledgers:
                rows = [{"Code": l.code, "Name": l.name, "Group": l.group.name if l.group else "",
                          "Nature": l.nature, "Tax?": "✓" if bool(l.is_tax_ledger) else "",
                          "Bank?": "✓" if bool(l.is_bank) else "", "Cash?": "✓" if bool(l.is_cash) else ""}
                         for l in ledgers]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=500)

            st.markdown("##### Add New Ledger")
            col1, col2 = st.columns(2)
            with col1:
                new_code = st.text_input("Code", placeholder="e.g. BANK04")
                new_name = st.text_input("Name", placeholder="e.g. Axis Bank Account")
            with col2:
                groups   = db.query(AccountGroup).order_by(AccountGroup.name).all()
                grp_opts = {g.name: g.id for g in groups}
                sel_grp  = st.selectbox("Group", list(grp_opts.keys()))
                new_nat  = st.selectbox("Nature", ["Dr","Cr"])
            new_open = st.number_input("Opening Balance (₹)", format="%.2f")
            is_bank_new = st.checkbox("Is Bank Account")
            is_cash_new = st.checkbox("Is Cash Account")

            if st.button("➕ Add Ledger"):
                if new_code and new_name:
                    exists = db.query(Ledger).filter_by(code=new_code).first()
                    if exists:
                        st.error("Ledger code already exists!")
                    else:
                        db.add(Ledger(code=new_code, name=new_name,
                                       group_id=grp_opts[sel_grp], nature=new_nat,
                                       opening_balance=new_open, is_bank=is_bank_new,
                                       is_cash=is_cash_new))
                        db.commit()
                        st.success(f"✅ Ledger {new_code} added!")
                        st.rerun()

        with tab2:
            st.markdown("#### Party Master (Customers / Suppliers)")
            parties = db.query(Party).order_by(Party.party_type, Party.name).all()
            if parties:
                rows = [{"Code": p.code, "Name": p.name, "Type": p.party_type,
                          "GSTIN": p.gstin or "", "City": p.city or ""}
                         for p in parties]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown("##### Add Party")

            # ── Step 1: GSTIN Lookup ─────────────────────────────────────────
            st.markdown("**Step 1 — Enter GSTIN to auto-fill details from GST Portal**")
            gcol1, gcol2 = st.columns([3, 1])
            with gcol1:
                gstin_input = st.text_input(
                    "GSTIN", placeholder="e.g. 36AABCS1234C1ZP",
                    key="gstin_lookup_input",
                    help="Enter 15-digit GSTIN. Click Fetch to auto-fill party details."
                )
            with gcol2:
                st.markdown("<br>", unsafe_allow_html=True)
                fetch_clicked = st.button("🔍 Fetch from GST Portal", use_container_width=True)

            if fetch_clicked and gstin_input:
                # Get API key from SystemConfig if set
                try:
                    cfg = db.query(SystemConfig).filter_by(key="GST_API_KEY").first()
                    api_key = str(cfg.value).strip() if cfg and cfg.value not in ("", "YOUR_API_KEY") else ""
                except Exception:
                    api_key = ""

                with st.spinner("Looking up GSTIN..."):
                    result = lookup_gstin(gstin_input, api_key)

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state["gst_fetched"] = result
                    if result.get("api_error"):
                        st.warning(f"⚠️ Live API unavailable ({result['api_error']}). "
                                   f"Decoded from GSTIN structure instead.")
                    else:
                        st.success(f"✅ Fetched via {result.get('source','')}")

            # Show fetched info badge
            fetched = st.session_state.get("gst_fetched", {})
            if fetched and fetched.get("gstin") == gstin_input.strip().upper():
                info_cols = st.columns(4)
                info_cols[0].info(f"**State:** {fetched.get('state','')}")
                info_cols[1].info(f"**Biz Type:** {fetched.get('biz_type','')}")
                if fetched.get("status"):
                    info_cols[2].info(f"**Status:** {fetched.get('status','')}")
                if fetched.get("reg_date"):
                    info_cols[3].info(f"**Reg Date:** {fetched.get('reg_date','')}")

            st.markdown("**Step 2 — Review & Save**")

            # ── Step 2: Party Form (pre-filled from GST lookup) ──────────────
            # Use fetched values as defaults
            def _gst_val(key, fallback=""):
                f = st.session_state.get("gst_fetched", {})
                if f and f.get("gstin","").upper() == gstin_input.strip().upper():
                    return f.get(key, fallback)
                return fallback

            col1, col2 = st.columns(2)
            with col1:
                p_code  = st.text_input("Party Code", placeholder="VEND001", key="p_code")
                p_name  = st.text_input(
                    "Legal Name",
                    value=_gst_val("legal_name"),
                    placeholder="Company Name", key="p_name"
                )
                p_trade = st.text_input(
                    "Trade Name",
                    value=_gst_val("trade_name"),
                    placeholder="Trade / Brand name", key="p_trade"
                )
                p_gstin = st.text_input(
                    "GSTIN",
                    value=_gst_val("gstin", gstin_input),
                    key="p_gstin"
                )
                p_pan   = st.text_input(
                    "PAN",
                    value=_gst_val("pan"),
                    key="p_pan"
                )
            with col2:
                p_type  = st.selectbox("Party Type",
                                        ["SUPPLIER","CUSTOMER","EMPLOYEE","OTHER"], key="p_type")
                p_state = st.text_input(
                    "State Code",
                    value=_gst_val("state_code"),
                    placeholder="e.g. 36", key="p_state"
                )
                p_city  = st.text_input(
                    "City / District",
                    value=_gst_val("city"),
                    key="p_city"
                )
                p_pin   = st.text_input(
                    "Pincode",
                    value=_gst_val("pincode"),
                    key="p_pin"
                )
                p_email = st.text_input("Email", key="p_email")

            p_addr  = st.text_area(
                "Address",
                value=_gst_val("address"),
                height=80, key="p_addr"
            )

            if st.button("➕ Save Party", use_container_width=True):
                if not p_code:
                    st.error("Party Code is required.")
                elif not p_name:
                    st.error("Legal Name is required.")
                else:
                    exists = db.query(Party).filter_by(code=p_code).first()
                    if exists:
                        st.error("Party code already exists!")
                    else:
                        db.add(Party(
                            code        = p_code,
                            name        = p_name,
                            party_type  = p_type,
                            gstin       = p_gstin,
                            city        = p_city,
                            state_code  = p_state,
                            email       = p_email,
                        ))
                        db.commit()
                        st.session_state.pop("gst_fetched", None)
                        st.success(f"✅ Party **{p_code}** — {p_name} saved!")
                        st.rerun()

        with tab3:
            st.markdown("#### Stock Item Master")
            items = db.query(StockItem).order_by(StockItem.code).all()
            if items:
                rows = [{"Code": i.code, "Name": i.name, "HSN": i.hsn_sac or "",
                          "GST%": i.gst_rate, "Stock": i.current_stock}
                         for i in items]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown("##### Add Stock Item")
            col1, col2 = st.columns(2)
            with col1:
                si_code = st.text_input("Item Code", key="si_code")
                si_name = st.text_input("Item Name", key="si_name")
                si_hsn  = st.text_input("HSN/SAC Code", key="si_hsn")
            with col2:
                si_gst  = st.selectbox("GST Rate%", [0,5,12,18,28], index=3, key="si_gst")
                units   = db.query(StockUnit).order_by(StockUnit.symbol).all()
                u_opts  = {u.symbol: u.id for u in units}
                si_unit = st.selectbox("Unit", list(u_opts.keys()), key="si_unit")
                si_rate = st.number_input("Sale Price (₹)", format="%.2f", key="si_rate")

            if st.button("➕ Add Item"):
                if si_code and si_name:
                    db.add(StockItem(code=si_code, name=si_name, hsn_sac=si_hsn,
                                      gst_rate=si_gst, unit_id=u_opts[si_unit],
                                      sale_price=si_rate))
                    db.commit()
                    st.success(f"✅ Item {si_code} added!")
                    st.rerun()

        with tab4:
            st.markdown("#### Bank Account Master")
            banks = db.query(Ledger).filter_by(is_bank=True).all()
            if banks:
                rows = [{"Code": b.code, "Name": b.name,
                          "Account No": b.bank_account_no or "",
                          "IFSC": b.ifsc_code or ""}
                         for b in banks]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — REPORTS
# ═══════════════════════════════════════════════════════════════════════════════

elif "Reports" in page:
    st.markdown('<div class="main-title">📊 Financial Reports</div>', unsafe_allow_html=True)
    st.markdown("---")

    db = get_db()
    try:
        report_type = st.selectbox("Select Report", [
            "Trial Balance",
            "Profit & Loss",
            "Balance Sheet",
            "GST Summary (GSTR-3B)",
            "TDS Summary",
            "Sales Register",
            "Purchase Register",
            "Print Invoice / PDF",
            "Company Profile",
            "Ledger Statement",
            "Voucher Register",
            "AR Aging",
            "AP Aging",
        ])

        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("From Date", value=date(2025, 4, 1), format="DD/MM/YYYY")
        with col2:
            to_date   = st.date_input("To Date",   value=date.today(), format="DD/MM/YYYY")

        generate_report = st.button("🔍 Generate Report", use_container_width=True)

        if report_type in ("Print Invoice / PDF", "Company Profile") or generate_report:

            # Helper: get all ledger balances
            def ledger_balances():
                ledgers = db.query(Ledger).filter_by(is_active=True).all()
                result  = []
                for led in ledgers:
                    txns = db.query(Transaction).join(Voucher).filter(
                        Transaction.ledger_id == led.id,
                        Voucher.voucher_date >= from_date,
                        Voucher.voucher_date <= to_date,
                        Voucher.status == "POSTED"
                    ).all()
                    dr = sum(_f(t.debit) for t in txns) + (_f(led.opening_balance) if led.opening_type == "Dr" else 0)
                    cr = sum(_f(t.credit) for t in txns) + (_f(led.opening_balance) if led.opening_type == "Cr" else 0)
                    net= dr - cr
                    if net != 0:
                        grp = db.query(AccountGroup).filter_by(id=led.group_id).first()
                        result.append({
                            "Code": led.code, "Ledger": led.name,
                            "Group": grp.name if grp else "",
                            "Group_Type": grp.group_type if grp else "",
                            "Debit":  round(dr, 2), "Credit": round(cr, 2),
                            "Net":    round(net, 2),
                        })
                return result

            if report_type == "Trial Balance":
                bals = ledger_balances()
                rows = []
                for b in sorted(bals, key=lambda x: x["Group"]):
                    dr = round(b["Net"],2) if b["Net"] > 0 else 0
                    cr = round(-b["Net"],2) if b["Net"] < 0 else 0
                    rows.append({"Ledger Code": b["Code"], "Ledger Name": b["Ledger"],
                                  "Group": b["Group"],
                                  "Debit (₹)": f"{dr:,.2f}" if dr else "",
                                  "Credit (₹)": f"{cr:,.2f}" if cr else ""})
                df = pd.DataFrame(rows)
                st.markdown(f"### Trial Balance — As on {to_date}")
                st.dataframe(df, use_container_width=True, hide_index=True, height=500)
                total_dr = sum(b["Debit"]  for b in bals if b["Net"] > 0)
                total_cr = sum(b["Credit"] for b in bals if b["Net"] < 0)
                col1,col2,col3 = st.columns(3)
                col1.metric("Total Dr", fmt_inr(total_dr))
                col2.metric("Total Cr", fmt_inr(total_cr))
                col3.metric("Difference", fmt_inr(total_dr - total_cr),
                             delta_color="off" if total_dr==total_cr else "inverse")

            elif report_type in ("Profit & Loss", "Balance Sheet"):
                bals = ledger_balances()
                groups = {b["Group"]: b["Group_Type"] for b in bals}

                income   = {b["Group"]: [] for b in bals if b["Group_Type"] == "INCOME"}
                expenses = {b["Group"]: [] for b in bals if b["Group_Type"] == "EXPENSE"}
                assets   = {b["Group"]: [] for b in bals if b["Group_Type"] == "ASSET"}
                liab     = {b["Group"]: [] for b in bals if b["Group_Type"] == "LIABILITY"}

                for b in bals:
                    amt = abs(b["Net"])
                    gt  = b["Group_Type"]
                    grp = b["Group"]
                    row = {"Ledger": b["Ledger"], "Amount": fmt_inr(amt)}
                    if gt == "INCOME":   income.setdefault(grp,[]).append(row)
                    elif gt == "EXPENSE":expenses.setdefault(grp,[]).append(row)
                    elif gt == "ASSET":  assets.setdefault(grp,[]).append(row)
                    elif gt == "LIABILITY":liab.setdefault(grp,[]).append(row)

                total_inc  = sum(abs(b["Net"]) for b in bals if b["Group_Type"]=="INCOME")
                total_exp  = sum(abs(b["Net"]) for b in bals if b["Group_Type"]=="EXPENSE")
                net_profit = total_inc - total_exp

                if report_type == "Profit & Loss":
                    st.markdown(f"### Profit & Loss — {from_date} to {to_date}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**INCOME**")
                        for grp, rows in income.items():
                            if rows:
                                st.markdown(f"*{grp}*")
                                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        st.metric("Total Income", fmt_inr(total_inc))
                    with col2:
                        st.markdown("**EXPENSES**")
                        for grp, rows in expenses.items():
                            if rows:
                                st.markdown(f"*{grp}*")
                                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        st.metric("Total Expenses", fmt_inr(total_exp))
                    st.metric(
                        "Net Profit / (Loss)",
                        fmt_inr(net_profit),
                        delta=f"{'Profit' if net_profit >= 0 else 'Loss'}"
                    )

                else:  # Balance Sheet
                    st.markdown(f"### Balance Sheet — As on {to_date}")
                    col1, col2 = st.columns(2)
                    total_assets = sum(abs(b["Net"]) for b in bals if b["Group_Type"]=="ASSET")
                    total_liab   = sum(abs(b["Net"]) for b in bals if b["Group_Type"]=="LIABILITY") + net_profit
                    with col1:
                        st.markdown("**ASSETS**")
                        for grp, rows in assets.items():
                            if rows:
                                st.markdown(f"*{grp}*")
                                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        st.metric("Total Assets", fmt_inr(total_assets))
                    with col2:
                        st.markdown("**LIABILITIES & EQUITY**")
                        for grp, rows in liab.items():
                            if rows:
                                st.markdown(f"*{grp}*")
                                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        st.markdown(f"*Retained Earnings / P&L*")
                        st.dataframe(pd.DataFrame([{"Ledger":"Net Profit/(Loss)","Amount":fmt_inr(net_profit)}]),
                                     use_container_width=True, hide_index=True)
                        st.metric("Total Liabilities + Equity", fmt_inr(total_liab))

            elif report_type == "Print Invoice / PDF":
                st.markdown("### Print Invoice / PDF")

                if CompanyProfile is None:
                    st.warning("Company profile model unavailable (backend import failed). Some fields will be hidden.")

                company = None
                if CompanyProfile is not None:
                    company = db.query(CompanyProfile).first()

                if company:
                    st.caption(f"Invoice header: {company.name} | GSTIN: {company.gstin or 'Not set'}")
                else:
                    st.warning("Company profile is not configured yet. PDF will use fallback header values.")

                recent_orders = []
                if Order is not None:
                    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
                else:
                    st.warning("Order model unavailable (backend import failed). Invoice report is disabled.")
                default_order_id = recent_orders[0].id if recent_orders else 1
                order_id = st.number_input("Order ID", value=default_order_id, min_value=1, step=1)

                selected_order = None
                if Order is not None:
                    selected_order = db.query(Order).filter_by(id=order_id).first()

                if selected_order:
                    status_value = selected_order.status.value if hasattr(selected_order.status, "value") else str(selected_order.status)
                    info_cols = st.columns(4)
                    info_cols[0].metric("Status", status_value)
                    info_cols[1].metric("Subtotal", fmt_inr(_f(selected_order.subtotal)))
                    info_cols[2].metric("Tax", fmt_inr(_f(selected_order.tax_amount)))
                    info_cols[3].metric("Total", fmt_inr(_f(selected_order.total_amount)))
                    if OrderStatus is not None and selected_order.status != OrderStatus.completed:
                        st.warning("This order is not completed yet. You can still generate a draft invoice, but journal posting is normally tied to completed orders.")
                else:
                    st.info("Select a valid order ID to preview and download its invoice.")

                if InvoiceService is None:
                    st.warning("Invoice generation service unavailable (backend module import failed). Install backend dependencies and restart.")
                elif st.button("Generate Invoice PDF", use_container_width=True):
                    if not selected_order:
                        st.error("Order not found")
                    else:
                        try:
                            pdf_path = InvoiceService.generate_pdf(selected_order, filename=f"Invoice_{order_id}.pdf")
                            st.success(f"Invoice generated: {pdf_path}")
                            with open(pdf_path, "rb") as f:
                                st.session_state["current_invoice_pdf_bytes"] = f.read()
                            st.session_state["current_invoice_pdf_name"] = f"Invoice_{order_id}.pdf"
                        except Exception as e:
                            st.error(f"Invoice generation failed: {e}")

                if st.session_state.get("current_invoice_pdf_bytes"):
                    st.download_button(
                        label="Download Invoice PDF",
                        data=st.session_state["current_invoice_pdf_bytes"],
                        file_name=st.session_state.get("current_invoice_pdf_name", f"Invoice_{order_id}.pdf"),
                        mime="application/pdf",
                        use_container_width=True,
                    )

                st.markdown("#### Recent Orders")
                if recent_orders:
                    order_rows = []
                    for order in recent_orders:
                        order_rows.append({
                            "Order ID": order.id,
                            "Customer": order.customer_id,
                            "Description": order.item_description or "-",
                            "HSN": order.hsn_code or "-",
                            "Status": order.status.value if hasattr(order.status, "value") else str(order.status),
                            "Total": round(_f(order.total_amount), 2),
                            "Created": order.created_at.strftime("%Y-%m-%d %H:%M"),
                        })
                    st.dataframe(pd.DataFrame(order_rows), use_container_width=True, hide_index=True)

                    quick_order_id = st.selectbox(
                        "Quick Download Recent Invoice",
                        options=[order.id for order in recent_orders],
                        index=0,
                    )
                    if st.button("Download Selected Recent Invoice"):
                        quick_order = db.query(Order).filter_by(id=quick_order_id).first()
                        if quick_order:
                            pdf_path = InvoiceService.generate_pdf(quick_order, filename=f"Invoice_{quick_order_id}.pdf")
                            with open(pdf_path, "rb") as f:
                                st.session_state["recent_invoice_pdf_bytes"] = f.read()
                            st.session_state["recent_invoice_pdf_name"] = f"Invoice_{quick_order_id}.pdf"

                    if st.session_state.get("recent_invoice_pdf_bytes"):
                        st.download_button(
                            label="Download Selected Recent Invoice PDF",
                            data=st.session_state["recent_invoice_pdf_bytes"],
                            file_name=st.session_state.get("recent_invoice_pdf_name", f"Invoice_{quick_order_id}.pdf"),
                            mime="application/pdf",
                            key="download_recent_invoice_pdf",
                            use_container_width=True,
                        )
                else:
                    st.info("No orders available yet.")

            elif report_type == "Company Profile":
                st.markdown("### Company Profile")

                if CompanyProfile is None:
                    st.error("CompanyProfile model not available; backend model import failed.")
                    CompanyProfile = None

                profile = None
                if CompanyProfile is not None:
                    profile = db.query(CompanyProfile).first()
                with st.form("company_profile_form"):
                    name = st.text_input("Company Name", value=profile.name if profile else "Spoorthy Solutions Pvt Ltd")
                    address = st.text_area("Address", value=profile.address if profile else "Plot 42, Tech Park, Hyderabad, 500081")
                    col1, col2 = st.columns(2)
                    with col1:
                        phone = st.text_input("Phone", value=profile.phone if profile else "+91 98765 43210")
                        email = st.text_input("Email", value=profile.email if profile else "info@spoorthy.erp")
                        gstin = st.text_input("GSTIN", value=profile.gstin if profile else "36ABCDE1234F1Z5")
                    with col2:
                        website = st.text_input("Website", value=profile.website if profile else "")
                        logo_path = st.text_input("Logo Path", value=profile.logo_path if profile else "static/logo.png")
                        bank_details = st.text_area(
                            "Bank Details",
                            value=profile.bank_details if profile else "Bank: ICICI Bank, A/c: 1234567890, IFSC: ICIC0000001",
                        )
                    save_profile = st.form_submit_button("Save Company Profile", use_container_width=True)

                if save_profile:
                    if profile:
                        profile.name = name
                        profile.address = address
                        profile.phone = phone
                        profile.email = email
                        profile.gstin = gstin
                        profile.website = website
                        profile.logo_path = logo_path
                        profile.bank_details = bank_details
                    else:
                        profile = CompanyProfile(
                            name=name,
                            address=address,
                            phone=phone,
                            email=email,
                            gstin=gstin,
                            website=website,
                            logo_path=logo_path,
                            bank_details=bank_details,
                        )
                        db.add(profile)
                    db.commit()
                    st.success("Company profile saved successfully.")

                preview = db.query(CompanyProfile).first()
                if preview:
                    st.markdown("#### Current Profile")
                    preview_rows = [{
                        "Name": preview.name,
                        "GSTIN": preview.gstin or "-",
                        "Phone": preview.phone or "-",
                        "Email": preview.email or "-",
                        "Website": preview.website or "-",
                        "Logo Path": preview.logo_path or "-",
                        "Address": preview.address,
                        "Bank Details": preview.bank_details or "-",
                    }]
                    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

            elif report_type == "GST Summary (GSTR-3B)":
                st.markdown(f"### GST Summary — {from_date} to {to_date}")
                bals = ledger_balances()
                gst_rows = [b for b in bals if any(t in b["Code"] for t in ["GST","IGST","CGST","SGST","CESS"])]
                output_tax = [b for b in gst_rows if "_O_" in b["Code"] or "OUT" in b["Code"]]
                input_tax  = [b for b in gst_rows if "_I_" in b["Code"] or "IN_" in b["Code"]]

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Output Tax (Sales)**")
                    if output_tax:
                        rows = [{"Ledger": b["Ledger"], "Amount": fmt_inr(abs(b["Net"]))} for b in output_tax]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    total_out = sum(abs(b["Net"]) for b in output_tax)
                    st.metric("Total Output", fmt_inr(total_out))
                with col2:
                    st.markdown("**Input Tax / ITC (Purchases)**")
                    if input_tax:
                        rows = [{"Ledger": b["Ledger"], "Amount": fmt_inr(abs(b["Net"]))} for b in input_tax]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    total_in  = sum(abs(b["Net"]) for b in input_tax)
                    st.metric("Total ITC", fmt_inr(total_in))
                st.metric("Net GST Payable", fmt_inr(total_out - total_in))

            elif report_type in ("Sales Register","Purchase Register"):
                vtype_filter = "SINV" if "Sales" in report_type else "PINV"
                vt = db.query(VoucherType).filter_by(code=vtype_filter).first()
                if not vt:
                    st.error(f"Voucher type '{vtype_filter}' not found. Please run python main.py to seed master data.")
                    st.stop()
                vouchers = db.query(Voucher).filter(
                    Voucher.voucher_type_id == vt.id,
                    Voucher.voucher_date >= from_date,
                    Voucher.voucher_date <= to_date,
                    Voucher.status == "POSTED"
                ).order_by(Voucher.voucher_date).all()

                if vouchers:
                    rows = [{"Date": fmt_date(v.voucher_date), "No": v.voucher_no,
                              "Taxable": fmt_inr(v.taxable_amount),
                              "Tax": fmt_inr(v.tax_amount),
                              "Total": fmt_inr(v.total_amount),
                              "Status": v.status}
                             for v in vouchers]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    st.metric("Grand Total", fmt_inr(sum(_f(v.total_amount) for v in vouchers)))
                else:
                    st.info("No vouchers found for the selected period.")

            elif report_type == "Ledger Statement":
                all_leds = db.query(Ledger).order_by(Ledger.name).all()
                sel_led  = st.selectbox("Select Ledger", [f"{l.code} — {l.name}" for l in all_leds])
                led_code = sel_led.split(" — ")[0]
                led_obj  = db.query(Ledger).filter_by(code=led_code).first()
                if led_obj:
                    txns = db.query(Transaction).join(Voucher).filter(
                        Transaction.ledger_id == led_obj.id,
                        Voucher.voucher_date >= from_date,
                        Voucher.voucher_date <= to_date,
                        Voucher.status == "POSTED"
                    ).order_by(Voucher.voucher_date).all()
                    opening = _f(led_obj.opening_balance)
                    balance = opening
                    rows    = [{"Date": "", "Voucher No": "Opening Balance",
                                 "Narration": "", "Dr": "", "Cr": "",
                                 "Balance": fmt_inr(opening)}]
                    for t in txns:
                        v = db.query(Voucher).filter_by(id=t.voucher_id).first()
                        balance += _f(t.debit) - _f(t.credit)
                        rows.append({
                            "Date": fmt_date(v.voucher_date) if v else "",
                            "Voucher No": v.voucher_no if v else "",
                            "Narration": (v.narration or "")[:60] if v else "",
                            "Dr": fmt_inr(t.debit)  if t.debit  else "",
                            "Cr": fmt_inr(t.credit) if t.credit else "",
                            "Balance": fmt_inr(balance),
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    st.metric("Closing Balance", fmt_inr(balance))

            elif report_type == "Voucher Register":
                vouchers = db.query(Voucher).filter(
                    Voucher.voucher_date >= from_date,
                    Voucher.voucher_date <= to_date,
                ).order_by(Voucher.voucher_date).all()
                if vouchers:
                    rows = []
                    for v in vouchers:
                        vt_obj = db.query(VoucherType).filter_by(id=v.voucher_type_id).first()
                        rows.append({
                            "Date": fmt_date(v.voucher_date),
                            "No": v.voucher_no,
                            "Type": vt_obj.name if vt_obj else "",
                            "Narration": (v.narration or "")[:50],
                            "Amount": fmt_inr(v.total_amount),
                            "Status": v.status,
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=500)

            elif report_type in ("AR Aging", "AP Aging"):
                is_ar = "AR" in report_type
                vtype_filter = "SINV" if is_ar else "PINV"
                vt = db.query(VoucherType).filter_by(code=vtype_filter).first()
                if not vt:
                    st.error(f"Voucher type '{vtype_filter}' not found. Please run python main.py to seed master data.")
                    st.stop()
                vouchers = db.query(Voucher).filter(
                    Voucher.voucher_type_id == vt.id,
                    Voucher.status == "POSTED"
                ).all()

                buckets = {"0-30":0.0,"31-60":0.0,"61-90":0.0,"91-180":0.0,"180+":0.0}
                rows = []
                for v in vouchers:
                    vdate = v.voucher_date.date() if isinstance(v.voucher_date, datetime) else v.voucher_date
                    age = (to_date - vdate).days if vdate else 0
                    amt = _f(v.total_amount)
                    bkt = ("0-30" if age<=30 else "31-60" if age<=60
                           else "61-90" if age<=90 else "91-180" if age<=180 else "180+")
                    buckets[bkt] += amt
                    rows.append({"Date":fmt_date(v.voucher_date),"Voucher":v.voucher_no,
                                  "Amount":fmt_inr(amt),"Age (days)":age,"Bucket":bkt})
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                cols = st.columns(5)
                for i,(k,v) in enumerate(buckets.items()):
                    cols[i].metric(f"{k} days", fmt_inr(v))

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — BANK RECONCILIATION
# ═══════════════════════════════════════════════════════════════════════════════

elif "Bank Reconciliation" in page:
    st.markdown('<div class="main-title">🏦 Bank Reconciliation</div>', unsafe_allow_html=True)
    st.markdown("---")
    db = get_db()
    try:
        banks   = db.query(Ledger).filter_by(is_bank=True).all()
        b_opts  = {b.name: b for b in banks}
        sel_bank= st.selectbox("Select Bank Account", list(b_opts.keys()))
        bank    = b_opts[sel_bank]

        # Book balance
        txns = db.query(Transaction).join(Voucher).filter(
            Transaction.ledger_id == bank.id,
            Voucher.status == "POSTED"
        ).all()
        book_bal = _f(bank.opening_balance) + sum(_f(t.debit) - _f(t.credit) for t in txns)

        st.metric("📖 Book Balance", fmt_inr(book_bal))

        st.markdown("#### Statement Details")
        col1,col2 = st.columns(2)
        with col1:
            stmt_date = st.date_input("Statement Date", value=date.today(), format="DD/MM/YYYY")
            stmt_bal  = st.number_input("Statement Balance (₹)", format="%.2f")
        with col2:
            bank_chgs = st.number_input("Bank Charges (₹)", min_value=0.0, format="%.2f")
            int_cred  = st.number_input("Interest Credited (₹)", min_value=0.0, format="%.2f")

        uncl_dep = st.number_input("Uncleared Deposits (₹)", min_value=0.0, format="%.2f")
        uncl_pay = st.number_input("Uncleared Payments (₹)", min_value=0.0, format="%.2f")

        adj_bal = stmt_bal - uncl_dep + uncl_pay
        diff    = round(adj_bal - book_bal, 2)

        col1,col2,col3 = st.columns(3)
        col1.metric("Adjusted Bank Balance", fmt_inr(adj_bal))
        col2.metric("Book Balance",          fmt_inr(book_bal))
        col3.metric("Difference",            fmt_inr(diff),
                     delta_color="off" if diff==0 else "inverse")

        if st.button("✅ Reconcile & Post JV", use_container_width=True):
            db2 = get_db()
            try:
                jv_entries = []
                if bank_chgs > 0:
                    jv_entries += [{"ledger_code":"IE014","debit":bank_chgs,"credit":0},
                                    {"ledger_code":bank.code,"debit":0,"credit":bank_chgs}]
                if int_cred > 0:
                    jv_entries += [{"ledger_code":bank.code,"debit":int_cred,"credit":0},
                                    {"ledger_code":"OI001","debit":0,"credit":int_cred}]
                if jv_entries:
                    vno = next_voucher_no(db2, "BRS")
                    post_double_entry(db2, vno, "BRS", stmt_date,
                                       f"Bank recon {bank.name} — {stmt_date}",
                                       jv_entries)
                    st.success(f"✅ Auto JV posted: {vno}")

                db2.add(BankReconciliation(
                    bank_ledger_id        = bank.id,
                    statement_date        = stmt_date,
                    statement_balance     = stmt_bal,
                    book_balance          = book_bal,
                    uncleared_deposits    = uncl_dep,
                    uncleared_payments    = uncl_pay,
                    bank_charges          = bank_chgs,
                    interest_credited     = int_cred,
                    adjusted_bank_balance = adj_bal,
                    difference            = diff,
                    is_reconciled         = diff == 0.0,
                ))
                db2.commit()
                st.success(f"✅ Bank reconciliation saved. {'RECONCILED ✓' if diff==0 else f'Difference ₹{diff:,.2f}'}")
            finally:
                db2.close()

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — FIXED ASSETS
# ═══════════════════════════════════════════════════════════════════════════════

elif "Fixed Assets" in page:
    st.markdown('<div class="main-title">🏭 Fixed Asset Register</div>', unsafe_allow_html=True)
    st.markdown("---")
    db = get_db()
    try:
        assets = db.query(FixedAsset).filter_by(is_disposed=False).all()
        if assets:
            rows = [{"Code":a.asset_code,"Name":a.name,"Category":a.category or "",
                      "Cost":fmt_inr(a.cost),"Acc. Dep":fmt_inr(a.accumulated_dep),
                      "Book Value":fmt_inr(a.book_value),"Method":a.depreciation_method}
                     for a in assets]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            total_cost = sum(_f(a.cost) for a in assets)
            total_dep  = sum(_f(a.accumulated_dep) for a in assets)
            col1,col2,col3 = st.columns(3)
            col1.metric("Total Cost",       fmt_inr(total_cost))
            col2.metric("Total Acc. Dep",   fmt_inr(total_dep))
            col3.metric("Total Book Value", fmt_inr(total_cost - total_dep))

        st.markdown("#### Add Fixed Asset")
        col1,col2 = st.columns(2)
        with col1:
            fa_code   = st.text_input("Asset Code", placeholder="FA-001")
            fa_name   = st.text_input("Asset Name")
            fa_cat    = st.selectbox("Category", ["Land & Building","Plant & Machinery",
                                                   "Furniture","Computers","Vehicles","Other"])
            fa_cost   = st.number_input("Cost (₹)", min_value=0.0, format="%.2f")
        with col2:
            fa_date   = st.date_input("Purchase Date", value=date.today(), format="DD/MM/YYYY")
            fa_life   = st.number_input("Useful Life (Years)", min_value=1, max_value=100, value=5)
            fa_method = st.selectbox("Depreciation Method", ["SLM","WDV"])
            fa_salv   = st.number_input("Salvage Value (₹)", min_value=0.0, format="%.2f")

        if st.button("➕ Add Asset"):
            bv = fa_cost - fa_salv
            db.add(FixedAsset(asset_code=fa_code, name=fa_name, category=fa_cat,
                               cost=fa_cost, salvage_value=fa_salv, book_value=bv,
                               useful_life_yrs=fa_life, depreciation_method=fa_method,
                               purchase_date=fa_date, accumulated_dep=0))
            db.commit()
            st.success(f"✅ Asset {fa_code} added!")
            st.rerun()

        st.markdown("#### Post Depreciation JV")
        if st.button("📊 Calculate & Post Annual Depreciation"):
            total_dep_jv = 0.0
            jv_entries = []
            for a in assets:
                if a.book_value > 0:
                    if a.depreciation_method == "SLM":
                        ann_dep = (_f(a.cost) - _f(a.salvage_value)) / max(a.useful_life_yrs, 1)
                    else:
                        rate = _f(a.wdv_rate or 20) / 100
                        ann_dep = _f(a.book_value) * rate
                    bv = _f(a.book_value)
                    ann_dep = round(min(ann_dep, bv), 2)
                    if ann_dep > 0:
                        total_dep_jv += ann_dep
                        # Update FA record
                        a.accumulated_dep = _f(a.accumulated_dep) + ann_dep
                        a.book_value = _f(a.book_value) - ann_dep
            if total_dep_jv > 0:
                db.flush()  # Persist asset updates before posting JV
                jv_entries = [
                    {"ledger_code":"IE009","debit":total_dep_jv,"credit":0},
                    {"ledger_code":"FA007","debit":0,"credit":total_dep_jv},
                ]
                vno = next_voucher_no(db, "DP")
                post_double_entry(db, vno, "DP", date.today(),
                                   f"Annual depreciation on fixed assets",
                                   jv_entries, total=total_dep_jv)
                st.success(f"✅ Depreciation JV {vno} posted | Total: {fmt_inr(total_dep_jv)}")
            else:
                st.info("No assets to depreciate.")

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — PAYROLL
# ═══════════════════════════════════════════════════════════════════════════════

elif "Payroll" in page:
    render_payroll_page()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — SYSTEM SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

elif "Quantum Accounting" in page:
    render_quantum_accounting()

elif "Quantum Finance" in page:
    render_quantum_finance()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE — COMPANY SETUP
# ═══════════════════════════════════════════════════════════════════════════════

elif "Organisation Settings" in page:
    render_settings_page()

elif "Company Setup" in page:
    st.markdown('<div class="main-title">🏢 Company Setup</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Configure your organisation details — shown on all reports and invoices</div>', unsafe_allow_html=True)
    st.markdown("---")
    db = get_db()
    try:
        company = db.query(Company).first()
        is_new  = company is None

        with st.form("company_form"):
            st.markdown("#### 🏢 Basic Details")
            col1, col2 = st.columns(2)
            with col1:
                c_name    = st.text_input("Company Display Name *", value=company.name if company else "", placeholder="Milvian Technologies Pvt Ltd")
                c_legal   = st.text_input("Legal / Registered Name", value=company.legal_name or "" if company else "", placeholder="MILVIAN TECHNOLOGIES PRIVATE LIMITED")
                c_gstin   = st.text_input("GSTIN", value=company.gstin or "" if company else "", placeholder="36AATCM3488J1ZN")
                c_pan     = st.text_input("PAN", value=company.pan or "" if company else "", placeholder="AATCM3488J")
                c_cin     = st.text_input("CIN (Company ID No)", value=company.cin or "" if company else "", placeholder="U72900TG2020PTC140XXX")
                c_tan     = st.text_input("TAN", value=company.tan or "" if company else "", placeholder="HYDA12345A")
            with col2:
                c_industry= st.selectbox("Industry", ["IT / Technology", "Manufacturing", "Trading", "Services", "Construction", "Healthcare", "Education", "Finance", "Other"],
                                         index=0 if not company or not company.industry else
                                         ["IT / Technology","Manufacturing","Trading","Services","Construction","Healthcare","Education","Finance","Other"].index(company.industry) if company.industry in ["IT / Technology","Manufacturing","Trading","Services","Construction","Healthcare","Education","Finance","Other"] else 0)
                c_reg_date= st.date_input("Date of Incorporation", value=company.reg_date or date(2020,1,1) if company else date(2020,1,1), format="DD/MM/YYYY")
                c_phone   = st.text_input("Phone", value=company.phone or "" if company else "", placeholder="+91 40 2345 6789")
                c_email   = st.text_input("Email", value=company.email or "" if company else "", placeholder="accounts@milvian.com")
                c_website = st.text_input("Website", value=company.website or "" if company else "", placeholder="https://milvian.com")
                c_currency= st.selectbox("Base Currency", ["INR","USD","EUR","GBP","AED"],
                                         index=["INR","USD","EUR","GBP","AED"].index(company.currency) if company and company.currency in ["INR","USD","EUR","GBP","AED"] else 0)

            st.markdown("#### 📍 Registered Address")
            col3, col4 = st.columns(2)
            with col3:
                c_addr1   = st.text_input("Address Line 1", value=company.address_line1 or "" if company else "", placeholder="Plot 12, HITEC City")
                c_addr2   = st.text_input("Address Line 2", value=company.address_line2 or "" if company else "", placeholder="Madhapur")
                c_city    = st.text_input("City", value=company.city or "" if company else "", placeholder="Hyderabad")
            with col4:
                states = ["01-Jammu & Kashmir","02-Himachal Pradesh","03-Punjab","04-Chandigarh","05-Uttarakhand","06-Haryana","07-Delhi","08-Rajasthan","09-Uttar Pradesh","10-Bihar","11-Sikkim","12-Arunachal Pradesh","13-Nagaland","14-Manipur","15-Mizoram","16-Tripura","17-Meghalaya","18-Assam","19-West Bengal","20-Jharkhand","21-Odisha","22-Chhattisgarh","23-Madhya Pradesh","24-Gujarat","25-Daman & Diu","26-Dadra & Nagar Haveli","27-Maharashtra","28-Andhra Pradesh","29-Karnataka","30-Goa","31-Lakshadweep","32-Kerala","33-Tamil Nadu","34-Puducherry","35-Andaman & Nicobar","36-Telangana","37-Andhra Pradesh (New)","38-Ladakh"]
                cur_state = (company.state_code or "36") if company else "36"
                state_idx = next((i for i,s in enumerate(states) if s.startswith(cur_state+"-")), 35)
                c_state   = st.selectbox("State", states, index=state_idx)
                c_pincode = st.text_input("Pincode", value=company.pincode or "" if company else "", placeholder="500081")
                c_fy      = st.selectbox("Fiscal Year Start", ["April (India Standard)", "January (Calendar Year)"],
                                         index=0 if not company or company.fiscal_year_start == "04-01" else 1)

            submitted = st.form_submit_button("💾 Save Company Details", use_container_width=True)

        if submitted:
            if not c_name:
                st.error("Company name is required.")
            else:
                state_code = c_state.split("-")[0]
                fy_start   = "04-01" if "April" in c_fy else "01-01"
                if is_new:
                    db.add(Company(
                        name=c_name, legal_name=c_legal, gstin=c_gstin or None,
                        pan=c_pan or None, cin=c_cin or None, tan=c_tan or None,
                        address_line1=c_addr1, address_line2=c_addr2, city=c_city,
                        state_code=state_code, pincode=c_pincode,
                        phone=c_phone, email=c_email, website=c_website,
                        currency=c_currency, industry=c_industry,
                        reg_date=c_reg_date, fiscal_year_start=fy_start,
                        date_format="DD-MM-YYYY", is_setup_done=True,
                    ))
                else:
                    company.name=c_name; company.legal_name=c_legal
                    company.gstin=c_gstin or None; company.pan=c_pan or None
                    company.cin=c_cin or None; company.tan=c_tan or None
                    company.address_line1=c_addr1; company.address_line2=c_addr2
                    company.city=c_city; company.state_code=state_code; company.pincode=c_pincode
                    company.phone=c_phone; company.email=c_email; company.website=c_website
                    company.currency=c_currency; company.industry=c_industry
                    company.reg_date=c_reg_date; company.fiscal_year_start=fy_start
                    company.is_setup_done=True
                db.commit()
                st.success(f"✅ Company **{c_name}** saved!")
                st.rerun()

        if not is_new:
            co = db.query(Company).first()
            st.markdown("---")
            st.markdown("#### Current Company Profile")
            col_a, col_b, col_c = st.columns(3)
            col_a.info(f"**{co.name}**\n\n{co.address_line1 or ''}, {co.city or ''} – {co.pincode or ''}")
            col_b.info(f"GSTIN: **{co.gstin or '—'}**\nPAN: {co.pan or '—'}\nCIN: {co.cin or '—'}")
            col_c.info(f"Email: {co.email or '—'}\nPhone: {co.phone or '—'}\nIncorp: {fmt_date(co.reg_date)}")
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE — USERS & ROLES
# ═══════════════════════════════════════════════════════════════════════════════

elif "Users & Roles" in page:
    st.markdown('<div class="main-title">👤 Users & Roles</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Manage user accounts and access permissions</div>', unsafe_allow_html=True)
    st.markdown("---")
    db = get_db()
    try:
        # ── Seed default roles if missing ──────────────────────────────────────
        DEFAULT_ROLES = [
            {"name":"ADMIN",      "description":"Full access — all modules, settings, user mgmt",         "can_post":True,  "can_approve":True,  "can_delete":True,  "can_export":True,  "can_admin":True},
            {"name":"ACCOUNTANT", "description":"Post & approve vouchers, view all reports",              "can_post":True,  "can_approve":True,  "can_delete":False, "can_export":True,  "can_admin":False},
            {"name":"HR",         "description":"Payroll, employee records, HR reports only",             "can_post":True,  "can_approve":False, "can_delete":False, "can_export":True,  "can_admin":False},
            {"name":"AUDITOR",    "description":"Read-only access to all vouchers, reports, trial balance","can_post":False, "can_approve":False, "can_delete":False, "can_export":True,  "can_admin":False},
            {"name":"VIEWER",     "description":"Dashboard and reports only — no posting",                "can_post":False, "can_approve":False, "can_delete":False, "can_export":False, "can_admin":False},
        ]
        for rd in DEFAULT_ROLES:
            if not db.query(Role).filter_by(name=rd["name"]).first():
                db.add(Role(**rd))
        db.commit()

        # ── Roles table ────────────────────────────────────────────────────────
        st.markdown("#### 🔑 Roles")
        roles = db.query(Role).all()
        role_rows = [{
            "Role": r.name, "Description": r.description,
            "Post": "✅" if r.can_post    else "—",
            "Approve": "✅" if r.can_approve else "—",
            "Delete": "✅" if r.can_delete  else "—",
            "Export": "✅" if r.can_export  else "—",
            "Admin": "✅" if r.can_admin   else "—",
        } for r in roles]
        st.dataframe(pd.DataFrame(role_rows), use_container_width=True, hide_index=True)

        st.markdown("---")

        # ── Users table ────────────────────────────────────────────────────────
        st.markdown("#### 👥 Users")
        users = db.query(AppUser).all()
        if users:
            user_rows = [{
                "Username": u.username, "Full Name": u.full_name,
                "Email": u.email, "Role": u.role.name if u.role else "—",
                "Active": "✅" if u.is_active else "❌",
                "First Login": "⚠️ Pending" if u.is_first_login else "Done",
                "Last Login": fmt_date(u.last_login) if u.last_login else "Never",
                "Created": fmt_date(u.created_at),
            } for u in users]
            st.dataframe(pd.DataFrame(user_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No users yet. Create the first admin user below.")

        st.markdown("---")
        st.markdown("#### ➕ Create User")
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                u_username  = st.text_input("Username *", placeholder="anil.kumar")
                u_fullname  = st.text_input("Full Name *", placeholder="Kakarala Anil Kumar")
                u_email     = st.text_input("Email *", placeholder="anil@milvian.com")
            with col2:
                role_names  = [r.name for r in roles]
                u_role      = st.selectbox("Role *", role_names)
                u_password  = st.text_input("Password *", type="password", placeholder="min 6 characters")
                u_confirm   = st.text_input("Confirm Password *", type="password")

            st.caption("ℹ️ Password is hashed with SHA-256 and never stored in plain text.")
            create_btn = st.form_submit_button("👤 Create User", use_container_width=True)

        if create_btn:
            if not all([u_username, u_fullname, u_email, u_password]):
                st.error("All fields are required.")
            elif u_password != u_confirm:
                st.error("Passwords do not match.")
            elif len(u_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif db.query(AppUser).filter_by(username=u_username).first():
                st.error(f"Username **{u_username}** already exists.")
            elif db.query(AppUser).filter_by(email=u_email).first():
                st.error(f"Email **{u_email}** already registered.")
            else:
                role_obj = db.query(Role).filter_by(name=u_role).first()
                db.add(AppUser(
                    username=u_username, full_name=u_fullname, email=u_email,
                    password_hash=hash_password(u_password),
                    role_id=role_obj.id, is_active=True, is_first_login=True,
                ))
                db.commit()
                st.success(f"✅ User **{u_username}** ({u_role}) created successfully!")
                st.rerun()

        # ── Edit / Deactivate user ─────────────────────────────────────────────
        if users:
            st.markdown("---")
            st.markdown("#### ✏️ Edit User")
            sel_user = st.selectbox("Select user to edit", [u.username for u in users])
            u_obj    = db.query(AppUser).filter_by(username=sel_user).first()
            if u_obj:
                with st.form("edit_user_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        eu_name    = st.text_input("Full Name", value=u_obj.full_name)
                        eu_email   = st.text_input("Email", value=u_obj.email)
                    with col2:
                        eu_role    = st.selectbox("Role", role_names, index=role_names.index(u_obj.role.name) if u_obj.role else 0)
                        eu_active  = st.checkbox("Active", value=u_obj.is_active)
                        eu_newpw   = st.text_input("New Password (leave blank to keep)", type="password")
                    save_btn = st.form_submit_button("💾 Save Changes")

                if save_btn:
                    role_obj = db.query(Role).filter_by(name=eu_role).first()
                    u_obj.full_name = eu_name
                    u_obj.email     = eu_email
                    u_obj.role_id   = role_obj.id
                    u_obj.is_active = eu_active
                    if eu_newpw:
                        u_obj.password_hash = hash_password(eu_newpw)
                        u_obj.is_first_login = False
                    db.commit()
                    st.success(f"✅ User **{sel_user}** updated!")
                    st.rerun()
    finally:
        db.close()


elif "Settings" in page:
    st.markdown('<div class="main-title">⚙️ System Settings</div>', unsafe_allow_html=True)
    st.markdown("---")
    db = get_db()
    try:
        configs = db.query(SystemConfig).order_by(SystemConfig.key).all()
        if configs:
            rows = [{"Key": c.key, "Value": c.value, "Description": c.description or ""} for c in configs]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("#### Update Config")
        all_keys = [c.key for c in configs]
        if not all_keys:
            st.info("No configuration entries found. Run python main.py to seed system config.")
        else:
            sel_key  = st.selectbox("Config Key", all_keys)
            new_val  = st.text_input("New Value")
            if st.button("💾 Update"):
                c = db.query(SystemConfig).filter_by(key=sel_key).first()
                if c:
                    c.value = new_val
                    db.commit()
                    st.success(f"✅ {sel_key} updated!")

        st.markdown("---")
        st.markdown("#### Database Stats")
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Ledgers",       db.query(Ledger).count())
        col2.metric("Vouchers",      db.query(Voucher).count())
        col3.metric("Transactions",  db.query(Transaction).count())
        col4.metric("Documents",     db.query(Document).count())

    finally:
        db.close()
