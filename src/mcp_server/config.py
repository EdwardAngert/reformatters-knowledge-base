"""Configuration for the MCP server."""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    """MCP server configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    environment: Literal["development", "production"] = Field(
        default="development",
        description="Environment mode",
    )

    # Don't read HOST from env - Railway sets it incorrectly
    # We always want to bind to 0.0.0.0 for container deployments
    host: str = Field(
        default="0.0.0.0",
        description="Server host",
    )

    port: int = Field(
        default=8000,
        description="Server port",
    )

    @field_validator("host", mode="before")
    @classmethod
    def force_bind_all_interfaces(cls, v):
        """Force host to 0.0.0.0 for container deployments."""
        # Railway incorrectly sets HOST=8000, ignore any bad values
        return "0.0.0.0"

    allowed_origins: list[str] | str = Field(
        default_factory=lambda: [
            "https://claude.ai",
            "http://localhost:*",
            "http://127.0.0.1:*",
        ],
        description="Allowed CORS origins (comma-separated string or list)",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from string or list."""
        if isinstance(v, str):
            # Split comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    knowledge_base_path: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "knowledge",
        description="Path to knowledge base directory",
    )

    reformatters_repo_url: str = Field(
        default="https://github.com/dynamical/reformatters.git",
        description="URL to reformatters repository",
    )

    enable_live_data_access: bool = Field(
        default=False,
        description="Enable access to live S3/R2 datasets",
    )

    aws_access_key_id: str | None = Field(
        default=None,
        description="AWS access key for S3 access",
    )

    aws_secret_access_key: str | None = Field(
        default=None,
        description="AWS secret key for S3 access",
    )

    r2_access_key_id: str | None = Field(
        default=None,
        description="R2 access key",
    )

    r2_secret_access_key: str | None = Field(
        default=None,
        description="R2 secret key",
    )

    r2_endpoint_url: str | None = Field(
        default=None,
        description="R2 endpoint URL",
    )

    max_template_expansion_years: int = Field(
        default=1,
        description="Maximum years to expand templates",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


config = ServerConfig()
