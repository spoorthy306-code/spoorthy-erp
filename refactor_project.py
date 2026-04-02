import os
import re

SCHEMA_FILE = "db/schema.py"

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema_content = f.read()

# Define common imports needed for models
COMMON_IMPORTS = """from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum, Numeric, Date, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from backend.db.base import Base
"""

# Categorize headers to target model files
categories = {
    "employee.py": ["17. EMPLOYEES", "21. USER ROLES & USERS", "28. USER PREFERENCES", "29. APPROVAL RULES"],
    "finance.py": ["1. ACCOUNT GROUPS", "2. LEDGERS", "3. PARTIES", "4. VOUCHER TYPES", "5. VOUCHERS", "6. TRANSACTIONS", "12. BANK RECONCILIATION", "13. COST CENTRES", "14. CURRENCIES", "15. FISCAL YEARS", "19. TDS CHALLANS", "20. FIXED ASSETS REGISTER", "21. PROJECTS"],
    "inventory.py": ["7. STOCK GROUPS", "8. STOCK UNITS", "9. STOCK ITEMS", "10. INVOICE LINE ITEMS"],
    "core.py": ["22. SYSTEM CONFIG", "20. COMPANY PROFILE"],
    "operations.py": ["11. DOCUMENTS", "16. AUDIT TRAIL", "22. ORG LOCATIONS", "23. TRANSACTION NUMBER SERIES"]
}

# Find all blocks separated by '# ═════════════════'
# Then put them into appropriate chunks!
blocks = re.split(r'# ═══════════════════════════════════════════════════════════════════════════════\n# \d+\.\s+', schema_content)

files_content = {k: COMMON_IMPORTS + "\n" for k in categories.keys()}
files_content["payroll.py"] = COMMON_IMPORTS + "\n"
files_content["attendance.py"] = COMMON_IMPORTS + "\n"

# Process blocks
for block in blocks[1:]:
    header_end_idx = block.find('\n# ════════')
    header = block[:header_end_idx].strip()
    
    # Identify which file this block belongs to
    assigned_file = None
    for file, headers in categories.items():
        if any(h in header for h in headers) or any(header in h for h in headers) or header.startswith(tuple(h.split('.')[1].strip() for h in headers)):
            assigned_file = file
            break
            
    if not assigned_file:
        assigned_file = "finance.py" # Default fallback
        
    code_body = block[header_end_idx+80:].strip()
    files_content[assigned_file] += "\n# " + header + "\n" + code_body + "\n\n"

# Write out files
os.makedirs("backend/app/models", exist_ok=True)
for filename, content in files_content.items():
    with open(f"backend/app/models/{filename}", "w", encoding="utf-8") as f:
        f.write(content)

# Base DB
with open("backend/db/base.py", "w", encoding="utf-8") as f:
    f.write('''from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here so Alembic can discover them
from backend.app.models.employee import *
from backend.app.models.finance import *
from backend.app.models.inventory import *
from backend.app.models.core import *
from backend.app.models.operations import *
from backend.app.models.payroll import *
from backend.app.models.attendance import *
''')

# DB Session
with open("backend/db/session.py", "w", encoding="utf-8") as f:
    f.write('''import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/erp")

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')

# FastAPI Main
os.makedirs("backend/app/api", exist_ok=True)
os.makedirs("backend/app/schemas", exist_ok=True)
os.makedirs("backend/app/services", exist_ok=True)
os.makedirs("backend/app/core", exist_ok=True)

with open("backend/app/main.py", "w", encoding="utf-8") as f:
    f.write('''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.base import Base
from backend.db.session import engine

app = FastAPI(title="Spoorthy ERP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"status": "Spoorthy ERP API is running"}
''')

# Requirements
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write('''fastapi==0.103.1
uvicorn==0.23.2
sqlalchemy==2.0.20
alembic==1.12.0
psycopg2-binary==2.9.9
redis==5.0.0
pydantic==2.3.0
''')

# Docker Compose
with open("docker-compose.yml", "w", encoding="utf-8") as f:
    f.write('''version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/erp
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - .:/app

  ui:
    image: node:18-alpine
    command: sh -c "mkdir -p ReactApp && cd ReactApp && npx create-react-app . && npm start"
    ports:
      - "3000:3000"
    volumes:
      - ./ui/react:/app/ReactApp

  postgres:
    image: postgres:15
    container_name: erp-postgres
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: erp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    container_name: erp-redis
    restart: always
    ports:
      - "6379:6379"

volumes:
  postgres_data:
''')

# Dockerfile
with open("Dockerfile", "w", encoding="utf-8") as f:
    f.write('''FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''')

# Setup Alembic structure
import subprocess
subprocess.run(["alembic", "init", "backend/db/migrations"], cwd=".")

print("Refactoring completed successfully. Project split into app/models and Docker updated.")
