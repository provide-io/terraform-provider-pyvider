from pathlib import Path
from typing import cast

import attrs

from pyvider.common_types import StateType
from pyvider.exceptions import ResourceError
from pyvider.hub import register_resource
from pyvider.resources.base import BaseResource
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_num, a_str, s_resource
from pyvider.telemetry import logger


@attrs.define(frozen=True)
class LocalDirectoryConfig:
    path: str
    permissions: str | None = None

@attrs.define(frozen=True)
class LocalDirectoryState:
    path: str
    permissions: str | None = None
    id: str | None = None
    file_count: int | None = None

@register_resource("pyvider_local_directory")
class LocalDirectoryResource(BaseResource["pyvider_local_directory", LocalDirectoryState, LocalDirectoryConfig]):

    config_class = LocalDirectoryConfig
    state_class = LocalDirectoryState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "path": a_str(required=True, description="The path of the directory to manage."),
            "permissions": a_str(optional=True, computed=True, description="The permissions for the directory in octal format. Must start with '0o' (e.g., '0o755')."),
            "id": a_str(computed=True, description="The absolute path of the directory."),
            "file_count": a_num(computed=True, description="The number of files in the directory."),
        })

    async def plan(self, ctx: ResourceContext) -> tuple[StateType | None, None]:
        config = cast(LocalDirectoryConfig, ctx.config)
        if not config:
            return None, None

        if config.permissions:
            is_valid = True
            if not config.permissions.startswith("0o"):
                is_valid = False
            else:
                try:
                    int(config.permissions, 8)
                except ValueError:
                    is_valid = False

            if not is_valid:
                ctx.add_attribute_error(
                    attribute_path="permissions",
                    summary="Invalid permissions format",
                    detail=f"The value '{config.permissions}' is not a valid octal string. It must be prefixed with '0o', for example: '0o755'."
                )
                return None, None

        # THE FIX: If the user provides a value, use it. If not, predict the default.
        planned_permissions = config.permissions
        if planned_permissions is None:
            # If the user did not specify permissions, the provider knows it will
            # use a default. The plan should reflect this known outcome.
            planned_permissions = "0o755"

        planned_state = self.state_class(
            path=config.path,
            permissions=planned_permissions,
            id=str(Path(config.path).resolve()),
            file_count=0
        )
        return planned_state, None

    async def apply(self, ctx: ResourceContext) -> tuple[StateType | None, None]:
        if not ctx.planned_state:
            await self.delete(ctx)
            return None, None

        planned_state = cast(LocalDirectoryState, ctx.planned_state)
        path = Path(planned_state.path)

        path.mkdir(parents=True, exist_ok=True)

        permissions_to_apply = planned_state.permissions

        try:
            permissions_octal = int(permissions_to_apply, 8)
            path.chmod(permissions_octal)
        except (ValueError, TypeError) as e:
            raise ResourceError(f"Invalid permissions format: {permissions_to_apply}. Must be an octal string like '0o755'.") from e

        return ctx.planned_state, None

    async def read(self, ctx: ResourceContext) -> LocalDirectoryState | None:
        if not ctx.state or not ctx.state.path:
            return None

        path = Path(ctx.state.path)
        if not path.is_dir():
            return None

        current_permissions = oct(path.stat().st_mode & 0o777)
        file_count = len([f for f in path.iterdir() if f.is_file()])

        return self.state_class(
            path=str(path),
            permissions=current_permissions,
            id=str(path.resolve()),
            file_count=file_count
        )

    async def delete(self, ctx: ResourceContext) -> None:
        state = cast(LocalDirectoryState, ctx.state)
        if not state or not state.path:
            return

        path = Path(state.path)
        if path.is_dir():
            try:
                path.rmdir()
            except OSError:
                logger.warning(f"Directory {path} is not empty and will not be removed.")
