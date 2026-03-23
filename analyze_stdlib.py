#!/usr/bin/env python3
"""Analyze which stdlib modules are actually used vs available."""

import sys
import os
from pathlib import Path
import json

# Get stdlib location
stdlib_path = Path(sys.base_prefix) / "Lib"
print(f"Stdlib path: {stdlib_path}")
print(f"Exists: {stdlib_path.exists()}")

# Get all available stdlib modules
available_modules = set()
if stdlib_path.exists():
    for item in stdlib_path.iterdir():
        name = item.name
        # Skip __pycache__ and .pyc files
        if name.startswith("_") and name != "__future__":
            available_modules.add(name)
        elif item.is_dir() and not name.startswith("."):
            available_modules.add(name)
        elif item.suffix == ".py":
            available_modules.add(item.stem)

print(f"\nTotal available stdlib modules: {len(available_modules)}")

# Modules we know are used (from trace and runtime requirements)
used_modules = {
    "_ast",
    "_bisect",
    "_blake2",
    "_codecs_cn",
    "_codecs_hk",
    "_codecs_iso2022",
    "_codecs_jp",
    "_codecs_kr",
    "_codecs_tw",
    "_contextvars",
    "_csv",
    "_datetime",
    "_heapq",
    "_json",
    "_locale",
    "_multibytecodec",
    "_opcode",
    "_pickle",
    "_random",
    "_sha512",
    "_string",
    "_struct",
    "_typing",
    "array",
    "atexit",
    "binascii",
    "importlib",
    "math",
    "mmap",
    "msvcrt",
    "typing",
    "zlib",
    # Add others we know are used at runtime:
    "asyncio",
    "json",
    "logging",
    "ssl",
    "socket",
    "pathlib",
    "tempfile",
    "os",
    "sys",
    "re",
    "enum",
    "inspect",
    "warnings",
    "io",
    "collections",
    "functools",
    "itertools",
    "operator",
    "types",
    "copy",
    "datetime",
    "time",
    "random",
    "string",
    "base64",
    "hashlib",
    "hmac",
    "secrets",
    "urllib",
    "http",
    "email",
    "uuid",
    "argparse",
    "shutil",
    "contextlib",
}

# Find modules that are NOT used
unused_modules = available_modules - used_modules

print(f"Used modules identified: {len(used_modules)}")
print(f"Potentially unused modules: {len(unused_modules)}")

# Categories of modules to potentially remove
dangerous_to_remove = {
    "__main__",
    "builtins",
    "sys",
    "os",
    "site",
    "sitecustomize",
    "usercustomize",
}

safe_to_remove = {
    "tkinter",
    "turtle",
    "idlelib",
    "sqlite3",
    "curses",
    "unittest",
    "doctest",
    "pdb",
    "cProfile",
    "profile",
    "timeit",
    "trace",
    "html",
    "xml",
    "xmlrpc",
    "ast",
    "token",
    "tokenize",
    "keyword",
    "lib2to3",
    "pydoc",
    "tabnanny",
    "compileall",
    "dis",
    "pickletools",
    "distutils",
    "ensurepip",
    "venv",
    "zipapp",
    "mailbox",
    "mailcap",
    "news",
}

# Estimate size savings
print("\n" + "="*80)
print("MODULES SAFE TO REMOVE")
print("="*80)

safe_and_available = safe_to_remove & available_modules & unused_modules
for mod in sorted(safe_and_available):
    mod_path = stdlib_path / mod
    if mod_path.is_dir():
        size_bytes = sum(f.stat().st_size for f in mod_path.rglob("*") if f.is_file())
        size_mb = size_bytes / (1024 * 1024)
        print(f"  {mod:30} {size_mb:7.2f} MB")
    else:
        try:
            size_bytes = (stdlib_path / f"{mod}.py").stat().st_size if (stdlib_path / f"{mod}.py").exists() else 0
            size_mb = size_bytes / 1024
            print(f"  {mod:30} {size_mb:7.2f} KB")
        except:
            pass

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

total_size = 0
removable_size = 0

for item in stdlib_path.iterdir():
    if item.is_dir() and not item.name.startswith("."):
        item_size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
        total_size += item_size
        if item.name in safe_and_available:
            removable_size += item_size
    elif item.suffix == ".py":
        item_size = item.stat().st_size
        total_size += item_size
        if item.stem in safe_and_available:
            removable_size += item_size

print(f"Total stdlib size: {total_size / (1024*1024):.1f} MB")
print(f"Removable size: {removable_size / (1024*1024):.1f} MB ({removable_size*100//total_size}%)")
print(f"Remaining size: {(total_size - removable_size) / (1024*1024):.1f} MB")
