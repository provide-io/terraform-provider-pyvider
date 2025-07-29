from decimal import Decimal
from typing import cast

import attrs
import httpx

from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_map, a_num, a_str, s_data_source
from pyvider.telemetry import logger


@attrs.define(frozen=True)
class HTTPAPIConfig:
    url: str
    method: str = "GET"
    headers: dict[str, str] | None = None
    timeout: int | Decimal = 30

@attrs.define(frozen=True)
class HTTPAPIState:
    url: str
    method: str
    status_code: int | None = None
    response_body: str | None = None
    response_time_ms: int | None = None
    response_headers: dict[str, str] | None = None
    header_count: int | None = None
    content_type: str | None = None
    error_message: str | None = None

@register_data_source("pyvider_http_api")
class HTTPAPIDataSource(BaseDataSource["pyvider_http_api", HTTPAPIState, HTTPAPIConfig]):
    config_class = HTTPAPIConfig
    state_class = HTTPAPIState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source({
            "url": a_str(required=True), "method": a_str(optional=True),
            "headers": a_map(a_str(), optional=True), "timeout": a_num(optional=True),
            "status_code": a_num(computed=True, optional=True),
            "response_body": a_str(computed=True, optional=True),
            "response_time_ms": a_num(computed=True, optional=True),
            "response_headers": a_map(a_str(), computed=True, optional=True),
            "header_count": a_num(computed=True, optional=True),
            "content_type": a_str(computed=True, optional=True),
            "error_message": a_str(computed=True, optional=True),
        })

    async def read(self, ctx: ResourceContext) -> HTTPAPIState:
        config = cast(HTTPAPIConfig, ctx.config)
        if not config: raise DataSourceError("Configuration is missing.")

        try:
            async with httpx.AsyncClient(timeout=float(config.timeout)) as client:
                response = await client.request(
                    method=config.method.upper(),
                    url=config.url,
                    headers=config.headers or {},
                )

                return HTTPAPIState(
                    url=str(response.url),
                    method=response.request.method,
                    status_code=response.status_code,
                    response_body=response.text,
                    response_time_ms=int(response.elapsed.total_seconds() * 1000),
                    response_headers=dict(response.headers),
                    header_count=len(response.headers),
                    content_type=response.headers.get("content-type"),
                )
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {e}", exc_info=True)
            return HTTPAPIState(url=config.url, method=config.method, error_message=str(e))
        except Exception as e:
            logger.error(f"An unexpected error occurred during HTTP request: {e}", exc_info=True)
            return HTTPAPIState(url=config.url, method=config.method, error_message=f"Unexpected error: {e}")

    async def delete(self, ctx: ResourceContext): pass
