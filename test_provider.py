#!/usr/bin/env python
"""Test if the terraform provider pyvider setup is working."""

import sys
import os

# Add paths for all pyvider packages
base_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(base_path)

packages = [
    "pyvider/src",
    "pyvider-components/src", 
    "pyvider-cty/src",
    "pyvider-rpcplugin/src",
    "pyvider-hcl/src",
    "pyvider-telemetry/src"
]

for pkg in packages:
    pkg_path = os.path.join(parent_path, pkg)
    if os.path.exists(pkg_path):
        sys.path.insert(0, pkg_path)

# Now try to import and run pyvider
try:
    from pyvider.cli.main import cli
    print("Successfully imported pyvider CLI")
    cli()
except ImportError as e:
    print(f"Failed to import pyvider: {e}")
    print(f"Python path: {sys.path}")