import os
import re
from collections import defaultdict

PROJECT_PATH = "."

duplicate_classes = defaultdict(list)
duplicate_tables = defaultdict(list)
import_errors = []
python_files = []

for root, dirs, files in os.walk(PROJECT_PATH):
    for file in files:
        if file.endswith(".py"):
            python_files.append(os.path.join(root, file))

class_pattern = re.compile(r"class\s+(\w+)\(")
table_pattern = re.compile(r'__tablename__\s*=\s*["\'](\w+)["\']')
import_pattern = re.compile(r"from\s+([\w\.]+)\s+import")

for file in python_files:
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

        # detect classes
        for match in class_pattern.findall(content):
            duplicate_classes[match].append(file)

        # detect tables
        for match in table_pattern.findall(content):
            duplicate_tables[match].append(file)

        # detect imports
        for match in import_pattern.findall(content):
            module = match.split(".")[0]
            if not os.path.exists(module):
                import_errors.append((file, module))

print("\n===== DUPLICATE CLASSES =====")
for cls, files in duplicate_classes.items():
    if len(files) > 1:
        print(cls, "->", files)

print("\n===== DUPLICATE TABLES =====")
for tbl, files in duplicate_tables.items():
    if len(files) > 1:
        print(tbl, "->", files)

print("\n===== POSSIBLE IMPORT ERRORS =====")
for err in import_errors[:20]:
    print(err)

print("\nScan Complete.")
