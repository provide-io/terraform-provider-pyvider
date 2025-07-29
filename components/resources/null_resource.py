from typing import ClassVar

from attrs import define

from pyvider.cty import CtyValue
from pyvider.schema import PvsSchema, a_dyn, a_map, s_resource


@define
class NullResource:
    name: ClassVar[str] = "pyvider_null_resource"
    schema: ClassVar[PvsSchema] = s_resource(
        attributes={
            "triggers": a_map(
                a_dyn(),
                optional=True,
                description="A map of arbitrary values that, when changed, will force the resource to be replaced."
            )
        }
    )
    async def plan(self, config: CtyValue, prior_state: CtyValue | None = None) -> CtyValue:
        return config
    async def apply(self, state: CtyValue, plan: CtyValue, prior_state: CtyValue | None = None) -> CtyValue:
        return state
    async def read(self, state: CtyValue) -> CtyValue:
        return state
