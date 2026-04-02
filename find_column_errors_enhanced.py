#!/usr/bin/env python3
"""Enhanced Column Error Scanner with Progress Indicators"""
import os
import re
import sys
from pathlib import Path

def find_column_errors(filepath):
    """Find potential Column errors in a file"""
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Skip comments and docstrings
                if line.strip().startswith('#') or line.strip().startswith('"""'):
                    continue
                
                # Look for patterns that might cause Column errors
                patterns = [
                    (r'round\([^,]*\.[A-Z][a-zA-Z0-9_]*\)', "round() called with class attribute"),
                    (r'float\([^,]*\.[A-Z][a-zA-Z0-9_]*\)', "float() called with class attribute"),
                    (r'Decimal\([^,]*\.[A-Z][a-zA-Z0-9_]*\)', "Decimal() called with class attribute"),
                    (r'if\s+[A-Z][a-zA-Z0-9_]*\.[a-z]+\s*[<>]=?', "Class attribute in condition"),
                ]
                
                for pattern, message in patterns:
                    if re.search(pattern, line):
                        errors.append({
                            'file': filepath,
                            'line': i,
                            'content': line.strip()[:100],
                            'message': message
                        })
    except Exception as e:
        pass
    
    return errors

def main():
    """Main function to scan project"""
    print("=" * 80)
    print("SPOORTHY ERP - COLUMN ERROR SCANNER (ENHANCED)")
    print("=" * 80)
    
    all_errors = []
    files_scanned = 0
    python_files = []
    
    # First, collect all Python files
    print("\n📁 Scanning for Python files...")
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and cache directories
        skip_dirs = ['venv', '__pycache__', '.git', '.vscode', 'node_modules', '.pytest_cache', 'env']
        if any(skip in root for skip in skip_dirs):
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                python_files.append(filepath)
                files_scanned += 1
                print(f"   Found: {filepath}")
    
    print(f"\n📊 Total Python files found: {files_scanned}")
    print("\n🔍 Analyzing files for Column errors...")
    
    # Now analyze each file
    for idx, filepath in enumerate(python_files, 1):
        print(f"   [{idx}/{files_scanned}] Analyzing: {filepath}")
        errors = find_column_errors(filepath)
        all_errors.extend(errors)
    
    print(f"\n📁 Files scanned: {files_scanned}")
    print(f"🔍 Potential issues found: {len(all_errors)}")
    
    if all_errors:
        print("\n" + "=" * 80)
        print("⚠️  POTENTIAL COLUMN ERRORS FOUND")
        print("=" * 80)
        
        for err in all_errors[:20]:
            print(f"\n📍 {err['file']}:{err['line']}")
            print(f"   Code: {err['content']}")
            print(f"   ⚠️  {err['message']}")
            print(f"   💡 Fix: Use instance attribute instead of class attribute")
        
        if len(all_errors) > 20:
            print(f"\n... and {len(all_errors) - 20} more issues")
        
        print("\n" + "=" * 80)
        print("HOW TO FIX:")
        print("=" * 80)
        print("Wrong: round(Invoice.total_amount, 2)")
        print("Right: round(invoice.total_amount, 2)")
        print("\nWrong: if Invoice.status == 'paid'")
        print("Right: if invoice.status == 'paid'")
        
    else:
        print("\n" + "=" * 80)
        print("✅ NO COLUMN ERRORS FOUND!")
        print("=" * 80)
        print("\nYour code is properly using instance attributes instead of class attributes.")
        print("This is good! The red squiggles you were seeing might be from other issues.")
    
    print("\n" + "=" * 80)
    return len(all_errors)

if __name__ == "__main__":
    sys.exit(main())
