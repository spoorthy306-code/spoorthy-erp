"""
quantum_ui.py — Streamlit UI for 25 Quantum Finance Modules
Quantum Accounting (A1-A12) + Quantum Financial Services (F1-F13)
"""

import json
import streamlit as st
import pandas as pd
from spoorthy_finance_complete import QuantumFinanceHub


@st.cache_resource
def get_hub():
    return QuantumFinanceHub(entity_id="SPOORTHY", group_id="SPOORTHY-GROUP")


def _show_json(data, label="Result"):
    st.markdown(f"**{label}**")
    st.json(data)


def _metrics_from_dict(d: dict, exclude=()):
    """Render top-level numeric values as st.metric cards."""
    items = [(k, v) for k, v in d.items()
             if isinstance(v, (int, float)) and k not in exclude]
    if not items:
        return
    cols = st.columns(min(len(items), 4))
    for i, (k, v) in enumerate(items):
        cols[i % 4].metric(k.replace("_", " ").title(), f"{v:,.4g}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: QUANTUM ACCOUNTING  (A1 – A12)
# ═══════════════════════════════════════════════════════════════════════════════

def render_quantum_accounting():
    st.markdown('<div class="main-title">⚛️ Quantum Accounting</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">12 AI-powered accounting engines — A1 to A12</div>', unsafe_allow_html=True)
    st.markdown("---")

    hub = get_hub()

    tabs = st.tabs([
        "A1 Reconciliation", "A2 Consolidation", "A3 Immutable Ledger",
        "A4 Transfer Pricing", "A5 Working Capital", "A6 Fin Statements",
        "A7 IC Elimination", "A8 Payroll Optimizer", "A9 Continuous Acctg",
        "A10 IFRS9 ECL", "A11 Collections", "A12 AP Optimizer",
    ])

    # ── A1: Quantum Reconciliation ────────────────────────────────────────────
    with tabs[0]:
        st.markdown("#### A1 · Quantum Reconciliation Engine")
        st.caption("Many-to-many bank reconciliation via D-Wave QUBO. Target: 99.2% auto-match rate.")

        with st.form("a1_form"):
            st.markdown("**Bank Credits** (JSON array)")
            bank_json = st.text_area("bank_credits", value=json.dumps([
                {"id": "BC1", "amount": 50000.0, "date": "2026-03-01"},
                {"id": "BC2", "amount": 25000.0, "date": "2026-03-02"},
                {"id": "BC3", "amount": 75000.0, "date": "2026-03-03"},
            ], indent=2), height=150)
            st.markdown("**Open Items / Invoices** (JSON array)")
            items_json = st.text_area("open_items", value=json.dumps([
                {"id": "INV01", "amount": 25000.0, "party": "Vendor A"},
                {"id": "INV02", "amount": 25000.0, "party": "Vendor B"},
                {"id": "INV03", "amount": 75000.0, "party": "Vendor C"},
            ], indent=2), height=150)
            submitted = st.form_submit_button("🔍 Run Reconciliation", use_container_width=True)

        if submitted:
            try:
                bank_credits = json.loads(bank_json)
                open_items   = json.loads(items_json)
                result = hub.reconciliation.reconcile(bank_credits, open_items)
                report = hub.reconciliation.get_reconciliation_report(result)

                col1, col2, col3 = st.columns(3)
                col1.metric("Match Rate", f"{report.get('match_rate_pct', 0):.1f}%")
                col2.metric("Matched", len(result.get("matched", [])))
                col3.metric("Unmatched Bank", report.get("unmatched_bank_count", 0))

                if result.get("matched"):
                    st.markdown("**Matched Pairs**")
                    st.dataframe(pd.DataFrame(result["matched"]), use_container_width=True, hide_index=True)
                _show_json(report, "Reconciliation Report")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A2: Financial Consolidation ───────────────────────────────────────────
    with tabs[1]:
        st.markdown("#### A2 · Real-Time Financial Consolidation")
        st.caption("Multi-entity, multi-currency consolidation with IC elimination and CTA.")

        with st.form("a2_form"):
            entities_json = st.text_area("Entities (JSON array)", value=json.dumps([
                {"id": "E1", "name": "Spoorthy India",  "currency": "INR",
                 "revenue": 10000000, "expenses": 7500000, "assets": 50000000,
                 "liabilities": 20000000,
                 "ic_transactions": [{"counterparty": "E2", "type": "loan", "amount": 1000000}]},
                {"id": "E2", "name": "Spoorthy UAE",    "currency": "AED",
                 "revenue": 5000000,  "expenses": 3000000, "assets": 20000000,
                 "liabilities": 8000000,
                 "ic_transactions": [{"counterparty": "E1", "type": "loan", "amount": 1000000}]},
            ], indent=2), height=220)
            submitted = st.form_submit_button("📊 Consolidate", use_container_width=True)

        if submitted:
            try:
                entities = json.loads(entities_json)
                result   = hub.consolidation.consolidate(entities)

                pl = result.get("consolidated_pl", {})
                bs = result.get("consolidated_bs", {})
                col1, col2, col3 = st.columns(3)
                col1.metric("Revenue (INR)", f"₹{pl.get('revenue',0):,.0f}")
                col2.metric("PAT",           f"₹{pl.get('pat',0):,.0f}")
                col3.metric("Total Assets",  f"₹{bs.get('total_assets',0):,.0f}")

                st.markdown("**Consolidated P&L**")
                st.json(pl)
                st.markdown("**Consolidated Balance Sheet**")
                st.json(bs)
                st.markdown("**IC Eliminations**")
                st.json(result.get("ic_eliminations", {}))
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A3: Quantum Immutable Ledger ──────────────────────────────────────────
    with tabs[2]:
        st.markdown("#### A3 · Quantum Audit Trail & Immutable Ledger")
        st.caption("PQC-signed (ML-DSA) journal entries with hash-chained audit trail.")

        op = st.selectbox("Operation", ["Post Entry", "Verify Chain", "Trial Balance"])

        if op == "Post Entry":
            with st.form("a3_post"):
                narration = st.text_input("Narration", value="Purchase of office supplies")
                lines_json = st.text_area("Journal Lines (JSON)", value=json.dumps([
                    {"account": "Office Expenses", "debit": 5000, "credit": 0},
                    {"account": "Cash",            "debit": 0,    "credit": 5000},
                ], indent=2), height=130)
                submitted = st.form_submit_button("📝 Post Entry", use_container_width=True)
            if submitted:
                try:
                    entry = {"date": str(pd.Timestamp.today().date()),
                             "narration": narration,
                             "lines": json.loads(lines_json)}
                    result = hub.ledger.post_entry(entry)
                    st.success(f"✅ Entry posted: {result.get('entry_id')}")
                    _show_json(result, "Posted Entry")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif op == "Verify Chain":
            if st.button("🔐 Verify Audit Chain", use_container_width=True):
                try:
                    result = hub.ledger.verify_chain()
                    status = result.get("integrity_status", "UNKNOWN")
                    if status == "VALID":
                        st.success(f"✅ Chain VALID — {result.get('chain_length', 0)} entries verified")
                    else:
                        st.error(f"❌ Chain {status} — {len(result.get('violations', []))} violations")
                    _show_json(result)
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            if st.button("📊 Generate Trial Balance", use_container_width=True):
                try:
                    result = hub.ledger.get_trial_balance()
                    st.metric("Balanced", "✅ Yes" if result.get("balanced") else "❌ No")
                    st.metric("Total Debit",  f"₹{result.get('total_debit',0):,.2f}")
                    st.metric("Total Credit", f"₹{result.get('total_credit',0):,.2f}")
                    _show_json(result.get("accounts", {}), "Accounts")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── A4: Transfer Pricing ──────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("#### A4 · Transfer Pricing Engine")
        st.caption("OECD BEPS compliant arm's-length pricing with CbCR stub.")

        with st.form("a4_form"):
            comp_json = st.text_area("Comparable Transactions (JSON)", value=json.dumps([
                {"id": "C1", "margin": 0.12}, {"id": "C2", "margin": 0.15},
                {"id": "C3", "margin": 0.10}, {"id": "C4", "margin": 0.18},
                {"id": "C5", "margin": 0.13},
            ], indent=2), height=130)
            txn_json = st.text_area("Intercompany Transactions (JSON)", value=json.dumps([
                {"id": "IC1", "amount": 1000000, "type": "services", "margin": 0.08},
                {"id": "IC2", "amount": 500000,  "type": "goods",    "margin": 0.20},
            ], indent=2), height=100)
            submitted = st.form_submit_button("⚖️ Optimize Prices", use_container_width=True)

        if submitted:
            try:
                comparables = json.loads(comp_json)
                transactions = json.loads(txn_json)
                arm_range = hub.transfer_pricing.calculate_arms_length_range(comparables)
                result    = hub.transfer_pricing.optimize_intercompany_price(transactions, comparables)

                col1, col2, col3 = st.columns(3)
                col1.metric("Arm's Length Range", f"{arm_range['q1']*100:.1f}% – {arm_range['q3']*100:.1f}%")
                col2.metric("Optimal Margin", f"{result.get('optimal_margin',0)*100:.2f}%")
                col3.metric("Tax Saving", f"₹{result.get('total_tax_saving',0):,.0f}")

                st.success("✅ BEPS Compliant" if result.get("beps_compliant") else "⚠️ Review Required")
                _show_json(result, "Pricing Result")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A5: Working Capital Optimizer ─────────────────────────────────────────
    with tabs[4]:
        st.markdown("#### A5 · Quantum Working Capital Optimizer")
        st.caption("AP/AR/Inventory QUBO optimization to maximise cash release.")

        with st.form("a5_form"):
            col1, col2 = st.columns(2)
            with col1:
                cash = st.number_input("Cash Balance (₹)", value=5000000.0, step=100000.0, format="%.0f")
            with col2:
                st.write("")

            ap_json = st.text_area("AP Items (JSON)", value=json.dumps([
                {"id":"AP1","amount":200000,"due_date":"2026-04-01","discount_pct":2.0,"discount_days":10,"supplier":"ABC"},
                {"id":"AP2","amount":150000,"due_date":"2026-04-15","discount_pct":1.5,"discount_days":7, "supplier":"XYZ"},
            ], indent=2), height=110)
            ar_json = st.text_area("AR Items (JSON)", value=json.dumps([
                {"id":"AR1","amount":300000,"collection_prob":0.9,"days_overdue":15,"party":"Client A"},
                {"id":"AR2","amount":100000,"collection_prob":0.6,"days_overdue":45,"party":"Client B"},
            ], indent=2), height=110)
            inv_json = st.text_area("Inventory (JSON)", value=json.dumps([
                {"sku":"SKU1","value":500000,"holding_cost_pct":0.20,"reorder_point":100,"current_stock":300},
            ], indent=2), height=80)
            submitted = st.form_submit_button("💰 Optimize", use_container_width=True)

        if submitted:
            try:
                result = hub.working_capital.optimize(
                    json.loads(ap_json), json.loads(ar_json),
                    json.loads(inv_json), cash
                )
                col1, col2 = st.columns(2)
                col1.metric("Cash Release", f"₹{result.get('total_cash_release',0):,.0f}")
                col2.metric("WC Improvement", f"₹{result.get('working_capital_improvement',0):,.0f}")
                _show_json(result, "Working Capital Plan")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A6: Financial Statement Generator ────────────────────────────────────
    with tabs[5]:
        st.markdown("#### A6 · Financial Statement Auto-Generator")
        st.caption("IFRS / Ind AS / US GAAP compliant statement generation.")

        stmt_type = st.selectbox("Statement", ["P&L", "Balance Sheet", "Cash Flow"])

        if stmt_type == "P&L":
            with st.form("a6_pl"):
                col1, col2 = st.columns(2)
                with col1:
                    revenue   = st.number_input("Revenue (₹)", value=10000000.0, format="%.0f")
                    cogs      = st.number_input("COGS (₹)",    value=6000000.0,  format="%.0f")
                    opex      = st.number_input("OpEx (₹)",    value=2000000.0,  format="%.0f")
                with col2:
                    other_inc = st.number_input("Other Income (₹)",  value=100000.0, format="%.0f")
                    int_exp   = st.number_input("Interest Expense (₹)", value=200000.0, format="%.0f")
                    tax_exp   = st.number_input("Tax Expense (₹)",    value=570000.0,  format="%.0f")
                submitted = st.form_submit_button("📄 Generate P&L", use_container_width=True)
            if submitted:
                try:
                    result = hub.statement_gen.generate_pl({
                        "revenue": revenue, "cogs": cogs, "opex": opex,
                        "other_income": other_inc, "int_expense": int_exp, "tax_expense": tax_exp
                    })
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Gross Profit",  f"₹{result.get('gross_profit',0):,.0f}")
                    col2.metric("EBIT",          f"₹{result.get('ebit',0):,.0f}")
                    col3.metric("PAT",           f"₹{result.get('pat',0):,.0f}")
                    col1.metric("Gross Margin",  f"{result.get('gross_margin_pct',0):.1f}%")
                    col2.metric("EBITDA",        f"₹{result.get('ebitda',0):,.0f}")
                    _show_json(result, "P&L Statement")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif stmt_type == "Balance Sheet":
            with st.form("a6_bs"):
                col1, col2 = st.columns(2)
                with col1:
                    curr_assets    = st.number_input("Current Assets (₹)",       value=15000000.0, format="%.0f")
                    nc_assets      = st.number_input("Non-Current Assets (₹)",   value=35000000.0, format="%.0f")
                with col2:
                    curr_liab      = st.number_input("Current Liabilities (₹)",  value=8000000.0,  format="%.0f")
                    nc_liab        = st.number_input("Non-Current Liabilities (₹)", value=12000000.0, format="%.0f")
                submitted = st.form_submit_button("📄 Generate Balance Sheet", use_container_width=True)
            if submitted:
                try:
                    result = hub.statement_gen.generate_balance_sheet({
                        "current_assets": curr_assets, "non_current_assets": nc_assets,
                        "current_liabilities": curr_liab, "non_current_liabilities": nc_liab
                    })
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Assets",      f"₹{result.get('total_assets',0):,.0f}")
                    col2.metric("Total Liabilities", f"₹{result.get('total_liabilities',0):,.0f}")
                    col3.metric("Equity",            f"₹{result.get('equity',0):,.0f}")
                    col1.metric("Current Ratio",     f"{result.get('current_ratio',0):.2f}")
                    col2.metric("D/E Ratio",         f"{result.get('debt_equity_ratio',0):.2f}")
                    st.success("✅ Balanced") if result.get("balance_check") else st.error("❌ Imbalanced")
                except Exception as e:
                    st.error(f"Error: {e}")

        else:  # Cash Flow
            with st.form("a6_cf"):
                col1, col2 = st.columns(2)
                with col1:
                    pat        = st.number_input("PAT (₹)",          value=1330000.0, format="%.0f")
                    dep        = st.number_input("Depreciation (₹)", value=500000.0,  format="%.0f")
                    wc_change  = st.number_input("Working Capital Δ (₹)", value=-200000.0, format="%.0f")
                with col2:
                    capex      = st.number_input("CapEx (₹)",          value=2000000.0, format="%.0f")
                    disposal   = st.number_input("Asset Disposal (₹)", value=300000.0,  format="%.0f")
                submitted = st.form_submit_button("📄 Generate Cash Flow", use_container_width=True)
            if submitted:
                try:
                    result = hub.statement_gen.generate_cash_flow(
                        {"pat": pat, "depreciation": dep},
                        {"working_capital_change": wc_change, "capex": capex, "asset_disposal": disposal}
                    )
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Operating CF",  f"₹{result.get('operating_activities',{}).get('net_operating_cf',0):,.0f}")
                    col2.metric("Investing CF",  f"₹{result.get('investing_activities',{}).get('net_investing_cf',0):,.0f}")
                    col3.metric("Net Change",    f"₹{result.get('net_change_in_cash',0):,.0f}")
                    col1.metric("Free Cash Flow", f"₹{result.get('free_cash_flow',0):,.0f}")
                    _show_json(result, "Cash Flow Statement")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── A7: Intercompany Elimination ──────────────────────────────────────────
    with tabs[6]:
        st.markdown("#### A7 · Intercompany Elimination Engine")
        st.caption("Auto IC netting with discrepancy detection.")

        with st.form("a7_form"):
            ic_json = st.text_area("IC Transactions (JSON)", value=json.dumps([
                {"id":"IC1","from":"E1","to":"E2","type":"loan",    "amount":1000000},
                {"id":"IC2","from":"E2","to":"E1","type":"services","amount":500000},
                {"id":"IC3","from":"E1","to":"E3","type":"goods",   "amount":750000},
            ], indent=2), height=150)
            submitted = st.form_submit_button("🔄 Eliminate IC Transactions", use_container_width=True)

        if submitted:
            try:
                result = hub.ic_elimination.eliminate(json.loads(ic_json))
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Eliminated",  f"₹{result.get('total_eliminated',0):,.0f}")
                col2.metric("Discrepancies",     len(result.get("discrepancies", [])))
                col3.metric("Clean",             "✅ Yes" if result.get("clean") else "⚠️ Review")
                _show_json(result, "Elimination Result")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A8: Payroll Structure Optimizer ──────────────────────────────────────
    with tabs[7]:
        st.markdown("#### A8 · Quantum Payroll Structure Optimizer")
        st.caption("India HRA/LTA/NPS optimization — minimises income tax under old & new regime.")

        with st.form("a8_form"):
            col1, col2 = st.columns(2)
            with col1:
                ctc = st.number_input("Annual CTC (₹)", value=1500000.0, step=100000.0, format="%.0f")
            with col2:
                city_type = st.selectbox("City Type", ["METRO", "NON-METRO"])
            submitted = st.form_submit_button("🧮 Optimize Salary Structure", use_container_width=True)

        if submitted:
            try:
                result = hub.payroll_optimizer.optimize(ctc, city_type)
                col1, col2, col3 = st.columns(3)
                col1.metric("Monthly Take-Home",  f"₹{result.get('monthly_take_home',0):,.0f}")
                col2.metric("Annual Tax Saving",  f"₹{result.get('annual_tax_saving',0):,.0f}")
                col3.metric("Recommended Regime", result.get("recommended_regime", ""))

                st.markdown("**Optimized Salary Structure**")
                struct = result.get("optimized_structure", {})
                if struct:
                    st.dataframe(pd.DataFrame([{"Component": k, "Amount (₹)": f"{v:,.0f}"}
                                               for k, v in struct.items()]),
                                 use_container_width=True, hide_index=True)
                col1, col2 = st.columns(2)
                col1.metric("Tax (Old Regime)", f"₹{result.get('tax_old_regime',0):,.0f}")
                col2.metric("Tax (New Regime)", f"₹{result.get('tax_new_regime',0):,.0f}")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A9: Continuous Accounting ─────────────────────────────────────────────
    with tabs[8]:
        st.markdown("#### A9 · Continuous Accounting Engine")
        st.caption("Real-time perpetual close — daily accruals and depreciation.")

        op = st.selectbox("Operation", ["Daily Accruals", "Daily Depreciation", "Live P&L"])

        if op == "Daily Accruals":
            with st.form("a9_acc"):
                contracts_json = st.text_area("Contracts (JSON)", value=json.dumps([
                    {"id":"C1","description":"Office Rent","monthly_amount":150000},
                    {"id":"C2","description":"Software License","monthly_amount":50000},
                ], indent=2), height=120)
                submitted = st.form_submit_button("📅 Post Daily Accruals", use_container_width=True)
            if submitted:
                try:
                    result = hub.continuous_accounting.post_daily_accruals(json.loads(contracts_json))
                    st.success(f"✅ {len(result)} accrual entries posted")
                    st.dataframe(pd.DataFrame(result), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")

        elif op == "Daily Depreciation":
            with st.form("a9_dep"):
                assets_json = st.text_area("Assets (JSON)", value=json.dumps([
                    {"id":"FA1","name":"Server","annual_depreciation":120000},
                    {"id":"FA2","name":"Furniture","annual_depreciation":25000},
                ], indent=2), height=120)
                submitted = st.form_submit_button("📅 Post Daily Depreciation", use_container_width=True)
            if submitted:
                try:
                    result = hub.continuous_accounting.post_daily_depreciation(json.loads(assets_json))
                    st.success(f"✅ {len(result)} depreciation entries posted")
                    st.dataframe(pd.DataFrame(result), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            if st.button("📊 Get Live P&L", use_container_width=True):
                try:
                    result = hub.continuous_accounting.get_live_pl()
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Revenue (YTD)",  f"₹{result.get('revenue',0):,.0f}")
                    col2.metric("Expenses (YTD)", f"₹{result.get('expenses',0):,.0f}")
                    col3.metric("PBT",            f"₹{result.get('pbt',0):,.0f}")
                    st.caption(f"Latency: {result.get('latency','—')}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── A10: IFRS9 ECL Model ──────────────────────────────────────────────────
    with tabs[9]:
        st.markdown("#### A10 · Quantum Bad Debt Provisioning (IFRS 9 ECL)")
        st.caption("Expected Credit Loss model with stage classification (Stage 1/2/3).")

        with st.form("a10_form"):
            recv_json = st.text_area("Receivables (JSON)", value=json.dumps([
                {"id":"AR1","amount":500000,"days_overdue":0,  "credit_rating":"AAA"},
                {"id":"AR2","amount":300000,"days_overdue":35, "credit_rating":"BBB"},
                {"id":"AR3","amount":200000,"days_overdue":95, "credit_rating":"BB"},
                {"id":"AR4","amount":100000,"days_overdue":200,"credit_rating":"CCC"},
            ], indent=2), height=160)
            submitted = st.form_submit_button("📊 Calculate ECL", use_container_width=True)

        if submitted:
            try:
                result = hub.ecl_model.calculate_ecl(json.loads(recv_json))
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Exposure",   f"₹{result.get('total_exposure',0):,.0f}")
                col2.metric("Total ECL",        f"₹{result.get('total_ecl',0):,.0f}")
                col3.metric("Coverage Ratio",   f"{result.get('coverage_ratio',0)*100:.2f}%")
                st.success("✅ IFRS 9 Compliant" if result.get("ifrs9_compliant") else "⚠️ Review")

                rows = [{"ID": r["id"], "Amount": f"₹{r['amount']:,.0f}",
                          "Stage": r.get("stage"), "ECL": f"₹{r.get('ecl',0):,.0f}"}
                         for r in result.get("receivables", [])]
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A11: Collections Optimizer ────────────────────────────────────────────
    with tabs[10]:
        st.markdown("#### A11 · Quantum Collections Optimizer")
        st.caption("Prioritise AR collections by expected recovery value.")

        with st.form("a11_form"):
            col1, col2 = st.columns(2)
            with col1:
                capacity = st.number_input("Agent Capacity (accounts/day)", value=5, min_value=1)
            ar_json = st.text_area("AR Accounts (JSON)", value=json.dumps([
                {"id":"C1","amount":500000,"days_overdue":10,"collection_prob":0.95,"contact_attempts":1},
                {"id":"C2","amount":200000,"days_overdue":45,"collection_prob":0.70,"contact_attempts":2},
                {"id":"C3","amount":800000,"days_overdue":90,"collection_prob":0.40,"contact_attempts":3},
                {"id":"C4","amount":100000,"days_overdue":5, "collection_prob":0.99,"contact_attempts":0},
                {"id":"C5","amount":350000,"days_overdue":60,"collection_prob":0.55,"contact_attempts":2},
                {"id":"C6","amount":150000,"days_overdue":120,"collection_prob":0.25,"contact_attempts":5},
            ], indent=2), height=180)
            submitted = st.form_submit_button("📞 Prioritize Collections", use_container_width=True)

        if submitted:
            try:
                result = hub.collections.prioritize(json.loads(ar_json), int(capacity))
                col1, col2, col3 = st.columns(3)
                col1.metric("Expected Recovery", f"₹{result.get('expected_recovery',0):,.0f}")
                col2.metric("Recovery Rate Est", f"{result.get('recovery_rate_est',0)*100:.1f}%")
                col3.metric("Accounts Assigned", len(result.get("assigned_accounts", [])))

                if result.get("assigned_accounts"):
                    st.markdown("**Priority Queue**")
                    rows = [{"ID": a["id"], "Amount": f"₹{a['amount']:,.0f}",
                              "Priority Score": f"{a.get('priority_score',0):.3f}",
                              "Action": a.get("action","")}
                             for a in result["assigned_accounts"]]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── A12: AP Payment Optimizer ─────────────────────────────────────────────
    with tabs[11]:
        st.markdown("#### A12 · Quantum Accounts Payable Optimizer")
        st.caption("Optimize payment timing to capture early-payment discounts while preserving cash.")

        with st.form("a12_form"):
            col1, col2 = st.columns(2)
            with col1:
                cash_bal = st.number_input("Available Cash (₹)", value=2000000.0, format="%.0f")
            invoices_json = st.text_area("Invoices (JSON)", value=json.dumps([
                {"id":"INV1","supplier":"Vendor A","amount":300000,"due_date":"2026-04-15","discount_pct":2.0,"discount_days":10},
                {"id":"INV2","supplier":"Vendor B","amount":500000,"due_date":"2026-04-20","discount_pct":1.5,"discount_days":7},
                {"id":"INV3","supplier":"Vendor C","amount":200000,"due_date":"2026-05-01","discount_pct":3.0,"discount_days":15},
            ], indent=2), height=150)
            submitted = st.form_submit_button("💳 Optimize Payments", use_container_width=True)

        if submitted:
            try:
                result = hub.ap_optimizer.optimize_payment_schedule(json.loads(invoices_json), cash_bal)
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Saving",   f"₹{result.get('total_saving',0):,.0f}")
                col2.metric("Early Pays",     result.get("early_pays", 0))
                col3.metric("Cash Remaining", f"₹{result.get('cash_after_schedule',0):,.0f}")

                if result.get("payment_schedule"):
                    rows = [{"Invoice": p["invoice_id"], "Supplier": p.get("supplier",""),
                              "Pay Early": "✅" if p.get("pay_early") else "—",
                              "Pay Date": p.get("pay_date",""), "Saving": f"₹{p.get('saving',0):,.0f}"}
                             for p in result["payment_schedule"]]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: QUANTUM FINANCIAL SERVICES  (F1 – F13)
# ═══════════════════════════════════════════════════════════════════════════════

def render_quantum_finance():
    st.markdown('<div class="main-title">💹 Quantum Financial Services</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">13 AI-powered financial engines — F1 to F13</div>', unsafe_allow_html=True)
    st.markdown("---")

    hub = get_hub()

    tabs = st.tabs([
        "F1 Portfolio Mgmt", "F2 Derivatives", "F3 VaR Engine",
        "F4 IR Risk", "F5 Loan Pricing", "F6 Reg Capital",
        "F7 Stress Test", "F8 Insurance", "F9 Robo Advisor",
        "F10 Debt Schedule", "F11 Settlement", "F12 FX Exposure", "F13 AI Risk Officer",
    ])

    # ── F1: Portfolio Manager ─────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("#### F1 · Quantum Portfolio Manager")
        st.caption("D-Wave QUBO allocation + rebalancing with Sharpe ratio optimization.")

        op = st.selectbox("Operation", ["Optimize Allocation", "Rebalance Portfolio"], key="f1_op")

        if op == "Optimize Allocation":
            with st.form("f1_opt"):
                universe_json = st.text_area("Asset Universe (JSON)", value=json.dumps([
                    {"ticker":"RELIANCE","expected_return":0.14,"volatility":0.22,"sector":"Energy","asset_class":"Equity"},
                    {"ticker":"INFY",    "expected_return":0.18,"volatility":0.25,"sector":"IT","asset_class":"Equity"},
                    {"ticker":"HDFCBK",  "expected_return":0.13,"volatility":0.20,"sector":"Finance","asset_class":"Equity"},
                    {"ticker":"GSEC10Y", "expected_return":0.072,"volatility":0.05,"sector":"Govt","asset_class":"Bond"},
                    {"ticker":"GOLDETF", "expected_return":0.08,"volatility":0.15,"sector":"Commodity","asset_class":"Gold"},
                ], indent=2), height=200)
                submitted = st.form_submit_button("📊 Optimize Portfolio", use_container_width=True)
            if submitted:
                try:
                    result = hub.portfolio.optimize_allocation(json.loads(universe_json))
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Expected Return", f"{result.get('portfolio_return_pct',0):.2f}%")
                    col2.metric("Volatility",       f"{result.get('portfolio_vol_pct',0):.2f}%")
                    col3.metric("Sharpe Ratio",     f"{result.get('sharpe_ratio',0):.3f}")

                    alloc = result.get("allocation", [])
                    if alloc:
                        df = pd.DataFrame(alloc)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            with st.form("f1_reb"):
                current_json = st.text_area("Current Positions (JSON)", value=json.dumps([
                    {"ticker":"RELIANCE","current_weight":0.30,"portfolio_value":1000000},
                    {"ticker":"INFY",    "current_weight":0.40,"portfolio_value":1000000},
                    {"ticker":"GSEC10Y", "current_weight":0.30,"portfolio_value":1000000},
                ], indent=2), height=150)
                target_json = st.text_area("Target Allocation (JSON)", value=json.dumps([
                    {"ticker":"RELIANCE","weight":0.25},
                    {"ticker":"INFY",    "weight":0.35},
                    {"ticker":"GSEC10Y", "weight":0.25},
                    {"ticker":"GOLDETF", "weight":0.15},
                ], indent=2), height=150)
                submitted = st.form_submit_button("🔄 Generate Rebalance Trades", use_container_width=True)
            if submitted:
                try:
                    trades = hub.portfolio.rebalance(json.loads(current_json), json.loads(target_json))
                    st.dataframe(pd.DataFrame(trades), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── F2: Derivatives Pricer ────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("#### F2 · Quantum Derivatives Pricing")
        st.caption("Black-Scholes + barrier options + interest rate swaps.")

        instr = st.selectbox("Instrument", ["European Option (BSM)", "Barrier Option", "Interest Rate Swap"], key="f2_inst")

        if instr == "European Option (BSM)":
            with st.form("f2_bsm"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    S     = st.number_input("Spot Price (S)", value=1450.0)
                    K     = st.number_input("Strike (K)",     value=1500.0)
                with col2:
                    T     = st.number_input("Expiry (Years)", value=0.25, step=0.05)
                    r     = st.number_input("Risk-free Rate", value=0.065, step=0.005, format="%.4f")
                with col3:
                    sigma = st.number_input("Volatility (σ)", value=0.22, step=0.01, format="%.3f")
                submitted = st.form_submit_button("💹 Price Option", use_container_width=True)
            if submitted:
                try:
                    result = hub.derivatives.black_scholes_call(S, K, T, r, sigma)
                    col1, col2 = st.columns(2)
                    col1.metric("Call Price", f"₹{result.get('call_price',0):,.2f}")
                    col2.metric("Put Price",  f"₹{result.get('put_price',0):,.2f}")
                    greeks = result.get("greeks", {})
                    g_cols = st.columns(4)
                    for i, (k, v) in enumerate(greeks.items()):
                        g_cols[i].metric(k.title(), f"{v:.4f}")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif instr == "Barrier Option":
            with st.form("f2_barrier"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    S   = st.number_input("Spot (S)",    value=1450.0)
                    K   = st.number_input("Strike (K)",  value=1500.0)
                    B   = st.number_input("Barrier (B)", value=1350.0)
                with col2:
                    T   = st.number_input("Expiry (Y)",  value=0.5, step=0.05)
                    r   = st.number_input("Rate (r)",    value=0.065, format="%.4f")
                with col3:
                    sig = st.number_input("Vol (σ)",     value=0.22, format="%.3f")
                    opt_type = st.selectbox("Type", ["down-and-out-call","up-and-out-call",
                                                      "down-and-in-call","up-and-in-call"])
                submitted = st.form_submit_button("💹 Price Barrier Option", use_container_width=True)
            if submitted:
                try:
                    result = hub.derivatives.price_barrier_option(S, K, B, T, r, sig, opt_type)
                    col1, col2 = st.columns(2)
                    col1.metric("Option Price", f"₹{result.get('price',0):,.4f}")
                    col2.metric("Barrier Level", f"₹{result.get('barrier',0):,.2f}")
                    _show_json(result)
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            with st.form("f2_swap"):
                col1, col2 = st.columns(2)
                with col1:
                    notional  = st.number_input("Notional (₹)", value=10000000.0, format="%.0f")
                    fixed_r   = st.number_input("Fixed Rate",   value=0.072, format="%.4f")
                    float_r   = st.number_input("Floating Rate (MIBOR)", value=0.068, format="%.4f")
                with col2:
                    tenor     = st.number_input("Tenor (Years)", value=5, min_value=1)
                    freq      = st.number_input("Frequency/Year", value=2, min_value=1)
                submitted = st.form_submit_button("💹 Price Swap", use_container_width=True)
            if submitted:
                try:
                    result = hub.derivatives.price_interest_rate_swap(notional, fixed_r, float_r, tenor, freq)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("PV Fixed Leg",    f"₹{result.get('pv_fixed_leg',0):,.0f}")
                    col2.metric("PV Floating Leg", f"₹{result.get('pv_floating_leg',0):,.0f}")
                    col3.metric("MTM (Fixed Payer)", f"₹{result.get('mtm_fixed_payer',0):,.0f}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── F3: VaR Engine ────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("#### F3 · Quantum Value at Risk (VaR)")
        st.caption("Parametric VaR + CVaR/ES via Quantum Monte Carlo (Grover amplitude estimation).")

        with st.form("f3_form"):
            col1, col2 = st.columns(2)
            with col1:
                confidence  = st.selectbox("Confidence Level", [0.95, 0.99], index=1)
                horizon     = st.number_input("Horizon (Days)", value=10, min_value=1)
            positions_json = st.text_area("Positions (JSON)", value=json.dumps([
                {"asset":"NIFTY50",  "value":5000000, "volatility_annual":0.18, "beta":1.0},
                {"asset":"USDINR",   "value":2000000, "volatility_annual":0.06, "beta":0.2},
                {"asset":"GSEC10Y",  "value":3000000, "volatility_annual":0.05, "beta":0.0},
            ], indent=2), height=150)
            submitted = st.form_submit_button("📊 Calculate VaR", use_container_width=True)

        if submitted:
            try:
                result = hub.var_engine.calculate_var(json.loads(positions_json), confidence, horizon)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Parametric VaR",  f"₹{result.get('parametric_var',0):,.0f}")
                col2.metric(f"VaR {horizon}D",  f"₹{result.get('var_10d',0):,.0f}")
                col3.metric("CVaR/ES",          f"₹{result.get('cvar_es',0):,.0f}")
                col4.metric("Quantum MC VaR",   f"₹{result.get('quantum_mc_var',0):,.0f}")
                st.success("✅ Basel IMS Compliant") if result.get("basel_ims_compliant") else st.warning("⚠️ Check Parameters")
                _show_json(result)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── F4: Interest Rate Risk ────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("#### F4 · Quantum Interest Rate Risk")
        st.caption("Duration, convexity, DV01 analysis with 13 parallel yield scenarios.")

        with st.form("f4_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                face   = st.number_input("Face Value (₹)", value=1000000.0, format="%.0f")
                coupon = st.number_input("Coupon Rate",    value=0.072, format="%.4f")
            with col2:
                ytm    = st.number_input("YTM",            value=0.075, format="%.4f")
                years  = st.number_input("Tenor (Years)",  value=10,    min_value=1)
            with col3:
                freq   = st.number_input("Coupon Freq/Year", value=2, min_value=1)
            submitted = st.form_submit_button("📐 Analyze Bond", use_container_width=True)

        if submitted:
            try:
                result = hub.ir_risk.analyze_bond(face, coupon, ytm, int(years), int(freq))
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Dirty Price",      f"₹{result.get('dirty_price',0):,.2f}")
                col2.metric("Mod. Duration",    f"{result.get('modified_duration',0):.3f}")
                col3.metric("Convexity",        f"{result.get('convexity',0):.3f}")
                col4.metric("DV01",             f"₹{result.get('dv01',0):,.2f}")

                scenarios = result.get("yield_scenarios", [])
                if scenarios:
                    st.markdown("**Yield Shift Scenarios**")
                    st.dataframe(pd.DataFrame(scenarios), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── F5: Loan Pricing ──────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("#### F5 · Quantum Loan Pricing Engine")
        st.caption("Risk-adjusted NIM optimizer with RAROC and RWA calculations.")

        op = st.selectbox("Operation", ["Price Single Loan", "Optimize Loan Portfolio"], key="f5_op")

        if op == "Price Single Loan":
            with st.form("f5_single"):
                col1, col2 = st.columns(2)
                with col1:
                    amount    = st.number_input("Loan Amount (₹)", value=5000000.0, format="%.0f")
                    rating    = st.selectbox("Credit Rating", ["AAA","AA","A","BBB","BB","B","CCC","D"])
                with col2:
                    tenor     = st.number_input("Tenor (Years)", value=5.0, step=0.5)
                    loan_type = st.selectbox("Loan Type", ["term_loan","working_capital","mortgage","personal"])
                submitted = st.form_submit_button("💳 Price Loan", use_container_width=True)
            if submitted:
                try:
                    result = hub.loan_pricing.price_loan(amount, rating, tenor, loan_type)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("All-In Rate",  f"{result.get('all_in_rate_pct',0):.2f}%")
                    col2.metric("Annual NIM",   f"₹{result.get('annual_nim',0):,.0f}")
                    col3.metric("RWA",          f"₹{result.get('risk_weighted_asset',0):,.0f}")
                    col1.metric("Expected Loss",f"₹{result.get('expected_loss',0):,.0f}")
                    col2.metric("ROE Est.",     f"{result.get('roe_est_pct',0):.2f}%")
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            with st.form("f5_port"):
                capital = st.number_input("Available Capital (₹)", value=50000000.0, format="%.0f")
                pipeline_json = st.text_area("Loan Pipeline (JSON)", value=json.dumps([
                    {"id":"L1","amount":10000000,"rating":"AAA","tenor":5,"type":"term_loan"},
                    {"id":"L2","amount":5000000, "rating":"BBB","tenor":3,"type":"working_capital"},
                    {"id":"L3","amount":20000000,"rating":"AA", "tenor":7,"type":"mortgage"},
                    {"id":"L4","amount":3000000, "rating":"B",  "tenor":2,"type":"personal"},
                ], indent=2), height=160)
                submitted = st.form_submit_button("📊 Optimize Portfolio", use_container_width=True)
            if submitted:
                try:
                    result = hub.loan_pricing.optimize_portfolio(json.loads(pipeline_json), capital)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Loans",   result.get("total_loans", 0))
                    col2.metric("Total NIM",     f"₹{result.get('total_nim',0):,.0f}")
                    col3.metric("Capital Used",  f"₹{result.get('capital_used',0):,.0f}")
                    _show_json(result)
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── F6: Regulatory Capital ────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("#### F6 · Regulatory Capital Optimizer")
        st.caption("Basel III/IV CET1, Tier-1, Total CAR compliance and RWA optimization.")

        op = st.selectbox("Operation", ["Calculate RWA", "Check Compliance"], key="f6_op")

        if op == "Calculate RWA":
            with st.form("f6_rwa"):
                assets_json = st.text_area("Assets (JSON)", value=json.dumps([
                    {"id":"A1","category":"sovereign",   "value":100000000},
                    {"id":"A2","category":"corporate_AA","value":50000000},
                    {"id":"A3","category":"retail",      "value":30000000},
                    {"id":"A4","category":"mortgage",    "value":80000000},
                    {"id":"A5","category":"equity",      "value":20000000},
                ], indent=2), height=180)
                submitted = st.form_submit_button("⚖️ Calculate RWA", use_container_width=True)
            if submitted:
                try:
                    result = hub.capital_optimizer.calculate_rwa(json.loads(assets_json))
                    st.metric("Total RWA", f"₹{result.get('total_rwa',0):,.0f}")
                    if result.get("breakdown"):
                        st.dataframe(pd.DataFrame(result["breakdown"]), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            with st.form("f6_comp"):
                col1, col2 = st.columns(2)
                with col1:
                    cet1     = st.number_input("CET1 Capital (₹)",   value=15000000.0, format="%.0f")
                    tier1    = st.number_input("Tier-1 Capital (₹)", value=18000000.0, format="%.0f")
                with col2:
                    total_c  = st.number_input("Total Capital (₹)",  value=22000000.0, format="%.0f")
                    rwa      = st.number_input("RWA (₹)",            value=140000000.0, format="%.0f")
                submitted = st.form_submit_button("✅ Check Basel Compliance", use_container_width=True)
            if submitted:
                try:
                    result = hub.capital_optimizer.check_compliance(cet1, tier1, total_c, rwa)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("CET1 Ratio",  f"{result.get('cet1_ratio',0):.2f}%")
                    col2.metric("Tier-1 Ratio", f"{result.get('tier1_ratio',0):.2f}%")
                    col3.metric("Total CAR",    f"{result.get('total_car',0):.2f}%")
                    col1.metric("Surplus Capital", f"₹{result.get('surplus_capital',0):,.0f}")
                    if result.get("cet1_compliant") and result.get("tier1_compliant"):
                        st.success("✅ Basel III/IV Compliant")
                    else:
                        st.error("❌ Capital Deficiency — Action Required")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── F7: Stress Testing ────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown("#### F7 · Quantum Stress Testing")
        st.caption("Adverse / Severe / Tail scenarios with regulatory breach detection.")

        with st.form("f7_form"):
            portfolio_val = st.number_input("Portfolio Value (₹)", value=100000000.0, format="%.0f")
            col1, col2, col3, col4 = st.columns(4)
            with col1: eq_pct  = st.number_input("Equity %",  value=40.0, step=5.0)
            with col2: bd_pct  = st.number_input("Bond %",    value=30.0, step=5.0)
            with col3: cr_pct  = st.number_input("Credit %",  value=20.0, step=5.0)
            with col4: fx_pct  = st.number_input("FX %",      value=10.0, step=5.0)
            submitted = st.form_submit_button("🔴 Run Stress Test", use_container_width=True)

        if submitted:
            try:
                composition = {"equity_pct": eq_pct, "bond_pct": bd_pct,
                                "credit_pct": cr_pct, "fx_pct": fx_pct}
                result = hub.stress_tester.run_stress_test(portfolio_val, composition)
                col1, col2, col3 = st.columns(3)
                col1.metric("Worst Scenario",  result.get("worst_scenario",""))
                col2.metric("Max Loss",        f"₹{result.get('max_loss',0):,.0f}")
                col3.metric("Reg. Breach",     "⚠️ YES" if result.get("regulatory_breach") else "✅ NO")

                scenarios = result.get("scenarios", {})
                if scenarios:
                    rows = [{"Scenario": s, "Total Loss %": f"{v.get('total_loss_pct',0):.1f}%",
                              "Total Loss ₹": f"₹{v.get('total_loss_pct',0)*portfolio_val/100:,.0f}"}
                             for s, v in scenarios.items()]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    _show_json(scenarios, "Scenario Details")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── F8: Insurance Underwriting ────────────────────────────────────────────
    with tabs[7]:
        st.markdown("#### F8 · Quantum Insurance Underwriting")
        st.caption("Actuarial pricing for term life and cyber insurance.")

        product = st.selectbox("Product", ["Term Life", "Cyber Insurance"], key="f8_prod")

        if product == "Term Life":
            with st.form("f8_life"):
                col1, col2 = st.columns(2)
                with col1:
                    age        = st.number_input("Age", value=35, min_value=18, max_value=70)
                    sum_assured= st.number_input("Sum Assured (₹)", value=10000000.0, format="%.0f")
                with col2:
                    term_years = st.number_input("Term (Years)", value=20, min_value=5)
                    smoker     = st.checkbox("Smoker")
                submitted = st.form_submit_button("🧮 Price Policy", use_container_width=True)
            if submitted:
                try:
                    result = hub.insurance.price_term_life(int(age), sum_assured, int(term_years), smoker)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Annual Premium",   f"₹{result.get('annual_premium',0):,.0f}")
                    col2.metric("Mortality Rate",   f"{result.get('mortality_rate',0)*100:.4f}%")
                    col3.metric("Loss Ratio Est.",  f"{result.get('loss_ratio_est',0)*100:.1f}%")
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            with st.form("f8_cyber"):
                col1, col2 = st.columns(2)
                with col1:
                    revenue     = st.number_input("Annual Revenue (₹)", value=500000000.0, format="%.0f")
                    data_records= st.number_input("Data Records", value=100000, step=10000)
                with col2:
                    maturity    = st.selectbox("Security Maturity", ["LOW","MEDIUM","HIGH"])
                submitted = st.form_submit_button("🔐 Price Cyber Policy", use_container_width=True)
            if submitted:
                try:
                    result = hub.insurance.price_cyber_insurance(revenue, int(data_records), maturity)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Annual Premium",     f"₹{result.get('annual_premium',0):,.0f}")
                    col2.metric("Breach Probability", f"{result.get('breach_probability',0)*100:.2f}%")
                    col3.metric("Expected Loss",      f"₹{result.get('expected_loss',0):,.0f}")
                    st.metric("Recommended Limit", f"₹{result.get('recommended_limit',0):,.0f}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── F9: Robo Advisor ──────────────────────────────────────────────────────
    with tabs[8]:
        st.markdown("#### F9 · Quantum Wealth Management (Robo Advisor)")
        st.caption("SEBI IA compliant portfolio recommendation for HNI clients.")

        with st.form("f9_form"):
            col1, col2 = st.columns(2)
            with col1:
                amount    = st.number_input("Investment Amount (₹)", value=5000000.0, format="%.0f")
                age_score = st.slider("Age Score (1=young, 5=near-retirement)", 1, 5, 2)
                inc_score = st.slider("Income Stability (1=low, 5=high)", 1, 5, 4)
            with col2:
                horizon   = st.slider("Investment Horizon (1=short, 5=long)", 1, 5, 4)
                loss_tol  = st.slider("Loss Tolerance (1=low, 5=high)", 1, 5, 3)
            submitted = st.form_submit_button("💼 Get Portfolio Recommendation", use_container_width=True)

        if submitted:
            try:
                q = {"age_score": age_score, "income_stability": inc_score,
                     "investment_horizon": horizon, "loss_tolerance": loss_tol}
                profile    = hub.robo_advisor.profile_investor(q)
                result     = hub.robo_advisor.recommend_portfolio(amount, profile)

                col1, col2, col3 = st.columns(3)
                col1.metric("Risk Profile",      profile)
                col2.metric("Expected Return",   f"{result.get('portfolio_return_pct',0):.2f}%")
                col3.metric("Sharpe Ratio",      f"{result.get('sharpe_ratio',0):.3f}")
                col1.metric("3Y Expected Value", f"₹{result.get('3yr_expected_value',0):,.0f}")
                col2.metric("3Y Worst Case P1",  f"₹{result.get('3yr_worst_case_p01',0):,.0f}")
                st.success("✅ SEBI IA Compliant") if result.get("sebi_ia_compliant") else st.warning("⚠️ Check")

                if result.get("allocation"):
                    st.dataframe(pd.DataFrame(result["allocation"]), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── F10: Debt Scheduling ──────────────────────────────────────────────────
    with tabs[9]:
        st.markdown("#### F10 · Quantum Debt Scheduling Optimizer")
        st.caption("Optimal debt repayment via QUBO — Avalanche strategy with prepayment analysis.")

        with st.form("f10_form"):
            col1, col2 = st.columns(2)
            with col1:
                monthly_fcf  = st.number_input("Monthly FCF (₹)", value=500000.0, format="%.0f")
                cash_buffer  = st.number_input("Min Cash Buffer (₹)", value=1000000.0, format="%.0f")
            debts_json = st.text_area("Debt Instruments (JSON)", value=json.dumps([
                {"id":"D1","name":"Term Loan","outstanding":5000000,"rate":0.115,"maturity_months":48,"prepayment_penalty":0.02},
                {"id":"D2","name":"CC Limit", "outstanding":1500000,"rate":0.185,"maturity_months":12,"prepayment_penalty":0.0},
                {"id":"D3","name":"NCD",      "outstanding":3000000,"rate":0.095,"maturity_months":24,"prepayment_penalty":0.01},
            ], indent=2), height=160)
            submitted = st.form_submit_button("📅 Optimize Debt Schedule", use_container_width=True)

        if submitted:
            try:
                result = hub.debt_scheduler.optimize(json.loads(debts_json), monthly_fcf, cash_buffer)
                col1, col2 = st.columns(2)
                col1.metric("Total Interest Saving", f"₹{result.get('total_interest_saving',0):,.0f}")
                col2.metric("Strategy", result.get("strategy",""))

                if result.get("payment_schedule"):
                    rows = [{"Debt": p["debt_id"], "Action": p.get("action",""),
                              "Prepay (₹)": f"₹{p.get('prepay_amount',0):,.0f}",
                              "Interest Saving": f"₹{p.get('interest_saving',0):,.0f}"}
                             for p in result["payment_schedule"]]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── F11: Interbank Settlement ─────────────────────────────────────────────
    with tabs[10]:
        st.markdown("#### F11 · Interbank Settlement Optimizer")
        st.caption("RTGS multilateral netting — reduces gross settlement by 60-85%.")

        with st.form("f11_form"):
            positions_json = st.text_area("Bilateral Positions (JSON)", value=json.dumps([
                {"from_bank":"HDFC","to_bank":"SBI",   "gross_amount":50000000},
                {"from_bank":"SBI", "to_bank":"HDFC",  "gross_amount":35000000},
                {"from_bank":"ICICI","to_bank":"HDFC", "gross_amount":25000000},
                {"from_bank":"HDFC","to_bank":"ICICI", "gross_amount":40000000},
                {"from_bank":"AXIS","to_bank":"SBI",   "gross_amount":15000000},
                {"from_bank":"SBI", "to_bank":"AXIS",  "gross_amount":20000000},
            ], indent=2), height=200)
            submitted = st.form_submit_button("⚡ Run Multilateral Netting", use_container_width=True)

        if submitted:
            try:
                result = hub.settlement.multilateral_netting(json.loads(positions_json))
                col1, col2, col3 = st.columns(3)
                col1.metric("Gross Total",      f"₹{result.get('gross_total',0):,.0f}")
                col2.metric("Net Total",        f"₹{result.get('net_total',0):,.0f}")
                col3.metric("Netting Ratio",    f"{result.get('netting_ratio',0)*100:.1f}%")
                st.metric("Liquidity Saved",    f"₹{result.get('liquidity_saved',0):,.0f}")

                instructions = result.get("settlement_instructions", [])
                if instructions:
                    st.dataframe(pd.DataFrame(instructions), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── F12: FX Exposure ──────────────────────────────────────────────────────
    with tabs[11]:
        st.markdown("#### F12 · Quantum FX Exposure Management")
        st.caption("Natural hedge + overlay strategy with cost-optimized hedge recommendations.")

        with st.form("f12_form"):
            col1, col2 = st.columns(2)
            with col1:
                hedge_ratio = st.slider("Hedge Ratio", 0.0, 1.0, 0.75, 0.05)
            fx_json = st.text_area("FX Positions (JSON)", value=json.dumps([
                {"currency":"USD","receivable":5000000,"payable":2000000,"investment":1000000},
                {"currency":"EUR","receivable":1000000,"payable":500000, "investment":0},
                {"currency":"AED","receivable":2000000,"payable":3000000,"investment":500000},
            ], indent=2), height=160)
            submitted = st.form_submit_button("🌐 Analyze & Hedge FX", use_container_width=True)

        if submitted:
            try:
                exposure = hub.fx_manager.measure_exposure(json.loads(fx_json))
                hedges   = hub.fx_manager.recommend_hedges(exposure, hedge_ratio)

                net_exp = exposure.get("net_exposures", {})
                col1, col2 = st.columns(2)
                col1.metric("Total Exposure (USD eq.)", f"${exposure.get('total_exposure',0):,.0f}")
                col2.metric("Total Hedge Cost",          f"₹{hedges.get('total_annual_cost',0):,.0f}")
                col1.metric("Residual Exposure",         f"${hedges.get('residual_exposure',0):,.0f}")

                if hedges.get("recommendations"):
                    recs = [{"Currency": r.get("currency"), "Direction": r.get("direction"),
                              "Instrument": r.get("instrument"), "Annual Cost": f"₹{r.get('annual_cost',0):,.0f}"}
                             for r in hedges["recommendations"]]
                    st.dataframe(pd.DataFrame(recs), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # ── F13: AI Risk Officer ──────────────────────────────────────────────────
    with tabs[12]:
        st.markdown("#### F13 · AI Risk Officer Agent")
        st.caption("Daily risk report combining VaR, Basel compliance, stress test — PQC signed.")

        with st.form("f13_form"):
            col1, col2 = st.columns(2)
            with col1:
                eq_pct2 = st.number_input("Equity %",  value=50.0, step=5.0, key="f13_eq")
                bd_pct2 = st.number_input("Bond %",    value=30.0, step=5.0, key="f13_bd")
            with col2:
                cr_pct2 = st.number_input("Credit %",  value=15.0, step=5.0, key="f13_cr")
                fx_pct2 = st.number_input("FX %",      value=5.0,  step=5.0, key="f13_fx")
            positions_json2 = st.text_area("Positions (JSON)", value=json.dumps([
                {"asset":"NIFTY50","value":10000000,"volatility_annual":0.18,"beta":1.0},
                {"asset":"GSEC",   "value":6000000, "volatility_annual":0.05,"beta":0.0},
                {"asset":"CREDIT", "value":3000000, "volatility_annual":0.08,"beta":0.3},
            ], indent=2), height=130)
            capital_json = st.text_area("Capital Data (JSON)", value=json.dumps(
                {"cet1":15000000,"tier1":18000000,"total_capital":22000000,"rwa":140000000},
                indent=2), height=100)
            submitted = st.form_submit_button("🤖 Generate Daily Risk Report", use_container_width=True)

        if submitted:
            try:
                composition = {"equity_pct": eq_pct2, "bond_pct": bd_pct2,
                                "credit_pct": cr_pct2, "fx_pct": fx_pct2}
                result = hub.risk_officer.daily_risk_report(
                    json.loads(positions_json2), composition, json.loads(capital_json)
                )
                severity = result.get("severity", "LOW")
                if severity == "HIGH" or result.get("escalate"):
                    st.error(f"🚨 ESCALATE — Severity: {severity}")
                else:
                    st.success(f"✅ Risk OK — Severity: {severity}")

                col1, col2, col3 = st.columns(3)
                col1.metric("VaR 10D 99%",   f"₹{result.get('var_10d_99pct',0):,.0f}")
                col2.metric("Capital CAR",    f"{result.get('capital_car_pct',0):.2f}%")
                col3.metric("Stress Worst",   result.get("stress_worst",""))

                breaches = result.get("breaches", [])
                if breaches:
                    st.warning("**Breaches Detected:**")
                    for b in breaches:
                        st.write(f"• {b}")

                st.info(f"**Recommendation:** {result.get('recommendation','')}")
                st.caption(f"PQC Signature: `{result.get('pqc_signature','')[:40]}...`")
            except Exception as e:
                st.error(f"Error: {e}")
