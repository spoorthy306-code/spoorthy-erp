#!/usr/bin/env python3
"""Test imports to verify everything works"""

import sys
import os
from decimal import Decimal
from datetime import datetime
from typing import Optional

print("=" * 60)
print("TESTING SPOORTHY ERP IMPORTS")
print("=" * 60)

# Test 1: Check Python version
print(f"\n✅ Python version: {sys.version}")

# Test 2: Check virtual environment
print(f"✅ Virtual environment: {sys.prefix}")

# Test 3: Import core packages
try:
    from fastapi import FastAPI, APIRouter, Depends, HTTPException
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    from sqlalchemy import Column, Integer, String, Numeric, create_engine
    from sqlalchemy.orm import Session, sessionmaker
    print("✅ SQLAlchemy imported successfully")
except ImportError as e:
    print(f"❌ SQLAlchemy import failed: {e}")

try:
    from pydantic import BaseModel, Field, validator
    print("✅ Pydantic imported successfully")
except ImportError as e:
    print(f"❌ Pydantic import failed: {e}")

try:
    import redis
    print("✅ Redis imported successfully")
except ImportError as e:
    print(f"❌ Redis import failed: {e}")

try:
    from passlib.context import CryptContext
    print("✅ Passlib imported successfully")
except ImportError as e:
    print(f"❌ Passlib import failed: {e}")

# Test 4: Import local modules
print("\n" + "=" * 60)
print("TESTING LOCAL MODULE IMPORTS")
print("=" * 60)

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Try to import your quantum finance module
try:
    # Check if the file exists
    if os.path.exists('spoorthy_finance_complete.py'):
        print("✅ Found spoorthy_finance_complete.py")
        
        # Try to import classes from it
        from spoorthy_finance_complete import (
            QuantumReconciliationEngine,
            FinancialConsolidationEngine,
            QuantumImmutableLedger,
            WorkingCapitalOptimizer,
            IFRS9ECLModel,
            QuantumPortfolioManager,
            QuantumVaREngine
        )
        print("✅ Quantum modules imported successfully")
    else:
        print("⚠️  spoorthy_finance_complete.py not found in current directory")
except ImportError as e:
    print(f"❌ Failed to import from spoorthy_finance_complete.py: {e}")

# Test 5: Try to import backend modules if they exist
try:
    if os.path.exists('backend'):
        from backend.app.models.finance import AccountGroup, Ledger, Journal
        print("✅ Backend models imported successfully")
except ImportError as e:
    print(f"⚠️  Backend models not found or not importable: {e}")

# Final result
print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\n✅ If you see '✅' for most checks, your environment is ready!")
print("ℹ️  Some warnings are OK if those modules don't exist yet.")
