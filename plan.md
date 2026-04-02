# Spoorthy ERP - Implementation Plan

## 1) Project structure audit
- [x] Confirm main app is Streamlit: `ui/app.py`
- [x] Confirm validation script in `main.py`
- [x] Confirm DB schema in `db/schema.py`, seed in `db/seed.py`
- [x] Added FastAPI ASGI compatibility at `asgi.py` for uvicorn deployments
- [x] Added `.cursorrules` for Cursor/Repo standards
- [x] Added this `plan.md`

## 2) Immediate bug fix
- `uvicorn main:app` failing because no FastAPI app object exists
- solution: `asgi.py` with `app = FastAPI()` + basic endpoints

## 3) Core feature tasks (micro-task loop)
1. auth module: implement login + token management in `auth.py`
2. inventory module: add CRUD endpoints, UI pages
3. billing module: voucher generation and printing
4. reporting module: trial balance, P&L, balance sheet
5. DB migrations: add Alembic scripts (for postgres)
6. tests: add pytest suite for each module

## 4) Testing and reliability
- [x] run `python -m py_compile app.py main.py ui/app.py db/schema.py db/seed.py asgi.py`
- [ ] create tests/test_app.py, tests/test_db.py
- [ ] add CI command for pytest and mypy

## 5) User flows (next sprints)
- login/logout + role-based access
- voucher creation + double-entry ledger
- automated GST/TDS calculation workflows
- document OCR upload + invoice extraction

## 6) Recommended run commands
- Streamlit UI: `streamlit run ui/app.py`
- API compatibility: `uvicorn asgi:app --host 0.0.0.0 --port 8080`
- DB seed: `python main.py`
- optional tests: `python -m pytest`
