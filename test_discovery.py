#!/usr/bin/env python3
"""Test script to demonstrate enhanced test discovery."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tofusoup" / "src"))

from tofusoup.stir.discovery import TestDiscovery, TestFilter

def test_discovery():
    """Test the enhanced discovery system."""
    base_path = Path("docs/examples")

    print("=" * 60)
    print("Testing Enhanced Test Discovery")
    print("=" * 60)

    # Test 1: Flat discovery (original behavior)
    print("\n1. Flat discovery (default):")
    discoverer = TestDiscovery()
    tests = discoverer.discover_tests(base_path)
    print(f"   Found {len(tests)} tests")
    for test in tests[:5]:
        print(f"   - {test.relative_to(Path.cwd())}")
    if len(tests) > 5:
        print(f"   ... and {len(tests) - 5} more")

    # Test 2: Recursive discovery
    print("\n2. Recursive discovery:")
    discoverer = TestDiscovery(recursive=True)
    tests = discoverer.discover_tests(base_path)
    print(f"   Found {len(tests)} tests")
    for test in tests[:5]:
        print(f"   - {test.relative_to(Path.cwd())}")
    if len(tests) > 5:
        print(f"   ... and {len(tests) - 5} more")

    # Test 3: Filter by type (function tests)
    print("\n3. Filter by type (function):")
    discoverer = TestDiscovery(recursive=True)
    tests = discoverer.discover_tests(base_path)
    filter_obj = TestFilter(types=["function"])
    filtered = filter_obj.filter_tests(tests)
    print(f"   Found {len(filtered)} function tests")
    for test in filtered[:5]:
        print(f"   - {test.relative_to(Path.cwd())}")
    if len(filtered) > 5:
        print(f"   ... and {len(filtered) - 5} more")

    # Test 4: Filter by path pattern
    print("\n4. Filter by path pattern (*/basic):")
    filter_obj = TestFilter(path_filters=["*/basic"])
    filtered = filter_obj.filter_tests(tests)
    print(f"   Found {len(filtered)} 'basic' tests")
    for test in filtered[:5]:
        print(f"   - {test.relative_to(Path.cwd())}")
    if len(filtered) > 5:
        print(f"   ... and {len(filtered) - 5} more")

    # Test 5: Multiple filters (data_source AND lens_jq)
    print("\n5. Multiple filters (data_source + lens_jq):")
    filter_obj = TestFilter(
        types=["data_source"],
        path_filters=["*lens_jq*"]
    )
    filtered = filter_obj.filter_tests(tests)
    print(f"   Found {len(filtered)} lens_jq data source tests")
    for test in filtered:
        print(f"   - {test.relative_to(Path.cwd())}")

    # Test 6: Exclusion filters
    print("\n6. Exclusion filter (!*example*):")
    filter_obj = TestFilter(path_filters=["!*example*"])
    all_tests = discoverer.discover_tests(base_path)
    filtered = filter_obj.filter_tests(all_tests)
    print(f"   Found {len(filtered)} non-example tests (from {len(all_tests)} total)")

    print("\n" + "=" * 60)
    print("Discovery test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_discovery()