#!/usr/bin/env python3
"""
Pre-process plating templates to inject global partials.

This script scans all .tmpl.md files in pyvider-components and replaces
{{ global('partial_name') }} with the content from docs/_partials/_partial_name.md

Usage:
    ./scripts/inject_global_partials.py           # Inject partials
    ./scripts/inject_global_partials.py --dry-run # Preview changes
"""

import re
from pathlib import Path
import sys


def inject_global_partials(
    components_dir: Path,
    partials_dir: Path,
    dry_run: bool = False
) -> int:
    """Inject global partials into component templates.

    Args:
        components_dir: Root directory of pyvider-components
        partials_dir: Directory containing global partials
        dry_run: If True, only print what would be changed

    Returns:
        Number of files processed
    """
    # Find all template files
    template_files = list(components_dir.rglob("*.tmpl.md"))

    if not template_files:
        print(f"⚠️  No template files found in {components_dir}")
        return 0

    # Pattern to match {{ global('name') }} or {{ global("name") }}
    pattern = re.compile(r"\{\{\s*global\(['\"]([^'\"]+)['\"]\)\s*\}\}")

    files_changed = 0
    files_with_warnings = []

    for template_file in template_files:
        try:
            content = template_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error reading {template_file}: {e}")
            continue

        original_content = content

        # Find all global() references
        matches = list(pattern.finditer(content))

        if not matches:
            continue

        for match in matches:
            partial_name = match.group(1)
            partial_file = partials_dir / f"_{partial_name}.md"

            if not partial_file.exists():
                print(f"⚠️  Warning: Global partial '{partial_name}' not found at {partial_file}")
                files_with_warnings.append((template_file, partial_name))
                continue

            try:
                # Read partial content
                partial_content = partial_file.read_text(encoding='utf-8').strip()
            except Exception as e:
                print(f"❌ Error reading partial {partial_file}: {e}")
                continue

            # Replace the {{ global('name') }} with actual content
            # Add a comment to indicate this was injected
            injection = f"<!-- Injected from global partial: _{partial_name}.md -->\n{partial_content}\n<!-- End global partial -->"

            content = content.replace(match.group(0), injection)

        # Write back if changed
        if content != original_content:
            if dry_run:
                print(f"Would update: {template_file}")
                # Show what changed
                rel_path = template_file.relative_to(components_dir)
                print(f"  Partials injected: {', '.join(m.group(1) for m in matches)}")
            else:
                try:
                    template_file.write_text(content, encoding='utf-8')
                    print(f"✅ Updated: {template_file}")
                except Exception as e:
                    print(f"❌ Error writing {template_file}: {e}")
                    continue

            files_changed += 1

    return files_changed


def main():
    # Paths - relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    components_root = project_root.parent / "pyvider-components"

    # Components can be in src/pyvider/components or directly in components/
    components_dir = components_root / "src" / "pyvider" / "components"
    if not components_dir.exists():
        components_dir = components_root / "components"

    partials_dir = components_root / "docs" / "_partials"

    # Check paths exist
    if not components_dir.exists():
        print(f"❌ Error: Components directory not found")
        print(f"   Checked: {components_root / 'src' / 'pyvider' / 'components'}")
        print(f"   Checked: {components_root / 'components'}")
        sys.exit(1)

    if not partials_dir.exists():
        print(f"⚠️  Warning: Global partials directory not found: {partials_dir}")
        print(f"Creating directory...")
        try:
            partials_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {partials_dir}")
        except Exception as e:
            print(f"❌ Error creating directory: {e}")
            sys.exit(1)

    # Parse arguments
    dry_run = "--dry-run" in sys.argv

    # Run injection
    print(f"🔍 Scanning for templates in: {components_dir}")
    print(f"📚 Using partials from: {partials_dir}")
    print()

    files_changed = inject_global_partials(components_dir, partials_dir, dry_run)

    print()
    if dry_run:
        print(f"📋 Dry run: {files_changed} files would be updated")
        return 0
    else:
        if files_changed == 0:
            print(f"✅ Complete: No files needed updating")
        else:
            print(f"✅ Complete: {files_changed} files updated")
        return 0


if __name__ == "__main__":
    sys.exit(main())
