from typing import cast

import attrs

from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.hub import hub
from pyvider.providers.context import ProviderContext
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_bool, a_map, a_num, a_str, s_data_source


@attrs.define(frozen=True)
class ProviderConfigReaderState:
    """Defines the output attributes of our test data source."""
    api_endpoint: str | None = None
    api_token: str | None = None
    api_timeout: int | None = None
    api_retries: int | None = None
    api_insecure_skip_verify: bool | None = None
    api_headers: dict[str, str] | None = None

@register_data_source("pyvider_provider_config_reader")
class ProviderConfigReaderDataSource(BaseDataSource):
    """
    A diagnostic data source that reads the configured provider context
    and exposes its values. This is used to test that provider configuration
    is working correctly end-to-end.
    """
    state_class = ProviderConfigReaderState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        # The schema for this data source mirrors the provider's config schema.
        # All attributes are computed because they are read from the provider context.
        return s_data_source(attributes={
            "api_endpoint": a_str(computed=True),
            "api_token": a_str(computed=True, sensitive=True),
            "api_timeout": a_num(computed=True),
            "api_retries": a_num(computed=True),
            "api_insecure_skip_verify": a_bool(computed=True),
            "api_headers": a_map(a_str(), computed=True),
        })

    async def read(self, ctx: ResourceContext) -> ProviderConfigReaderState:
        """Reads the provider context from the hub and returns its state."""
        provider_ctx = cast(ProviderContext, hub.get_component("singleton", "provider_context"))

        if not provider_ctx or not provider_ctx.config:
            raise DataSourceError("Provider context has not been configured.")

        # The provider_ctx.config is the dynamically-generated attrs instance.
        # We can directly access its attributes.
        provider_config = provider_ctx.config

        return ProviderConfigReaderState(
            api_endpoint=provider_config.api_endpoint,
            api_token=provider_config.api_token,
            api_timeout=provider_config.api_timeout,
            api_retries=provider_config.api_retries,
            api_insecure_skip_verify=provider_config.api_insecure_skip_verify,
            api_headers=provider_config.api_headers,
        )
