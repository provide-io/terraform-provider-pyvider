import json
from pathlib import Path
from typing import Any

import pytest

from components.helpers.jq_processor import JqProcessor

TF_DATA_PATH = Path("components/tf/advanced_jq_test")

@pytest.fixture(scope="module")
def full_system_data() -> dict[str, Any]:
    return {"schematics": json.loads((TF_DATA_PATH / "project_apollo_schematics.json").read_text()),
            "supply_chain": json.loads((TF_DATA_PATH / "supply_chain_database.json").read_text()),
            "materials": json.loads((TF_DATA_PATH / "materials_properties.json").read_text())}

@pytest.fixture(scope="module")
def complex_material_audit_query() -> str:
    return "[ .schematics.system.subsystems[]?.assemblies[]?.parts[]? as $part | { part_name: $part.name, supplier: (.supply_chain.suppliers[]? | select(.id == $part.supplier_id) | .name // \"In-House\"), materials: [ $part.material_ids[]? as $mid | .materials.materials[]? | select(.material_id == $mid) | .element ] } ]"

class TestJqAdvancedIntegration:
    def test_processor_with_complex_material_audit(self, full_system_data: dict, complex_material_audit_query: str):
        result = JqProcessor.execute(complex_material_audit_query, full_system_data)
        assert isinstance(result, list)
        # THE FIX: The query constructs a list of 3 parts.
        assert len(result) == 3
        first_part = result[0]
        assert "part_name" in first_part
        assert first_part["supplier"] == "Q-Fab Inc."
