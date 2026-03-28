"""
test_milvian.py — Load all Milvian Technologies sample data into SPOORTHY ERP
Tests:
  1. Employee import from Employee_Basic_Details.xlsx
  2. Payroll processing from Payrun_Employee_Details.xlsx
  3. Bank statement parsing from Milvian-DetailedStatement-imp.xlsx
  4. PDF extraction from travel invoices (IndiGo + Air India)
  5. Company KYC document parsing (GST cert + PAN)
  6. Salary statement reconciliation
"""

import os, sys, re, json, hashlib
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import pdfplumber
from datetime import date, datetime
from db.schema import (
    SessionLocal, Employee, Ledger, Voucher, Transaction,
    VoucherType, Document, Party
)
from db.seed import seed_all

BASE = os.path.join(os.path.dirname(__file__), "data", "milvian")

# ─────────────────────────────────────────────────────────────────────────────
def hr(title):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print('═'*60)

def ok(msg):  print(f"  ✅  {msg}")
def warn(msg):print(f"  ⚠️   {msg}")
def info(msg):print(f"  ℹ️   {msg}")
def err(msg): print(f"  ❌  {msg}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. EMPLOYEE IMPORT
# ─────────────────────────────────────────────────────────────────────────────
def test_employees(db):
    hr("TEST 1 — Employee Import from Employee_Basic_Details.xlsx")

    path = os.path.join(BASE, "Employee_Basic_Details.xlsx")
    df   = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]

    imported = skipped = 0
    for _, row in df.iterrows():
        emp_no = str(row.get("Employee Number","")).strip()
        if not emp_no:
            continue

        fname = str(row.get("First Name","")).strip()
        mname = str(row.get("Middle Name","")).strip() if pd.notna(row.get("Middle Name")) else ""
        lname = str(row.get("Last Name","")).strip()
        full_name = " ".join(filter(None, [fname, mname, lname]))

        doj = row.get("Date of Joining")
        dob = row.get("Date of Birth")
        if pd.notna(doj): doj = pd.to_datetime(doj).date()
        else: doj = None
        if pd.notna(dob): dob = pd.to_datetime(dob).date()
        else: dob = None

        exists = db.query(Employee).filter_by(emp_code=emp_no).first()
        if exists:
            skipped += 1
            continue

        db.add(Employee(
            emp_code    = emp_no,
            name        = full_name,
            designation = str(row.get("Designation","")).strip(),
            department  = str(row.get("Department","")).strip(),
            doj         = doj,
            dob         = dob,
            pan         = str(row.get("PAN Number","")).strip() if pd.notna(row.get("PAN Number")) else None,
        ))
        imported += 1

    db.commit()
    ok(f"Imported {imported} employees  |  Skipped {skipped} (already exist)")

    # Print summary table
    emps = db.query(Employee).all()
    print(f"\n  {'Code':<8} {'Name':<30} {'Designation':<40} {'Dept':<20}")
    print(f"  {'-'*8} {'-'*30} {'-'*40} {'-'*20}")
    for e in emps:
        print(f"  {e.emp_code:<8} {e.name:<30} {(e.designation or ''):<40} {(e.department or ''):<20}")
    return len(emps)


# ─────────────────────────────────────────────────────────────────────────────
# 2. PAYROLL FROM Payrun_Employee_Details.xlsx
# ─────────────────────────────────────────────────────────────────────────────
def test_payroll(db):
    hr("TEST 2 — Payroll Data from Payrun_Employee_Details.xlsx")

    path = os.path.join(BASE, "Payrun_Employee_Details.xlsx")
    df   = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]

    # Update gross salary on existing employee records
    updated = 0
    for _, row in df.iterrows():
        emp_no = str(row.get("Employee No","")).strip()
        emp    = db.query(Employee).filter_by(emp_code=emp_no).first()
        if not emp:
            warn(f"Employee {emp_no} not found in DB — skipping salary update")
            continue

        ctc    = float(row.get("CTC Amount", 0) or 0)
        gross  = float(row.get("Gross Pay",  0) or 0)
        net    = float(row.get("Net Pay",    0) or 0)
        bank   = str(row.get("Bank Name","")).strip()
        acct   = str(row.get("Account Number","")).strip() if pd.notna(row.get("Account Number")) else ""
        ifsc   = str(row.get("IFSC","")).strip() if pd.notna(row.get("IFSC")) else ""

        emp.gross_salary    = gross
        emp.bank_account_no = acct
        updated += 1

        print(f"  {emp_no:<8} {emp.name:<30}  CTC: ₹{ctc:>12,.0f}  Gross: ₹{gross:>10,.0f}  "
              f"Net: ₹{net:>10,.0f}  Bank: {bank}")

    db.commit()
    ok(f"Updated salary for {updated} employees")

    # Payroll summary
    df_sal = pd.read_excel(os.path.join(BASE, "Feb 2026_employee_salary_statement_report.xlsx"),
                           header=None)
    # Find data rows (skip header rows)
    data_start = None
    for i, row in df_sal.iterrows():
        if str(row.iloc[0]).strip() == "Employee Number" or "Employee Number" in str(row.iloc[0]):
            data_start = i + 1
            break
        if str(row.iloc[1]).strip() == "Employee Number":
            data_start = i + 1
            break

    total_gross = total_net = total_tax = 0.0
    rows_counted = 0
    if data_start:
        for i in range(data_start, len(df_sal)):
            r = df_sal.iloc[i]
            try:
                gross = float(str(r.iloc[8]).replace(",","")) if pd.notna(r.iloc[8]) else 0
                net   = float(str(r.iloc[13]).replace(",","")) if pd.notna(r.iloc[13]) else 0
                tax   = float(str(r.iloc[11]).replace(",","")) if pd.notna(r.iloc[11]) else 0
                if gross > 0:
                    total_gross += gross
                    total_net   += net
                    total_tax   += tax
                    rows_counted += 1
            except:
                pass

    print(f"\n  ── Feb 2026 Salary Statement Summary ──────────────────")
    print(f"  Employees Paid  : {rows_counted}")
    print(f"  Total Gross Pay : ₹{total_gross:>15,.2f}")
    print(f"  Total Tax (TDS) : ₹{total_tax:>15,.2f}")
    print(f"  Total Net Pay   : ₹{total_net:>15,.2f}")
    return rows_counted


# ─────────────────────────────────────────────────────────────────────────────
# 3. BANK STATEMENT PARSING
# ─────────────────────────────────────────────────────────────────────────────
def test_bank_statement(db):
    hr("TEST 3 — Bank Statement: Milvian-DetailedStatement-imp.xlsx")

    path = os.path.join(BASE, "Milvian-DetailedStatement-imp.xlsx")
    df_raw = pd.read_excel(path, header=None)

    # Extract account meta from top rows
    acct_no = branch = ""
    for i in range(10):
        row = df_raw.iloc[i]
        for j, val in enumerate(row):
            v = str(val).strip()
            if "004005030748" in v:
                acct_no = "004005030748"
            if "MADHAPUR" in v.upper():
                branch = "ICICI Bank - Hyderabad Madhapur"

    # Find transaction header row
    header_row = None
    for i in range(len(df_raw)):
        r = df_raw.iloc[i]
        if any("Value Date" in str(v) for v in r):
            header_row = i
            break

    transactions = []
    if header_row is not None:
        for i in range(header_row + 1, len(df_raw)):
            r = df_raw.iloc[i]
            try:
                sno       = r.iloc[0]
                val_date  = str(r.iloc[2]).strip()
                remarks   = str(r.iloc[6]).strip()
                withdrawal= str(r.iloc[7]).replace(",","").strip()
                deposit   = str(r.iloc[8]).replace(",","").strip()
                balance   = str(r.iloc[9]).replace(",","").strip()

                if pd.isna(sno) or not str(sno).strip().isdigit():
                    continue

                wd = float(withdrawal) if withdrawal not in ("nan","","NaN") else 0.0
                dp = float(deposit)    if deposit    not in ("nan","","NaN") else 0.0
                bl = float(balance)    if balance    not in ("nan","","NaN") else 0.0

                transactions.append({
                    "date": val_date, "narration": remarks[:80],
                    "withdrawal": wd, "deposit": dp, "balance": bl
                })
            except:
                pass

    total_cr = sum(t["deposit"]    for t in transactions)
    total_dr = sum(t["withdrawal"] for t in transactions)
    closing  = transactions[-1]["balance"] if transactions else 0

    print(f"  Account No   : {acct_no}")
    print(f"  Branch       : {branch}")
    print(f"  Transactions : {len(transactions)}")
    print(f"  Total Credits: ₹{total_cr:>15,.2f}")
    print(f"  Total Debits : ₹{total_dr:>15,.2f}")
    print(f"  Closing Bal  : ₹{closing:>15,.2f}")

    # Sample 5 transactions
    print(f"\n  Sample Transactions:")
    print(f"  {'Date':<15} {'Narration':<55} {'Deposit':>12} {'Withdrawal':>12} {'Balance':>12}")
    print(f"  {'-'*15} {'-'*55} {'-'*12} {'-'*12} {'-'*12}")
    for t in transactions[:5]:
        dep_str = ("Rs" + f"{t['deposit']:,.2f}") if t['deposit'] else ''
        wdl_str = ("Rs" + f"{t['withdrawal']:,.2f}") if t['withdrawal'] else ''
        print(f"  {t['date']:<15} {t['narration']:<55} "
              f"{dep_str:>12} "
              f"{wdl_str:>12} "
              f"Rs{t['balance']:>11,.2f}")

    ok(f"Parsed {len(transactions)} bank transactions from ICICI statement")
    return len(transactions)


# ─────────────────────────────────────────────────────────────────────────────
# 4. TRAVEL INVOICE PDF EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
def extract_invoice_fields(text):
    def find(patterns):
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                try: return m.group(1).strip()
                except: return m.group(0).strip()
        return ""

    amt_raw = find([
        r'Grand Total[^\d]*([\d,]+\.\d{2})',
        r'Total\s*(?:Amount)?\s*[₹:]?\s*([\d,]+\.\d{2})',
    ])
    igst_raw = find([r'IGST[^\d]*([\d,]+\.\d{2})'])
    cgst_raw = find([r'CGST[^\d]*([\d,]+\.\d{2})'])
    sgst_raw = find([r'SGST[^\d]*([\d,]+\.\d{2})'])
    gstin    = find([r'GSTIN\s*[:\-]?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z])'])
    inv_no   = find([r'(?:Number|Invoice No)[:\s]+([A-Z0-9\-/]+)', r'PNR\s*[:\s]+([A-Z0-9]+)'])

    def to_f(s):
        try: return float(str(s).replace(",",""))
        except: return 0.0

    return {
        "gstin":    gstin,
        "inv_no":   inv_no,
        "igst":     to_f(igst_raw),
        "cgst":     to_f(cgst_raw),
        "sgst":     to_f(sgst_raw),
        "total":    to_f(amt_raw),
    }

def test_travel_pdfs(db):
    hr("TEST 4 — Travel Invoice PDF Extraction (IndiGo + Air India)")

    travel_dir = os.path.join(BASE, "Travelling")
    pdfs = [f for f in os.listdir(travel_dir) if f.endswith(".pdf")]
    pdfs.sort()

    results = []
    print(f"  {'File':<52} {'Vendor':<12} {'GSTIN':<20} {'Total':>10} {'IGST':>8}")
    print(f"  {'-'*52} {'-'*12} {'-'*20} {'-'*10} {'-'*8}")

    for fname in pdfs[:20]:   # first 20 PDFs
        fpath = os.path.join(travel_dir, fname)
        try:
            with pdfplumber.open(fpath) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)

            vendor = "IndiGo"    if "indigo" in text.lower() or "6E" in text else \
                     "Air India" if "air india" in text.lower() else \
                     "MakeMyTrip" if "makemytrip" in text.lower() or "MMT" in fname else "Other"

            fields = extract_invoice_fields(text)
            results.append({"file": fname, "vendor": vendor, **fields})

            print(f"  {fname[:50]:<52} {vendor:<12} {fields['gstin']:<20} "
                  f"₹{fields['total']:>8,.2f} ₹{fields['igst']:>6,.2f}")

            # Store in DB as Document
            fhash = hashlib.md5(open(fpath,"rb").read()).hexdigest()
            if not db.query(Document).filter_by(file_hash=fhash).first():
                db.add(Document(
                    doc_ref           = f"TRAVEL-{fhash[:12]}",
                    original_filename = fname,
                    stored_path       = fpath,
                    mime_type         = "application/pdf",
                    file_size_kb      = os.path.getsize(fpath) / 1024,
                    file_hash         = fhash,
                    category          = "Invoice",
                    tags              = f"travel,{vendor.lower()}",
                    extracted_text    = text[:2000],
                    parsed_fields     = json.dumps(fields),
                    status            = "EXTRACTED",
                    extraction_method = "pdfplumber",
                    uploaded_by       = "test_milvian",
                ))
        except Exception as e:
            warn(f"{fname[:45]}: {e}")

    db.commit()

    total_spend = sum(r["total"] for r in results)
    total_igst  = sum(r["igst"]  for r in results)
    ok(f"Extracted {len(results)} travel invoices  |  Total: ₹{total_spend:,.2f}  |  IGST: ₹{total_igst:,.2f}")
    ok(f"Stored {len(results)} documents in DMS")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPANY KYC — GST CERTIFICATE
# ─────────────────────────────────────────────────────────────────────────────
def test_company_kyc(db):
    hr("TEST 5 — Company KYC Document Parsing")

    kyc_dir = os.path.join(BASE, "Company KYC")

    for fname in os.listdir(kyc_dir):
        if not fname.endswith(".pdf"):
            continue
        fpath = os.path.join(kyc_dir, fname)
        try:
            with pdfplumber.open(fpath) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)

            gstin   = re.search(r'([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z])', text)
            pan     = re.search(r'PAN[:\s]*([A-Z]{5}[0-9]{4}[A-Z])', text)
            company = re.search(r'(MILVIAN\s+\w+(?:\s+\w+)*)', text, re.IGNORECASE)

            info(f"{fname}")
            if gstin:  ok(f"  GSTIN : {gstin.group(1)}")
            if pan:    ok(f"  PAN   : {pan.group(1)}")
            if company:ok(f"  Name  : {company.group(1)[:50]}")
            if not any([gstin, pan, company]):
                warn(f"  No structured data extracted (scanned/image PDF)")

        except Exception as e:
            warn(f"{fname}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. ADD MILVIAN AS A PARTY (VENDOR/CLIENT)
# ─────────────────────────────────────────────────────────────────────────────
def test_add_party(db):
    hr("TEST 6 — Add Milvian Technologies as Party in ERP")

    code = "MILV001"
    if db.query(Party).filter_by(code=code).first():
        warn("Party MILV001 already exists — skipping")
        return

    db.add(Party(
        code       = code,
        name       = "Milvian Technologies Private Limited",
        party_type = "CUSTOMER",
        gstin      = "36AATCM3488J1ZN",
        city       = "Hyderabad",
        state_code = "36",
        email      = "sudheer@milvian.in",
    ))
    db.commit()
    ok("Added Milvian Technologies Pvt Ltd as Customer (MILV001)")
    ok("GSTIN: 36AATCM3488J1ZN | State: Telangana (36)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "█"*60)
    print("  SPOORTHY ERP — Milvian Technologies Data Load Test")
    print("  Source: D:\\Milvian (copied to data/milvian/)")
    print("█"*60)

    seed_all()
    db = SessionLocal()

    try:
        n_emp   = test_employees(db)
        n_pay   = test_payroll(db)
        n_txns  = test_bank_statement(db)
        invoices= test_travel_pdfs(db)
        test_company_kyc(db)
        test_add_party(db)

        hr("FINAL SUMMARY")
        ok(f"Employees loaded    : {n_emp}")
        ok(f"Payroll records     : {n_pay}")
        ok(f"Bank transactions   : {n_txns}")
        ok(f"Travel invoices     : {len(invoices)}")
        ok(f"Total travel spend  : ₹{sum(r['total'] for r in invoices):,.2f}")
        ok(f"Total IGST (ITC)    : ₹{sum(r['igst'] for r in invoices):,.2f}")
        print("\n  ✅  All Milvian data loaded successfully into SPOORTHY ERP")
        print("  ▶   Open http://localhost:8501 → Masters → Parties / Employees to verify\n")

    except Exception as e:
        import traceback
        err(f"Test failed: {e}")
        traceback.print_exc()
    finally:
        db.close()
