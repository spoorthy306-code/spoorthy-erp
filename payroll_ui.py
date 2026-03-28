"""
payroll_ui.py — Zoho Payroll-style UI for SPOORTHY ERP
Tabs: Employees | Pay Runs | Taxes & Forms | Reports
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from db.schema import SessionLocal, Employee, Voucher, Transaction, Ledger, VoucherType, TDSChallan


# ── Helpers ───────────────────────────────────────────────────────────────────

def _db():
    return SessionLocal()

def _fmt(val):
    try:
        return f"₹{float(val):,.2f}"
    except:
        return "₹0.00"

def _avatar(name: str, size=36, bg="#007aff") -> str:
    initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
    return f"""<div style="width:{size}px;height:{size}px;border-radius:50%;
        background:{bg};color:#fff;display:inline-flex;align-items:center;
        justify-content:center;font-weight:700;font-size:{size//3}px;
        flex-shrink:0;">{initials}</div>"""

_AVATAR_COLORS = ["#007aff","#34c759","#ff9500","#af52de","#ff2d55","#5ac8fa","#ff6b35","#30d158"]

def _emp_color(idx: int) -> str:
    return _AVATAR_COLORS[idx % len(_AVATAR_COLORS)]

def _salary_structure(emp) -> dict:
    gross = float(emp.gross_salary or 0)
    basic_pct = float(emp.basic_pct or 50)
    hra_pct   = float(emp.hra_pct or 40)
    conveyance = float(emp.conveyance or 1600)
    basic      = round(gross * basic_pct / 100, 2)
    hra        = round(basic * hra_pct / 100, 2)
    fixed_all  = round(gross - basic - hra - conveyance, 2)
    return {
        "Basic":                (basic,     round(basic * 12, 2),     f"{basic_pct:.0f}% of CTC"),
        "House Rent Allowance": (hra,       round(hra * 12, 2),       f"{hra_pct:.0f}% of Basic"),
        "Conveyance Allowance": (conveyance,round(conveyance * 12, 2),"Fixed"),
        "Fixed Allowance":      (fixed_all, round(fixed_all * 12, 2), "Balance"),
        "Cost to Company":      (gross,     round(gross * 12, 2),     ""),
    }


# ── Main Render ───────────────────────────────────────────────────────────────

def render_payroll_page():
    st.markdown('<div class="main-title">👥 Payroll</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Milvian Technologies &nbsp;·&nbsp; FY 2025-26 &nbsp;·&nbsp; {date.today().strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["👤  Employees", "💰  Pay Runs", "📋  Taxes & Forms", "📊  Reports"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — EMPLOYEES
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        db = _db()
        try:
            employees = db.query(Employee).filter_by(is_active=True).order_by(Employee.emp_code).all()

            # ── Top action bar ────────────────────────────────────────────────
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                search_q = st.text_input("", placeholder="🔍  Search by name, code, designation…", label_visibility="collapsed")
            with col_b:
                st.markdown(f"""<div style="padding:8px 0; color:#86868b; font-size:0.85rem;">
                    <b style="color:#1d1d1f; font-size:1.1rem;">{len(employees)}</b>&nbsp; Active Employees</div>""",
                    unsafe_allow_html=True)
            with col_c:
                if st.button("➕  Add Employee", type="primary", use_container_width=True):
                    st.session_state["show_add_emp"] = True

            # ── Filter ────────────────────────────────────────────────────────
            if search_q:
                q = search_q.lower()
                employees = [e for e in employees if q in e.name.lower()
                             or q in (e.emp_code or "").lower()
                             or q in (e.designation or "").lower()]

            # ── Employee List Table (Zoho style) ─────────────────────────────
            if employees:
                selected_emp_id = st.session_state.get("selected_emp_id")

                for idx, emp in enumerate(employees):
                    bg = _emp_color(idx)
                    is_selected = str(emp.id) == str(selected_emp_id)
                    row_bg = "#f0f6ff" if is_selected else "#ffffff"
                    border = f"border-left:3px solid {bg}" if is_selected else "border-left:3px solid transparent"

                    col_av, col_info, col_stat, col_btn = st.columns([0.5, 3, 1.5, 1])
                    with col_av:
                        st.markdown(_avatar(emp.name, bg=bg), unsafe_allow_html=True)
                    with col_info:
                        work_email = emp.work_email or (emp.pan or "—")
                        st.markdown(f"""
                        <div style="padding:2px 0;">
                            <div style="font-weight:600;color:#1d1d1f;font-size:0.92rem;">{emp.name}</div>
                            <div style="color:#86868b;font-size:0.78rem;">{emp.emp_code} &nbsp;·&nbsp; {emp.designation or '—'}</div>
                            <div style="color:#86868b;font-size:0.78rem;">{work_email}</div>
                        </div>""", unsafe_allow_html=True)
                    with col_stat:
                        badge_color = "#34c759" if emp.is_active else "#ff3b30"
                        st.markdown(f'<span style="background:{badge_color}22;color:{badge_color};padding:3px 10px;border-radius:980px;font-size:0.72rem;font-weight:600;">{"Active" if emp.is_active else "Inactive"}</span>', unsafe_allow_html=True)
                    with col_btn:
                        if st.button("View →", key=f"view_emp_{emp.id}", use_container_width=True):
                            st.session_state["selected_emp_id"] = emp.id
                            st.rerun()

                    st.markdown('<hr style="margin:4px 0;border-color:#f0f0f0;">', unsafe_allow_html=True)

            else:
                st.info("No active employees found.")

        finally:
            db.close()

        # ── Employee Detail Panel ─────────────────────────────────────────────
        if "selected_emp_id" in st.session_state and st.session_state["selected_emp_id"]:
            db2 = _db()
            try:
                emp = db2.query(Employee).filter_by(id=st.session_state["selected_emp_id"]).first()
                if emp:
                    st.markdown("---")
                    # Header
                    idx2 = 0
                    hcol1, hcol2, hcol3 = st.columns([0.5, 4, 1])
                    with hcol1:
                        st.markdown(_avatar(emp.name, size=48, bg=_emp_color(idx2)), unsafe_allow_html=True)
                    with hcol2:
                        st.markdown(f"""
                        <div>
                          <span style="font-weight:700;font-size:1.05rem;color:#1d1d1f;">{emp.name}</span>
                          &nbsp;<span style="background:#dcfce7;color:#065f46;padding:2px 8px;border-radius:980px;font-size:0.72rem;font-weight:600;">Active</span>
                          <div style="color:#86868b;font-size:0.8rem;">{emp.emp_code} &nbsp;·&nbsp; {emp.designation or '—'} &nbsp;·&nbsp; {emp.department or '—'}</div>
                        </div>""", unsafe_allow_html=True)
                    with hcol3:
                        if st.button("✕ Close", key="close_emp"):
                            del st.session_state["selected_emp_id"]
                            st.rerun()

                    # Sub-tabs
                    et1, et2, et3, et4 = st.tabs(["📋 Overview", "💵 Salary Details", "🧾 Payslips", "🏦 Loans"])

                    # ── Overview ──────────────────────────────────────────────
                    with et1:
                        oc1, oc2 = st.columns(2)
                        with oc1:
                            st.markdown("**Basic Information**")
                            info = {
                                "Employee ID":   emp.emp_code,
                                "Full Name":     emp.name,
                                "Designation":   emp.designation or "—",
                                "Department":    emp.department or "—",
                                "Work Location": emp.work_location or "Head Office",
                                "Date of Joining": emp.doj.strftime("%d/%m/%Y") if emp.doj else "—",
                                "Gender":        emp.gender or "—",
                                "Work Email":    emp.work_email or "—",
                                "Mobile":        emp.mobile or "—",
                                "Portal Access": "✅ Enabled" if emp.portal_access else "❌ Disabled",
                            }
                            for label, val in info.items():
                                st.markdown(f"""<div style="display:flex;padding:5px 0;border-bottom:1px solid #f5f5f7;">
                                    <div style="width:140px;color:#86868b;font-size:0.82rem;">{label}</div>
                                    <div style="color:#1d1d1f;font-size:0.82rem;font-weight:500;">{val}</div>
                                </div>""", unsafe_allow_html=True)

                            st.markdown("<br>**Statutory Information**", unsafe_allow_html=True)
                            for label, enabled in [("EPF", emp.epf_enabled), ("ESI", emp.esi_enabled), ("Professional Tax", emp.pt_enabled)]:
                                color = "#34c759" if enabled else "#ff3b30"
                                status = "Enabled" if enabled else "Disabled"
                                st.markdown(f"""<div style="display:flex;align-items:center;padding:5px 0;border-bottom:1px solid #f5f5f7;">
                                    <div style="width:140px;color:#86868b;font-size:0.82rem;">{label}</div>
                                    <span style="background:{color}22;color:{color};padding:2px 9px;border-radius:980px;font-size:0.72rem;font-weight:600;">{status}</span>
                                </div>""", unsafe_allow_html=True)

                        with oc2:
                            st.markdown("**Personal Information**")
                            pinfo = {
                                "Date of Birth": emp.dob.strftime("%d/%m/%Y") if emp.dob else "—",
                                "Father's Name": emp.father_name or "—",
                                "PAN":           emp.pan or "—",
                                "UAN":           emp.uan_no or "—",
                                "PF Number":     emp.pf_no or "—",
                                "ESIC Number":   emp.esic_no or "—",
                            }
                            for label, val in pinfo.items():
                                st.markdown(f"""<div style="display:flex;padding:5px 0;border-bottom:1px solid #f5f5f7;">
                                    <div style="width:130px;color:#86868b;font-size:0.82rem;">{label}</div>
                                    <div style="color:#1d1d1f;font-size:0.82rem;font-weight:500;">{val}</div>
                                </div>""", unsafe_allow_html=True)

                            st.markdown("<br>**Payment Information**", unsafe_allow_html=True)
                            acct = emp.bank_account_no or ""
                            masked = f"XXXX{acct[-4:]}" if len(acct) >= 4 else acct or "—"
                            bpinfo = {
                                "Payment Mode": emp.payment_mode or "Manual Bank Transfer",
                                "Account":      masked,
                                "Bank Name":    emp.bank_name or "—",
                                "IFSC":         emp.ifsc_code or "—",
                            }
                            for label, val in bpinfo.items():
                                st.markdown(f"""<div style="display:flex;padding:5px 0;border-bottom:1px solid #f5f5f7;">
                                    <div style="width:130px;color:#86868b;font-size:0.82rem;">{label}</div>
                                    <div style="color:#1d1d1f;font-size:0.82rem;font-weight:500;">{val}</div>
                                </div>""", unsafe_allow_html=True)

                        # ── Edit Employee Form ──────────────────────────────
                        with st.expander("✏️  Edit Employee Details"):
                            with st.form(f"edit_emp_{emp.id}"):
                                fc1, fc2, fc3 = st.columns(3)
                                with fc1:
                                    n_name   = st.text_input("Full Name*", value=emp.name)
                                    n_desig  = st.text_input("Designation", value=emp.designation or "")
                                    n_dept   = st.text_input("Department", value=emp.department or "")
                                    n_loc    = st.text_input("Work Location", value=emp.work_location or "Head Office")
                                    n_gender = st.selectbox("Gender", ["—","Male","Female","Other"],
                                                             index=["—","Male","Female","Other"].index(emp.gender or "—") if emp.gender in ["—","Male","Female","Other"] else 0)
                                with fc2:
                                    n_email  = st.text_input("Work Email", value=emp.work_email or "")
                                    n_mobile = st.text_input("Mobile", value=emp.mobile or "")
                                    n_doj    = st.date_input("Date of Joining", value=emp.doj or date.today(), format="DD/MM/YYYY")
                                    n_dob    = st.date_input("Date of Birth", value=emp.dob or date(1990,1,1), format="DD/MM/YYYY")
                                    n_father = st.text_input("Father's Name", value=emp.father_name or "")
                                with fc3:
                                    n_pan    = st.text_input("PAN", value=emp.pan or "")
                                    n_uan    = st.text_input("UAN", value=emp.uan_no or "")
                                    n_bank   = st.text_input("Bank Account No", value=emp.bank_account_no or "")
                                    n_ifsc   = st.text_input("IFSC Code", value=emp.ifsc_code or "")
                                    n_bname  = st.text_input("Bank Name", value=emp.bank_name or "")
                                sc1, sc2, sc3 = st.columns(3)
                                with sc1:
                                    n_gross  = st.number_input("Gross Salary/Month (₹)*", value=float(emp.gross_salary or 0), format="%.2f", min_value=0.0)
                                    n_basic  = st.number_input("Basic %", value=float(emp.basic_pct or 50), min_value=0.0, max_value=100.0)
                                with sc2:
                                    n_hra    = st.number_input("HRA % of Basic", value=float(emp.hra_pct or 40), min_value=0.0, max_value=100.0)
                                    n_conv   = st.number_input("Conveyance/Month (₹)", value=float(emp.conveyance or 1600), format="%.2f", min_value=0.0)
                                with sc3:
                                    n_epf    = st.checkbox("EPF Enabled", value=bool(emp.epf_enabled))
                                    n_esi    = st.checkbox("ESI Enabled", value=bool(emp.esi_enabled))
                                    n_pt     = st.checkbox("Prof. Tax Enabled", value=bool(emp.pt_enabled))
                                    n_portal = st.checkbox("Portal Access", value=bool(emp.portal_access))
                                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                    emp.name            = n_name
                                    emp.designation     = n_desig
                                    emp.department      = n_dept
                                    emp.work_location   = n_loc
                                    emp.gender          = None if n_gender == "—" else n_gender
                                    emp.work_email      = n_email
                                    emp.mobile          = n_mobile
                                    emp.doj             = n_doj
                                    emp.dob             = n_dob
                                    emp.father_name     = n_father
                                    emp.pan             = n_pan
                                    emp.uan_no          = n_uan
                                    emp.bank_account_no = n_bank
                                    emp.ifsc_code       = n_ifsc
                                    emp.bank_name       = n_bname
                                    emp.gross_salary    = n_gross
                                    emp.basic_pct       = n_basic
                                    emp.hra_pct         = n_hra
                                    emp.conveyance      = n_conv
                                    emp.epf_enabled     = n_epf
                                    emp.esi_enabled     = n_esi
                                    emp.pt_enabled      = n_pt
                                    emp.portal_access   = n_portal
                                    db2.commit()
                                    st.success("✅ Employee updated!")
                                    st.rerun()

                    # ── Salary Details ────────────────────────────────────────
                    with et2:
                        gross = float(emp.gross_salary or 0)
                        annual = gross * 12
                        mc1, mc2 = st.columns(2)
                        mc1.metric("Annual CTC", f"₹{annual:,.2f}")
                        mc2.metric("Monthly CTC", f"₹{gross:,.2f}")
                        st.markdown("---")
                        st.markdown("**Salary Structure**")
                        struct = _salary_structure(emp)
                        rows = []
                        for comp, (monthly, yearly, note) in struct.items():
                            rows.append({
                                "Salary Component": comp,
                                "Basis":            note,
                                "Monthly (₹)":      f"{monthly:,.2f}",
                                "Annual (₹)":       f"{yearly:,.2f}",
                            })
                        df = pd.DataFrame(rows)
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        st.markdown("---")
                        st.markdown("**Deductions**")
                        pf_emp  = round(min(gross * 0.12, 1800), 2) if emp.epf_enabled else 0
                        esi_emp = round(gross * 0.0075, 2) if emp.esi_enabled and gross <= 21000 else 0
                        pt_amt  = 200.0 if emp.pt_enabled and gross >= 15000 else (150.0 if emp.pt_enabled and gross >= 10000 else 0)
                        net_pay = gross - pf_emp - esi_emp - pt_amt

                        ded_rows = []
                        if pf_emp: ded_rows.append({"Deduction": "Provident Fund (Employee 12%)", "Monthly (₹)": f"{pf_emp:,.2f}", "Annual (₹)": f"{pf_emp*12:,.2f}"})
                        if esi_emp: ded_rows.append({"Deduction": "ESI (Employee 0.75%)", "Monthly (₹)": f"{esi_emp:,.2f}", "Annual (₹)": f"{esi_emp*12:,.2f}"})
                        if pt_amt: ded_rows.append({"Deduction": "Professional Tax", "Monthly (₹)": f"{pt_amt:,.2f}", "Annual (₹)": f"{pt_amt*12:,.2f}"})
                        if ded_rows:
                            st.dataframe(pd.DataFrame(ded_rows), use_container_width=True, hide_index=True)

                        st.markdown(f"""<div style="background:#f0f6ff;border-radius:12px;padding:14px 20px;margin-top:12px;display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-weight:600;color:#1d1d1f;">Estimated Net Take-Home</span>
                            <span style="font-size:1.3rem;font-weight:700;color:#007aff;">₹{net_pay:,.2f} / month</span>
                        </div>""", unsafe_allow_html=True)

                    # ── Payslips & Forms ──────────────────────────────────────
                    with et3:
                        fy = st.selectbox("Financial Year", ["2025-26", "2024-25"], key=f"fy_sel_{emp.id}")
                        months = ["April","May","June","July","August","September","October","November","December","January","February","March"]
                        yr_start = 2025 if fy.startswith("2025") else 2024
                        payslip_data = []
                        for i, m in enumerate(months):
                            yr = yr_start if i < 9 else yr_start + 1
                            pay_dt = date(yr + (1 if i >= 9 else 0), (i + 4 if i < 9 else i - 8), 5)
                            if pay_dt <= date.today():
                                payslip_data.append({"Pay Date": pay_dt.strftime("%d/%m/%Y"), "Month": f"{m} {yr}", "Payslip": "📄 View", "TDS Sheet": "📋 View"})
                        if payslip_data:
                            st.dataframe(pd.DataFrame(payslip_data), use_container_width=True, hide_index=True)
                        else:
                            st.info("No payslips generated for this period yet.")

                        st.markdown("---")
                        st.markdown("**Form 16**")
                        st.info(f"Form 16 not yet generated for {fy}. Process all pay runs and file Form 24Q first.")

                    # ── Loans ──────────────────────────────────────────────────
                    with et4:
                        st.info("No active loans for this employee.")
                        if st.button("➕ Add Loan", key=f"add_loan_{emp.id}"):
                            st.info("Loan module coming soon.")
            finally:
                db2.close()

        # ── Add Employee Form ─────────────────────────────────────────────────
        if st.session_state.get("show_add_emp"):
            st.markdown("---")
            st.markdown("#### ➕ Add New Employee")
            with st.form("add_employee_form"):
                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    ne_code  = st.text_input("Employee Code*", placeholder="MG120")
                    ne_name  = st.text_input("Full Name*")
                    ne_desig = st.text_input("Designation", placeholder="Software Engineer")
                    ne_dept  = st.text_input("Department", placeholder="Engineering")
                    ne_loc   = st.text_input("Work Location", placeholder="Head Office")
                with fc2:
                    ne_email  = st.text_input("Work Email", placeholder="name@company.com")
                    ne_mobile = st.text_input("Mobile", placeholder="+91 99999 00000")
                    ne_gender = st.selectbox("Gender", ["Male","Female","Other"])
                    ne_doj    = st.date_input("Date of Joining", value=date.today(), format="DD/MM/YYYY")
                    ne_dob    = st.date_input("Date of Birth", value=date(1995,1,1), format="DD/MM/YYYY")
                with fc3:
                    ne_pan    = st.text_input("PAN", placeholder="AABCS1234C")
                    ne_gross  = st.number_input("Gross Salary/Month (₹)*", min_value=0.0, format="%.2f")
                    ne_basic  = st.number_input("Basic %", value=50.0, min_value=0.0, max_value=100.0)
                    ne_hra    = st.number_input("HRA % of Basic", value=50.0, min_value=0.0, max_value=100.0)
                    ne_epf    = st.checkbox("EPF Enabled")
                    ne_esi    = st.checkbox("ESI Enabled")
                    ne_pt     = st.checkbox("Prof. Tax Enabled", value=True)
                sc1, sc2 = st.columns(2)
                with sc1:
                    ne_bank  = st.text_input("Bank Account No")
                    ne_bname = st.text_input("Bank Name", placeholder="SBI / HDFC / ICICI")
                with sc2:
                    ne_ifsc  = st.text_input("IFSC Code", placeholder="SBIN0001234")
                    ne_mode  = st.selectbox("Payment Mode", ["Manual Bank Transfer","NEFT","RTGS","Cheque"])
                col_sub, col_can = st.columns(2)
                with col_sub:
                    if st.form_submit_button("➕ Add Employee", use_container_width=True):
                        if ne_code and ne_name and ne_gross:
                            db3 = _db()
                            try:
                                db3.add(Employee(
                                    emp_code=ne_code, name=ne_name, designation=ne_desig,
                                    department=ne_dept, work_location=ne_loc, work_email=ne_email,
                                    mobile=ne_mobile, gender=ne_gender, doj=ne_doj, dob=ne_dob,
                                    pan=ne_pan, gross_salary=ne_gross, basic_pct=ne_basic,
                                    hra_pct=ne_hra, epf_enabled=ne_epf, esi_enabled=ne_esi,
                                    pt_enabled=ne_pt, bank_account_no=ne_bank, bank_name=ne_bname,
                                    ifsc_code=ne_ifsc, payment_mode=ne_mode, is_active=True,
                                ))
                                db3.commit()
                                st.success(f"✅ Employee {ne_code} — {ne_name} added!")
                                st.session_state["show_add_emp"] = False
                                st.rerun()
                            except Exception as e:
                                db3.rollback()
                                st.error(f"Error: {e}")
                            finally:
                                db3.close()
                        else:
                            st.warning("Employee Code, Name and Gross Salary are required.")
                with col_can:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state["show_add_emp"] = False
                        st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — PAY RUNS
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        pr_tab1, pr_tab2 = st.tabs(["🚀 Run Payroll", "📜 Payroll History"])

        with pr_tab1:
            db = _db()
            try:
                employees = db.query(Employee).filter_by(is_active=True).all()
                emp_count = len(employees)

                # ── Pay Run Card (Zoho style) ─────────────────────────────────
                today = date.today()
                pay_month_date = date(today.year, today.month, 1)
                due_date = date(today.year + (1 if today.month == 12 else 0),
                                (today.month % 12) + 1, 3)

                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e8e8ed;border-radius:18px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,0.06);margin-bottom:16px;">
                    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                        <span style="font-size:1.1rem;font-weight:700;color:#1d1d1f;">Process Pay Run for {today.strftime('%B %Y')}</span>
                        <span style="background:#fef9c3;color:#92400e;padding:3px 10px;border-radius:980px;font-size:0.72rem;font-weight:700;">READY</span>
                    </div>
                    <div style="display:flex;gap:40px;">
                        <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">Employees' Net Pay</div>
                             <div style="font-size:1rem;font-weight:600;color:#1d1d1f;">YET TO PROCESS</div></div>
                        <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">Payment Date</div>
                             <div style="font-size:1rem;font-weight:600;color:#1d1d1f;">{due_date.strftime('%d/%m/%Y')}</div></div>
                        <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">No. of Employees</div>
                             <div style="font-size:1rem;font-weight:600;color:#1d1d1f;">{emp_count}</div></div>
                    </div>
                    <div style="margin-top:12px;font-size:0.78rem;color:#86868b;">
                        ℹ️ Please process and approve this pay run before {due_date.strftime('%d/%m/%Y')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Config & Process ──────────────────────────────────────────
                col_cfg1, col_cfg2 = st.columns(2)
                with col_cfg1:
                    pay_period = st.selectbox("Pay Period", [
                        f"{today.strftime('%B %Y')}",
                        f"{(today.replace(day=1) - timedelta(days=1)).strftime('%B %Y')}",
                    ])
                with col_cfg2:
                    pay_bank = st.selectbox("Payment Bank", ["BANK01 — SBI Current", "BANK02 — HDFC Current"])
                bank_code = pay_bank.split(" — ")[0]

                if employees and st.button("💰  Process & Approve Pay Run", type="primary", use_container_width=True):
                    total_gross = total_pf = total_esi = total_tds = total_net = 0.0
                    payslip_rows = []
                    for emp in employees:
                        gross  = float(emp.gross_salary or 0)
                        pf_emp = round(min(gross * 0.12, 1800), 2) if emp.epf_enabled else 0
                        pf_er  = round(min(gross * 0.12, 1800), 2) if emp.epf_enabled else 0
                        esi_emp= round(gross * 0.0075, 2) if emp.esi_enabled and gross <= 21000 else 0
                        esi_er = round(gross * 0.0325, 2) if emp.esi_enabled and gross <= 21000 else 0
                        pt     = 200.0 if emp.pt_enabled and gross >= 15000 else 0
                        tds    = round(max(0, gross * 12 - 250000) / 12 * 0.05, 2)
                        net    = round(gross - pf_emp - esi_emp - pt - tds, 2)
                        total_gross += gross; total_pf += pf_emp + pf_er
                        total_esi   += esi_emp + esi_er; total_tds += tds; total_net += net
                        payslip_rows.append({
                            "Employee": emp.name, "Code": emp.emp_code,
                            "Gross (₹)": f"{gross:,.2f}", "PF (₹)": f"{pf_emp:,.2f}",
                            "ESI (₹)": f"{esi_emp:,.2f}", "PT (₹)": f"{pt:,.2f}",
                            "TDS (₹)": f"{tds:,.2f}", "Net Pay (₹)": f"{net:,.2f}",
                        })

                    from app import get_db as _adb, next_voucher_no, post_double_entry
                    adb = _adb()
                    try:
                        jv_entries = [
                            {"ledger_code":"IE001",   "debit":total_gross,"credit":0,         "narration":f"Gross salary {pay_period}"},
                            {"ledger_code":"PF_EMP",  "debit":0,"credit":total_pf,            "narration":"PF payable"},
                            {"ledger_code":"ESI_EMP", "debit":0,"credit":total_esi,           "narration":"ESI payable"},
                            {"ledger_code":"TDS_192", "debit":0,"credit":total_tds,           "narration":"TDS on salary"},
                            {"ledger_code":bank_code, "debit":0,"credit":total_net,           "narration":"Net salary disbursed"},
                        ]
                        vno = next_voucher_no(adb, "PYRL")
                        post_double_entry(adb, vno, "PYRL", date.today(),
                                          f"Payroll — {pay_period}", jv_entries, total=total_gross)
                        kc1, kc2, kc3, kc4 = st.columns(4)
                        kc1.metric("Gross Payroll", f"₹{total_gross:,.2f}")
                        kc2.metric("PF + ESI",      f"₹{(total_pf+total_esi):,.2f}")
                        kc3.metric("TDS Deducted",  f"₹{total_tds:,.2f}")
                        kc4.metric("Net Disbursed", f"₹{total_net:,.2f}")
                        st.success(f"✅  Payroll JV **{vno}** posted successfully!")
                        st.markdown("#### Employee-wise Payslip Summary")
                        st.dataframe(pd.DataFrame(payslip_rows), use_container_width=True, hide_index=True)
                    finally:
                        adb.close()
            finally:
                db.close()

        with pr_tab2:
            db = _db()
            try:
                vouchers = db.query(Voucher).filter(
                    Voucher.voucher_type_code == "PYRL",
                    Voucher.status == "POSTED"
                ).order_by(Voucher.date.desc()).limit(24).all()
                if vouchers:
                    rows = [{"Voucher No": v.voucher_no,
                             "Period": v.narration.replace("Payroll — ","") if v.narration else "—",
                             "Date": v.date.strftime("%d/%m/%Y") if v.date else "—",
                             "Total (₹)": f"{float(v.total_amount or 0):,.2f}",
                             "Status": v.status}
                            for v in vouchers]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.info("No payroll history yet. Process a pay run to see it here.")
            finally:
                db.close()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — TAXES & FORMS
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        tf1, tf2, tf3 = st.tabs(["📌 TDS Liabilities", "🧾 Challans", "📑 Form 24Q / Form 16"])

        with tf1:
            tl_tab1, tl_tab2 = st.tabs(["Unpaid", "Paid"])
            with tl_tab1:
                # Compute TDS liabilities from posted payroll vouchers
                db = _db()
                try:
                    tds_led = db.query(Ledger).filter_by(code="TDS_192").first()
                    months_data = []
                    today = date.today()
                    for offset in range(1, 4):
                        mo = today.month - offset
                        yr = today.year
                        if mo <= 0: mo += 12; yr -= 1
                        month_start = date(yr, mo, 1)
                        if mo == 12: month_end = date(yr+1, 1, 1) - timedelta(days=1)
                        else:        month_end = date(yr, mo+1, 1) - timedelta(days=1)
                        due = date(yr, mo+1 if mo < 12 else 1, 7)
                        if mo == 3: due = date(yr, 4, 30)
                        overdue_days = (today - due).days if today > due else 0
                        months_data.append((month_start, month_end, due, overdue_days))

                    for mo_start, mo_end, due_dt, overdue in months_data:
                        mo_name = mo_start.strftime("%B %Y")
                        tds_amt = 214864.0  # placeholder — from actual posted vouchers
                        color = "#ff3b30" if overdue > 0 else "#ff9500"
                        badge = f'<span style="background:#fee2e2;color:#ff3b30;padding:2px 8px;border-radius:980px;font-size:0.7rem;font-weight:700;">OVERDUE BY {overdue} DAYS</span>' if overdue > 0 else '<span style="background:#fef9c3;color:#92400e;padding:2px 8px;border-radius:980px;font-size:0.7rem;font-weight:700;">UPCOMING</span>'
                        st.markdown(f"""
                        <div style="border:1px solid #e8e8ed;border-left:4px solid {color};border-radius:12px;padding:18px;margin-bottom:10px;background:#fff;">
                            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                                <b style="color:#1d1d1f;">TDS Liability for {mo_name}</b> {badge}
                            </div>
                            <div style="display:flex;gap:40px;">
                                <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">Total TDS</div>
                                     <div style="font-weight:600;color:#1d1d1f;">₹{tds_amt:,.2f}</div></div>
                                <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">Period</div>
                                     <div style="font-weight:600;color:#1d1d1f;">{mo_start.strftime('%d/%m/%Y')} – {mo_end.strftime('%d/%m/%Y')}</div></div>
                                <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">Due Date</div>
                                     <div style="font-weight:600;color:{'#ff3b30' if overdue>0 else '#1d1d1f'};">{due_dt.strftime('%d/%m/%Y')}</div></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"View Details →", key=f"tds_{mo_start}"):
                            st.info(f"TDS detail for {mo_name} — add challan to mark paid.")
                finally:
                    db.close()
            with tl_tab2:
                st.info("No paid TDS challans recorded yet.")

        with tf2:
            db = _db()
            try:
                challans = db.query(TDSChallan).order_by(TDSChallan.payment_date.desc()).all()
                col_ch1, col_ch2 = st.columns([4,1])
                with col_ch2:
                    if st.button("➕ New Challan", type="primary", use_container_width=True):
                        st.session_state["show_challan_form"] = True

                if challans:
                    rows = [{
                        "Challan No":    c.challan_no,
                        "BSR Code":      c.bsr_code if hasattr(c, "bsr_code") else "—",
                        "Section":       c.section,
                        "Paid Date":     c.payment_date.strftime("%d/%m/%Y") if c.payment_date else "—",
                        "Deductee":      c.deductee_name,
                        "PAN":           c.deductee_pan or "—",
                        "TDS (₹)":       f"{float(c.tds_amount or 0):,.2f}",
                        "Total (₹)":     f"{float(c.total or 0):,.2f}",
                    } for c in challans]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.info("No TDS challans recorded yet. Add one to associate with TDS liabilities.")

                if st.session_state.get("show_challan_form"):
                    with st.form("add_challan"):
                        st.markdown("#### Add TDS Challan")
                        cc1, cc2, cc3 = st.columns(3)
                        with cc1:
                            ch_no    = st.text_input("Challan No*", placeholder="00253")
                            ch_bsr   = st.text_input("BSR Code*", placeholder="6390009")
                            ch_sec   = st.selectbox("Section", ["192","194A","194C","194H","194I","194J"])
                        with cc2:
                            ch_name  = st.text_input("Deductee Name*")
                            ch_pan   = st.text_input("PAN")
                            ch_date  = st.date_input("Payment Date", value=date.today(), format="DD/MM/YYYY")
                        with cc3:
                            ch_tds   = st.number_input("TDS Amount (₹)*", min_value=0.0, format="%.2f")
                            ch_sur   = st.number_input("Surcharge (₹)", min_value=0.0, format="%.2f")
                            ch_cess  = st.number_input("Education Cess (₹)", min_value=0.0, format="%.2f")
                        ch_total = ch_tds + ch_sur + ch_cess
                        st.metric("Total Challan Amount", f"₹{ch_total:,.2f}")
                        if st.form_submit_button("💾 Save Challan", use_container_width=True):
                            if ch_no and ch_name:
                                new_ch = TDSChallan(
                                    challan_no=ch_no, section=ch_sec,
                                    deductee_name=ch_name, deductee_pan=ch_pan,
                                    payment_date=ch_date, tds_amount=ch_tds,
                                    surcharge=ch_sur, cess=ch_cess, total=ch_total,
                                )
                                if hasattr(new_ch, "bsr_code"):
                                    new_ch.bsr_code = ch_bsr
                                db.add(new_ch); db.commit()
                                st.success(f"✅ Challan {ch_no} saved!")
                                st.session_state["show_challan_form"] = False
                                st.rerun()
            finally:
                db.close()

        with tf3:
            st.markdown("#### Form 24Q — Quarterly TDS Returns")
            today = date.today()
            quarters = [
                ("Q1", date(2025,4,1),  date(2025,6,30),  date(2025,7,31),  144),
                ("Q2", date(2025,7,1),  date(2025,9,30),  date(2025,10,31), 52),
                ("Q3", date(2025,10,1), date(2025,12,31), date(2026,1,31),  -1),
                ("Q4", date(2026,1,1),  date(2026,3,31),  date(2026,5,31),  0),
            ]
            for q, start, end, due, overdue in quarters:
                overdue_days = (today - due).days if today > due else 0
                if overdue_days > 0:
                    badge = f'<span style="background:#fee2e2;color:#ff3b30;padding:2px 8px;border-radius:980px;font-size:0.7rem;font-weight:700;">OVERDUE BY {overdue_days} DAYS</span>'
                    color = "#ff3b30"
                elif today > end:
                    badge = '<span style="background:#fef9c3;color:#92400e;padding:2px 8px;border-radius:980px;font-size:0.7rem;font-weight:700;">DUE SOON</span>'
                    color = "#ff9500"
                else:
                    badge = '<span style="background:#f0f6ff;color:#007aff;padding:2px 8px;border-radius:980px;font-size:0.7rem;font-weight:700;">UPCOMING</span>'
                    color = "#007aff"
                st.markdown(f"""
                <div style="border:1px solid #e8e8ed;border-left:4px solid {color};border-radius:12px;padding:16px;margin-bottom:8px;background:#fff;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <b style="color:#1d1d1f;">Form 24Q — {q} ({start.strftime('%b %Y')} to {end.strftime('%b %Y')})</b> {badge}
                    </div>
                    <div style="display:flex;gap:40px;">
                        <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">Due Date</div>
                             <div style="font-weight:600;color:#1d1d1f;">{due.strftime('%d/%m/%Y')}</div></div>
                        <div><div style="font-size:0.7rem;color:#86868b;text-transform:uppercase;letter-spacing:0.8px;">Deposit Period</div>
                             <div style="font-weight:600;color:#1d1d1f;">{start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Form 16 — Annual TDS Certificate")
            st.markdown("""
            <div style="background:#fff;border:1px solid #e8e8ed;border-radius:16px;padding:24px;text-align:center;">
                <div style="font-size:2rem;margin-bottom:8px;">📋</div>
                <div style="font-weight:600;color:#1d1d1f;margin-bottom:4px;">Generate Form 16 for FY 2025-26</div>
                <div style="color:#86868b;font-size:0.85rem;margin-bottom:16px;">
                    Steps: Upload Part A → Generate → Sign → Publish/Email to Employees
                </div>
                <div style="display:flex;justify-content:center;gap:24px;flex-wrap:wrap;">
                    <div style="text-align:center;"><div style="width:40px;height:40px;border-radius:50%;background:#007aff;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;margin:0 auto 6px;">1</div><div style="font-size:0.78rem;color:#86868b;">Upload Part A</div></div>
                    <div style="font-size:1.2rem;color:#d2d2d7;padding-top:8px;">→</div>
                    <div style="text-align:center;"><div style="width:40px;height:40px;border-radius:50%;background:#e8e8ed;color:#86868b;display:flex;align-items:center;justify-content:center;font-weight:700;margin:0 auto 6px;">2</div><div style="font-size:0.78rem;color:#86868b;">Generate</div></div>
                    <div style="font-size:1.2rem;color:#d2d2d7;padding-top:8px;">→</div>
                    <div style="text-align:center;"><div style="width:40px;height:40px;border-radius:50%;background:#e8e8ed;color:#86868b;display:flex;align-items:center;justify-content:center;font-weight:700;margin:0 auto 6px;">3</div><div style="font-size:0.78rem;color:#86868b;">Sign</div></div>
                    <div style="font-size:1.2rem;color:#d2d2d7;padding-top:8px;">→</div>
                    <div style="text-align:center;"><div style="width:40px;height:40px;border-radius:50%;background:#e8e8ed;color:#86868b;display:flex;align-items:center;justify-content:center;font-weight:700;margin:0 auto 6px;">4</div><div style="font-size:0.78rem;color:#86868b;">Publish</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — REPORTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown("**Payroll Overview**")
            for r in ["Payroll Summary","Salary Register - Monthly","Salary Statement","Pay Summary","Payroll Liability Summary","LOP Summary","Variable Pay Earnings Report"]:
                if st.button(f"📄 {r}", key=f"rpt_{r}", use_container_width=True):
                    st.session_state["active_payroll_report"] = r
        with rc2:
            st.markdown("**Statutory Reports**")
            for r in ["EPF Summary","EPF-ECR Report","ESI Summary","ESIC Return","PT Summary","PT Monthly Statement","LWF Summary"]:
                if st.button(f"📋 {r}", key=f"rpt_{r}", use_container_width=True):
                    st.session_state["active_payroll_report"] = r
        with rc3:
            st.markdown("**Employee Reports**")
            for r in ["Compensation Details","Reimbursement Summary","Perquisite Summary","Full & Final Settlement"]:
                if st.button(f"👤 {r}", key=f"rpt_{r}", use_container_width=True):
                    st.session_state["active_payroll_report"] = r

        if st.session_state.get("active_payroll_report"):
            rpt = st.session_state["active_payroll_report"]
            st.markdown("---")
            st.markdown(f"#### {rpt}")

            if rpt == "Payroll Summary":
                db = _db()
                try:
                    employees = db.query(Employee).filter_by(is_active=True).all()
                    yr_filter = st.selectbox("Period", ["This Year", "Last Month", "This Month"], key="rpt_period")
                    totals = {"Basic":0,"HRA":0,"Conveyance":0,"Fixed Allowance":0,
                              "Gross":0,"PF Employee":0,"ESI Employee":0,"Prof. Tax":0,"Net Pay":0}
                    for emp in employees:
                        gross = float(emp.gross_salary or 0)
                        s = _salary_structure(emp)
                        totals["Basic"]          += s["Basic"][0]
                        totals["HRA"]            += s["House Rent Allowance"][0]
                        totals["Conveyance"]     += s["Conveyance Allowance"][0]
                        totals["Fixed Allowance"]+= s["Fixed Allowance"][0]
                        totals["Gross"]          += gross
                        totals["PF Employee"]    += round(min(gross * 0.12, 1800), 2) if emp.epf_enabled else 0
                        totals["ESI Employee"]   += round(gross * 0.0075, 2) if emp.esi_enabled and gross <= 21000 else 0
                        totals["Prof. Tax"]      += 200.0 if emp.pt_enabled and gross >= 15000 else 0
                        totals["Net Pay"]        += gross - totals["PF Employee"] - totals["ESI Employee"] - totals["Prof. Tax"]

                    summary_rows = [{"Pay Component": k, "Monthly Amount (₹)": f"{v:,.2f}", "Annual Amount (₹)": f"{v*12:,.2f}"} for k, v in totals.items()]
                    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
                    col_e, col_d = st.columns(2)
                    col_e.download_button("⬇️ Export CSV", pd.DataFrame(summary_rows).to_csv(index=False), f"payroll_summary.csv", "text/csv")
                finally:
                    db.close()
            else:
                st.info(f"Report '{rpt}' — select a period and click Run Report.")
                st.button("▶️ Run Report", key="run_rpt")
