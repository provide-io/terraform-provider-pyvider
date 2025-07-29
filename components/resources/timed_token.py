import uuid

import attrs

from pyvider.exceptions import ResourceError
from pyvider.hub import register_resource
from pyvider.resources.base import BaseResource
from pyvider.resources.context import ResourceContext
from pyvider.resources.private_state import PrivateState
from pyvider.schema import PvsSchema, a_str, a_unknown, s_resource
from pyvider.telemetry import logger


@attrs.define(frozen=True)
class TimedTokenConfig:
    name: str

@attrs.define(frozen=True)
class TimedTokenState:
    name: str
    id: str | None = None

@attrs.define(frozen=True)
class TimedTokenPrivateState(PrivateState):
    # The private state no longer needs the ID.
    transient_token: str

@register_resource("pyvider_timed_token")
class TimedTokenResource(BaseResource):
    config_class = TimedTokenConfig
    state_class = TimedTokenState
    private_state_class = TimedTokenPrivateState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "name": a_str(required=True),
            "id": a_str(computed=True),
        })

    async def plan(self, ctx: ResourceContext) -> tuple[TimedTokenState, TimedTokenPrivateState]:
        logger.debug("PLAN: Starting plan for timed_token", config=ctx.config)

        # THE FIX: For a create, the 'id' is unknown until apply.
        # We create a planned state with the known config values and an
        # unknown placeholder for the computed 'id'.
        planned_state = self.state_class(
            name=ctx.config.name,
            id=a_unknown(a_str())
        )

        # The private state can still be generated here.
        private_state = self.private_state_class(
            transient_token="secret-token-for-creation"
        )

        logger.debug("PLAN: Finished planning.", planned_state=planned_state)
        return planned_state, private_state

    async def apply(self, ctx: ResourceContext) -> tuple[TimedTokenState, TimedTokenPrivateState]:
        logger.debug("APPLY: Starting apply for timed_token", planned_state=ctx.planned_state)

        if not ctx.private_state:
            raise ResourceError("Apply phase failed: private state was not received.")

        if ctx.private_state.transient_token != "secret-token-for-creation":
            raise ResourceError("Apply phase failed: transient token mismatch.")

        logger.info("APPLY: Private state token verified successfully.")

        # THE FIX: Generate the computed value here, in apply.
        new_id = f"token-resource-{uuid.uuid4()}"

        # Construct the final, complete state object.
        final_state = self.state_class(
            name=ctx.config.name,
            id=new_id
        )

        # Persist the private state.
        private_state_to_persist = ctx.private_state

        logger.debug("APPLY: Finished apply.", final_state=final_state)
        return final_state, private_state_to_persist

    async def read(self, ctx: ResourceContext) -> TimedTokenState | None:
        return ctx.state

    async def delete(self, ctx: ResourceContext) -> None:
        pass
