#!/usr/bin/env python
"""Test terraform-provider-pyvider components."""

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

# Test importing components
try:
    # Import base pyvider
    import pyvider
    print("✓ pyvider imported")
    
    # Import component modules directly
    from pyvider.components import resources
    print("✓ pyvider.components.resources imported")
    
    from pyvider.components import data_sources
    print("✓ pyvider.components.data_sources imported")
    
    from pyvider.components import functions
    print("✓ pyvider.components.functions imported")
    
    # List available resources
    print("\nAvailable resources:")
    for item in dir(resources):
        if not item.startswith('_'):
            print(f"  - {item}")
    
    # List available data sources
    print("\nAvailable data sources:")
    for item in dir(data_sources):
        if not item.startswith('_'):
            print(f"  - {item}")
    
    # List available functions
    print("\nAvailable functions:")
    for item in dir(functions):
        if not item.startswith('_'):
            print(f"  - {item}")
    
    print("\n✅ terraform-provider-pyvider components are properly configured!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()