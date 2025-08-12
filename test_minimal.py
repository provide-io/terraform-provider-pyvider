#!/usr/bin/env python
"""Minimal test to verify terraform-provider-pyvider setup."""

import sys
import os

# Add parent directories to path
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add all necessary paths
paths_to_add = [
    os.path.join(parent_path, "pyvider/src"),
    os.path.join(parent_path, "pyvider-components/src"),
    os.path.join(parent_path, "pyvider-cty/src"),
    os.path.join(parent_path, "pyvider-rpcplugin/src"),
    os.path.join(parent_path, "pyvider-telemetry/src"),
]

for path in paths_to_add:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Try to import basic pyvider modules
try:
    import pyvider
    print("✓ pyvider imported successfully")
    
    import pyvider.components
    print("✓ pyvider.components imported successfully")
    
    import pyvider.providers
    print("✓ pyvider.providers imported successfully")
    
    import pyvider.resources
    print("✓ pyvider.resources imported successfully")
    
    import pyvider.data_sources
    print("✓ pyvider.data_sources imported successfully")
    
    print("\nPyvider packages are properly set up!")
    print(f"Pyvider version: {getattr(pyvider, '__version__', 'unknown')}")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print(f"\nPython path:")
    for p in sys.path:
        print(f"  - {p}")