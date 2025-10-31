#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Generate documentation for terraform-provider-pyvider using plating."""

import asyncio
import sys
from pathlib import Path

# Add pyvider-components to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PYVIDER_COMPONENTS_DIR = PROJECT_ROOT.parent / "pyvider-components"
sys.path.insert(0, str(PYVIDER_COMPONENTS_DIR / "src"))

from plating import Plating, PlatingContext


async def generate_docs(output_dir: Path, provider_name: str = "pyvider") -> int:
    """Generate documentation using plating.

    Args:
        output_dir: Directory to write documentation
        provider_name: Name of the Terraform provider

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Create plating context with provider name
        context = PlatingContext(provider_name=provider_name)
        api = Plating(context, "pyvider.components")

        # Generate all documentation
        print(f"📝 Generating documentation for {provider_name} provider...")
        result = await api.plate(output_dir, validate_markdown=False, force=True)

        if result.success:

            if result.output_files:
                for file in result.output_files[:5]:
                    print(f"  • {file.relative_to(output_dir)}")
                if len(result.output_files) > 5:
                    print(f"  ... and {len(result.output_files) - 5} more")

            return 0
        else:
            print("❌ Documentation generation failed:")
            for error in result.errors:
                print(f"  • {error}")
            return 1

    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point."""
    # Default output directory
    output_dir = PROJECT_ROOT / "docs"

    # Get provider name from environment or use default
    import os
    provider_name = os.environ.get("PROVIDER_NAME", "pyvider")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run async documentation generation
    return asyncio.run(generate_docs(output_dir, provider_name))


if __name__ == "__main__":
    sys.exit(main())

# 🌍🔌🔚
