#!/usr/bin/env python3
"""Fix Pydantic V2 orm_mode to from_attributes"""

import os
import re

def fix_orm_mode_in_file(filepath):
    """Replace orm_mode with from_attributes in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if orm_mode exists
    if 'orm_mode' not in content:
        return False
    
    # Replace orm_mode with from_attributes
    new_content = re.sub(r'orm_mode\s*=\s*True', 'from_attributes = True', content)
    
    # Write backup
    backup = filepath + '.backup'
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write fixed content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

# Find all Python files in schemas directory
schema_files = []
for root, dirs, files in os.walk('backend/app/schemas'):
    for file in files:
        if file.endswith('.py'):
            schema_files.append(os.path.join(root, file))

print(f"🔍 Found {len(schema_files)} schema files")
fixed_count = 0

for filepath in schema_files:
    if fix_orm_mode_in_file(filepath):
        print(f"✅ Fixed: {filepath}")
        fixed_count += 1

print(f"\n📊 Fixed {fixed_count} files")
print("💡 Changed 'orm_mode = True' to 'from_attributes = True'")

