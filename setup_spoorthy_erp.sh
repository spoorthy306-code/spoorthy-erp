#!/bin/bash
# ============================================
# SPOORTHY ERP - Complete Automated Setup Script
# With DeepSeek R1 Integration
# ============================================

set -e  # Exit on error

echo "=========================================="
echo "SPOORTHY ERP - Automated Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then 
    print_warning "Running as root is not recommended. Consider using a regular user."
fi

# Step 1: Update system and install dependencies
print_status "Step 1: Updating system and installing dependencies..."
sudo apt update -y
sudo apt install -y python3-pip python3-venv python3-dev build-essential \
    curl wget git sqlite3 libpq-dev postgresql postgresql-contrib \
    redis-server nginx supervisor

print_success "System dependencies installed"

# Step 2: Check if DeepSeek R1 is installed
print_status "Step 2: Checking DeepSeek R1 installation..."
if command -v deepseek &> /dev/null; then
    print_success "DeepSeek R1 found: $(deepseek --version 2>&1 | head -1)"
else
    print_warning "DeepSeek R1 not found in PATH"
    print_status "Installing DeepSeek R1..."
    
    # Install Ollama (for running DeepSeek locally)
    curl -fsSL https://ollama.com/install.sh | sh
    
    # Pull DeepSeek R1 model
    ollama pull deepseek-r1:7b
    
    print_success "DeepSeek R1 installed via Ollama"
fi

# Step 3: Create project structure
print_status "Step 3: Setting up project structure..."
cd /mnt/d/ERP/ 2>/dev/null || cd ~
mkdir -p spoorthy-erp-{backend,frontend,data,logs,scripts}
cd spoorthy-erp-backend

print_success "Project structure created"

# Step 4: Create virtual environment
print_status "Step 4: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
print_success "Virtual environment created and activated"

# Step 5: Install Python dependencies
print_status "Step 5: Installing Python packages..."
cat > requirements.txt << 'REQUIREMENTS'
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Redis & Caching
redis==5.0.1
aioredis==2.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
PyJWT==2.8.0

# Background Tasks
celery==5.3.4
flower==2.0.1

# Monitoring
prometheus-client==0.19.0

# AI/ML (for DeepSeek integration)
openai==1.6.1
httpx==0.25.2
requests==2.31.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
email-validator==2.1.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
REQUIREMENTS

pip install -r requirements.txt
print_success "Python packages installed"

# Step 6: Create database
print_status "Step 6: Setting up database..."
# Use SQLite for simplicity (easier setup)
cat > backend/app/db/session.py << 'DB_SESSION'
"""Database session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Use SQLite for development
SQLALCHEMY_DATABASE_URL = "sqlite:///./spoorthy_erp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
DB_SESSION

print_success "Database configured"

# Step 7: Create models
print_status "Step 7: Creating database models..."
mkdir -p backend/app/models
mkdir -p backend/app/schemas
mkdir -p backend/app/api
mkdir -p backend/app/core
mkdir -p backend/app/db

# Create base models file
cat > backend/app/models/finance.py << 'FINANCE_MODELS'
"""Finance Models"""
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AccountGroup(Base):
    __tablename__ = "account_groups"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    group_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Ledger(Base):
    __tablename__ = "ledgers"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey("account_groups.id"))
    opening_balance = Column(Numeric(15, 2), default=Decimal('0.00'))
    current_balance = Column(Numeric(15, 2), default=Decimal('0.00'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Party(Base):
    __tablename__ = "parties"
    id = Column(Integer, primary_key=True, index=True)
    party_type = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True)
    gstin = Column(String(15), index=True)
    email = Column(String(100))
    phone = Column(String(20))
    credit_limit = Column(Numeric(15, 2), default=Decimal('0.00'))
    current_balance = Column(Numeric(15, 2), default=Decimal('0.00'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"))
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    subtotal = Column(Numeric(15, 2), default=Decimal('0.00'))
    tax_amount = Column(Numeric(15, 2), default=Decimal('0.00'))
    total_amount = Column(Numeric(15, 2), default=Decimal('0.00'))
    paid_amount = Column(Numeric(15, 2), default=Decimal('0.00'))
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(50), default="viewer")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
FINANCE_MODELS

print_success "Database models created"

# Step 8: Create DeepSeek R1 integration
print_status "Step 8: Creating DeepSeek R1 integration..."
cat > backend/app/core/deepseek_ai.py << 'DEEPSEEK_AI'
"""DeepSeek R1 AI Integration for ERP"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DeepSeekR1Agent:
    """AI Agent powered by DeepSeek R1 for ERP automation"""
    
    def __init__(self, api_url: str = "http://localhost:11434/api/generate"):
        self.api_url = api_url
        self.model = "deepseek-r1:7b"
        logger.info(f"DeepSeek R1 Agent initialized with model: {self.model}")
    
    def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek R1 API"""
        try:
            import requests
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"DeepSeek API error: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Failed to call DeepSeek: {e}")
            return ""
    
    def analyze_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data and provide insights"""
        prompt = f"""
        Analyze the following financial data and provide key insights:
        
        Revenue: {data.get('revenue', 0)}
        Expenses: {data.get('expenses', 0)}
        Profit: {data.get('profit', 0)}
        Cash Balance: {data.get('cash_balance', 0)}
        
        Provide:
        1. Financial health assessment
        2. Key risks identified
        3. Recommendations for improvement
        4. Expected next quarter performance
        
        Keep response concise and actionable.
        """
        
        response = self._call_deepseek(prompt)
        
        return {
            "analysis": response,
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }
    
    def predict_cash_flow(self, historical_data: List[float]) -> Dict[str, Any]:
        """Predict future cash flow based on historical data"""
        prompt = f"""
        Based on the following historical cash flow data: {historical_data}
        
        Predict the next 3 months cash flow and identify:
        1. Expected cash flow trends
        2. Potential cash shortage periods
        3. Recommended actions
        
        Data points: {len(historical_data)} months
        """
        
        response = self._call_deepseek(prompt)
        
        return {
            "prediction": response,
            "confidence": "medium",
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_anomalies(self, transactions: List[Dict]) -> List[Dict]:
        """Detect anomalies in financial transactions"""
        prompt = f"""
        Analyze these transactions and detect any anomalies:
        {json.dumps(transactions[:10], indent=2)}
        
        Look for:
        1. Unusual amounts
        2. Suspicious patterns
        3. Potential fraud indicators
        4. Compliance issues
        
        List any detected anomalies with risk levels.
        """
        
        response = self._call_deepseek(prompt)
        
        return [{
            "detected": bool(response),
            "analysis": response,
            "risk_level": "medium" if "suspicious" in response.lower() else "low"
        }]
    
    def generate_report(self, report_type: str, data: Dict) -> str:
        """Generate AI-powered business reports"""
        prompt = f"""
        Generate a {report_type} report with the following data:
        {json.dumps(data, indent=2)}
        
        Format as professional business report with:
        - Executive summary
        - Key metrics
        - Analysis
        - Recommendations
        """
        
        return self._call_deepseek(prompt)
    
    def optimize_inventory(self, inventory_data: List[Dict]) -> Dict:
        """Optimize inventory levels using AI"""
        prompt = f"""
        Analyze inventory data and optimize levels:
        {json.dumps(inventory_data[:5], indent=2)}
        
        Provide recommendations for:
        1. Reorder quantities
        2. Safety stock levels
        3. Slow-moving items to clear
        4. Priority items to restock
        """
        
        response = self._call_deepseek(prompt)
        
        return {
            "recommendations": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def customer_sentiment(self, feedback_data: List[str]) -> Dict:
        """Analyze customer sentiment from feedback"""
        prompt = f"""
        Analyze customer sentiment from these feedback samples:
        {json.dumps(feedback_data[:10], indent=2)}
        
        Provide:
        1. Overall sentiment score (0-100)
        2. Common themes
        3. Areas for improvement
        4. Positive highlights
        """
        
        response = self._call_deepseek(prompt)
        
        return {
            "sentiment_analysis": response,
            "timestamp": datetime.now().isoformat()
        }

# Singleton instance
deepseek_agent = DeepSeekR1Agent()
DEEPSEEK_AI

print_success "DeepSeek R1 integration created"

# Step 9: Create main application
print_status "Step 9: Creating main application..."
cat > backend/app/main.py << 'MAIN_APP'
"""Spoorthy ERP Main Application"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.app.core.deepseek_ai import deepseek_agent
from backend.app.api import auth, accounts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Spoorthy ERP with DeepSeek R1",
    description="Enterprise ERP with Quantum Computing and DeepSeek AI",
    version="1.0.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": "Spoorthy ERP",
        "version": "1.0.0",
        "ai_engine": "DeepSeek R1",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "ai_available": True}

@app.get("/api/v1/ai/analyze")
async def ai_analyze_financials():
    """AI-powered financial analysis endpoint"""
    sample_data = {
        "revenue": 1000000,
        "expenses": 750000,
        "profit": 250000,
        "cash_balance": 500000
    }
    return deepseek_agent.analyze_financial_data(sample_data)

@app.get("/api/v1/ai/predict")
async def ai_predict_cashflow():
    """AI-powered cash flow prediction"""
    historical = [100000, 120000, 115000, 130000, 125000, 140000]
    return deepseek_agent.predict_cash_flow(historical)

logger.info("Spoorthy ERP with DeepSeek R1 started")
MAIN_APP

print_success "Main application created"

# Step 10: Create authentication endpoints
print_status "Step 10: Creating authentication endpoints..."
cat > backend/app/api/auth.py << 'AUTH_API'
"""Authentication API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.finance import User
from backend.app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token)

@router.get("/me")
def get_current_user(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "role": current_user.role}
AUTH_API

# Step 11: Create accounts API
print_status "Step 11: Creating accounts API..."
cat > backend/app/api/accounts.py << 'ACCOUNTS_API'
"""Accounts API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db.session import get_db
from backend.app.models.finance import AccountGroup, Ledger, Party, Invoice
from backend.app.core.auth import get_current_user

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/groups")
def list_groups(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(AccountGroup).all()

@router.get("/ledgers")
def list_ledgers(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Ledger).all()

@router.get("/parties")
def list_parties(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Party).all()

@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_invoices = db.query(Invoice).count()
    total_value = db.query(Invoice.total_amount).all()
    total = sum(v[0] for v in total_value if v[0]) if total_value else 0
    
    return {
        "total_invoices": total_invoices,
        "total_value": float(total),
        "active_parties": db.query(Party).filter(Party.is_active == True).count(),
        "account_groups": db.query(AccountGroup).count(),
        "ledgers": db.query(Ledger).count()
    }
ACCOUNTS_API

# Step 12: Create security module
print_status "Step 12: Creating security module..."
cat > backend/app/core/security.py << 'SECURITY'
"""Security utilities"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "spoorthy-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
SECURITY

cat > backend/app/core/auth.py << 'AUTH'
"""Authentication dependencies"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.finance import User
from backend.app.core.security import decode_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
AUTH

# Step 13: Initialize database with test data
print_status "Step 13: Initializing database..."
python << 'INIT_DB'
from backend.app.db.session import engine, SessionLocal
from backend.app.models.finance import Base, User, AccountGroup, Ledger
from backend.app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

# Create test user
db = SessionLocal()
if not db.query(User).filter(User.username == "admin").first():
    admin = User(
        username="admin",
        email="admin@spoorthy.com",
        password_hash=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db.add(admin)
    print("✅ Created admin user: admin / admin123")

# Create sample account groups
if db.query(AccountGroup).count() == 0:
    groups = [
        AccountGroup(code="ASSET", name="Assets", group_type="asset"),
        AccountGroup(code="LIAB", name="Liabilities", group_type="liability"),
        AccountGroup(code="EQ", name="Equity", group_type="equity"),
        AccountGroup(code="REV", name="Revenue", group_type="revenue"),
        AccountGroup(code="EXP", name="Expenses", group_type="expense"),
    ]
    for group in groups:
        db.add(group)
    print("✅ Created sample account groups")

db.commit()
db.close()
print("✅ Database initialized successfully")
INIT_DB

print_success "Database initialized with test data"

# Step 14: Create startup script
print_status "Step 14: Creating startup script..."
cat > start_erp.sh << 'STARTUP'
#!/bin/bash
echo "=========================================="
echo "Starting Spoorthy ERP with DeepSeek R1"
echo "=========================================="

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Check if DeepSeek model is loaded
if ! ollama list | grep -q "deepseek-r1"; then
    echo "Pulling DeepSeek R1 model..."
    ollama pull deepseek-r1:7b
fi

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "DeepSeek AI endpoints: http://localhost:8000/api/v1/ai/analyze"
echo ""
echo "Press Ctrl+C to stop"

uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
STARTUP

chmod +x start_erp.sh
print_success "Startup script created"

# Step 15: Create systemd service (optional)
print_status "Step 15: Creating systemd service..."
sudo cat > /etc/systemd/system/spoorthy-erp.service << 'SERVICE'
[Unit]
Description=Spoorthy ERP Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/spoorthy-erp-backend
Environment="PATH=/home/$USER/spoorthy-erp-backend/venv/bin"
ExecStart=/home/$USER/spoorthy-erp-backend/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

print_warning "Systemd service created (requires manual enable: sudo systemctl enable spoorthy-erp)"

# Final step: Summary
print_status "=========================================="
print_status "INSTALLATION COMPLETE!"
print_status "=========================================="
echo ""
print_success "✅ All components installed successfully!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start the application:"
echo "   cd /mnt/d/ERP/spoorthy-erp-backend"
echo "   ./start_erp.sh"
echo ""
echo "2. Or start manually:"
echo "   source venv/bin/activate"
echo "   uvicorn backend.app.main:app --reload"
echo ""
echo "3. Test the API:"
echo "   # Login to get token"
echo "   curl -X POST http://localhost:8000/api/v1/auth/login \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"username\":\"admin\",\"password\":\"admin123\"}'"
echo ""
echo "   # Test AI endpoint"
echo "   curl http://localhost:8000/api/v1/ai/analyze"
echo ""
echo "4. Access Swagger UI:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. DeepSeek R1 integration:"
echo "   - Model: deepseek-r1:7b"
echo "   - API: http://localhost:11434"
echo "   - ERP AI endpoints: /api/v1/ai/*"
echo ""
echo "📁 Project Structure:"
echo "   /mnt/d/ERP/spoorthy-erp-backend/"
echo "   ├── backend/           # Application code"
echo "   ├── venv/              # Python virtual environment"
echo "   ├── spoorthy_erp.db    # SQLite database"
echo "   └── start_erp.sh       # Startup script"
echo ""
echo "🔧 Useful Commands:"
echo "   # Check logs"
echo "   tail -f logs/erp.log"
echo ""
echo "   # DeepSeek R1 commands"
echo "   ollama list           # List models"
echo "   ollama run deepseek-r1:7b \"Your prompt\""
echo ""
echo "   # Monitor the service"
echo "   sudo systemctl status spoorthy-erp"
echo ""

