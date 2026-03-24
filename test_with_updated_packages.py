#!/usr/bin/env python3
"""
Wrapper that uses the updated pyvider packages with lazy loading.
"""
import sys
import os

# Add updated packages to path
sys.path.insert(0, r'/c/code/pyvider/src')
sys.path.insert(0, r'/c/code/pyvider-components/src')

# Set required environment
if sys.platform == "win32" and "PLUGIN_SERVER_TRANSPORTS" not in os.environ:
    os.environ["PLUGIN_SERVER_TRANSPORTS"] = "tcp"

# Import and run CLI
from pyvider.cli import cli

if __name__ == "__main__":
    cli()
