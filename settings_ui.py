"""
settings_ui.py — Comprehensive Organisation Settings for SPOORTHY ERP
Mirrors Zoho Books settings structure: 10 top-level sections, each with tabs.
"""

import streamlit as st
import pandas as pd
import json, hashlib
from datetime import date, datetime
from db.schema import (
    SessionLocal, Company, Role, AppUser, SystemConfig,
    OrgLocation, TxnNumberSeries, ReportingTag,
    EmailTemplate, SMSTemplate,
    WorkflowRule, WorkflowAction, WorkflowLog,
    Webhook, UserPreference, ApprovalRule,
    VoucherType, Ledger, Currency, GSTRegistration,
)

# ── Indian States ─────────────────────────────────────────────────────────────
STATES = [
    "01-Jammu & Kashmir","02-Himachal Pradesh","03-Punjab","04-Chandigarh",
    "05-Uttarakhand","06-Haryana","07-Delhi","08-Rajasthan","09-Uttar Pradesh",
    "10-Bihar","11-Sikkim","12-Arunachal Pradesh","13-Nagaland","14-Manipur",
    "15-Mizoram","16-Tripura","17-Meghalaya","18-Assam","19-West Bengal",
    "20-Jharkhand","21-Odisha","22-Chhattisgarh","23-Madhya Pradesh","24-Gujarat",
    "25-Daman & Diu","26-Dadra & Nagar Haveli","27-Maharashtra","28-Andhra Pradesh",
    "29-Karnataka","30-Goa","31-Lakshadweep","32-Kerala","33-Tamil Nadu",
    "34-Puducherry","35-Andaman & Nicobar","36-Telangana","37-Andhra Pradesh (New)",
    "38-Ladakh",
]

INDUSTRIES = [
    "IT / Technology","Manufacturing","Trading","Services","Construction",
    "Healthcare","Education","Finance","Real Estate","Logistics","Other",
]

DEFAULT_ROLES = [
    {"name":"ADMIN",      "description":"Full access — all modules, settings, user management",
     "can_post":True,  "can_approve":True,  "can_delete":True,  "can_export":True,  "can_admin":True,
     "can_view_reports":True,  "can_manage_masters":True},
    {"name":"ACCOUNTANT", "description":"Post & approve vouchers, view all reports",
     "can_post":True,  "can_approve":True,  "can_delete":False, "can_export":True,  "can_admin":False,
     "can_view_reports":True,  "can_manage_masters":True},
    {"name":"HR",         "description":"Payroll, employee records, HR reports only",
     "can_post":True,  "can_approve":False, "can_delete":False, "can_export":True,  "can_admin":False,
     "can_view_reports":True,  "can_manage_masters":False},
    {"name":"AUDITOR",    "description":"Read-only — all vouchers, reports, trial balance",
     "can_post":False, "can_approve":False, "can_delete":False, "can_export":True,  "can_admin":False,
     "can_view_reports":True,  "can_manage_masters":False},
    {"name":"VIEWER",     "description":"Dashboard and reports only — no posting",
     "can_post":False, "can_approve":False, "can_delete":False, "can_export":False, "can_admin":False,
     "can_view_reports":True,  "can_manage_masters":False},
    {"name":"MANAGER",    "description":"Approve transactions, view all reports, manage masters",
     "can_post":True,  "can_approve":True,  "can_delete":False, "can_export":True,  "can_admin":False,
     "can_view_reports":True,  "can_manage_masters":True},
]

DEFAULT_EMAIL_TEMPLATES = [
    {"event_code":"INVOICE_SENT",    "subject":"Invoice {invoice_no} from {company_name}",
     "body_html":"<p>Dear {customer_name},</p><p>Please find attached Invoice <b>{invoice_no}</b> for ₹{amount} due on {due_date}.</p><p>Regards,<br>{company_name}</p>"},
    {"event_code":"PAYMENT_RECEIVED","subject":"Payment Received — {company_name}",
     "body_html":"<p>Dear {customer_name},</p><p>We have received your payment of ₹{amount} against Invoice {invoice_no}. Thank you!</p>"},
    {"event_code":"PO_SENT",         "subject":"Purchase Order {po_no} — {company_name}",
     "body_html":"<p>Dear {vendor_name},</p><p>Please find attached Purchase Order <b>{po_no}</b>.</p>"},
    {"event_code":"PAYMENT_REMINDER","subject":"Payment Due Reminder — Invoice {invoice_no}",
     "body_html":"<p>Dear {customer_name},</p><p>This is a reminder that Invoice <b>{invoice_no}</b> for ₹{amount} is due on {due_date}.</p>"},
    {"event_code":"PAYMENT_OVERDUE", "subject":"OVERDUE: Invoice {invoice_no} — Action Required",
     "body_html":"<p>Dear {customer_name},</p><p>Invoice <b>{invoice_no}</b> for ₹{amount} was due on {due_date} and is now overdue. Please settle at earliest.</p>"},
]

DEFAULT_SMS_TEMPLATES = [
    {"event_code":"INVOICE_SENT",    "message":"Invoice {invoice_no} for Rs.{amount} from {company_name}. Due: {due_date}. Pay: {portal_link}"},
    {"event_code":"PAYMENT_RECEIVED","message":"Payment of Rs.{amount} received against Invoice {invoice_no}. Thank you! -{company_name}"},
    {"event_code":"PAYMENT_REMINDER","message":"Reminder: Invoice {invoice_no} Rs.{amount} due {due_date}. Pay: {portal_link} -{company_name}"},
]

EXTRA_SYSCONFIG_KEYS = [
    ("CUSTOMER_PORTAL_ENABLED", "false",  "Enable customer self-service portal"),
    ("VENDOR_PORTAL_ENABLED",   "false",  "Enable vendor portal for PO acknowledgements"),
    ("PORTAL_SUBDOMAIN",        "",       "Portal subdomain (e.g. pay.milvian.com)"),
    ("CUSTOM_DOMAIN",           "",       "Custom domain for portal/app"),
    ("REMINDER_DUE_DAYS",       "7,3,1",  "Days before due date to send reminders (comma-separated)"),
    ("REMINDER_OVERDUE_DAYS",   "1,7,15", "Days after due to send overdue reminders"),
    ("DEFAULT_REMINDER_CHANNEL","EMAIL",  "EMAIL / SMS / BOTH"),
    ("TIMESHEET_ENABLED",       "true",   "Enable timesheet module"),
    ("PROJECT_BILLING_TYPE",    "FIXED",  "Default project billing: FIXED / HOURLY"),
    ("API_RATE_LIMIT_PER_DAY",  "1000",   "Max API calls per day per token"),
    ("EINVOICE_IRN_API_URL",    "",       "IRP endpoint for e-Invoice IRN generation"),
    ("TDS_QUARTERLY_RETURN",    "true",   "Enable quarterly TDS return (24Q/26Q)"),
    ("DEFAULT_CREDIT_DAYS",     "30",     "Default payment due days for new parties"),
    ("INVENTORY_VALUATION",     "FIFO",   "FIFO / WEIGHTED_AVG"),
    ("OPENING_BALANCE_DATE",    "2025-04-01", "Opening balance as-at date"),
    ("WHATSAPP_API_KEY",        "",       "WhatsApp Business API key"),
    ("SMS_PROVIDER",            "",       "SMS provider: TWILIO / MSG91 / TEXTLOCAL"),
    ("SMS_API_KEY",             "",       "SMS provider API key"),
]


def _cfg(db, key: str, default="") -> str:
    c = db.query(SystemConfig).filter_by(key=key).first()
    return c.value or default if c else default


def _set_cfg(db, key: str, value: str):
    c = db.query(SystemConfig).filter_by(key=key).first()
    if c:
        c.value = value
    else:
        db.add(SystemConfig(key=key, value=value))


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def fmt_date(d) -> str:
    if d is None:
        return ""
    if isinstance(d, str):
        try:
            d = datetime.strptime(d[:10], "%Y-%m-%d").date()
        except Exception:
            return d
    try:
        return d.strftime("%d-%m-%Y")
    except Exception:
        return str(d)


def _seed_defaults(db):
    """Seed roles, email/sms templates, extra SystemConfig keys on first visit."""
    for rd in DEFAULT_ROLES:
        if not db.query(Role).filter_by(name=rd["name"]).first():
            db.add(Role(**rd))
    for et in DEFAULT_EMAIL_TEMPLATES:
        if not db.query(EmailTemplate).filter_by(event_code=et["event_code"]).first():
            db.add(EmailTemplate(**et))
    for st_ in DEFAULT_SMS_TEMPLATES:
        if not db.query(SMSTemplate).filter_by(event_code=st_["event_code"]).first():
            db.add(SMSTemplate(**st_))
    for key, val, desc in EXTRA_SYSCONFIG_KEYS:
        if not db.query(SystemConfig).filter_by(key=key).first():
            db.add(SystemConfig(key=key, value=val, description=desc))
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def _section_organization(db):
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏢 Profile", "🎨 Branding", "🌐 Custom Domain",
        "📍 Locations", "✅ Approvals", "💳 Subscription",
    ])

    # ── Profile ───────────────────────────────────────────────────────────────
    with tab1:
        company  = db.query(Company).first()
        is_new   = company is None
        with st.form("co_profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                nm    = st.text_input("Company Display Name *", value=company.name if company else "", placeholder="Milvian Technologies Pvt Ltd")
                legal = st.text_input("Legal / Registered Name", value=company.legal_name or "" if company else "", placeholder="MILVIAN TECHNOLOGIES PRIVATE LIMITED")
                gstin = st.text_input("GSTIN", value=company.gstin or "" if company else "", placeholder="36AATCM3488J1ZN")
                pan   = st.text_input("PAN", value=company.pan or "" if company else "", placeholder="AATCM3488J")
                cin   = st.text_input("CIN", value=company.cin or "" if company else "", placeholder="U72900TG2020PTC140XXX")
                tan   = st.text_input("TAN", value=company.tan or "" if company else "", placeholder="HYDA12345A")
            with c2:
                ind_list = INDUSTRIES
                ind_idx  = INDUSTRIES.index(company.industry) if company and company.industry in INDUSTRIES else 0
                industry = st.selectbox("Industry", ind_list, index=ind_idx)
                reg_date = st.date_input("Date of Incorporation", value=company.reg_date or date(2020, 5, 14) if company else date(2020, 5, 14), format="DD/MM/YYYY")
                phone    = st.text_input("Phone", value=company.phone or "" if company else "", placeholder="+91 40 2345 6789")
                email    = st.text_input("Email", value=company.email or "" if company else "", placeholder="accounts@milvian.com")
                website  = st.text_input("Website", value=company.website or "" if company else "", placeholder="https://milvian.com")
                curr_idx = ["INR","USD","EUR","GBP","AED"].index(company.currency) if company and company.currency in ["INR","USD","EUR","GBP","AED"] else 0
                currency = st.selectbox("Base Currency", ["INR","USD","EUR","GBP","AED"], index=curr_idx)

            st.markdown("**Registered Address**")
            a1, a2 = st.columns(2)
            with a1:
                addr1   = st.text_input("Address Line 1", value=company.address_line1 or "" if company else "", placeholder="Plot 12, HITEC City")
                addr2   = st.text_input("Address Line 2", value=company.address_line2 or "" if company else "", placeholder="Madhapur")
                city    = st.text_input("City", value=company.city or "" if company else "", placeholder="Hyderabad")
            with a2:
                cur_sc   = (company.state_code or "36") if company else "36"
                st_idx   = next((i for i, s in enumerate(STATES) if s.startswith(cur_sc + "-")), 35)
                state    = st.selectbox("State", STATES, index=st_idx)
                pincode  = st.text_input("Pincode", value=company.pincode or "" if company else "", placeholder="500081")
                fy_start = st.selectbox("Fiscal Year Start", ["April (India Standard)", "January (Calendar Year)"],
                                        index=0 if not company or company.fiscal_year_start == "04-01" else 1)
            save = st.form_submit_button("💾 Save Profile", use_container_width=True)

        if save:
            if not nm:
                st.error("Company name is required.")
            else:
                sc    = state.split("-")[0]
                fy    = "04-01" if "April" in fy_start else "01-01"
                msme  = company.msme_udyam_no if company else None
                if is_new:
                    db.add(Company(
                        name=nm, legal_name=legal, gstin=gstin or None, pan=pan or None,
                        cin=cin or None, tan=tan or None, address_line1=addr1, address_line2=addr2,
                        city=city, state_code=sc, pincode=pincode, phone=phone, email=email,
                        website=website, currency=currency, industry=industry,
                        reg_date=reg_date, fiscal_year_start=fy, date_format="DD-MM-YYYY",
                        is_setup_done=True,
                    ))
                else:
                    company.name=nm; company.legal_name=legal; company.gstin=gstin or None
                    company.pan=pan or None; company.cin=cin or None; company.tan=tan or None
                    company.address_line1=addr1; company.address_line2=addr2; company.city=city
                    company.state_code=sc; company.pincode=pincode; company.phone=phone
                    company.email=email; company.website=website; company.currency=currency
                    company.industry=industry; company.reg_date=reg_date
                    company.fiscal_year_start=fy; company.is_setup_done=True
                db.commit()
                st.success(f"✅ Profile for **{nm}** saved!")
                st.rerun()

        co = db.query(Company).first()
        if co:
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.success(f"**{co.name}**\n\n{co.address_line1 or ''}, {co.city or ''} – {co.pincode or ''}")
            c2.info(f"GSTIN: **{co.gstin or '—'}**\nPAN: {co.pan or '—'}\nCIN: {co.cin or '—'}")
            c3.info(f"Email: {co.email or '—'}\nPhone: {co.phone or '—'}\nIncorp: {fmt_date(co.reg_date)}")

    # ── Branding ──────────────────────────────────────────────────────────────
    with tab2:
        co = db.query(Company).first()
        if not co:
            st.warning("Save company profile first.")
        else:
            with st.form("branding_form"):
                st.markdown("**Brand Colors** (used in PDF templates and portal)")
                bc1, bc2 = st.columns(2)
                primary   = bc1.color_picker("Primary Color", value=co.brand_primary_color or "#1e293b")
                secondary = bc2.color_picker("Secondary Color", value=co.brand_secondary_color or "#3b82f6")
                footer    = st.text_area("Invoice Footer Text", value=co.invoice_footer_text or "",
                                         placeholder="Thank you for your business! | GSTIN: 36AATCM3488J1ZN | PAN: AATCM3488J | CIN: ...")
                save_b = st.form_submit_button("💾 Save Branding")
            if save_b:
                co.brand_primary_color   = primary
                co.brand_secondary_color = secondary
                co.invoice_footer_text   = footer
                db.commit()
                st.success("✅ Branding saved!")
            st.markdown("---")
            st.markdown("**Preview**")
            st.markdown(
                f'<div style="background:{co.brand_primary_color};padding:12px;border-radius:8px;color:white;font-size:1.2rem;font-weight:600;">'
                f'  {co.name or "Company Name"}'
                f'  <span style="float:right;background:{co.brand_secondary_color};padding:2px 12px;border-radius:4px;font-size:0.8rem;">INVOICE</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if co.invoice_footer_text:
                st.caption(f"Footer: {co.invoice_footer_text}")

    # ── Custom Domain ─────────────────────────────────────────────────────────
    with tab3:
        with st.form("domain_form"):
            custom_domain = st.text_input("Custom Domain", value=_cfg(db, "CUSTOM_DOMAIN"),
                                          placeholder="app.milvian.com")
            portal_sub    = st.text_input("Portal Subdomain", value=_cfg(db, "PORTAL_SUBDOMAIN"),
                                          placeholder="pay.milvian.com")
            cust_portal   = st.checkbox("Customer Portal Enabled", value=_cfg(db, "CUSTOMER_PORTAL_ENABLED") == "true")
            vend_portal   = st.checkbox("Vendor Portal Enabled",   value=_cfg(db, "VENDOR_PORTAL_ENABLED") == "true")
            save_d = st.form_submit_button("💾 Save Domain Settings")
        if save_d:
            _set_cfg(db, "CUSTOM_DOMAIN",           custom_domain)
            _set_cfg(db, "PORTAL_SUBDOMAIN",         portal_sub)
            _set_cfg(db, "CUSTOMER_PORTAL_ENABLED",  "true" if cust_portal else "false")
            _set_cfg(db, "VENDOR_PORTAL_ENABLED",    "true" if vend_portal else "false")
            db.commit()
            st.success("✅ Domain settings saved!")
        st.info("DNS configuration must be done at your domain registrar. Point CNAME to `erp.spoorthy.in`.")

    # ── Locations ─────────────────────────────────────────────────────────────
    with tab4:
        locs = db.query(OrgLocation).all()
        if locs:
            loc_rows = [{
                "Name": l.name, "GSTIN": l.gstin or "—", "City": l.city or "—",
                "State": l.state_code or "—", "Primary": "✅" if l.is_primary else "—",
                "Active": "✅" if l.is_active else "❌",
            } for l in locs]
            st.dataframe(pd.DataFrame(loc_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No locations yet. Add your registered office below.")

        st.markdown("---")
        st.markdown("#### ➕ Add Location")
        with st.form("add_location_form"):
            l1, l2 = st.columns(2)
            with l1:
                l_name   = st.text_input("Location Name *", placeholder="Hyderabad — Head Office")
                l_gstin  = st.text_input("GSTIN", placeholder="36AATCM3488J1ZN")
                l_addr   = st.text_area("Address", placeholder="Plot 12, HITEC City, Madhapur")
            with l2:
                l_city   = st.text_input("City", placeholder="Hyderabad")
                cur_sc   = "36"
                st_idx   = next((i for i, s in enumerate(STATES) if s.startswith(cur_sc + "-")), 35)
                l_state  = st.selectbox("State", STATES, index=st_idx)
                l_pin    = st.text_input("Pincode", placeholder="500081")
                l_phone  = st.text_input("Phone", placeholder="+91 40 6789 0000")
                l_primary= st.checkbox("Set as Primary Location", value=not bool(locs))
            add_loc = st.form_submit_button("➕ Add Location")
        if add_loc:
            if not l_name:
                st.error("Location name is required.")
            else:
                if l_primary:
                    for loc in locs:
                        loc.is_primary = False
                db.add(OrgLocation(
                    name=l_name, gstin=l_gstin or None, address=l_addr,
                    city=l_city, state_code=l_state.split("-")[0], pincode=l_pin,
                    phone=l_phone, is_primary=l_primary,
                ))
                db.commit()
                st.success(f"✅ Location **{l_name}** added!")
                st.rerun()

    # ── Approvals ─────────────────────────────────────────────────────────────
    with tab5:
        rules = db.query(ApprovalRule).all()
        if rules:
            roles_map = {r.id: r.name for r in db.query(Role).all()}
            rrows = [{
                "Module": r.module,
                "Min Amount": f"₹{float(r.min_amount):,.0f}",
                "Max Amount": f"₹{float(r.max_amount):,.0f}" if r.max_amount else "No limit",
                "Approver Role": roles_map.get(r.approver_role_id, "—"),
                "Seq": r.sequence,
                "Active": "✅" if r.is_active else "❌",
            } for r in rules]
            st.dataframe(pd.DataFrame(rrows), use_container_width=True, hide_index=True)
        else:
            st.info("No approval rules configured. All transactions are auto-approved.")

        st.markdown("---")
        st.markdown("#### ➕ Add Approval Rule")
        with st.form("add_approval_form"):
            ap1, ap2 = st.columns(2)
            roles = db.query(Role).all()
            with ap1:
                ap_module  = st.selectbox("Module", ["INVOICE","PURCHASE_ORDER","EXPENSE","PAYMENT","CREDIT_NOTE"])
                ap_min     = st.number_input("Min Amount (₹)", min_value=0.0, value=0.0, format="%.0f")
                ap_max     = st.number_input("Max Amount (₹, 0 = no limit)", min_value=0.0, value=0.0, format="%.0f")
            with ap2:
                ap_role    = st.selectbox("Approver Role", [r.name for r in roles])
                ap_seq     = st.number_input("Sequence", min_value=1, value=1, step=1)
            add_ap = st.form_submit_button("➕ Add Rule")
        if add_ap:
            role_obj = db.query(Role).filter_by(name=ap_role).first()
            db.add(ApprovalRule(
                module=ap_module, min_amount=ap_min,
                max_amount=ap_max if ap_max > 0 else None,
                approver_role_id=role_obj.id if role_obj else None,
                sequence=ap_seq,
            ))
            db.commit()
            st.success("✅ Approval rule added!")
            st.rerun()

    # ── Subscription ──────────────────────────────────────────────────────────
    with tab6:
        co = db.query(Company).first()
        plans = {
            "FREE":       ("Free",       "Up to 2 users, 100 txns/month, basic reports", "#64748b"),
            "PRO":        ("Pro",        "Up to 10 users, unlimited txns, GST reports, e-Invoice", "#3b82f6"),
            "ENTERPRISE": ("Enterprise", "Unlimited users, API access, white-label portal, dedicated support", "#7c3aed"),
        }
        cur_plan = co.subscription_plan if co else "FREE"
        c1, c2, c3 = st.columns(3)
        for i, (pid, (pname, pdesc, pcol)) in enumerate(plans.items()):
            col = [c1, c2, c3][i]
            border = "4px solid " + pcol if pid == cur_plan else "1px solid #e2e8f0"
            badge = (f'<div style="margin-top:8px;background:{pcol};color:white;'
                     f'border-radius:4px;padding:2px 8px;font-size:0.75rem;'
                     f'display:inline-block;">CURRENT PLAN</div>') if pid == cur_plan else ""
            col.markdown(
                f'<div style="border:{border};border-radius:10px;padding:16px;">'
                f'<div style="color:{pcol};font-size:1.1rem;font-weight:700;">{pname}</div>'
                f'<div style="color:#64748b;font-size:0.8rem;margin-top:4px;">{pdesc}</div>'
                f'{badge}</div>',
                unsafe_allow_html=True,
            )
        if co:
            st.markdown(f"---\nExpires: **{fmt_date(co.subscription_expires) or 'Never'}**")


# ── Section: Users & Roles ────────────────────────────────────────────────────

def _section_users_roles(db):
    tab1, tab2, tab3 = st.tabs(["👥 Users", "🔑 Roles", "⚙️ User Preferences"])

    # ── Users ─────────────────────────────────────────────────────────────────
    with tab1:
        users = db.query(AppUser).all()
        roles = db.query(Role).all()
        role_names = [r.name for r in roles]

        if users:
            urows = [{
                "Username": u.username, "Full Name": u.full_name,
                "Email": u.email, "Phone": u.phone or "—",
                "Role": u.role.name if u.role else "—",
                "Active": "✅" if u.is_active else "❌",
                "MFA": "🔐 On" if u.mfa_enabled else "Off",
                "First Login": "⚠️ Pending" if u.is_first_login else "Done",
                "Last Login": fmt_date(u.last_login) if u.last_login else "Never",
                "Created": fmt_date(u.created_at),
            } for u in users]
            st.dataframe(pd.DataFrame(urows), use_container_width=True, hide_index=True)
        else:
            st.info("No users yet. Create the first admin user below.")

        st.markdown("---")
        st.markdown("#### ➕ Create User")
        with st.form("create_user_form_s"):
            uc1, uc2 = st.columns(2)
            with uc1:
                u_un   = st.text_input("Username *", placeholder="anil.kumar")
                u_fn   = st.text_input("Full Name *", placeholder="Kakarala Anil Kumar")
                u_em   = st.text_input("Email *", placeholder="anil@milvian.com")
                u_ph   = st.text_input("Phone", placeholder="+91 98765 43210")
            with uc2:
                u_role = st.selectbox("Role *", role_names)
                u_pw   = st.text_input("Password *", type="password", placeholder="min 6 characters")
                u_cpw  = st.text_input("Confirm Password *", type="password")
                u_mfa  = st.checkbox("Enable MFA (TOTP)")
            st.caption("Password is hashed with SHA-256 and never stored in plain text.")
            cr_btn = st.form_submit_button("👤 Create User", use_container_width=True)

        if cr_btn:
            if not all([u_un, u_fn, u_em, u_pw]):
                st.error("All fields marked * are required.")
            elif u_pw != u_cpw:
                st.error("Passwords do not match.")
            elif len(u_pw) < 6:
                st.error("Password must be at least 6 characters.")
            elif db.query(AppUser).filter_by(username=u_un).first():
                st.error(f"Username **{u_un}** already exists.")
            elif db.query(AppUser).filter_by(email=u_em).first():
                st.error(f"Email **{u_em}** is already registered.")
            else:
                role_obj = db.query(Role).filter_by(name=u_role).first()
                db.add(AppUser(
                    username=u_un, full_name=u_fn, email=u_em, phone=u_ph or None,
                    password_hash=hash_password(u_pw),
                    role_id=role_obj.id, is_active=True, is_first_login=True,
                    mfa_enabled=u_mfa,
                ))
                db.commit()
                st.success(f"✅ User **{u_un}** ({u_role}) created!")
                st.rerun()

        # Edit user
        if users:
            st.markdown("---")
            st.markdown("#### ✏️ Edit User")
            sel = st.selectbox("Select user", [u.username for u in users], key="edit_user_sel")
            u_obj = db.query(AppUser).filter_by(username=sel).first()
            if u_obj:
                with st.form("edit_user_form_s"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        en  = st.text_input("Full Name", value=u_obj.full_name)
                        ee  = st.text_input("Email", value=u_obj.email)
                        ep  = st.text_input("Phone", value=u_obj.phone or "")
                    with ec2:
                        er  = st.selectbox("Role", role_names, index=role_names.index(u_obj.role.name) if u_obj.role else 0)
                        ea  = st.checkbox("Active", value=u_obj.is_active)
                        em  = st.checkbox("MFA Enabled", value=u_obj.mfa_enabled)
                        epw = st.text_input("New Password (blank = keep)", type="password")
                    sv = st.form_submit_button("💾 Save Changes")
                if sv:
                    role_obj = db.query(Role).filter_by(name=er).first()
                    u_obj.full_name = en; u_obj.email = ee; u_obj.phone = ep or None
                    u_obj.role_id = role_obj.id; u_obj.is_active = ea; u_obj.mfa_enabled = em
                    if epw:
                        u_obj.password_hash = hash_password(epw)
                        u_obj.is_first_login = False
                    db.commit()
                    st.success(f"✅ User **{sel}** updated!")
                    st.rerun()

    # ── Roles ─────────────────────────────────────────────────────────────────
    with tab2:
        roles = db.query(Role).all()
        if roles:
            rrows = [{
                "Role": r.name,
                "Description": r.description,
                "Post": "✅" if r.can_post else "—",
                "Approve": "✅" if r.can_approve else "—",
                "Delete": "✅" if r.can_delete else "—",
                "Export": "✅" if r.can_export else "—",
                "Admin": "✅" if r.can_admin else "—",
                "View Reports": "✅" if r.can_view_reports else "—",
                "Manage Masters": "✅" if r.can_manage_masters else "—",
            } for r in roles]
            st.dataframe(pd.DataFrame(rrows), use_container_width=True, hide_index=True)
        else:
            st.info("Roles will be seeded on save.")

        st.markdown("---")
        st.markdown("#### ➕ Create Custom Role")
        with st.form("create_role_form"):
            r1, r2 = st.columns(2)
            with r1:
                rn   = st.text_input("Role Name *", placeholder="BRANCH_MANAGER")
                rd   = st.text_input("Description", placeholder="Manage branch transactions")
            with r2:
                rp   = st.checkbox("Can Post Vouchers")
                rap  = st.checkbox("Can Approve")
                rdl  = st.checkbox("Can Delete")
                rex  = st.checkbox("Can Export", value=True)
                radm = st.checkbox("Admin Access")
                rvr  = st.checkbox("View Reports", value=True)
                rmm  = st.checkbox("Manage Masters")
            cr = st.form_submit_button("➕ Create Role")
        if cr:
            if not rn:
                st.error("Role name is required.")
            elif db.query(Role).filter_by(name=rn.upper()).first():
                st.error(f"Role **{rn.upper()}** already exists.")
            else:
                db.add(Role(
                    name=rn.upper(), description=rd, can_post=rp, can_approve=rap,
                    can_delete=rdl, can_export=rex, can_admin=radm,
                    can_view_reports=rvr, can_manage_masters=rmm, is_system=False,
                ))
                db.commit()
                st.success(f"✅ Role **{rn.upper()}** created!")
                st.rerun()

    # ── User Preferences ──────────────────────────────────────────────────────
    with tab3:
        users = db.query(AppUser).all()
        if not users:
            st.info("Create users first.")
        else:
            sel_u = st.selectbox("User", [u.username for u in users], key="pref_user_sel")
            u_obj = db.query(AppUser).filter_by(username=sel_u).first()
            if u_obj:
                pref = db.query(UserPreference).filter_by(user_id=u_obj.id).first()
                with st.form("user_pref_form"):
                    p1, p2 = st.columns(2)
                    with p1:
                        pfy   = st.text_input("Default Fiscal Year", value=pref.default_fy if pref else "2025-26")
                        ptz   = st.selectbox("Timezone", ["Asia/Kolkata","UTC","Asia/Dubai","US/Eastern"],
                                             index=["Asia/Kolkata","UTC","Asia/Dubai","US/Eastern"].index(pref.timezone) if pref and pref.timezone in ["Asia/Kolkata","UTC","Asia/Dubai","US/Eastern"] else 0)
                        pipp  = st.number_input("Items per Page", min_value=10, max_value=200, value=pref.items_per_page if pref else 25, step=5)
                    with p2:
                        pem   = st.checkbox("Email Notifications", value=pref.notify_by_email if pref else True)
                        psms  = st.checkbox("SMS Notifications",   value=pref.notify_by_sms   if pref else False)
                    sp = st.form_submit_button("💾 Save Preferences")
                if sp:
                    if pref:
                        pref.default_fy=pfy; pref.timezone=ptz; pref.items_per_page=pipp
                        pref.notify_by_email=pem; pref.notify_by_sms=psms
                    else:
                        db.add(UserPreference(
                            user_id=u_obj.id, default_fy=pfy, timezone=ptz,
                            items_per_page=pipp, notify_by_email=pem, notify_by_sms=psms,
                        ))
                    db.commit()
                    st.success(f"✅ Preferences for **{sel_u}** saved!")


# ── Section: Taxes & Compliance ───────────────────────────────────────────────

def _section_taxes(db):
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧾 GST Rates", "📋 TDS Sections", "🚚 e-Way Bills", "📄 e-Invoicing", "🏭 MSME"
    ])

    with tab1:
        st.markdown("**GST Rate Configuration**")
        gst_data = [
            {"Rate": "0%",   "CGST": "0%",  "SGST": "0%",  "IGST": "0%",  "Category": "Exempt / Nil rated"},
            {"Rate": "0.25%","CGST": "0.125%","SGST":"0.125%","IGST":"0.25%","Category":"Rough diamonds"},
            {"Rate": "3%",   "CGST": "1.5%","SGST": "1.5%","IGST": "3%",  "Category": "Gold, silver, jewellery"},
            {"Rate": "5%",   "CGST": "2.5%","SGST": "2.5%","IGST": "5%",  "Category": "Essential goods, food grains"},
            {"Rate": "12%",  "CGST": "6%",  "SGST": "6%",  "IGST": "12%", "Category": "Processed food, computers"},
            {"Rate": "18%",  "CGST": "9%",  "SGST": "9%",  "IGST": "18%", "Category": "IT services, most goods (standard)"},
            {"Rate": "28%",  "CGST": "14%", "SGST": "14%", "IGST": "28%", "Category": "Luxury goods, automobiles, tobacco"},
        ]
        st.dataframe(pd.DataFrame(gst_data), use_container_width=True, hide_index=True)
        st.info("Default rate for new items: **18%**. Change per-item in Masters → Stock Items.")

        st.markdown("---")
        st.markdown("**Your GST Registrations**")
        gst_regs = db.query(GSTRegistration).all()
        if gst_regs:
            gr_rows = [{"GSTIN": g.gstin, "Trade Name": g.trade_name, "State": g.state_code,
                        "Type": g.reg_type, "Primary": "✅" if g.is_primary else "—",
                        "Reg Date": fmt_date(g.reg_date)} for g in gst_regs]
            st.dataframe(pd.DataFrame(gr_rows), use_container_width=True, hide_index=True)
        else:
            st.warning("No GST registrations. Add via Masters → GSTIN.")

    with tab2:
        tds_sections = [
            {"Section": "192",  "Description": "Salary",                            "Rate": "As per slab", "Threshold": "₹2,50,000/yr"},
            {"Section": "194C", "Description": "Contractor (Individual)",            "Rate": "1%",          "Threshold": "₹1,00,000/yr"},
            {"Section": "194C", "Description": "Contractor (Company)",               "Rate": "2%",          "Threshold": "₹1,00,000/yr"},
            {"Section": "194D", "Description": "Insurance Commission",               "Rate": "5%",          "Threshold": "₹15,000"},
            {"Section": "194H", "Description": "Commission / Brokerage",             "Rate": "5%",          "Threshold": "₹15,000"},
            {"Section": "194I", "Description": "Rent (Land/Building)",               "Rate": "10%",         "Threshold": "₹2,40,000/yr"},
            {"Section": "194I", "Description": "Rent (Plant/Machinery)",             "Rate": "2%",          "Threshold": "₹2,40,000/yr"},
            {"Section": "194J", "Description": "Professional / Technical Services",  "Rate": "10%",         "Threshold": "₹30,000"},
            {"Section": "194Q", "Description": "Purchase of Goods",                  "Rate": "0.1%",        "Threshold": "₹50 L/yr"},
            {"Section": "195",  "Description": "Payment to Non-Resident",            "Rate": "20-30%",      "Threshold": "Any"},
        ]
        st.dataframe(pd.DataFrame(tds_sections), use_container_width=True, hide_index=True)
        tds_return = st.checkbox("Enable Quarterly TDS Return (24Q/26Q)", value=_cfg(db, "TDS_QUARTERLY_RETURN") == "true")
        if st.button("💾 Save TDS Settings"):
            _set_cfg(db, "TDS_QUARTERLY_RETURN", "true" if tds_return else "false")
            db.commit()
            st.success("✅ TDS settings saved!")

    with tab3:
        co = db.query(Company).first()
        with st.form("eway_form"):
            eway_en  = st.checkbox("Enable e-Way Bill Generation",
                                   value=co.eway_bill_enabled if co else False)
            eway_thr = st.number_input("e-Way Bill Threshold (₹)", min_value=0.0,
                                       value=float(co.eway_bill_threshold) if co else 50000.0,
                                       step=1000.0, format="%.0f")
            st.caption("Generate e-Way Bill for consignments exceeding this value (default: ₹50,000).")
            sv_eway = st.form_submit_button("💾 Save")
        if sv_eway and co:
            co.eway_bill_enabled   = eway_en
            co.eway_bill_threshold = eway_thr
            db.commit()
            st.success("✅ e-Way Bill settings saved!")
        st.info("e-Way Bill API credentials must be configured via the NIC portal (ewaybillgst.gov.in).")

    with tab4:
        co = db.query(Company).first()
        with st.form("einv_form"):
            einv_en = st.checkbox("Enable e-Invoicing (IRP)", value=co.einvoice_enabled if co else False)
            irn_url = st.text_input("IRP API Endpoint", value=_cfg(db, "EINVOICE_IRN_API_URL"),
                                    placeholder="https://einvoice1.gst.gov.in/EIVITAL/v1.04/...")
            st.caption("Required for taxpayers with turnover > ₹10 Cr. Generates IRN + QR code on each invoice.")
            sv_einv = st.form_submit_button("💾 Save")
        if sv_einv:
            if co:
                co.einvoice_enabled = einv_en
            _set_cfg(db, "EINVOICE_IRN_API_URL", irn_url)
            db.commit()
            st.success("✅ e-Invoicing settings saved!")

    with tab5:
        co = db.query(Company).first()
        with st.form("msme_form"):
            udyam = st.text_input("Udyam Registration No", value=co.msme_udyam_no or "" if co else "",
                                   placeholder="UDYAM-TS-00-XXXXXXX")
            pay_d = st.number_input("Statutory Payment Days (MSMED Act)", min_value=1, max_value=45,
                                     value=co.msme_payment_days if co else 45, step=1)
            st.caption("Payments to MSME suppliers must be made within 45 days under the MSMED Act 2006.")
            sv_msme = st.form_submit_button("💾 Save MSME Settings")
        if sv_msme and co:
            co.msme_udyam_no    = udyam or None
            co.msme_payment_days = pay_d
            db.commit()
            st.success("✅ MSME settings saved!")


# ── Section: Setup & Configurations ──────────────────────────────────────────

def _section_setup(db):
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⚙️ General", "💱 Currencies", "📂 Opening Balances",
        "🔔 Reminders", "🖥️ Customer Portal", "🏢 Vendor Portal",
    ])

    with tab1:
        with st.form("general_cfg"):
            g1, g2 = st.columns(2)
            with g1:
                def_cr = st.number_input("Default Credit Days", min_value=0, value=int(_cfg(db,"DEFAULT_CREDIT_DAYS","30")), step=1)
                inv_val= st.selectbox("Inventory Valuation", ["FIFO","WEIGHTED_AVG"],
                                       index=0 if _cfg(db,"INVENTORY_VALUATION")!="WEIGHTED_AVG" else 1)
            with g2:
                ts_en  = st.checkbox("Timesheet Module", value=_cfg(db,"TIMESHEET_ENABLED")=="true")
                pb_type= st.selectbox("Project Billing Type", ["FIXED","HOURLY"],
                                       index=0 if _cfg(db,"PROJECT_BILLING_TYPE")!="HOURLY" else 1)
            sv_gen = st.form_submit_button("💾 Save")
        if sv_gen:
            _set_cfg(db,"DEFAULT_CREDIT_DAYS", str(def_cr))
            _set_cfg(db,"INVENTORY_VALUATION",  inv_val)
            _set_cfg(db,"TIMESHEET_ENABLED",     "true" if ts_en else "false")
            _set_cfg(db,"PROJECT_BILLING_TYPE",  pb_type)
            db.commit()
            st.success("✅ General settings saved!")

    with tab2:
        currencies = db.query(Currency).all()
        if currencies:
            cr_rows = [{"Code": c.code, "Name": c.name, "Symbol": c.symbol,
                        "Rate to INR": float(c.rate_to_inr), "Active": "✅" if c.is_active else "❌"}
                       for c in currencies]
            st.dataframe(pd.DataFrame(cr_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Currency master will be seeded on startup.")

    with tab3:
        ob_date = st.date_input("Opening Balance Date", value=date(2025, 4, 1), format="DD/MM/YYYY")
        st.caption("Set the as-at date for opening balances. All ledgers with opening_balance > 0 will be included.")
        ledgers_with_ob = db.query(Ledger).filter(Ledger.opening_balance != 0).all()
        if ledgers_with_ob:
            ob_rows = [{"Ledger": l.name, "Code": l.code,
                        "Opening Balance": f"₹{float(l.opening_balance):,.2f}",
                        "Type": l.opening_type} for l in ledgers_with_ob]
            st.dataframe(pd.DataFrame(ob_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No opening balances set. Edit ledgers in Masters → Ledgers.")
        if st.button("💾 Set Opening Balance Date"):
            _set_cfg(db, "OPENING_BALANCE_DATE", str(ob_date))
            db.commit()
            st.success(f"✅ Opening balance date set to {fmt_date(ob_date)}")

    with tab4:
        with st.form("reminders_form"):
            due_days = st.text_input("Reminder Days (before due)", value=_cfg(db,"REMINDER_DUE_DAYS","7,3,1"),
                                      placeholder="7,3,1 (comma-separated)")
            ov_days  = st.text_input("Reminder Days (after due)", value=_cfg(db,"REMINDER_OVERDUE_DAYS","1,7,15"),
                                      placeholder="1,7,15")
            ch_idx   = ["EMAIL","SMS","BOTH"].index(_cfg(db,"DEFAULT_REMINDER_CHANNEL","EMAIL")) if _cfg(db,"DEFAULT_REMINDER_CHANNEL","EMAIL") in ["EMAIL","SMS","BOTH"] else 0
            channel  = st.selectbox("Default Channel", ["EMAIL","SMS","BOTH"], index=ch_idx)
            sv_rem = st.form_submit_button("💾 Save")
        if sv_rem:
            _set_cfg(db,"REMINDER_DUE_DAYS",       due_days)
            _set_cfg(db,"REMINDER_OVERDUE_DAYS",    ov_days)
            _set_cfg(db,"DEFAULT_REMINDER_CHANNEL", channel)
            db.commit()
            st.success("✅ Reminder settings saved!")

    with tab5:
        with st.form("cust_portal_form"):
            cp_en = st.checkbox("Enable Customer Portal", value=_cfg(db,"CUSTOMER_PORTAL_ENABLED")=="true")
            cp_sub= st.text_input("Portal Subdomain", value=_cfg(db,"PORTAL_SUBDOMAIN"), placeholder="pay.milvian.com")
            st.caption("Customers can view invoices and make payments via the portal.")
            sv_cp = st.form_submit_button("💾 Save")
        if sv_cp:
            _set_cfg(db,"CUSTOMER_PORTAL_ENABLED","true" if cp_en else "false")
            _set_cfg(db,"PORTAL_SUBDOMAIN",        cp_sub)
            db.commit()
            st.success("✅ Customer portal settings saved!")

    with tab6:
        with st.form("vend_portal_form"):
            vp_en = st.checkbox("Enable Vendor Portal", value=_cfg(db,"VENDOR_PORTAL_ENABLED")=="true")
            st.caption("Vendors can acknowledge POs and submit bills via the portal.")
            sv_vp = st.form_submit_button("💾 Save")
        if sv_vp:
            _set_cfg(db,"VENDOR_PORTAL_ENABLED","true" if vp_en else "false")
            db.commit()
            st.success("✅ Vendor portal settings saved!")


# ── Section: Customization ────────────────────────────────────────────────────

def _section_customization(db):
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔢 Txn Number Series", "📧 Email Templates", "📱 SMS Templates",
        "🏷️ Reporting Tags", "🖊️ Digital Signature", "📑 Web Tabs",
    ])

    with tab1:
        vtypes = db.query(VoucherType).all()
        series = db.query(TxnNumberSeries).all()
        series_map = {s.voucher_type_code: s for s in series}

        if series:
            sr = [{"Type": s.voucher_type_code, "Prefix": s.prefix,
                   "Suffix": s.suffix or "—", "Next #": s.current_seq + 1,
                   "Padding": s.padding, "Reset": s.reset_period} for s in series]
            st.dataframe(pd.DataFrame(sr), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### ➕ Configure Series")
        vtype_codes = [v.code for v in vtypes]
        with st.form("txn_series_form"):
            ts1, ts2 = st.columns(2)
            with ts1:
                ts_vt  = st.selectbox("Voucher Type", vtype_codes)
                ts_pfx = st.text_input("Prefix", placeholder="INV/2025-26/")
                ts_sfx = st.text_input("Suffix (optional)", placeholder="")
            with ts2:
                ts_pad = st.number_input("Zero Padding", min_value=3, max_value=10, value=6, step=1)
                ts_rst = st.selectbox("Reset Period", ["YEARLY","MONTHLY","NEVER"])
                ts_fy  = st.text_input("Fiscal Year", value="2025-26")
            sv_ts = st.form_submit_button("💾 Save Series")
        if sv_ts and ts_vt:
            existing = series_map.get(ts_vt)
            if existing:
                existing.prefix=ts_pfx; existing.suffix=ts_sfx or None
                existing.padding=ts_pad; existing.reset_period=ts_rst; existing.fy_label=ts_fy
            else:
                db.add(TxnNumberSeries(
                    voucher_type_code=ts_vt, prefix=ts_pfx, suffix=ts_sfx or None,
                    padding=ts_pad, reset_period=ts_rst, fy_label=ts_fy,
                ))
            db.commit()
            st.success(f"✅ Number series for **{ts_vt}** saved!")
            st.rerun()

    with tab2:
        templates = db.query(EmailTemplate).all()
        if templates:
            et_rows = [{"Event": t.event_code, "Subject": t.subject,
                        "Active": "✅" if t.is_active else "❌"} for t in templates]
            st.dataframe(pd.DataFrame(et_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        event_codes = [t.event_code for t in templates] if templates else ["INVOICE_SENT"]
        sel_et = st.selectbox("Edit Template", event_codes, key="et_sel")
        et_obj = db.query(EmailTemplate).filter_by(event_code=sel_et).first()
        if et_obj:
            with st.form("email_tpl_form"):
                et_subj = st.text_input("Subject", value=et_obj.subject)
                et_body = st.text_area("Body (HTML)", value=et_obj.body_html, height=200)
                et_act  = st.checkbox("Active", value=et_obj.is_active)
                sv_et   = st.form_submit_button("💾 Save Template")
            if sv_et:
                et_obj.subject=et_subj; et_obj.body_html=et_body; et_obj.is_active=et_act
                db.commit()
                st.success("✅ Email template saved!")
        st.caption("Available variables: {customer_name}, {invoice_no}, {amount}, {due_date}, {company_name}, {portal_link}")

    with tab3:
        sms_tpls = db.query(SMSTemplate).all()
        if sms_tpls:
            sm_rows = [{"Event": t.event_code, "Message (160 chars)": t.message[:80]+"...",
                        "Active": "✅" if t.is_active else "❌"} for t in sms_tpls]
            st.dataframe(pd.DataFrame(sm_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        sms_codes = [t.event_code for t in sms_tpls] if sms_tpls else []
        if sms_codes:
            sel_sms = st.selectbox("Edit SMS Template", sms_codes, key="sms_sel")
            sms_obj = db.query(SMSTemplate).filter_by(event_code=sel_sms).first()
            if sms_obj:
                with st.form("sms_tpl_form"):
                    sm_msg = st.text_area("Message (max 160 chars)", value=sms_obj.message, max_chars=160)
                    sm_act = st.checkbox("Active", value=sms_obj.is_active)
                    sv_sm  = st.form_submit_button("💾 Save SMS Template")
                if sv_sm:
                    sms_obj.message=sm_msg; sms_obj.is_active=sm_act
                    db.commit()
                    st.success("✅ SMS template saved!")

        with st.form("sms_provider_form"):
            st.markdown("**SMS Provider**")
            sp1, sp2 = st.columns(2)
            sms_prov = sp1.selectbox("Provider", ["MSG91","TWILIO","TEXTLOCAL","KALEYRA"],
                                      index=["MSG91","TWILIO","TEXTLOCAL","KALEYRA"].index(_cfg(db,"SMS_PROVIDER","MSG91")) if _cfg(db,"SMS_PROVIDER") in ["MSG91","TWILIO","TEXTLOCAL","KALEYRA"] else 0)
            sms_key  = sp2.text_input("API Key", value=_cfg(db,"SMS_API_KEY"), type="password")
            sv_sp = st.form_submit_button("💾 Save Provider")
        if sv_sp:
            _set_cfg(db,"SMS_PROVIDER",sms_prov)
            _set_cfg(db,"SMS_API_KEY",sms_key)
            db.commit()
            st.success("✅ SMS provider saved!")

    with tab4:
        tags = db.query(ReportingTag).all()
        if tags:
            tg_rows = [{"Tag": t.name, "Description": t.description or "—",
                        "Color": t.color_hex, "Active": "✅" if t.is_active else "❌"} for t in tags]
            st.dataframe(pd.DataFrame(tg_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No reporting tags yet. Tags can be attached to vouchers and parties for custom reports.")

        st.markdown("---")
        with st.form("add_tag_form"):
            tg1, tg2 = st.columns([3, 1])
            tg_name  = tg1.text_input("Tag Name *", placeholder="Marketing Expenses")
            tg_color = tg2.color_picker("Color", value="#3b82f6")
            tg_desc  = st.text_input("Description", placeholder="Track all marketing-related costs")
            add_tg   = st.form_submit_button("➕ Add Tag")
        if add_tg and tg_name:
            if db.query(ReportingTag).filter_by(name=tg_name).first():
                st.error(f"Tag **{tg_name}** already exists.")
            else:
                db.add(ReportingTag(name=tg_name, description=tg_desc, color_hex=tg_color))
                db.commit()
                st.success(f"✅ Tag **{tg_name}** added!")
                st.rerun()

    with tab5:
        st.info("Digital Signature Certificate (DSC) configuration for e-Invoice signing.")
        with st.form("dsc_form"):
            dsc_path  = st.text_input("Certificate Path / Thumbprint", placeholder="/certs/milvian_dsc.pfx")
            dsc_valid = st.date_input("Valid Until", value=date(2026, 12, 31), format="DD/MM/YYYY")
            sv_dsc = st.form_submit_button("💾 Save DSC Config")
        if sv_dsc:
            _set_cfg(db, "DSC_PATH",       dsc_path)
            _set_cfg(db, "DSC_VALID_UNTIL", str(dsc_valid))
            db.commit()
            st.success("✅ DSC configuration saved!")

    with tab6:
        st.info("Configure custom web tabs visible in the sidebar navigation for your team.")
        st.markdown("This feature allows you to embed internal tools, dashboards, or third-party iframes as sidebar tabs.")
        with st.form("web_tab_form"):
            wt_name = st.text_input("Tab Name", placeholder="Power BI Dashboard")
            wt_url  = st.text_input("URL", placeholder="https://app.powerbi.com/...")
            wt_icon = st.text_input("Emoji Icon", placeholder="📊")
            sv_wt   = st.form_submit_button("➕ Add Web Tab")
        if sv_wt:
            st.info("Web tabs will appear in the sidebar navigation after saving.")
            st.success(f"✅ Web tab **{wt_icon} {wt_name}** registered (restart app to see in sidebar).")


# ── Section: Automation ───────────────────────────────────────────────────────

def _section_automation(db):
    tab1, tab2, tab3 = st.tabs(["⚙️ Workflow Rules", "▶️ Workflow Actions", "📋 Workflow Logs"])

    with tab1:
        rules = db.query(WorkflowRule).all()
        if rules:
            wr_rows = [{"Name": r.name, "Module": r.module, "Trigger": r.trigger_event,
                        "Actions": len(r.actions), "Active": "✅" if r.is_active else "❌"} for r in rules]
            st.dataframe(pd.DataFrame(wr_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No workflow rules yet. Rules automate notifications, approvals, and field updates.")

        st.markdown("---")
        st.markdown("#### ➕ Create Workflow Rule")
        with st.form("wr_form"):
            wr1, wr2 = st.columns(2)
            with wr1:
                wr_name = st.text_input("Rule Name *", placeholder="Notify on large invoice")
                wr_mod  = st.selectbox("Module", ["INVOICE","PURCHASE_ORDER","EXPENSE","PAYMENT","CREDIT_NOTE"])
            with wr2:
                wr_trig = st.selectbox("Trigger Event", ["ON_CREATE","ON_APPROVE","ON_DUE","AMOUNT_EXCEEDS","STATUS_CHANGE"])
                wr_cond = st.text_input("Condition (JSON)", placeholder='{"amount_gt": 100000}')
            add_wr = st.form_submit_button("➕ Create Rule")
        if add_wr and wr_name:
            db.add(WorkflowRule(name=wr_name, module=wr_mod, trigger_event=wr_trig,
                                condition_json=wr_cond or None))
            db.commit()
            st.success(f"✅ Rule **{wr_name}** created! Add actions in the next tab.")
            st.rerun()

    with tab2:
        rules = db.query(WorkflowRule).all()
        if not rules:
            st.info("Create workflow rules first.")
        else:
            sel_rule = st.selectbox("Select Rule", [r.name for r in rules], key="wa_rule_sel")
            rule_obj = db.query(WorkflowRule).filter_by(name=sel_rule).first()
            if rule_obj:
                actions = db.query(WorkflowAction).filter_by(rule_id=rule_obj.id).all()
                if actions:
                    ac_rows = [{"Seq": a.sequence, "Action": a.action_type,
                                "Config": (a.action_config_json or "")[:80]} for a in actions]
                    st.dataframe(pd.DataFrame(ac_rows), use_container_width=True, hide_index=True)

                with st.form("wa_form"):
                    wa1, wa2 = st.columns(2)
                    wa_type = wa1.selectbox("Action Type", ["SEND_EMAIL","SEND_SMS","WEBHOOK","NOTIFY","FIELD_UPDATE"])
                    wa_seq  = wa2.number_input("Sequence", min_value=1, value=len(actions)+1, step=1)
                    wa_cfg  = st.text_area("Config (JSON)", placeholder='{"to": "{customer_email}", "template": "INVOICE_SENT"}', height=80)
                    add_wa  = st.form_submit_button("➕ Add Action")
                if add_wa:
                    db.add(WorkflowAction(rule_id=rule_obj.id, action_type=wa_type,
                                          action_config_json=wa_cfg or None, sequence=wa_seq))
                    db.commit()
                    st.success(f"✅ Action **{wa_type}** added to rule **{sel_rule}**!")
                    st.rerun()

    with tab3:
        logs = db.query(WorkflowLog).order_by(WorkflowLog.triggered_at.desc()).limit(50).all()
        if logs:
            lg_rows = [{
                "Triggered": fmt_date(l.triggered_at),
                "Rule": l.rule.name if l.rule else "—",
                "Record": f"{l.record_type} #{l.record_id}",
                "Outcome": "✅" if l.outcome == "SUCCESS" else "❌",
                "Log": (l.log_text or "")[:100],
            } for l in logs]
            st.dataframe(pd.DataFrame(lg_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No workflow logs yet. Logs appear when rules are triggered by transactions.")


# ── Section: Module Settings ──────────────────────────────────────────────────

def _section_modules(db):
    tabs = st.tabs(["⚙️ General", "👤 Customers/Vendors", "📦 Items",
                    "📊 Accountant", "📁 Projects", "⏱️ Timesheet", "🏭 Inventory"])

    with tabs[0]:
        st.markdown("**Module Enable/Disable**")
        mods = {"Timesheet":"TIMESHEET_ENABLED","Projects":"PROJECT_ENABLED",
                "Inventory":"INVENTORY_ENABLED","e-Way Bills":"EWAY_BILL_ENABLED",
                "e-Invoicing":"EINVOICE_ENABLED"}
        with st.form("mod_gen_form"):
            checks = {m: st.checkbox(m, value=_cfg(db,k)!="false") for m,k in mods.items()}
            sv = st.form_submit_button("💾 Save")
        if sv:
            for m, k in mods.items():
                _set_cfg(db, k, "true" if checks[m] else "false")
            db.commit()
            st.success("✅ Module settings saved!")

    with tabs[1]:
        with st.form("cv_form"):
            cr_d = st.number_input("Default Credit Days (Customers)", min_value=0,
                                    value=int(_cfg(db,"DEFAULT_CREDIT_DAYS","30")), step=1)
            auto_po = st.checkbox("Auto-generate PO number on vendor bill")
            dup_pan = st.checkbox("Warn on duplicate PAN", value=True)
            sv_cv = st.form_submit_button("💾 Save")
        if sv_cv:
            _set_cfg(db,"DEFAULT_CREDIT_DAYS",str(cr_d))
            db.commit()
            st.success("✅ Customer/Vendor settings saved!")

    with tabs[2]:
        with st.form("items_form"):
            iv = st.selectbox("Default Inventory Valuation", ["FIFO","WEIGHTED_AVG"],
                               index=0 if _cfg(db,"INVENTORY_VALUATION")!="WEIGHTED_AVG" else 1)
            st.caption("FIFO: First In First Out. Weighted Average: recalculates on each purchase.")
            sv_it = st.form_submit_button("💾 Save")
        if sv_it:
            _set_cfg(db,"INVENTORY_VALUATION",iv)
            db.commit()
            st.success("✅ Items settings saved!")

    with tabs[3]:
        st.markdown("Accountant settings — fiscal year, depreciation method, rounding.")
        co = db.query(Company).first()
        with st.form("acct_form"):
            fy_s = st.selectbox("Fiscal Year Start", ["April (India Standard)","January (Calendar Year)"],
                                  index=0 if not co or co.fiscal_year_start=="04-01" else 1)
            dep_m = st.selectbox("Default Depreciation Method", ["WDV (Written Down Value)","SLM (Straight Line)"])
            round_off = st.number_input("Rounding Off Threshold (₹)", min_value=0.0, value=0.5, step=0.01, format="%.2f")
            sv_ac = st.form_submit_button("💾 Save")
        if sv_ac and co:
            co.fiscal_year_start = "04-01" if "April" in fy_s else "01-01"
            db.commit()
            st.success("✅ Accountant settings saved!")

    with tabs[4]:
        with st.form("proj_form"):
            pb = st.selectbox("Default Billing Type", ["FIXED","HOURLY","MILESTONE"],
                               index=["FIXED","HOURLY","MILESTONE"].index(_cfg(db,"PROJECT_BILLING_TYPE","FIXED")) if _cfg(db,"PROJECT_BILLING_TYPE") in ["FIXED","HOURLY","MILESTONE"] else 0)
            sv_p = st.form_submit_button("💾 Save")
        if sv_p:
            _set_cfg(db,"PROJECT_BILLING_TYPE",pb)
            db.commit()
            st.success("✅ Project settings saved!")

    with tabs[5]:
        with st.form("ts_form"):
            ts = st.checkbox("Enable Timesheet", value=_cfg(db,"TIMESHEET_ENABLED")=="true")
            sv_ts = st.form_submit_button("💾 Save")
        if sv_ts:
            _set_cfg(db,"TIMESHEET_ENABLED","true" if ts else "false")
            db.commit()
            st.success("✅ Timesheet settings saved!")

    with tabs[6]:
        with st.form("inv_form"):
            iv2 = st.selectbox("Valuation", ["FIFO","WEIGHTED_AVG"],
                                index=0 if _cfg(db,"INVENTORY_VALUATION")!="WEIGHTED_AVG" else 1)
            iv_adj = st.checkbox("Allow negative stock (e-commerce / dropship)")
            sv_in = st.form_submit_button("💾 Save")
        if sv_in:
            _set_cfg(db,"INVENTORY_VALUATION",iv2)
            db.commit()
            st.success("✅ Inventory settings saved!")


# ── Section: Sales ────────────────────────────────────────────────────────────

def _section_sales(db):
    tabs = st.tabs(["💬 Quotes", "📋 Sales Orders", "🚚 Delivery Challans",
                    "🧾 Invoices", "🔄 Recurring", "💵 Payments Received", "📝 Credit Notes"])

    modules = [
        ("SINV","Invoices","Invoice prefix, due days, auto-number"),
        ("QUOT","Quotes","Quote validity, terms"),
        ("SO",  "Sales Orders","Confirm SO before invoicing"),
        ("DCH", "Delivery Challans","Link DC to invoice"),
        ("RECI","Payments Received","Receipt number series"),
        ("CN",  "Credit Notes","Credit note reason codes"),
    ]

    for i, (code, name, hint) in enumerate(modules):
        with tabs[i if i < 7 else 6]:
            vt = db.query(VoucherType).filter_by(code=code).first()
            st.caption(f"**{name}** — {hint}")
            if vt:
                with st.form(f"sales_{code}_form"):
                    pfx = st.text_input("Prefix", value=vt.prefix, placeholder=f"SPRY/{code}/")
                    due = st.number_input("Default Due Days", min_value=0, value=30, step=1)
                    sv  = st.form_submit_button("💾 Save")
                if sv:
                    vt.prefix = pfx
                    db.commit()
                    st.success(f"✅ {name} settings saved!")
            else:
                st.warning(f"VoucherType **{code}** not found in master.")


# ── Section: Purchases ────────────────────────────────────────────────────────

def _section_purchases(db):
    tabs = st.tabs(["💸 Expenses", "📄 Purchase Orders", "🧾 Bills",
                    "💳 Payments Made", "📝 Vendor Credits"])

    modules = [
        ("EXP", "Expenses",        "Expense categories, approvals"),
        ("PINV","Bills",           "Bill number series, payment terms"),
        ("PO",  "Purchase Orders", "PO approval threshold, auto-close"),
        ("PAYO","Payments Made",   "Payment mode defaults"),
        ("VC",  "Vendor Credits",  "Vendor credit application rules"),
    ]

    for i, (code, name, hint) in enumerate(modules):
        with tabs[i]:
            vt = db.query(VoucherType).filter_by(code=code).first()
            st.caption(f"**{name}** — {hint}")
            if vt:
                with st.form(f"pur_{code}_form"):
                    pfx = st.text_input("Prefix", value=vt.prefix)
                    sv  = st.form_submit_button("💾 Save")
                if sv:
                    vt.prefix = pfx
                    db.commit()
                    st.success(f"✅ {name} settings saved!")
            else:
                st.info(f"VoucherType **{code}** not in master data.")


# ── Section: Developer Data ───────────────────────────────────────────────────

def _section_developer(db):
    tab1, tab2, tab3 = st.tabs(["🔗 Webhooks", "🔌 Connections", "📊 API Usage"])

    with tab1:
        hooks = db.query(Webhook).all()
        if hooks:
            hw_rows = [{"Name": h.name, "Event": h.event_code, "URL": h.url[:60]+"...",
                        "Active": "✅" if h.is_active else "❌",
                        "Last Triggered": fmt_date(h.last_triggered_at) if h.last_triggered_at else "Never"}
                       for h in hooks]
            st.dataframe(pd.DataFrame(hw_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No webhooks configured.")

        st.markdown("---")
        st.markdown("#### ➕ Register Webhook")
        with st.form("webhook_form"):
            wh1, wh2 = st.columns(2)
            wh_name  = wh1.text_input("Name *", placeholder="Slack Notification")
            wh_event = wh2.selectbox("Event", [
                "INVOICE_CREATED","INVOICE_PAID","PAYMENT_RECEIVED",
                "PO_CREATED","PO_APPROVED","EXPENSE_SUBMITTED",
                "VOUCHER_POSTED","PARTY_CREATED",
            ])
            wh_url   = st.text_input("URL *", placeholder="https://hooks.slack.com/services/...")
            wh_token = st.text_input("Secret Token (optional)", type="password")
            add_wh   = st.form_submit_button("➕ Add Webhook")
        if add_wh:
            if not wh_name or not wh_url:
                st.error("Name and URL are required.")
            else:
                db.add(Webhook(name=wh_name, url=wh_url, event_code=wh_event,
                               secret_token=wh_token or None))
                db.commit()
                st.success(f"✅ Webhook **{wh_name}** registered!")
                st.rerun()

    with tab2:
        st.markdown("**Configured Integrations**")
        integ = [
            {"Integration": "WhatsApp Business API",  "Status": "⚠️ Not configured",  "Key": "WHATSAPP_API_KEY"},
            {"Integration": "SMS (MSG91 / Twilio)",    "Status": "⚠️ Not configured",  "Key": "SMS_API_KEY"},
            {"Integration": "API Setu (GSTIN Lookup)", "Status": "⚠️ Set API key",     "Key": "GST_API_KEY"},
            {"Integration": "IRP (e-Invoice)",         "Status": "⚠️ Not configured",  "Key": "EINVOICE_IRN_API_URL"},
        ]
        for item in integ:
            val = _cfg(db, item["Key"])
            item["Status"] = "✅ Configured" if val else "⚠️ Not configured"
        st.dataframe(pd.DataFrame(integ).drop(columns=["Key"]), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**WhatsApp Business API**")
        wa_key = st.text_input("WhatsApp API Key", value=_cfg(db,"WHATSAPP_API_KEY"), type="password")
        if st.button("💾 Save WhatsApp Key"):
            _set_cfg(db,"WHATSAPP_API_KEY",wa_key)
            db.commit()
            st.success("✅ WhatsApp API key saved!")

    with tab3:
        api_limit = _cfg(db, "API_RATE_LIMIT_PER_DAY", "1000")
        st.metric("Daily API Limit", api_limit)
        st.metric("API Calls Today", "0")
        st.metric("Webhooks Fired (30d)", db.query(WorkflowLog).count())
        st.info("Full API documentation available at: `/api/docs` (requires API key in Authorization header).")
        new_limit = st.number_input("Update Daily Limit", min_value=100, value=int(api_limit), step=100)
        if st.button("💾 Update Limit"):
            _set_cfg(db,"API_RATE_LIMIT_PER_DAY",str(new_limit))
            db.commit()
            st.success("✅ API limit updated!")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def render_settings_page():
    st.markdown('<div class="main-title">⚙️ Organisation Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Milvian Technologies Private Limited — Complete configuration</div>', unsafe_allow_html=True)
    st.markdown("---")

    db = SessionLocal()
    try:
        _seed_defaults(db)

        SECTIONS = [
            "🏢 Organization",
            "👤 Users & Roles",
            "🧾 Taxes & Compliance",
            "⚙️ Setup & Configurations",
            "🎨 Customization",
            "🤖 Automation",
            "📦 Module Settings",
            "💼 Sales",
            "🛒 Purchases",
            "🔧 Developer Data",
        ]

        nav_col, content_col = st.columns([2, 10])

        with nav_col:
            st.markdown("**Settings**")
            section = st.radio("", SECTIONS, label_visibility="collapsed")
            st.markdown("---")
            co = db.query(Company).first()
            if co:
                st.caption(f"**{co.name}**")
                st.caption(f"Plan: {co.subscription_plan}")
                if co.gstin:
                    st.caption(f"GSTIN: {co.gstin}")

        with content_col:
            if "Organization" in section:
                _section_organization(db)
            elif "Users & Roles" in section:
                _section_users_roles(db)
            elif "Taxes" in section:
                _section_taxes(db)
            elif "Setup" in section:
                _section_setup(db)
            elif "Customization" in section:
                _section_customization(db)
            elif "Automation" in section:
                _section_automation(db)
            elif "Module" in section:
                _section_modules(db)
            elif "Sales" in section:
                _section_sales(db)
            elif "Purchases" in section:
                _section_purchases(db)
            elif "Developer" in section:
                _section_developer(db)
    finally:
        db.close()
