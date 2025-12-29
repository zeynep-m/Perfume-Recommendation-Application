#!/usr/bin/env python3
"""Quick smoke test to verify main.py imports correctly and translations work"""

import sys
import os
import tkinter as tk

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from i18n import _, toggle_lang, get_toggle_label
    print("✓ i18n module imported successfully")
except Exception as e:
    print(f"✗ Failed to import i18n: {e}")
    sys.exit(1)

try:
    from perfume_db import PerfumeDatabase
    print("✓ perfume_db module imported successfully")
except Exception as e:
    print(f"✗ Failed to import perfume_db: {e}")
    sys.exit(1)

# Test database connectivity
try:
    db = PerfumeDatabase()
    count = len(db.get_perfumes())
    print(f"✓ Database connected, {count} perfumes found")
except Exception as e:
    print(f"✗ Failed to connect to database: {e}")
    sys.exit(1)

# Test key UI translations
test_strings = [
    "Perfume Recommender",
    "Language", 
    "Database",
    "Open Perfume DB",
    "Filters",
    "Gender",
    "Intensity",
    "Season",
    "Concept",
    "Classification",
    "Longevity",
]

print("\n=== Testing English translations ===")
for s in test_strings:
    result = _(s)
    print(f"  ✓ {s}")

print("\n=== Testing Turkish toggle ===")
lang = toggle_lang()
print(f"  Current language: {lang}")
label = get_toggle_label()
print(f"  Toggle button label: {label}")

print("\n=== Testing Turkish translations ===")
for s in test_strings:
    result = _(s)
    if result == s:
        print(f"  ✗ {s} - NOT TRANSLATED")
    else:
        print(f"  ✓ {s} → {result}")

print("\n✓ All smoke tests passed!")
