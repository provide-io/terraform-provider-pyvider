# pyvider/components/data_sources/env_variables.py
import os
import re
from typing import Any, cast

import attrs

from pyvider.data_sources.base import BaseDataSource
from pyvider.data_sources.decorators import register_data_source
from pyvider.exceptions import DataSourceError
from pyvider.resources.context import ResourceContext
from pyvider.schema import PvsSchema, a_bool, a_list, a_map, a_str, s_data_source
from pyvider.telemetry import logger


@attrs.define(frozen=True)
class EnvVariablesConfig:
    keys: list[str] | None = None
    prefix: str | None = None
    regex: str | None = None
    exclude_empty: bool | None = None
    transform_keys: str | None = None
    transform_values: str | None = None
    case_sensitive: bool | None = None
    sensitive_keys: list[str] | None = None

@attrs.define(frozen=True)
class EnvVariablesState:
    values: dict[str, str] = attrs.field(factory=dict)
    sensitive_values: dict[str, str] = attrs.field(factory=dict)
    all_values: dict[str, str] = attrs.field(factory=dict)
    # New field to capture the entire environment
    all_environment: dict[str, str] = attrs.field(factory=dict)

@register_data_source("pyvider_env_variables")
class EnvVariablesDataSource(BaseDataSource["pyvider_env_variables", EnvVariablesState, EnvVariablesConfig]):
    config_class = EnvVariablesConfig
    state_class = EnvVariablesState

    @classmethod
    def get_schema(cls) -> PvsSchema:
        return s_data_source(
            attributes={
                "keys": a_list(a_str(), optional=True, description="A specific list of environment variable keys to read."),
                "prefix": a_str(optional=True, description="A prefix to filter environment variables by."),
                "regex": a_str(optional=True, description="A regex pattern to filter environment variable keys."),
                "exclude_empty": a_bool(optional=True, default=True, description="If true, variables with empty values are excluded."),
                "transform_keys": a_str(optional=True, description="Transform keys to 'upper' or 'lower' case."),
                "transform_values": a_str(optional=True, description="Transform values to 'upper' or 'lower' case."),
                "case_sensitive": a_bool(optional=True, default=True, description="Whether prefix/regex matching is case-sensitive."),
                "sensitive_keys": a_list(a_str(), optional=True, description="A list of keys whose values should be marked as sensitive."),
                "values": a_map(a_str(), computed=True, description="The map of non-sensitive environment variables found."),
                "sensitive_values": a_map(a_str(), computed=True, sensitive=True, description="The map of sensitive environment variables found."),
                "all_values": a_map(a_str(), computed=True, description="The map of all environment variables found, including sensitive ones."),
                # Add the new attribute to the schema
                "all_environment": a_map(a_str(), computed=True, description="A complete map of all environment variables available to the provider process."),
            }
        )

    async def validate(self, config_data: dict[str, Any]) -> list[str]:
        """
        Custom validation logic, now correctly placed to be called by the framework
        during the plan phase.
        """
        if sum(1 for v in [config_data.get("keys"), config_data.get("prefix"), config_data.get("regex")] if v) > 1:
            return ["Only one of 'keys', 'prefix', or 'regex' can be specified."]
        return []

    async def read(self, ctx: ResourceContext) -> EnvVariablesState:
        if not ctx.config: raise DataSourceError("Configuration is required.")
        config = cast(EnvVariablesConfig, ctx.config)

        logger.debug("Starting read operation for EnvVariablesDataSource", config=config)

        exclude_empty = True if config.exclude_empty is None else config.exclude_empty
        case_sensitive = True if config.case_sensitive is None else config.case_sensitive

        # Capture the entire environment at the beginning
        source_vars = os.environ.copy()

        filtered_vars = {}

        if config.keys is not None:
            logger.debug("Filtering by specific keys", keys=config.keys)
            for key in config.keys:
                if (value := source_vars.get(key)) is not None:
                    if exclude_empty and not value: continue
                    filtered_vars[key] = value
        elif config.prefix is not None:
            logger.debug("Filtering by prefix", prefix=config.prefix, case_sensitive=case_sensitive)
            prefix_to_match = config.prefix if case_sensitive else config.prefix.lower()
            for key, value in source_vars.items():
                key_to_check = key if case_sensitive else key.lower()
                if key_to_check.startswith(prefix_to_match):
                    if exclude_empty and not value: continue
                    filtered_vars[key] = value
        elif config.regex is not None:
            logger.debug("Filtering by regex", regex=config.regex, case_sensitive=case_sensitive)
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                compiled_regex = re.compile(config.regex, flags)
                for key, value in source_vars.items():
                    if compiled_regex.match(key):
                        if exclude_empty and not value: continue
                        filtered_vars[key] = value
            except re.error as e:
                raise DataSourceError(f"Invalid regex provided: {e}") from e
        else:
            logger.debug("No filters provided, reading all environment variables")
            for key, value in source_vars.items():
                if exclude_empty and not value: continue
                filtered_vars[key] = value

        logger.debug("Initial filtering complete", count=len(filtered_vars))

        transformed_vars = {}
        for key, value in filtered_vars.items():
            final_key = key.upper() if config.transform_keys == "upper" else (key.lower() if config.transform_keys == "lower" else key)
            final_value = value.upper() if config.transform_values == "upper" else (value.lower() if config.transform_values == "lower" else value)
            transformed_vars[final_key] = final_value

        logger.debug("Transformations applied", count=len(transformed_vars))

        sensitive_keys_set = set(config.sensitive_keys or [])
        sensitive_vals = {k: v for k, v in transformed_vars.items() if k in sensitive_keys_set}
        non_sensitive_vals = {k: v for k, v in transformed_vars.items() if k not in sensitive_keys_set}

        logger.info("Read operation successful", non_sensitive_count=len(non_sensitive_vals), sensitive_count=len(sensitive_vals))

        return EnvVariablesState(
            values=non_sensitive_vals,
            sensitive_values=sensitive_vals,
            all_values=transformed_vars,
            all_environment=source_vars  # Populate the new field
        )

    async def delete(self, ctx: ResourceContext): pass
