#!/usr/bin/env python3
"""Initialize database with roles and test user"""
import sys
import os
sys.path.insert(0, os.getcwd())

from backend.app.db.session import SessionLocal
from backend.app.models.user import User, Role
from backend.app.core.security import get_password_hash

def init_database():
    """Initialize database with initial data"""
    db = SessionLocal()
    
    try:
        # Create roles
        roles = [
            {"name": "admin", "description": "Administrator - Full access"},
            {"name": "accountant", "description": "Accountant - Financial operations"},
            {"name": "manager", "description": "Manager - Reports and approvals"},
            {"name": "viewer", "description": "Viewer - Read-only access"},
            {"name": "sales", "description": "Sales - Create invoices and quotes"},
            {"name": "cashier", "description": "Cashier - Record payments"},
        ]
        
        created_roles = {}
        for role_data in roles:
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                role = Role(**role_data)
                db.add(role)
                db.flush()
                print(f"✅ Created role: {role_data['name']}")
            else:
                print(f"⚠️  Role already exists: {role_data['name']}")
            created_roles[role_data["name"]] = role
        
        # Create admin user
        admin_role = created_roles.get("admin")
        if admin_role:
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                admin = User(
                    username="admin",
                    email="spoorthy306@gmail.com",
                    password_hash=get_password_hash("admin123"),
                    role_id=admin_role.id,
                    is_active=True
                )
                db.add(admin)
                print("✅ Created admin user: admin / admin123")
            else:
                print("⚠️  Admin user already exists")
        
        # Create test accountant
        accountant_role = created_roles.get("accountant")
        if accountant_role:
            accountant = db.query(User).filter(User.username == "accountant").first()
            if not accountant:
                accountant = User(
                    username="accountant",
                    email="spoorthy306@gmail.com",
                    password_hash=get_password_hash("accountant123"),
                    role_id=accountant_role.id,
                    is_active=True
                )
                db.add(accountant)
                print("✅ Created accountant user: accountant / accountant123")
        
        db.commit()
        print("\n🎉 Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

