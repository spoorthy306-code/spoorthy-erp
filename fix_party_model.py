#!/usr/bin/env python3
"""Fix missing Party model in finance.py"""

import os
import re

finance_file = 'backend/app/models/finance.py'

# Check if file exists
if not os.path.exists(finance_file):
    print(f"❌ {finance_file} not found")
    exit(1)

print(f"📝 Reading {finance_file}...")

with open(finance_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if Party class already exists
if 'class Party' in content:
    print("✅ Party class already exists")
else:
    print("⚠️  Party class not found, adding it...")
    
    # Find where to insert the Party class
    # Look for the last class definition
    class_positions = [m.start() for m in re.finditer(r'\nclass ', content)]
    
    if class_positions:
        # Insert before the last class or at the end
        insert_pos = class_positions[-1]
        
        # Prepare the Party class definition
        party_class = '''
class Party(Base):
    """Customer/Vendor Party Model"""
    __tablename__ = "parties"
    
    id = Column(Integer, primary_key=True, index=True)
    party_type = Column(String(20), nullable=False)  # 'customer' or 'vendor'
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True)
    gstin = Column(String(15), index=True)
    pan = Column(String(10), index=True)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    credit_limit = Column(Numeric(15, 2), default=0.0)
    current_balance = Column(Numeric(15, 2), default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="party")
    bills = relationship("Bill", back_populates="party")
'''
        
        # Insert the Party class
        new_content = content[:insert_pos] + party_class + content[insert_pos:]
        
        # Write backup
        backup_file = finance_file + '.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📁 Backup saved to {backup_file}")
        
        # Write updated content
        with open(finance_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Added Party class to {finance_file}")
    else:
        print("❌ Could not find where to insert Party class")

print("\n🔍 Verifying Party class...")
with open(finance_file, 'r', encoding='utf-8') as f:
    content = f.read()
    if 'class Party' in content:
        print("✅ Party class successfully added!")
    else:
        print("❌ Failed to add Party class")

