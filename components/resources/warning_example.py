
import attrs

from pyvider.hub import register_resource
from pyvider.resources.base import BaseResource
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_str, a_unknown, s_resource


@attrs.define(frozen=True)
class WarningExampleState:
    name: str | None = None
    old_name: str | None = None
    source_file: str | None = None

@register_resource("pyvider_warning_example")
class WarningExampleResource(BaseResource):
    """
    An example resource that demonstrates how to use the diagnostics API
    and correctly handle computed attributes with deprecated fallbacks.
    """
    state_class = WarningExampleState
    config_class = WarningExampleState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "name": a_str(optional=True, computed=True, description="The primary name for the resource. Conflicts with 'source_file'."),
            "old_name": a_str(optional=True, description="[DEPRECATED] Use the 'name' attribute instead."),
            "source_file": a_str(optional=True, description="Path to a file to use as the name. Conflicts with 'name'."),
        })

    async def plan(self, ctx: ResourceContext) -> tuple[WarningExampleState, None]:
        config = ctx.config

        if config.old_name is not None:
            ctx.add_attribute_warning(
                attribute_path="old_name",
                summary="Attribute 'old_name' is deprecated",
                detail="The 'old_name' attribute is deprecated and will be removed in a future version. Please use the 'name' attribute instead."
            )

        if config.name is not None and config.source_file is not None:
            ctx.add_attribute_error(
                attribute_path="source_file",
                summary="Conflicting attributes",
                detail="The 'name' and 'source_file' attributes are mutually exclusive. Please specify only one."
            )
            return None, None

        if config.name is None and config.old_name is None and config.source_file is None:
             ctx.add_error("One of 'name', 'old_name', or 'source_file' must be specified.")
             return None, None

        planned_name = config.name or config.old_name
        if config.source_file:
            planned_name = f"from_file:{config.source_file}"

        if planned_name is None:
            planned_name = a_unknown(a_str())

        planned_state = self.state_class(
            name=planned_name,
            old_name=config.old_name,
            source_file=config.source_file
        )
        return planned_state, None

    async def apply(self, ctx: ResourceContext) -> tuple[WarningExampleState, None]:
        """
        Creates the resource. This is the correct place to implement the
        fallback logic and to evolve the planned state into the final state.
        """
        config = ctx.config

        # This is the computed value.
        final_name = config.name or config.old_name
        if config.source_file:
            final_name = f"from_file:{config.source_file}"

        # THE FIX: Evolve the planned state. Start with the exact object
        # from the plan and only change the fields that were computed.
        final_state = attrs.evolve(
            ctx.planned_state,
            name=final_name
        )

        return final_state, None

    async def read(self, ctx: ResourceContext) -> WarningExampleState | None:
        return ctx.state

    async def delete(self, ctx: ResourceContext) -> None:
        pass
