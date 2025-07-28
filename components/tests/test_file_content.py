import hashlib
from pathlib import Path

import pytest

from components.resources.file_content import (
    FileContentConfig,
    FileContentResource,
    FileContentState,
)
from pyvider.resources.context import ResourceContext


class TestFileContent:

    @pytest.fixture
    def temp_file(self) -> Path:
        """Create a temporary file path in /tmp."""
        path = Path("/tmp/pyvider-test.txt")
        path.unlink(missing_ok=True)
        yield path
        path.unlink(missing_ok=True)

    @pytest.fixture
    def resource(self) -> FileContentResource:
        """Create a FileContentResource instance."""
        return FileContentResource()

    @pytest.mark.asyncio
    async def test_create_and_read(self, resource: FileContentResource, temp_file: Path):
        config = FileContentConfig(filename=str(temp_file), content="hello world")
        # Plan for a CREATE operation (no prior state)
        plan_ctx = ResourceContext(config=config, state=None)
        planned_state, _ = await resource.plan(plan_ctx)

        assert planned_state.filename == str(temp_file)
        assert planned_state.content == "hello world"

        # For a create, computed values MUST be predicted in the plan.
        assert planned_state.exists is True
        assert planned_state.content_hash == hashlib.sha256(b"hello world").hexdigest()

        apply_ctx = ResourceContext(config=config, planned_state=planned_state)
        final_state, _ = await resource.apply(apply_ctx)
        assert temp_file.exists()
        assert temp_file.read_text() == "hello world"

        # After apply, the final state MUST be identical to the planned state.
        assert final_state == planned_state

    @pytest.mark.asyncio
    async def test_delete(self, resource: FileContentResource, temp_file: Path):
        content = "to be deleted"
        config = FileContentConfig(filename=str(temp_file), content=content)
        temp_file.write_text(content)
        current_state = FileContentState(filename=str(temp_file), content=content, exists=True)

        # To delete, the planned_state is None.
        delete_ctx = ResourceContext(config=config, state=current_state, planned_state=None)
        await resource.apply(delete_ctx)

        assert not temp_file.exists()
