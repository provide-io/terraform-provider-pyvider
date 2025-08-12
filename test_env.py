#!/usr/bin/env python
"""Test script to verify environment setup."""

import sys
print(f"Python version: {sys.version}")

try:
    import pyvider_components
    print("✅ pyvider-components imported successfully")
except ImportError as e:
    print(f"❌ Failed to import pyvider-components: {e}")

try:
    import pytest
    print(f"✅ pytest version: {pytest.__version__}")
except ImportError as e:
    print(f"❌ pytest not available: {e}")

print("\nEnvironment test complete!")