#!/usr/bin/env python3
"""Fix duplicate model definitions in finance.py"""

import os

finance_file = 'backend/app/models/finance.py'

# Read the current file
with open(finance_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check for duplicate class definitions
classes_found = {}
duplicate_lines = []
new_lines = []
seen_classes = set()

for i, line in enumerate(lines):
    # Check for class definition
    if line.startswith('class '):
        class_name = line.split('(')[0].replace('class ', '').strip()
        
        if class_name in seen_classes:
            print(f"⚠️  Duplicate class found: {class_name} at line {i+1}")
            duplicate_lines.append(i)
            continue
        else:
            seen_classes.add(class_name)
            new_lines.append(line)
    else:
        new_lines.append(line)

# Write the cleaned file
if duplicate_lines:
    backup = finance_file + '.clean_backup'
    with open(backup, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"📁 Backup saved to {backup}")
    
    with open(finance_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"✅ Removed {len(duplicate_lines)} duplicate class definitions")
else:
    print("✅ No duplicate classes found")

