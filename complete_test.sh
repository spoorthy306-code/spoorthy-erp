#!/bin/bash
# Complete testing script for Spoorthy ERP

echo "=========================================="
echo "SPOORTHY ERP - COMPLETE SYSTEM TEST"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check virtual environment
echo "1. Checking Virtual Environment..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Virtual environment is active: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment active${NC}"
fi
echo ""

# Test 2: Check Python version
echo "2. Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
echo ""

# Test 3: Check installed packages
echo "3. Checking required packages..."
PACKAGES=("fastapi" "uvicorn" "sqlalchemy" "pydantic" "redis" "passlib" "PyJWT")
MISSING=()
for pkg in "${PACKAGES[@]}"; do
    if pip show $pkg > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $pkg installed${NC}"
    else
        echo -e "${RED}❌ $pkg NOT installed${NC}"
        MISSING+=($pkg)
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Missing packages: ${MISSING[*]}${NC}"
    echo "Run: pip install ${MISSING[*]}"
fi
echo ""

# Test 4: Check Python imports
echo "4. Testing Python imports..."
python test_imports.py 2>&1 | grep -E "✅|❌|⚠️"
echo ""

# Test 5: Check for Column errors
echo "5. Scanning for Column errors..."
python find_column_errors.py 2>&1 | tail -5
echo ""

# Test 6: Check database connection (if PostgreSQL is running)
echo "6. Checking database configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    
    # Check if PostgreSQL is installed and running
    if command -v pg_isready > /dev/null 2>&1; then
        if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ PostgreSQL is running${NC}"
        else
            echo -e "${YELLOW}⚠️  PostgreSQL not running (optional for development)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  PostgreSQL not installed (optional)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found (optional, can use environment variables)${NC}"
fi
echo ""

# Test 7: Check Redis (if configured)
echo "7. Checking Redis..."
if command -v redis-cli > /dev/null 2>&1; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis not running (optional)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis not installed (optional)${NC}"
fi
echo ""

# Test 8: Check project structure
echo "8. Checking project structure..."
STRUCTURE_OK=true
for dir in "backend" "backend/app" "backend/app/api" "backend/app/models" "backend/app/schemas" "backend/app/core"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir/ exists${NC}"
    else
        echo -e "${YELLOW}⚠️  $dir/ missing (will be created as needed)${NC}"
        STRUCTURE_OK=false
    fi
done
echo ""

# Test 9: Check main.py
echo "9. Checking application entry point..."
if [ -f "backend/app/main.py" ]; then
    echo -e "${GREEN}✅ backend/app/main.py exists${NC}"
    
    # Try to import the app
    python -c "from backend.app.main import app" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Application can be imported successfully${NC}"
    else
        echo -e "${RED}❌ Application import failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  backend/app/main.py not found${NC}"
    echo "   Run: mkdir -p backend/app && touch backend/app/main.py"
fi
echo ""

# Final summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Make sure PostgreSQL is running (if using)"
echo "  2. Run: uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"
echo "  3. Open browser: http://localhost:8000/docs"
echo ""
echo "To fix common issues:"
echo "  - Install missing packages: pip install -r requirements.txt"
echo "  - Fix Column errors: Use instance attributes (lowercase) instead of class attributes"
echo "  - Restart language server: Ctrl+Shift+P → 'Python: Restart Language Server'"
echo ""

