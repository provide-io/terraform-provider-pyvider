import hashlib
from pathlib import Path
from typing import cast

from attrs import define, field

from pyvider.common_types import StateType
from pyvider.hub import register_resource
from pyvider.resources.base import BaseResource
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_bool, a_str, s_resource


@define(frozen=True)
class FileContentConfig:
    filename: str = field()
    content: str = field()

@define(frozen=True)
class FileContentState:
    filename: str = field()
    content: str = field()
    exists: bool | None = field(default=None)
    content_hash: str | None = field(default=None)

@register_resource("pyvider_file_content")
class FileContentResource(BaseResource["pyvider_file_content", FileContentState, FileContentConfig]):

    config_class = FileContentConfig
    state_class = FileContentState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "filename": a_str(required=True),
            "content": a_str(required=True),
            "exists": a_bool(computed=True),
            "content_hash": a_str(computed=True),
        })

    async def read(self, ctx: ResourceContext) -> FileContentState | None:
        filename_to_read = ctx.state.filename if ctx.state else (ctx.config.filename if ctx.config else None)
        if not filename_to_read: return None
        path = Path(filename_to_read)
        if not path.is_file(): return None

        content = path.read_text(encoding='utf-8')
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return self.state_class(
            filename=filename_to_read,
            content=content,
            exists=True,
            content_hash=content_hash
        )

    async def plan(self, ctx: ResourceContext) -> tuple[StateType | None, None]:
        config = cast(FileContentConfig, ctx.config)

        # A plan for a destroy operation is signaled by an absent config.
        # In this case, the resource's plan method should return None.
        if not config:
            return None, None

        # For a create or update, the plan must predict the final state.
        # The file will exist, and we can compute the hash from the config.
        content_hash = hashlib.sha256(config.content.encode("utf-8")).hexdigest()

        planned_state = self.state_class(
            filename=config.filename,
            content=config.content,
            exists=True,
            content_hash=content_hash
        )
        return planned_state, None

    async def apply(self, ctx: ResourceContext) -> tuple[StateType | None, None]:
        if not ctx.planned_state:
            await self.delete(ctx)
            return None, None

        planned_state = cast(FileContentState, ctx.planned_state)
        path = Path(planned_state.filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(planned_state.content, encoding='utf-8')

        return planned_state, None

    async def delete(self, ctx: ResourceContext) -> None:
        state = cast(FileContentState, ctx.state)
        if not state or not state.filename:
            return
        path = Path(state.filename)
        if path.is_file():
            path.unlink(missing_ok=True)
