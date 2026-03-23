#!/usr/bin/env python3
"""
Manually build a PSPF (Polyglot Python Self-extracting File) without FlavorPack.

The PSPF format is simple: a Windows PE executable with a ZIP archive appended.
This bypasses FlavorPack's network-dependent build system.
"""

import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Generator


def create_venv_zip(venv_path: Path, output_zip: Path) -> None:
    """Create a ZIP of the venv, excluding unnecessary files."""

    venv_path = venv_path.resolve()

    # Files/directories to exclude from the ZIP
    EXCLUDE_PATTERNS = {
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.pytest_cache',
        '.mypy_cache',
        'pip-*',
        'pip_*',
        'setuptools-*',
        'wheel-*',
        '*.dist-info',
        '*.egg-info',
        '.git',
        '.gitignore',
        '.terraform',
        '.venv',
        'venv',
    }

    def should_include(path: Path) -> bool:
        """Check if a path should be included in the ZIP."""
        name = path.name

        # Skip exact matches
        if name in EXCLUDE_PATTERNS:
            return False

        # Skip patterns
        for pattern in EXCLUDE_PATTERNS:
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    return False

        return True

    def walk_files(directory: Path) -> Generator[Path, None, None]:
        """Walk all files, excluding unwanted patterns."""
        for item in directory.iterdir():
            if should_include(item):
                if item.is_dir():
                    yield from walk_files(item)
                else:
                    yield item

    print(f"Creating ZIP archive: {output_zip}")
    print(f"Source venv: {venv_path}")

    total_size = 0
    file_count = 0

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in walk_files(venv_path):
            # Create archive name relative to venv (without the venv root dir)
            arcname = file_path.relative_to(venv_path)

            # Add file to ZIP
            zf.write(file_path, arcname)

            file_size = file_path.stat().st_size
            total_size += file_size
            file_count += 1

            if file_count % 100 == 0:
                print(f"  Added {file_count} files...")

    zip_size = output_zip.stat().st_size
    compression = (1 - zip_size / total_size) * 100 if total_size > 0 else 0

    print(f"[OK] ZIP created successfully")
    print(f"  Files: {file_count}")
    print(f"  Original size: {total_size / 1024 / 1024:.1f} MB")
    print(f"  Compressed size: {zip_size / 1024 / 1024:.1f} MB")
    print(f"  Compression: {compression:.1f}%")


def create_pspf(launcher_exe: Path, venv_zip: Path, output_exe: Path) -> None:
    """Create PSPF by appending ZIP to launcher executable."""

    launcher_exe = launcher_exe.resolve()
    venv_zip = venv_zip.resolve()
    output_exe = output_exe.resolve()

    if not launcher_exe.exists():
        raise FileNotFoundError(f"Launcher not found: {launcher_exe}")

    if not venv_zip.exists():
        raise FileNotFoundError(f"Venv ZIP not found: {venv_zip}")

    print(f"\nCreating PSPF: {output_exe}")
    print(f"  Launcher: {launcher_exe}")
    print(f"  Venv ZIP: {venv_zip}")

    launcher_size = launcher_exe.stat().st_size
    venv_size = venv_zip.stat().st_size

    # Copy launcher as base
    shutil.copy2(launcher_exe, output_exe)

    # Append ZIP to executable
    with open(output_exe, 'ab') as exe_file:
        with open(venv_zip, 'rb') as zip_file:
            exe_file.write(zip_file.read())

    final_size = output_exe.stat().st_size

    print(f"[OK] PSPF created successfully")
    print(f"  Launcher size: {launcher_size / 1024 / 1024:.1f} MB")
    print(f"  Venv ZIP size: {venv_size / 1024 / 1024:.1f} MB")
    print(f"  Final PSPF size: {final_size / 1024 / 1024:.1f} MB")


def main():
    """Build the PSPF manually."""

    # Paths (use Windows backslash format for proper path handling)
    terraform_provider_dir = Path("C:\\code\\terraform-provider-pyvider")
    venv_path = terraform_provider_dir / ".venv"
    launcher_exe = Path("C:\\code\\provide-io\\dist\\bin\\flavor-go-launcher-windows_arm64.exe")
    output_dir = terraform_provider_dir / "dist"
    output_dir.mkdir(exist_ok=True, parents=True)

    venv_zip = terraform_provider_dir / "terraform-provider-pyvider-venv.zip"
    output_exe = output_dir / "terraform-provider-pyvider.exe"

    print("=" * 70)
    print("Manual PSPF Builder (No Network Required)")
    print("=" * 70)

    # Step 1: Create venv ZIP
    try:
        if venv_zip.exists():
            venv_zip.unlink()
        create_venv_zip(venv_path, venv_zip)
    except Exception as e:
        print(f"ERROR: Failed to create venv ZIP: {e}", file=sys.stderr)
        return 1

    # Step 2: Create PSPF
    try:
        if output_exe.exists():
            output_exe.unlink()
        create_pspf(launcher_exe, venv_zip, output_exe)
    except Exception as e:
        print(f"ERROR: Failed to create PSPF: {e}", file=sys.stderr)
        return 1

    # Step 3: Install to Terraform plugin directory
    try:
        plugin_dir = Path.home() / ".terraform.d" / "plugins" / "local" / "providers" / "pyvider" / "0.3.21" / "windows_arm64"
        plugin_dir.mkdir(parents=True, exist_ok=True)

        plugin_exe = plugin_dir / "terraform-provider-pyvider.exe"
        shutil.copy2(output_exe, plugin_exe)

        print(f"[OK] Installed to: {plugin_exe}")

        # Also copy lazy-packages.zip if it exists
        lazy_packages = terraform_provider_dir / "lazy-packages.zip"
        if lazy_packages.exists():
            plugin_lazy = plugin_dir / "lazy-packages.zip"
            shutil.copy2(lazy_packages, plugin_lazy)
            print(f"[OK] Copied lazy packages to: {plugin_lazy}")

    except Exception as e:
        print(f"[WARNING] Could not install to Terraform directory: {e}", file=sys.stderr)
        print(f"[INFO] But the executable was created at: {output_exe}")
        return 1

    print("\n" + "=" * 70)
    print("[SUCCESS] PSPF is ready for testing with Terraform")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
