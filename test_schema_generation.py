#!/usr/bin/env python3
"""Test schema generation improvements."""

import sys
from pathlib import Path

# Add paths to the local development packages
sys.path.insert(0, str(Path("../plating/src")))
sys.path.insert(0, str(Path("../pyvider-components/src")))
sys.path.insert(0, str(Path("../provide-foundation/src")))

try:
    # Test schema extraction
    from plating.plating import Plating
    from plating.types import ComponentType

    print("🔍 Testing schema generation...")

    # Create Plating instance
    plating_api = Plating(package_name="pyvider.components")

    # Test schema extraction
    print("📊 Extracting provider schema...")
    import asyncio

    async def test_schema():
        provider_schema = await plating_api._extract_provider_schema()

        print(f"✅ Provider schema extracted with {len(provider_schema)} top-level keys")

        # Check resource schemas
        resource_schemas = provider_schema.get("resource_schemas", {})
        print(f"📦 Found {len(resource_schemas)} resource schemas")

        # Check data source schemas
        data_source_schemas = provider_schema.get("data_source_schemas", {})
        print(f"🔢 Found {len(data_source_schemas)} data source schemas")

        # Test specific component schema extraction
        for component_type in [ComponentType.RESOURCE, ComponentType.DATA_SOURCE]:
            components = plating_api.registry.get_components_with_templates(component_type)
            if components:
                component = components[0]
                print(f"\n🧪 Testing {component_type.value} schema for {component.name}...")

                schema_info = await plating_api._get_component_schema(component, component_type)
                if schema_info:
                    print(f"✅ Schema extracted for {component.name}")
                    markdown = schema_info.to_markdown()
                    if markdown.strip():
                        print(f"📝 Schema markdown generated ({len(markdown)} chars)")
                        print("Preview:")
                        print(markdown[:200] + "..." if len(markdown) > 200 else markdown)
                    else:
                        print("⚠️  Schema markdown is empty")
                else:
                    print(f"❌ No schema found for {component.name}")

    # Run the test
    asyncio.run(test_schema())

    print("\n✅ Schema generation test completed")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()