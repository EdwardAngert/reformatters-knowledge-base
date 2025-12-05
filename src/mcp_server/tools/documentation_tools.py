"""Tools for generating documentation."""

import logging
from typing import Any

from mcp.server import Server

logger = logging.getLogger(__name__)


def register_tools(server: Server) -> None:
    """Register documentation generation tools with the MCP server."""

    @server.list_tools()
    async def list_tools() -> list[dict[str, Any]]:
        """List available documentation tools."""
        return [
            {
                "name": "generate_dataset_readme",
                "description": "Auto-generate markdown documentation for a dataset",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {
                            "type": "string",
                            "description": "Dataset identifier",
                        },
                    },
                    "required": ["dataset_id"],
                },
            },
            {
                "name": "generate_cli_command",
                "description": "Generate CLI command for a dataset operation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["update-template", "backfill-local", "validate"],
                            "description": "Operation to perform",
                        },
                        "dataset_id": {
                            "type": "string",
                            "description": "Dataset identifier",
                        },
                    },
                    "required": ["operation", "dataset_id"],
                },
            },
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Handle tool calls for documentation operations."""
        if name == "generate_dataset_readme":
            return await _generate_dataset_readme(arguments["dataset_id"])
        elif name == "generate_cli_command":
            return await _generate_cli_command(
                arguments["operation"],
                arguments["dataset_id"],
            )
        else:
            raise ValueError(f"Unknown tool: {name}")


async def _generate_dataset_readme(dataset_id: str) -> list[dict[str, Any]]:
    """Generate README documentation for a dataset."""
    logger.info(f"Generating README for dataset: {dataset_id}")

    try:
        from reformatters.__main__ import DYNAMICAL_DATASETS
    except ImportError:
        return [
            {
                "type": "text",
                "text": "Error: Unable to import reformatters.",
            }
        ]

    dataset = None
    for ds in DYNAMICAL_DATASETS:
        if ds.dataset_id == dataset_id:
            dataset = ds
            break

    if not dataset:
        return [
            {
                "type": "text",
                "text": f"Dataset '{dataset_id}' not found.",
            }
        ]

    attrs = dataset.template_config.dataset_attributes
    template_config = dataset.template_config

    readme = f"# {attrs.name}\n\n"
    readme += f"**Dataset ID**: `{dataset_id}`  \n"
    readme += f"**Version**: {attrs.dataset_version}\n\n"

    readme += f"## Description\n\n{attrs.description}\n\n"

    readme += f"## Attribution\n\n{attrs.attribution}\n\n"

    readme += f"## Spatial Coverage\n\n"
    readme += f"- **Domain**: {attrs.spatial_domain}\n"
    readme += f"- **Resolution**: {attrs.spatial_resolution}\n\n"

    readme += f"## Temporal Coverage\n\n"
    readme += f"- **Domain**: {attrs.time_domain}\n"
    readme += f"- **Resolution**: {attrs.time_resolution}\n\n"

    if attrs.forecast_domain:
        readme += f"## Forecast Coverage\n\n"
        readme += f"- **Domain**: {attrs.forecast_domain}\n"
        readme += f"- **Resolution**: {attrs.forecast_resolution}\n\n"

    readme += f"## Dimensions\n\n"
    readme += "| Dimension | Append Dimension |\n"
    readme += "|-----------|------------------|\n"
    for dim in template_config.dims:
        is_append = "✓" if dim == template_config.append_dim else ""
        readme += f"| `{dim}` | {is_append} |\n"
    readme += "\n"

    readme += f"## Variables\n\n"
    readme += "| Name | Long Name | Units | Type |\n"
    readme += "|------|-----------|-------|------|\n"
    for var in template_config.data_vars[:10]:  # First 10 variables
        readme += f"| `{var.name}` | {var.attrs.long_name} | {var.attrs.units} | {var.attrs.step_type} |\n"

    if len(template_config.data_vars) > 10:
        readme += f"\n*... and {len(template_config.data_vars) - 10} more variables*\n"

    readme += "\n## Usage\n\n"
    readme += "### Generate/Update Template\n\n"
    readme += "```bash\n"
    readme += f"uv run main {dataset_id} update-template\n"
    readme += "```\n\n"

    readme += "### Backfill Locally\n\n"
    readme += "```bash\n"
    readme += f"uv run main {dataset_id} backfill-local <end-date>\n"
    readme += "```\n\n"

    readme += "### Validate Dataset\n\n"
    readme += "```bash\n"
    readme += f"JOB_NAME=validation uv run main {dataset_id} validate\n"
    readme += "```\n"

    return [{"type": "text", "text": readme}]


async def _generate_cli_command(operation: str, dataset_id: str) -> list[dict[str, Any]]:
    """Generate CLI command for an operation."""
    logger.info(f"Generating CLI command: {operation} for {dataset_id}")

    commands = {
        "update-template": f"uv run main {dataset_id} update-template",
        "backfill-local": f"uv run main {dataset_id} backfill-local <INIT_TIME_END>",
        "validate": f"JOB_NAME=validation uv run main {dataset_id} validate",
    }

    command = commands.get(operation)
    if not command:
        return [
            {
                "type": "text",
                "text": f"Unknown operation: {operation}",
            }
        ]

    result = f"**Command**: `{command}`\n\n"
    result += f"**Description**: {operation.replace('-', ' ').title()} for dataset `{dataset_id}`\n"

    return [{"type": "text", "text": result}]
