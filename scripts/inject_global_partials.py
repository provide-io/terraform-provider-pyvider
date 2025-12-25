#!/usr/bin/env python3
"""
Pre-process plating templates and provider guides to inject global partials.

This script implements a hybrid approach:
1. AUTOMATIC INJECTION: Injects global_header after first heading and global_footer at end
   - Unless opted-out via frontmatter (skip_global_header: true / skip_global_footer: true)
2. MANUAL INJECTION: Also processes {{ global('partial_name') }} syntax

Usage:
    ./scripts/inject_global_partials.py                    # Process provider guides (default)
    ./scripts/inject_global_partials.py --guides          # Process provider guides only
    ./scripts/inject_global_partials.py --components      # Process component templates only
    ./scripts/inject_global_partials.py --dry-run         # Preview changes without writing
"""

import re
from pathlib import Path
import sys
import yaml


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and remaining content.

    Returns:
        (frontmatter_dict, body_without_frontmatter)
    """
    if not content.startswith('---'):
        return {}, content

    # Find the second --- delimiter
    lines = content.split('\n')
    if len(lines) < 2:
        return {}, content

    # Find closing ---
    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            close_idx = i
            break

    if close_idx is None:
        return {}, content

    # Parse YAML frontmatter
    frontmatter_text = '\n'.join(lines[1:close_idx])
    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        frontmatter = {}

    # Reconstruct body (keep the closing --- and everything after)
    body = '\n'.join(lines[close_idx:])

    return frontmatter, body


def should_skip_header(frontmatter: dict) -> bool:
    """Check if global_header should be skipped."""
    return frontmatter.get('skip_global_header', False)


def should_skip_footer(frontmatter: dict) -> bool:
    """Check if global_footer should be skipped."""
    return frontmatter.get('skip_global_footer', False)


def remove_old_injections(body: str) -> str:
    """Remove old HTML-comment based injections to prepare for new ones."""
    # Remove old header injection (with HTML comments)
    body = re.sub(
        r'\n*<!-- Injected from global partial: _global_header\.md -->\n.*?\n<!-- End global partial -->\n*',
        '',
        body,
        flags=re.DOTALL
    )
    # Remove old footer injection (with HTML comments)
    body = re.sub(
        r'\n*<!-- Injected from global partial: _global_footer\.md -->\n.*?\n<!-- End global partial -->',
        '',
        body,
        flags=re.DOTALL
    )
    return body


def inject_global_partials(
    components_dir: Path,
    partials_dir: Path,
    dry_run: bool = False,
    file_pattern: str = "*.tmpl.md"
) -> int:
    """Inject global partials into component templates or guide files.

    Implements hybrid approach:
    - Auto-inject header after first heading and footer at end
    - Allow opt-out via frontmatter flags
    - Still process manual {{ global(...) }} syntax

    Args:
        components_dir: Root directory of pyvider-components or provider guides
        partials_dir: Directory containing global partials
        dry_run: If True, only print what would be changed
        file_pattern: Pattern to match files (default: "*.tmpl.md", can also use "*.md")

    Returns:
        Number of files processed
    """
    # Find all template/guide files
    template_files = list(components_dir.rglob(file_pattern))

    if not template_files:
        print(f"⚠️  No template files found in {components_dir}")
        return 0

    # Load global partials
    global_header_file = partials_dir / "_global_header.md"
    global_footer_file = partials_dir / "_global_footer.md"

    global_header_content = ""
    global_footer_content = ""

    if global_header_file.exists():
        global_header_content = global_header_file.read_text(encoding='utf-8').strip()
    if global_footer_file.exists():
        global_footer_content = global_footer_file.read_text(encoding='utf-8').strip()

    # Pattern to match {{ global('name') }} or {{ global("name") }}
    manual_pattern = re.compile(r"\{\{\s*global\(['\"]([^'\"]+)['\"]\)\s*\}\}")

    files_changed = 0

    for template_file in template_files:
        try:
            content = template_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error reading {template_file}: {e}")
            continue

        original_content = content

        # Parse frontmatter FIRST (before cleaning)
        frontmatter, full_body_with_delim = parse_frontmatter(content)

        # Remove old HTML-comment based injections from body only
        body = remove_old_injections(full_body_with_delim)

        skip_header = should_skip_header(frontmatter)
        skip_footer = should_skip_footer(frontmatter)

        # Check if file already has injected content (to prevent double injection)
        # Check for both HTML comment markers and actual content
        already_has_header = ("<!-- Injected from global partial: _global_header.md -->" in body or
                              "POC (proof-of-concept)" in body) if global_header_content else False
        already_has_footer = ("<!-- Injected from global partial: _global_footer.md -->" in body) if global_footer_content else False

        # --- AUTOMATIC INJECTION ---

        # Auto-inject header after H1 heading and its description paragraph
        # (unless opted-out or already present)
        if global_header_content and not skip_header and not already_has_header:
            # Find first # heading
            heading_pattern = re.compile(r'^# .+$', re.MULTILINE)
            heading_match = heading_pattern.search(body)

            if heading_match:
                # Start after the heading
                insert_pos = heading_match.end()

                # Find the first non-empty line after heading (the description paragraph)
                # and insert after that paragraph
                remaining = body[insert_pos:]
                lines = remaining.split('\n')

                # Skip empty lines and the description paragraph
                desc_end = 0
                found_desc = False
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('#'):
                        # Found the description line
                        found_desc = True
                        desc_end = i + 1
                        break

                if found_desc:
                    # Insert after the description line
                    insert_pos += len('\n'.join(lines[:desc_end])) + 1

                # Inject without HTML comments (plating may strip them)
                header_injection = f"\n\n{global_header_content}\n"
                body = body[:insert_pos] + header_injection + body[insert_pos:]

        # Auto-inject footer at end (unless opted-out or already present)
        if global_footer_content and not skip_footer and not already_has_footer:
            # Inject without HTML comments
            footer_injection = f"\n\n{global_footer_content}"
            body = body.rstrip() + footer_injection

        # --- MANUAL INJECTION ---

        # Process manual {{ global('name') }} syntax
        manual_matches = list(manual_pattern.finditer(body))

        for match in manual_matches:
            partial_name = match.group(1)
            partial_file = partials_dir / f"_{partial_name}.md"

            if not partial_file.exists():
                print(f"⚠️  Warning: Global partial '{partial_name}' not found at {partial_file}")
                continue

            try:
                partial_content = partial_file.read_text(encoding='utf-8').strip()
            except Exception as e:
                print(f"❌ Error reading partial {partial_file}: {e}")
                continue

            # Replace with content plus markers
            injection = f"<!-- Injected from global partial: _{partial_name}.md -->\n{partial_content}\n<!-- End global partial -->"
            body = body.replace(match.group(0), injection)

        # Reconstruct full content: original frontmatter + updated body
        # body includes the closing --- delimiter from parse_frontmatter
        if frontmatter:
            # Extract original frontmatter section from original content
            if original_content.startswith('---'):
                close_idx = original_content.find('---', 3)
                if close_idx != -1:
                    original_fm_section = original_content[:close_idx + 3]
                    # body starts with "---\n", remove that since we have the fm section
                    body_lines = body.split('\n', 1)  # Split on first newline only
                    if body_lines[0].strip() == '---' and len(body_lines) > 1:
                        body_without_delim = body_lines[1]
                    else:
                        body_without_delim = body
                    updated_content = original_fm_section + '\n' + body_without_delim
                else:
                    updated_content = body
            else:
                updated_content = body
        else:
            updated_content = body

        # Write back if changed
        if updated_content != original_content:
            if dry_run:
                print(f"Would update: {template_file}")
                changes = []
                if global_header_content and not skip_header and not already_has_header:
                    changes.append("auto-inject header")
                if global_footer_content and not skip_footer and not already_has_footer:
                    changes.append("auto-inject footer")
                if manual_matches:
                    changes.append(f"manual inject: {', '.join(m.group(1) for m in manual_matches)}")
                if changes:
                    print(f"  Changes: {', '.join(changes)}")
            else:
                try:
                    template_file.write_text(updated_content, encoding='utf-8')
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

    # Parse arguments
    dry_run = "--dry-run" in sys.argv
    process_guides = "--guides" in sys.argv or "--provider-guides" in sys.argv

    total_files_changed = 0

    # Process provider guides if requested or if no target specified
    if process_guides or not any(arg in sys.argv for arg in ["--components", "--guides", "--provider-guides"]):
        provider_guides_dir = project_root / "plating" / "guides"
        provider_partials_dir = project_root / "plating" / "partials"

        if provider_guides_dir.exists():
            print("=" * 60)
            print("🔧 Processing Provider Guides")
            print("=" * 60)
            print(f"🔍 Scanning for guides in: {provider_guides_dir}")
            print(f"📚 Using partials from: {provider_partials_dir}")
            print()

            # Create partials dir if it doesn't exist
            if not provider_partials_dir.exists():
                print(f"⚠️  Creating partials directory: {provider_partials_dir}")
                provider_partials_dir.mkdir(parents=True, exist_ok=True)

            files_changed = inject_global_partials(
                provider_guides_dir,
                provider_partials_dir,
                dry_run,
                file_pattern="*.md"
            )
            total_files_changed += files_changed
            print()

    # Process components if requested
    if "--components" in sys.argv:
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

        print("=" * 60)
        print("🔧 Processing Component Templates")
        print("=" * 60)
        print(f"🔍 Scanning for templates in: {components_dir}")
        print(f"📚 Using partials from: {partials_dir}")
        print()

        files_changed = inject_global_partials(
            components_dir,
            partials_dir,
            dry_run,
            file_pattern="*.tmpl.md"
        )
        total_files_changed += files_changed
        print()

    if dry_run:
        print(f"📋 Dry run: {total_files_changed} files would be updated")
        return 0
    else:
        if total_files_changed == 0:
            print(f"✅ Complete: No files needed updating")
        else:
            print(f"✅ Complete: {total_files_changed} files updated")
        return 0


if __name__ == "__main__":
    sys.exit(main())
