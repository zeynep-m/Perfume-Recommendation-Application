#!/usr/bin/env python3
"""Test translations to verify .mo file is working correctly"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i18n import _, _load_language

# Test English (default)
print("=== English (Default) ===")
_load_language("en")
test_strings = [
    "Perfume Recommender",
    "Language",
    "Database",
    "Filters",
    "Perfume name",
    "Gender",
    "Intensity",
    "Season",
    "Concept",
    "Classification",
    "Longevity",
]

for s in test_strings:
    print(f"  {s}: {_(s)}")

# Test Turkish
print("\n=== Turkish ===")
_load_language("tr")
for s in test_strings:
    translation = _(s)
    status = "✓" if translation != s else "✗ MISSING"
    print(f"  {s}: {translation} {status}")

# Test translate_list function
print("\n=== Testing translate_list for filter values ===")
from i18n import translate_list
gender_values = ["Any", "Woman", "Man", "Unisex"]
print(f"  Original: {gender_values}")
translated = translate_list(gender_values)
print(f"  Turkish:  {translated}")

intensity_values = ["Any", "Light", "Moderate", "Intense"]
print(f"\n  Original: {intensity_values}")
translated = translate_list(intensity_values)
print(f"  Turkish:  {translated}")
