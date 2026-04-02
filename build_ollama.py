import os
os.system('mkdir -p ui')
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
prompt = """Build COMPLETE Spoorthy ERP Streamlit ui/app.py for ~/spoorthy_complete.

BACKEND: FastAPI localhost:8000 (companies/vouchers/parties/inventory/dashboard/ledger), PostgreSQL, 50 MCP tools (db_get_trial_balance, calculate_working_capital).

9 PAGES: 
- Dashboard: Live metrics, Plotly quantum QAOA charts (CuPy), risk alerts
- Company: GSTIN/FY setup, 28 Tally groups
- Masters: Groups/Ledgers/UOM/HSN/37 GST states
- Vouchers: CRUD sales/purchase/journal, PDF OCR upload (pdfplumber)
- Parties: Customers/suppliers, GSTR-2B alerts
- Inventory: Stock/MRP/WMS
- Payroll: Attendance/PF-ESI
- BankRec: Auto-match, working capital tool
- Reports: TB/P&L/GST returns, PDF export

FEATURES: Telugu/English toggle, admin/admin@123 login (st.session_state), PySwissEph Panchangam dates, JWT auth, Railway.app ready.

MCP INTEGRATE: import subprocess; subprocess.run(["python", "-c", "from mcp_server import db_get_trial_balance; print(db_get_trial_balance())"])

Output ONLY valid Python Streamlit code for ui/app.py (3000+ lines)."""
resp = client.chat.completions.create(model="codestral:22b", messages=[{"role": "user", "content": prompt}], temperature=0.1)
with open("ui/app.py", "w") as f:
    f.write(resp.choices[0].message.content)
print("✅ ui/app.py GENERATED (43 modules)!")
