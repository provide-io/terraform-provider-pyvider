from pyvider.capabilities import BaseCapability, register_capability
from pyvider.schema import PvsAttribute, a_bool, a_map, a_num, a_str
from pyvider.telemetry import logger


@register_capability("api")
class ApiCapability(BaseCapability):
    """
    A capability that extends the provider's schema with common configuration
    options for interacting with a RESTful API.
    """

    @staticmethod
    def get_schema_contribution() -> dict[str, PvsAttribute]:
        """
        Contributes API-related optional attributes to the provider schema.
        """
        logger.debug(
            "🤝 [ApiCapability] Contributing schema attributes to provider",
            capability_name="api"
        )

        contribution = {
            "api_endpoint": a_str(
                optional=True,
                description="The base URL of the API endpoint (e.g., 'https://api.example.com').",
            ),
            "api_token": a_str(
                optional=True,
                sensitive=True,
                description="The authentication token (e.g., Bearer token) for API requests.",
            ),
            "api_timeout": a_num(
                optional=True,
                description="Request timeout in seconds for API calls.",
            ),
            "api_retries": a_num(
                optional=True,
                description="The maximum number of retries for failed API requests.",
            ),
            "api_insecure_skip_verify": a_bool(
                optional=True,
                description="If true, bypasses TLS certificate verification. Use with caution.",
            ),
            "api_headers": a_map(
                a_str(),
                optional=True,
                description="A map of custom HTTP headers to send with every API request.",
            ),
        }

        logger.debug(
            "🤝 [ApiCapability] Schema contribution defined",
            attributes=list(contribution.keys())
        )

        return contribution

    def __init__(self):
        """
        Initializes the API capability, potentially setting up an API client
        based on the provider's configuration.
        
        Note: This is a placeholder for where client initialization logic would go.
        The actual configuration would be passed in from the provider.
        """
        logger.debug("🤝 [ApiCapability] Instance created.")
        # In a real implementation, you might have something like:
        # self.api_client = self._create_client(config)

    def _create_client(self, config: dict):
        """Placeholder for creating and configuring an HTTP client."""
        logger.debug("🤝 [ApiCapability] Creating API client with config", config=config)
        # Logic to initialize httpx.AsyncClient or similar would go here.
        pass
