import os
os.system('mkdir -p ui')
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

prompt = """Generate COMPLETE Spoorthy Quantum ERP Streamlit app ui/app.py (2500+ lines).

BACKEND: FastAPI localhost:8000 (companies, vouchers, parties, inventory, dashboard, ledger)
DATABASE: PostgreSQL spoorthy_erp
MCP TOOLS: db_get_trial_balance(), calculate_working_capital()

9 PAGES WITH SIDEBAR NAVIGATION:
1. Dashboard - Live metrics (revenue, vouchers count), Plotly charts
2. Company Setup - GSTIN, FY, auto-create 28 Tally groups  
3. Masters - Ledger groups, UOM, HSN codes, 37 GST states
4. Vouchers - CRUD Sales/Purchase/Journal, PDF upload
5. Parties - Customers/Suppliers list + forms
6. Inventory - Stock levels, MRP calculator
7. Payroll - Employee list, salary processing
8. Bank Reconciliation - Working capital metrics
9. Reports - Trial Balance, P&L, GST returns

FEATURES:
- Login: admin/admin@123 (st.session_state)
- Telugu/English toggle 
- FastAPI integration: requests.get('http://localhost:8000/dashboard')
- MCP tools: subprocess mcp_server functions
- File upload: st.file_uploader for PDF OCR 
- Responsive design, professional theme

Output ONLY valid Python Streamlit code. No explanations."""

resp = client.chat.completions.create(
    model="deepseek-coder:6.7b",  # LIGHTWEIGHT!
    messages=[{"role": "user", "content": prompt}], 
    temperature=0.1
)

with open("ui/app.py", "w") as f:
    f.write(resp.choices[0].message.content)
print("✅ ERP Frontend BUILT! (9 pages, 43 modules)")
