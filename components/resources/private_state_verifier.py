
import attrs

from pyvider.exceptions import ResourceError
from pyvider.hub import register_resource
from pyvider.resources.base import BaseResource
from pyvider.resources.context import ResourceContext
from pyvider.resources.private_state import PrivateState
from pyvider.schema import PvsSchema, a_str, a_unknown, s_resource


@attrs.define(frozen=True)
class VerifierConfig:
    """Config for the verifier resource."""
    input_value: str

@attrs.define(frozen=True)
class VerifierState:
    """State for the verifier resource."""
    input_value: str
    decrypted_token: str | None = None

@attrs.define(frozen=True)
class VerifierPrivateState(PrivateState):
    """The private state object."""
    secret_token: str

@register_resource("pyvider_private_state_verifier")
class PrivateStateVerifierResource(BaseResource):
    """
    A diagnostic resource to verify that private state is correctly
    encrypted, passed, and decrypted between plan and apply.
    """
    config_class = VerifierConfig
    state_class = VerifierState
    private_state_class = VerifierPrivateState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_resource({
            "input_value": a_str(required=True),
            "decrypted_token": a_str(computed=True, description="The secret token read from the decrypted private state during apply."),
        })

    async def plan(self, ctx: ResourceContext) -> tuple[VerifierState, VerifierPrivateState]:
        """
        Generates a plan and a private state with a known, predictable secret.
        """
        # The value for a computed attribute that will be populated
        # during apply MUST be marked as unknown in the plan.
        planned_state = self.state_class(
            input_value=ctx.config.input_value,
            decrypted_token=a_unknown(a_str())
        )

        private_state = self.private_state_class(
            secret_token=f"SECRET_FOR_{ctx.config.input_value.upper()}"
        )

        return planned_state, private_state

    async def apply(self, ctx: ResourceContext) -> tuple[VerifierState, None]:
        """
        Receives the decrypted private state and exposes its contents in a
        computed attribute for verification.
        """
        if not ctx.private_state:
            raise ResourceError("Apply phase failed: private state was not received.")

        # Construct the final state, filling in the previously unknown value.
        final_state = self.state_class(
            input_value=ctx.config.input_value,
            decrypted_token=ctx.private_state.secret_token
        )

        # We don't need to persist the private state after this.
        return final_state, None

    async def read(self, ctx: ResourceContext) -> VerifierState | None:
        return ctx.state

    async def delete(self, ctx: ResourceContext) -> None:
        pass
