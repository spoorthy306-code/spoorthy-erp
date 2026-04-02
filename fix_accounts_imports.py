#!/usr/bin/env python3
"""Fix missing imports in accounts.py"""

import re

accounts_file = 'backend/app/api/accounts.py'

# Read the file
with open(accounts_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check what imports are present
print("Current imports:")
import_lines = re.findall(r'^from .+ import .+$|^import .+$', content, re.MULTILINE)
for line in import_lines:
    print(f"  {line}")

# Add missing imports if needed
missing_imports = []

if 'Optional' not in content and 'typing' not in content:
    missing_imports.append('from typing import Optional, List, Dict, Any')
elif 'Optional' not in content and 'from typing' in content:
    # Need to add Optional to existing typing import
    content = re.sub(r'from typing import (.*)', r'from typing import \1, Optional', content)
    print("\n✅ Added Optional to typing import")
elif 'Optional' not in content:
    # Add new typing import at the top
    content = 'from typing import Optional, List, Dict, Any\n' + content
    print("\n✅ Added typing import")

# Also check for date import if needed
if 'date' not in content and 'datetime' in content:
    # date is already imported via datetime
    pass

# Write the fixed file
with open(accounts_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Fixed missing imports in accounts.py")

