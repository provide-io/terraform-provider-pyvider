#!/usr/bin/env python3
"""Trace all modules imported during pyvider startup."""

import sys
import os
from pathlib import Path

# Capture initial modules before any imports
initial_modules = set(sys.modules.keys())

# Import pyvider
try:
    import pyvider.cli
except Exception as e:
    print(f"Error importing pyvider: {e}", file=sys.stderr)

# Get all modules imported
final_modules = set(sys.modules.keys())
new_modules = sorted(final_modules - initial_modules)

# Categorize modules
stdlib_prefix = sys.base_prefix.replace("\\", "/")
stdlib_modules = []
third_party_modules = []
pyvider_modules = []

for mod in new_modules:
    if mod in ("__main__", "__loader__"):
        continue

    try:
        spec = sys.modules[mod].__spec__
        if spec and spec.origin:
            origin = spec.origin.replace("\\", "/")

            if "site-packages" in origin:
                third_party_modules.append(f"{mod} ({spec.origin})")
            elif f"{stdlib_prefix}/lib" in origin or f"{stdlib_prefix}\\Lib" in origin.replace("\\", "/"):
                stdlib_modules.append(f"{mod} ({spec.origin})")
            elif "pyvider" in origin:
                pyvider_modules.append(f"{mod} ({spec.origin})")
            else:
                # Built-in or vendored
                if "/" in origin or "\\" in origin:
                    third_party_modules.append(f"{mod} (unknown: {spec.origin})")
                else:
                    stdlib_modules.append(f"{mod} (builtin)")
    except (AttributeError, TypeError):
        # Built-in modules
        stdlib_modules.append(f"{mod} (builtin)")

print("\n" + "="*80)
print("STDLIB MODULES IMPORTED")
print("="*80)
for mod in stdlib_modules:
    print(mod)

print("\n" + "="*80)
print("THIRD-PARTY MODULES IMPORTED")
print("="*80)
for mod in third_party_modules:
    print(mod)

print("\n" + "="*80)
print("PYVIDER MODULES IMPORTED")
print("="*80)
for mod in pyvider_modules:
    print(mod)

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Stdlib modules: {len(stdlib_modules)}")
print(f"Third-party modules: {len(third_party_modules)}")
print(f"Pyvider modules: {len(pyvider_modules)}")
print(f"Total modules imported: {len(new_modules)}")

# Extract just the module names (no paths)
stdlib_names = set()
for item in stdlib_modules:
    name = item.split()[0].split(".")[0]
    stdlib_names.add(name)

print("\n" + "="*80)
print("STDLIB MODULE NAMES (top-level only)")
print("="*80)
for name in sorted(stdlib_names):
    print(name)
