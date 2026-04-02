#!/usr/bin/env python3
"""Script to find potential Column errors in your code"""
import os
import re
import sys
from pathlib import Path

def find_column_errors(filepath):
    """Find potential Column errors in a file"""
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Skip comments and docstrings
                if line.strip().startswith('#') or line.strip().startswith('"""'):
                    continue
                
                # Look for patterns that might cause Column errors
                patterns = [
                    (r'round\([^,]*\.\w+\)', "Potential Column passed to round() - use instance value"),
                    (r'float\([^,]*\.\w+\)', "Potential Column passed to float() - use instance value"),
                    (r'Decimal\([^,]*\.\w+\)', "Potential Column passed to Decimal() - use instance value"),
                    (r'[\+\-\*\/]\s*[A-Z][a-zA-Z0-9_]*\.\w+', "Potential Column arithmetic with class attribute"),
                    (r'if\s+[A-Z][a-zA-Z0-9_]*\.\w+\s*[<>]=?', "Potential Column comparison with class"),
                ]
                
                for pattern, message in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Check if it's actually a class attribute (starts with capital)
                        if re.search(r'[A-Z][a-zA-Z0-9_]*\.', line):
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
    print("SPOORTHY ERP - COLUMN ERROR SCANNER")
    print("=" * 80)
    
    all_errors = []
    files_scanned = 0
    
    # Scan Python files
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and cache directories
        skip_dirs = ['venv', '__pycache__', '.git', '.vscode', 'node_modules', '.pytest_cache']
        if any(skip in root for skip in skip_dirs):
            continue
        
        for file in files:
            if file.endswith('.py'):
                files_scanned += 1
                filepath = os.path.join(root, file)
                errors = find_column_errors(filepath)
                all_errors.extend(errors)
    
    print(f"\n📁 Files scanned: {files_scanned}")
    print(f"🔍 Potential issues found: {len(all_errors)}")
    
    if all_errors:
        print("\n" + "=" * 80)
        print("⚠️  POTENTIAL COLUMN ERRORS FOUND")
        print("=" * 80)
        
        for err in all_errors[:20]:  # Show first 20
            print(f"\n📍 {err['file']}:{err['line']}")
            print(f"   Code: {err['content']}")
            print(f"   ⚠️  {err['message']}")
            print(f"   💡 Fix: Use instance attribute (lowercase) instead of class attribute (uppercase)")
        
        if len(all_errors) > 20:
            print(f"\n... and {len(all_errors) - 20} more issues")
        
        print("\n" + "=" * 80)
        print("HOW TO FIX:")
        print("=" * 80)
        print("Wrong: round(Invoice.total_amount, 2)")
        print("Right: round(invoice.total_amount, 2)")
        print("\nWrong: Decimal(Journal.total_debit)")
        print("Right: Decimal(journal.total_debit)")
        print("\nWrong: if Invoice.status == 'paid'")
        print("Right: if invoice.status == 'paid'")
        
    else:
        print("\n✅ No obvious Column errors found!")
        print("   Your code looks good!")
    
    print("\n" + "=" * 80)
    
    return len(all_errors)

if __name__ == "__main__":
    sys.exit(main())
