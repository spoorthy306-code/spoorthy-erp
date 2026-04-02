"""
Spoorthy ERP
db/seed.py — Complete default master data seeder
Seeds: Groups, Ledgers, Tax Ledgers, Units, Currencies,
       Voucher Types, Fiscal Year, GST Registration, System Config
"""

import sys, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.schema import (
    engine, SessionLocal, create_all_tables,
    AccountGroup, Ledger, StockUnit, StockGroup, Currency,
    VoucherType, FiscalYear, SystemConfig, CostCentre,
    Company, Role, AppUser, GSTRegistration, Party, OrgLocation
)
from datetime import date


def seed_all(force: bool = False):
    create_all_tables()
    db = SessionLocal()
    try:
        _seed_company(db, force)
        _seed_groups(db, force)
        _seed_ledgers(db, force)
        _seed_tax_ledgers(db, force)
        _seed_stock_units(db, force)
        _seed_stock_groups(db, force)
        _seed_currencies(db, force)
        _seed_voucher_types(db, force)
        _seed_fiscal_year(db, force)
        _seed_cost_centres(db, force)
        _seed_system_config(db, force)
        _seed_roles(db, force)
        _seed_admin_user(db, force)
        _seed_gst_registration(db, force)
        _seed_default_parties(db, force)
        _seed_org_location(db, force)
        db.commit()
        print("\n✅  Spoorthy ERP — All master data seeded successfully.\n")
    except Exception as e:
        db.rollback()
        print(f"❌  Seed error: {e}")
        raise
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
def _upsert(db, Model, key_field, records, label):
    inserted = 0
    for r in records:
        exists = db.query(Model).filter(
            getattr(Model, key_field) == r[key_field]
        ).first()
        if not exists:
            db.add(Model(**r))
            inserted += 1
    db.flush()
    print(f"  ✅  {label:<30} {inserted:>4} records")
    return inserted


# ─────────────────────────────────────────────────────────────────────────────
def _seed_company(db, force):
    if db.query(Company).first():
        print(f"  ✅  {'Company Profile':<30}    0 records (exists)")
        return
    db.add(Company(
        name="SPOORTHY GROUP",
        legal_name="Spoorthy Enterprises Private Limited",
        gstin="36AABCS1234C1ZP",
        pan="AABCS1234C",
        tan="HYDS12345A",
        address_line1="Plot No. 42, HITEC City",
        address_line2="Madhapur",
        city="Hyderabad",
        state_code="36",
        pincode="500081",
        country="India",
        phone="+91-40-12345678",
        email="accounts@spoorthy.in",
        website="https://spoorthy.in",
        fiscal_year_start="04-01",
        currency="INR",
        date_format="DD-MM-YYYY",
        industry="Manufacturing & Trading",
        reg_date=date(2010, 4, 1),
        invoice_footer_text="Thank you for your business. Payment due within 30 days.",
        subscription_plan="ENTERPRISE",
        einvoice_enabled=True,
        eway_bill_enabled=True,
        eway_bill_threshold=50000,
        is_setup_done=True,
    ))
    db.flush()
    print(f"  ✅  {'Company Profile':<30}    1 records")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_roles(db, force):
    roles = [
        {"name":"ADMIN",      "description":"Full system access",          "can_post":True,  "can_approve":True,  "can_delete":True,  "can_export":True, "can_admin":True,  "can_view_reports":True,  "can_manage_masters":True},
        {"name":"ACCOUNTANT", "description":"Accounting & voucher posting", "can_post":True,  "can_approve":False, "can_delete":False, "can_export":True, "can_admin":False, "can_view_reports":True,  "can_manage_masters":False},
        {"name":"AUDITOR",    "description":"Read-only audit access",       "can_post":False, "can_approve":False, "can_delete":False, "can_export":True, "can_admin":False, "can_view_reports":True,  "can_manage_masters":False},
        {"name":"HR",         "description":"HR & Payroll module",          "can_post":True,  "can_approve":False, "can_delete":False, "can_export":True, "can_admin":False, "can_view_reports":False, "can_manage_masters":False},
        {"name":"VIEWER",     "description":"Read-only access",             "can_post":False, "can_approve":False, "can_delete":False, "can_export":False,"can_admin":False, "can_view_reports":True,  "can_manage_masters":False},
    ]
    _upsert(db, Role, "name", roles, "Roles (5)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_admin_user(db, force):
    if db.query(AppUser).filter_by(username="admin").first():
        print(f"  ✅  {'Admin User':<30}    0 records (exists)")
        return
    admin_role = db.query(Role).filter_by(name="ADMIN").first()
    if not admin_role:
        return
    pw_hash = hashlib.sha256("admin@123".encode()).hexdigest()
    db.add(AppUser(
        username="admin",
        full_name="System Administrator",
        email="admin@spoorthy.in",
        password_hash=pw_hash,
        role_id=admin_role.id,
        is_active=True,
        is_first_login=True,
    ))
    db.flush()
    print(f"  ✅  {'Admin User':<30}    1 records  [admin / admin@123]")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_gst_registration(db, force):
    if db.query(GSTRegistration).first():
        print(f"  ✅  {'GST Registration':<30}    0 records (exists)")
        return
    db.add(GSTRegistration(
        gstin="36AABCS1234C1ZP",
        trade_name="SPOORTHY GROUP",
        legal_name="Spoorthy Enterprises Private Limited",
        state_code="36",
        reg_type="Regular",
        is_primary=True,
        reg_date=date(2018, 7, 1),
        email="gst@spoorthy.in",
        mobile="+91-9876543210",
    ))
    db.flush()
    print(f"  ✅  {'GST Registration':<30}    1 records")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_default_parties(db, force):
    parties = [
        {"code":"CUST001","name":"ABC Traders",          "party_type":"CUSTOMER","gstin":"27AABCA1234C1Z5","city":"Mumbai",    "state_code":"27","credit_days":30,"credit_limit":500000},
        {"code":"CUST002","name":"XYZ Enterprises",      "party_type":"CUSTOMER","gstin":"29AABCX1234C1Z1","city":"Bangalore", "state_code":"29","credit_days":45,"credit_limit":1000000},
        {"code":"CUST003","name":"PQR Industries",       "party_type":"CUSTOMER","gstin":"36AABCP1234C1Z3","city":"Hyderabad", "state_code":"36","credit_days":30,"credit_limit":750000},
        {"code":"SUPP001","name":"Raw Material Suppliers","party_type":"SUPPLIER","gstin":"27AABCR1234C1Z9","city":"Pune",     "state_code":"27","credit_days":30,"credit_limit":0},
        {"code":"SUPP002","name":"XYZ Supplier Pvt Ltd", "party_type":"SUPPLIER","gstin":"06AABCX1234C1Z3","city":"Delhi",    "state_code":"06","credit_days":45,"credit_limit":0},
        {"code":"CASH_PARTY","name":"Cash Customer",     "party_type":"CUSTOMER","city":"Hyderabad","state_code":"36","credit_days":0,"credit_limit":0},
    ]
    inserted = 0
    for p in parties:
        if not db.query(Party).filter_by(code=p["code"]).first():
            db.add(Party(**p))
            inserted += 1
    db.flush()
    print(f"  ✅  {'Default Parties':<30} {inserted:>4} records")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_org_location(db, force):
    if db.query(OrgLocation).first():
        print(f"  ✅  {'Org Locations':<30}    0 records (exists)")
        return
    locs = [
        OrgLocation(name="Head Office – Hyderabad",  gstin="36AABCS1234C1ZP", city="Hyderabad", state_code="36", pincode="500081", is_primary=True,  is_active=True),
        OrgLocation(name="Branch – Mumbai",          gstin="27AABCS1234C1ZP", city="Mumbai",    state_code="27", pincode="400001", is_primary=False, is_active=True),
        OrgLocation(name="Warehouse – Pune",         city="Pune",             state_code="27",  pincode="411001", is_primary=False, is_active=True),
    ]
    for l in locs:
        db.add(l)
    db.flush()
    print(f"  ✅  {'Org Locations':<30}    3 records")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_groups(db, force):
    records = [
        # ── Capital & Liabilities ────────────────────────────────────────────
        {"code":"CAP",  "name":"Capital Account",         "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"RES",  "name":"Reserves & Surplus",      "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"SCL",  "name":"Secured Loans",           "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"USL",  "name":"Unsecured Loans",         "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"CL",   "name":"Current Liabilities",     "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"SUP",  "name":"Sundry Creditors",        "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"DUT",  "name":"Duties & Taxes",          "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"PRO",  "name":"Provisions",              "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        {"code":"BKOD", "name":"Bank OD Accounts",        "group_type":"LIABILITY", "affects_gross":False, "is_system":True},
        # ── Assets ───────────────────────────────────────────────────────────
        {"code":"FA",   "name":"Fixed Assets",            "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"INVST","name":"Investments",             "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"CA",   "name":"Current Assets",          "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"STK",  "name":"Stock-in-Hand",           "group_type":"ASSET",     "affects_gross":True,  "is_system":True},
        {"code":"DEP",  "name":"Deposits (Asset)",        "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"LNA",  "name":"Loans & Advances (Asset)","group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"SUN",  "name":"Sundry Debtors",          "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"CASH", "name":"Cash-in-Hand",            "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"BANK", "name":"Bank Accounts",           "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        {"code":"MISC", "name":"Misc. Expenses (Asset)",  "group_type":"ASSET",     "affects_gross":False, "is_system":True},
        # ── Income ───────────────────────────────────────────────────────────
        {"code":"SAL",  "name":"Sales Accounts",          "group_type":"INCOME",    "affects_gross":True,  "is_system":True},
        {"code":"DRVS", "name":"Direct Incomes",          "group_type":"INCOME",    "affects_gross":True,  "is_system":True},
        {"code":"OINC", "name":"Other Income",            "group_type":"INCOME",    "affects_gross":False, "is_system":True},
        {"code":"IDRVS","name":"Indirect Incomes",        "group_type":"INCOME",    "affects_gross":False, "is_system":True},
        # ── Expenses ─────────────────────────────────────────────────────────
        {"code":"PURCH","name":"Purchase Accounts",       "group_type":"EXPENSE",   "affects_gross":True,  "is_system":True},
        {"code":"DEXP", "name":"Direct Expenses",         "group_type":"EXPENSE",   "affects_gross":True,  "is_system":True},
        {"code":"IEXP", "name":"Indirect Expenses",       "group_type":"EXPENSE",   "affects_gross":False, "is_system":True},
        {"code":"MFG",  "name":"Manufacturing Expenses",  "group_type":"EXPENSE",   "affects_gross":True,  "is_system":True},
    ]
    _upsert(db, AccountGroup, "code", records, "Account Groups (28)")


def _get_grp(db, code):
    g = db.query(AccountGroup).filter_by(code=code).first()
    return g.id if g else None


# ─────────────────────────────────────────────────────────────────────────────
def _seed_ledgers(db, force):
    def L(code, name, grp, nature="Dr", opening=0.0, is_bank=False, is_cash=False):
        gid = _get_grp(db, grp)
        return dict(code=code, name=name, group_id=gid, nature=nature,
                    opening_balance=opening, opening_type=nature,
                    is_bank=is_bank, is_cash=is_cash)

    records = [
        # Capital
        L("CAP001","Capital Account",            "CAP","Cr"),
        L("CAP002","Drawings Account",           "CAP","Dr"),
        L("RES001","General Reserve",            "RES","Cr"),
        L("RES002","Profit & Loss Account",      "RES","Cr"),
        L("RES003","Retained Earnings",          "RES","Cr"),
        # Loans
        L("SCL001","Term Loan - SBI",            "SCL","Cr"),
        L("SCL002","Vehicle Loan",               "SCL","Cr"),
        L("USL001","Director's Loan",            "USL","Cr"),
        # Cash & Bank
        L("CASH01","Cash",                       "CASH","Dr",is_cash=True),
        L("CASH02","Petty Cash",                 "CASH","Dr",is_cash=True),
        L("BANK01","SBI Current Account",        "BANK","Dr",is_bank=True),
        L("BANK02","HDFC Current Account",       "BANK","Dr",is_bank=True),
        L("BANK03","ICICI Current Account",      "BANK","Dr",is_bank=True),
        L("BKOD01","CC Account - SBI",           "BKOD","Cr"),
        # Fixed Assets
        L("FA001","Land & Building",             "FA","Dr"),
        L("FA002","Plant & Machinery",           "FA","Dr"),
        L("FA003","Furniture & Fixtures",        "FA","Dr"),
        L("FA004","Computers & Peripherals",     "FA","Dr"),
        L("FA005","Vehicles",                    "FA","Dr"),
        L("FA006","Office Equipment",            "FA","Dr"),
        L("FA007","Accumulated Depreciation",    "FA","Cr"),
        # Investments
        L("INV001","Investments - Equity Shares","INVST","Dr"),
        L("INV002","Investments - Mutual Funds", "INVST","Dr"),
        L("INV003","Fixed Deposits with Banks",  "INVST","Dr"),
        # Debtors / Creditors
        L("SUN001","Sundry Debtors (Control)",   "SUN","Dr"),
        L("SUP001","Sundry Creditors (Control)", "SUP","Cr"),
        # Current Assets
        L("STK001","Opening Stock",              "STK","Dr"),
        L("STK002","Closing Stock",              "STK","Dr"),
        L("DEP001","Security Deposit",           "DEP","Dr"),
        L("DEP002","Rental Deposit",             "DEP","Dr"),
        L("LNA001","Advance to Staff",           "LNA","Dr"),
        L("LNA002","Advance to Suppliers",       "LNA","Dr"),
        L("LNA003","Prepaid Expenses",           "LNA","Dr"),
        L("LNA004","Advance Tax",                "LNA","Dr"),
        L("LNA005","TDS Receivable",             "LNA","Dr"),
        # Sales
        L("SAL001","Sales - Local Taxable",      "SAL","Cr"),
        L("SAL002","Sales - Local Exempt",       "SAL","Cr"),
        L("SAL003","Sales - Inter State",        "SAL","Cr"),
        L("SAL004","Sales - Export (LUT/Bond)",  "SAL","Cr"),
        L("SAL005","Sales Returns",              "SAL","Dr"),
        L("SAL006","Discount Allowed",           "SAL","Dr"),
        # Purchases
        L("PUR001","Purchases - Local Taxable",  "PURCH","Dr"),
        L("PUR002","Purchases - Local Exempt",   "PURCH","Dr"),
        L("PUR003","Purchases - Inter State",    "PURCH","Dr"),
        L("PUR004","Purchases - Import",         "PURCH","Dr"),
        L("PUR005","Purchase Returns",           "PURCH","Cr"),
        L("PUR006","Discount Received",          "PURCH","Cr"),
        L("PUR007","Freight Inward",             "DEXP","Dr"),
        # Direct Expenses
        L("DE001","Wages",                       "DEXP","Dr"),
        L("DE002","Factory Rent",                "DEXP","Dr"),
        L("DE003","Power & Fuel",                "DEXP","Dr"),
        L("DE004","Carriage Inward",             "DEXP","Dr"),
        L("DE005","Packing Charges",             "DEXP","Dr"),
        # Indirect Expenses
        L("IE001","Salaries",                    "IEXP","Dr"),
        L("IE002","Office Rent",                 "IEXP","Dr"),
        L("IE003","Electricity Charges",         "IEXP","Dr"),
        L("IE004","Telephone & Internet",        "IEXP","Dr"),
        L("IE005","Postage & Courier",           "IEXP","Dr"),
        L("IE006","Printing & Stationery",       "IEXP","Dr"),
        L("IE007","Travelling & Conveyance",     "IEXP","Dr"),
        L("IE008","Repairs & Maintenance",       "IEXP","Dr"),
        L("IE009","Depreciation",                "IEXP","Dr"),
        L("IE010","Insurance",                   "IEXP","Dr"),
        L("IE011","Audit Fees",                  "IEXP","Dr"),
        L("IE012","Legal & Professional Fees",   "IEXP","Dr"),
        L("IE013","Advertisement & Marketing",   "IEXP","Dr"),
        L("IE014","Bank Charges",                "IEXP","Dr"),
        L("IE015","Interest on Term Loan",       "IEXP","Dr"),
        L("IE016","Interest on CC / OD",         "IEXP","Dr"),
        L("IE017","Bad Debts Written Off",       "IEXP","Dr"),
        L("IE018","Miscellaneous Expenses",      "IEXP","Dr"),
        L("IE019","Staff Welfare Expenses",      "IEXP","Dr"),
        L("IE020","Vehicle Running Expenses",    "IEXP","Dr"),
        # Other Income
        L("OI001","Interest Received",           "OINC","Cr"),
        L("OI002","Commission Received",         "OINC","Cr"),
        L("OI003","Rent Received",               "OINC","Cr"),
        L("OI004","Dividend Received",           "OINC","Cr"),
        L("OI005","Profit on Sale of Assets",    "OINC","Cr"),
        L("OI006","Forex Gain",                  "OINC","Cr"),
    ]
    _upsert(db, Ledger, "code", records, "Master Ledgers (77)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_tax_ledgers(db, force):
    def T(code, name, grp, tax_type, rate, section=None):
        gid = _get_grp(db, grp)
        nature = "Cr" if grp in ("DUT","CL","PRO") else "Dr"
        return dict(code=code, name=name, group_id=gid, nature=nature,
                    is_tax_ledger=True, tax_type=tax_type, tax_rate=rate,
                    tax_section=section, opening_balance=0.0)

    records = [
        # GST Output
        T("CGST_O_5",  "Output CGST  5% (2.5%)",   "DUT","GST_OUTPUT",  2.5),
        T("SGST_O_5",  "Output SGST  5% (2.5%)",   "DUT","GST_OUTPUT",  2.5),
        T("IGST_O_5",  "Output IGST  5%",           "DUT","IGST_OUT",    5.0),
        T("CGST_O_12", "Output CGST 12% (6%)",      "DUT","GST_OUTPUT",  6.0),
        T("SGST_O_12", "Output SGST 12% (6%)",      "DUT","GST_OUTPUT",  6.0),
        T("IGST_O_12", "Output IGST 12%",           "DUT","IGST_OUT",   12.0),
        T("CGST_O_18", "Output CGST 18% (9%)",      "DUT","GST_OUTPUT",  9.0),
        T("SGST_O_18", "Output SGST 18% (9%)",      "DUT","GST_OUTPUT",  9.0),
        T("IGST_O_18", "Output IGST 18%",           "DUT","IGST_OUT",   18.0),
        T("CGST_O_28", "Output CGST 28% (14%)",     "DUT","GST_OUTPUT", 14.0),
        T("SGST_O_28", "Output SGST 28% (14%)",     "DUT","GST_OUTPUT", 14.0),
        T("IGST_O_28", "Output IGST 28%",           "DUT","IGST_OUT",   28.0),
        T("CESS_O",    "Output GST Cess",            "DUT","GST_OUTPUT",  0.0),
        # GST Input (ITC)
        T("CGST_I_5",  "Input CGST  5% (2.5%)",     "CA", "GST_INPUT",   2.5),
        T("SGST_I_5",  "Input SGST  5% (2.5%)",     "CA", "GST_INPUT",   2.5),
        T("IGST_I_5",  "Input IGST  5%",             "CA", "IGST_IN",     5.0),
        T("CGST_I_12", "Input CGST 12% (6%)",        "CA", "GST_INPUT",   6.0),
        T("SGST_I_12", "Input SGST 12% (6%)",        "CA", "GST_INPUT",   6.0),
        T("IGST_I_12", "Input IGST 12%",             "CA", "IGST_IN",    12.0),
        T("CGST_I_18", "Input CGST 18% (9%)",        "CA", "GST_INPUT",   9.0),
        T("SGST_I_18", "Input SGST 18% (9%)",        "CA", "GST_INPUT",   9.0),
        T("IGST_I_18", "Input IGST 18%",             "CA", "IGST_IN",    18.0),
        T("CGST_I_28", "Input CGST 28% (14%)",       "CA", "GST_INPUT",  14.0),
        T("SGST_I_28", "Input SGST 28% (14%)",       "CA", "GST_INPUT",  14.0),
        T("IGST_I_28", "Input IGST 28%",             "CA", "IGST_IN",    28.0),
        # TDS Payable
        T("TDS_192",  "TDS 192 - Salary",            "DUT","TDS",    10.0, "192"),
        T("TDS_194A", "TDS 194A - Interest",         "DUT","TDS",    10.0, "194A"),
        T("TDS_194C", "TDS 194C - Contractor (Ind)", "DUT","TDS",     1.0, "194C"),
        T("TDS_194C2","TDS 194C - Contractor (Co.)", "DUT","TDS",     2.0, "194C"),
        T("TDS_194H", "TDS 194H - Commission",       "DUT","TDS",     5.0, "194H"),
        T("TDS_194I", "TDS 194I - Rent (Plant)",     "DUT","TDS",     2.0, "194I"),
        T("TDS_194I2","TDS 194I - Rent (Property)",  "DUT","TDS",    10.0, "194I"),
        T("TDS_194J", "TDS 194J - Prof. Fees",       "DUT","TDS",    10.0, "194J"),
        T("TDS_194Q", "TDS 194Q - Purchases",        "DUT","TDS",     0.1, "194Q"),
        T("TDS_206C", "TCS 206C",                    "DUT","TCS",     1.0, "206C"),
        # Payroll Taxes
        T("PF_EMP",   "PF Payable - Employee 12%",   "DUT","PF",     12.0),
        T("PF_ER",    "PF Payable - Employer 12%",   "DUT","PF",     12.0),
        T("ESI_EMP",  "ESI Payable - Employee 0.75%","DUT","ESI",     0.75),
        T("ESI_ER",   "ESI Payable - Employer 3.25%","DUT","ESI",     3.25),
        T("PT_001",   "Professional Tax Payable",    "DUT","PT",      0.0),
        T("LWF_001",  "Labour Welfare Fund",         "DUT","PT",      0.0),
        # Income Tax
        T("ITAX_PAY", "Income Tax Payable",          "DUT","INCOME_TAX", 0.0),
        T("ITAX_ADV", "Advance Tax Paid",            "CA", "INCOME_TAX", 0.0),
        # Customs
        T("BCD_001",  "Basic Customs Duty",          "DUT","CUSTOMS",  0.0),
        T("IGST_IMP", "IGST on Imports",             "DUT","IGST_OUT",18.0),
    ]
    _upsert(db, Ledger, "code", records, "Tax Ledgers (46)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_stock_units(db, force):
    records = [
        # Count
        {"symbol":"NOS",  "name":"Numbers",        "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"PCS",  "name":"Pieces",          "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"DZ",   "name":"Dozen",           "unit_type":"count",  "base_symbol":"NOS","factor":12.0},
        {"symbol":"GRS",  "name":"Gross",           "unit_type":"count",  "base_symbol":"NOS","factor":144.0},
        {"symbol":"PRS",  "name":"Pairs",           "unit_type":"count",  "base_symbol":"NOS","factor":2.0},
        {"symbol":"SET",  "name":"Set",             "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"BOX",  "name":"Box",             "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"PKT",  "name":"Packet",          "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"BAG",  "name":"Bag",             "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"BTL",  "name":"Bottle",          "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"CTN",  "name":"Carton",          "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"BDL",  "name":"Bundle",          "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"ROL",  "name":"Roll",            "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        {"symbol":"SHT",  "name":"Sheet",           "unit_type":"count",  "base_symbol":"NOS","factor":1.0},
        # Weight
        {"symbol":"KG",   "name":"Kilogram",        "unit_type":"weight", "base_symbol":"KG", "factor":1.0},
        {"symbol":"G",    "name":"Gram",            "unit_type":"weight", "base_symbol":"KG", "factor":0.001},
        {"symbol":"MG",   "name":"Milligram",       "unit_type":"weight", "base_symbol":"KG", "factor":0.000001},
        {"symbol":"MT",   "name":"Metric Ton",      "unit_type":"weight", "base_symbol":"KG", "factor":1000.0},
        {"symbol":"QTL",  "name":"Quintal",         "unit_type":"weight", "base_symbol":"KG", "factor":100.0},
        {"symbol":"LB",   "name":"Pound",           "unit_type":"weight", "base_symbol":"KG", "factor":0.4536},
        # Volume
        {"symbol":"L",    "name":"Litre",           "unit_type":"volume", "base_symbol":"L",  "factor":1.0},
        {"symbol":"ML",   "name":"Millilitre",      "unit_type":"volume", "base_symbol":"L",  "factor":0.001},
        {"symbol":"KL",   "name":"Kilolitre",       "unit_type":"volume", "base_symbol":"L",  "factor":1000.0},
        {"symbol":"GAL",  "name":"Gallon (US)",     "unit_type":"volume", "base_symbol":"L",  "factor":3.785},
        # Length
        {"symbol":"MTR",  "name":"Metre",           "unit_type":"length", "base_symbol":"MTR","factor":1.0},
        {"symbol":"CM",   "name":"Centimetre",      "unit_type":"length", "base_symbol":"MTR","factor":0.01},
        {"symbol":"MM",   "name":"Millimetre",      "unit_type":"length", "base_symbol":"MTR","factor":0.001},
        {"symbol":"KM",   "name":"Kilometre",       "unit_type":"length", "base_symbol":"MTR","factor":1000.0},
        {"symbol":"FT",   "name":"Feet",            "unit_type":"length", "base_symbol":"MTR","factor":0.3048},
        {"symbol":"IN",   "name":"Inch",            "unit_type":"length", "base_symbol":"MTR","factor":0.0254},
        {"symbol":"YD",   "name":"Yard",            "unit_type":"length", "base_symbol":"MTR","factor":0.9144},
        # Area
        {"symbol":"SQM",  "name":"Square Metre",    "unit_type":"area",   "base_symbol":"SQM","factor":1.0},
        {"symbol":"SQFT", "name":"Square Feet",     "unit_type":"area",   "base_symbol":"SQM","factor":0.0929},
        {"symbol":"ACRE", "name":"Acre",            "unit_type":"area",   "base_symbol":"SQM","factor":4046.86},
        {"symbol":"SQYD", "name":"Square Yard",     "unit_type":"area",   "base_symbol":"SQM","factor":0.8361},
        # Energy / Power / Time
        {"symbol":"KWH",  "name":"Kilowatt Hour",   "unit_type":"energy", "base_symbol":"KWH","factor":1.0},
        {"symbol":"HRS",  "name":"Hours",           "unit_type":"time",   "base_symbol":"HRS","factor":1.0},
        {"symbol":"DAYS", "name":"Days",            "unit_type":"time",   "base_symbol":"HRS","factor":24.0},
        {"symbol":"MON",  "name":"Months",          "unit_type":"time",   "base_symbol":"HRS","factor":720.0},
        {"symbol":"LUMP", "name":"Lumpsum",         "unit_type":"other",  "base_symbol":"LUMP","factor":1.0},
    ]
    _upsert(db, StockUnit, "symbol", records, "Stock Units (40)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_stock_groups(db, force):
    records = [
        {"code":"ALL",  "name":"All Items (Primary)"},
        {"code":"RM",   "name":"Raw Materials"},
        {"code":"WIP",  "name":"Work-in-Progress"},
        {"code":"FG",   "name":"Finished Goods"},
        {"code":"TG",   "name":"Trading Goods"},
        {"code":"SP",   "name":"Spare Parts"},
        {"code":"CONS", "name":"Consumables"},
        {"code":"PKG",  "name":"Packing Materials"},
        {"code":"SCRAP","name":"Scrap"},
        {"code":"SVC",  "name":"Services"},
    ]
    _upsert(db, StockGroup, "code", records, "Stock Groups (10)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_currencies(db, force):
    records = [
        {"code":"INR","name":"Indian Rupee",     "symbol":"₹",   "is_base":True,  "exchange_rate":1.0},
        {"code":"USD","name":"US Dollar",        "symbol":"$",   "is_base":False, "exchange_rate":83.50},
        {"code":"EUR","name":"Euro",             "symbol":"€",   "is_base":False, "exchange_rate":90.10},
        {"code":"GBP","name":"British Pound",    "symbol":"£",   "is_base":False, "exchange_rate":105.20},
        {"code":"AED","name":"UAE Dirham",       "symbol":"د.إ", "is_base":False, "exchange_rate":22.73},
        {"code":"SGD","name":"Singapore Dollar", "symbol":"S$",  "is_base":False, "exchange_rate":62.10},
        {"code":"JPY","name":"Japanese Yen",     "symbol":"¥",   "is_base":False, "exchange_rate":0.55},
        {"code":"CHF","name":"Swiss Franc",      "symbol":"Fr",  "is_base":False, "exchange_rate":92.80},
        {"code":"CAD","name":"Canadian Dollar",  "symbol":"C$",  "is_base":False, "exchange_rate":61.50},
        {"code":"AUD","name":"Australian Dollar","symbol":"A$",  "is_base":False, "exchange_rate":53.40},
    ]
    _upsert(db, Currency, "code", records, "Currencies (10)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_voucher_types(db, force):
    records = [
        {"code":"PV",   "name":"Payment",          "prefix":"PV",   "affects_bank":True,  "affects_stock":False,"current_seq":0},
        {"code":"RV",   "name":"Receipt",          "prefix":"RV",   "affects_bank":True,  "affects_stock":False,"current_seq":0},
        {"code":"JV",   "name":"Journal",          "prefix":"JV",   "affects_bank":False, "affects_stock":False,"current_seq":0},
        {"code":"CV",   "name":"Contra",           "prefix":"CV",   "affects_bank":True,  "affects_stock":False,"current_seq":0},
        {"code":"PINV", "name":"Purchase",         "prefix":"PUR",  "affects_bank":False, "affects_stock":True, "current_seq":0},
        {"code":"PCNV", "name":"Purchase Return",  "prefix":"PRET", "affects_bank":False, "affects_stock":True, "current_seq":0},
        {"code":"SINV", "name":"Sales",            "prefix":"SAL",  "affects_bank":False, "affects_stock":True, "current_seq":0},
        {"code":"SCNV", "name":"Sales Return",     "prefix":"SRET", "affects_bank":False, "affects_stock":True, "current_seq":0},
        {"code":"DN",   "name":"Debit Note",       "prefix":"DN",   "affects_bank":False, "affects_stock":False,"current_seq":0},
        {"code":"CN",   "name":"Credit Note",      "prefix":"CN",   "affects_bank":False, "affects_stock":False,"current_seq":0},
        {"code":"PYRL", "name":"Payroll",          "prefix":"PYRL", "affects_bank":True,  "affects_stock":False,"current_seq":0},
        {"code":"BRS",  "name":"Bank Recon JV",    "prefix":"BRS",  "affects_bank":True,  "affects_stock":False,"current_seq":0},
        {"code":"GRN",  "name":"Goods Receipt",    "prefix":"GRN",  "affects_bank":False, "affects_stock":True, "current_seq":0},
        {"code":"DNO",  "name":"Delivery Note",    "prefix":"DNO",  "affects_bank":False, "affects_stock":True, "current_seq":0},
        {"code":"SJ",   "name":"Stock Journal",    "prefix":"SJ",   "affects_bank":False, "affects_stock":True, "current_seq":0},
        {"code":"DP",   "name":"Depreciation",     "prefix":"DEP",  "affects_bank":False, "affects_stock":False,"current_seq":0},
    ]
    _upsert(db, VoucherType, "code", records, "Voucher Types (16)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_fiscal_year(db, force):
    fy = db.query(FiscalYear).filter_by(label="2025-26").first()
    if not fy:
        db.add(FiscalYear(
            label="2025-26",
            start_date=date(2025, 4, 1),
            end_date=date(2026, 3, 31),
            is_current=True,
            is_closed=False
        ))
        db.flush()
        print(f"  ✅  {'Fiscal Year 2025-26':<30}    1 records")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_cost_centres(db, force):
    records = [
        {"code":"HO",    "name":"Head Office",           "budget":0.0},
        {"code":"PROD",  "name":"Production",            "budget":0.0},
        {"code":"SALES", "name":"Sales & Marketing",     "budget":0.0},
        {"code":"ADMIN", "name":"Administration",        "budget":0.0},
        {"code":"IT",    "name":"Information Technology","budget":0.0},
        {"code":"HR",    "name":"Human Resources",       "budget":0.0},
        {"code":"FIN",   "name":"Finance & Accounts",    "budget":0.0},
        {"code":"LOG",   "name":"Logistics",             "budget":0.0},
        {"code":"RND",   "name":"R & D",                 "budget":0.0},
    ]
    _upsert(db, CostCentre, "code", records, "Cost Centres (9)")


# ─────────────────────────────────────────────────────────────────────────────
def _seed_system_config(db, force):
    configs = [
        {"key":"COMPANY_NAME",     "value":"SPOORTHY GROUP",          "description":"Legal company name"},
        {"key":"COMPANY_GSTIN",    "value":"36AABCS1234C1ZP",         "description":"Primary GSTIN"},
        {"key":"BASE_CURRENCY",    "value":"INR",                     "description":"Functional currency"},
        {"key":"FISCAL_YEAR",      "value":"2025-26",                 "description":"Current FY"},
        {"key":"GST_STATE_CODE",   "value":"36",                      "description":"Telangana"},
        {"key":"DECIMAL_PLACES",   "value":"2",                       "description":"Amount decimal precision"},
        {"key":"VOUCHER_PREFIX",   "value":"SPRY",                    "description":"Global voucher prefix"},
        {"key":"TDS_DEDUCTOR_TAN", "value":"HYDS12345A",              "description":"TAN for TDS"},
        {"key":"BOOKS_START_DATE", "value":"2025-04-01",              "description":"First date of books"},
        {"key":"AUTO_ROUND_OFF",   "value":"true",                    "description":"Auto round-off to ₹1"},
        {"key":"GST_API_KEY",      "value":"",                        "description":"API Setu key for live GSTIN lookup (apisetu.gov.in)"},
    ]
    _upsert(db, SystemConfig, "key", configs, "System Config (11)")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    seed_all()
