"""Tools for querying reformatters dataset metadata."""

import logging
from typing import Any

from mcp.server import Server

logger = logging.getLogger(__name__)


def register_tools(server: Server) -> None:
    """Register dataset metadata tools with the MCP server."""

    @server.list_tools()
    async def list_tools() -> list[dict[str, Any]]:
        """List available dataset tools."""
        return [
            {
                "name": "list_datasets",
                "description": "List all available reformatters datasets with optional filtering",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "Filter by provider (e.g., 'NOAA', 'ECMWF')",
                        },
                        "search": {
                            "type": "string",
                            "description": "Search term for dataset name or description",
                        },
                    },
                },
            },
            {
                "name": "get_dataset_info",
                "description": "Get detailed information about a specific dataset",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {
                            "type": "string",
                            "description": "Dataset identifier (e.g., 'noaa-gfs-forecast')",
                        },
                    },
                    "required": ["dataset_id"],
                },
            },
            {
                "name": "get_dataset_implementation",
                "description": "Show how a dataset is implemented (TemplateConfig, RegionJob paths)",
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
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Handle tool calls for dataset operations."""
        if name == "list_datasets":
            return await _list_datasets(
                arguments.get("provider"),
                arguments.get("search"),
            )
        elif name == "get_dataset_info":
            return await _get_dataset_info(arguments["dataset_id"])
        elif name == "get_dataset_implementation":
            return await _get_dataset_implementation(arguments["dataset_id"])
        else:
            raise ValueError(f"Unknown tool: {name}")


async def _list_datasets(provider: str | None, search: str | None) -> list[dict[str, Any]]:
    """List all datasets with optional filtering."""
    logger.info(f"Listing datasets (provider={provider}, search={search})")

    try:
        from reformatters.__main__ import DYNAMICAL_DATASETS
    except ImportError:
        return [
            {
                "type": "text",
                "text": "Error: Unable to import reformatters. Make sure it's installed as a dependency.",
            }
        ]

    datasets = []
    for dataset in DYNAMICAL_DATASETS:
        try:
            attrs = dataset.template_config.dataset_attributes
            dataset_id = dataset.dataset_id

            if provider and not dataset_id.startswith(provider.lower()):
                continue

            if search:
                search_lower = search.lower()
                if not (
                    search_lower in attrs.name.lower() or search_lower in attrs.description.lower()
                ):
                    continue

            datasets.append(
                {
                    "dataset_id": dataset_id,
                    "name": attrs.name,
                    "description": attrs.description,
                    "spatial_domain": attrs.spatial_domain,
                    "spatial_resolution": attrs.spatial_resolution,
                    "time_domain": attrs.time_domain,
                    "time_resolution": attrs.time_resolution,
                }
            )
        except Exception as e:
            logger.error(f"Error processing dataset {dataset.dataset_id}: {e}")
            continue

    result_text = f"Found {len(datasets)} dataset(s)\n\n"
    for ds in datasets:
        result_text += f"**{ds['name']}** (`{ds['dataset_id']}`)\n"
        result_text += f"{ds['description']}\n"
        result_text += f"- Spatial: {ds['spatial_domain']} at {ds['spatial_resolution']}\n"
        result_text += f"- Temporal: {ds['time_domain']}, {ds['time_resolution']}\n\n"

    return [{"type": "text", "text": result_text}]


async def _get_dataset_info(dataset_id: str) -> list[dict[str, Any]]:
    """Get detailed information about a dataset."""
    logger.info(f"Getting info for dataset: {dataset_id}")

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
                "text": f"Dataset '{dataset_id}' not found. Use list_datasets to see available datasets.",
            }
        ]

    attrs = dataset.template_config.dataset_attributes
    template_config = dataset.template_config

    result_text = f"# {attrs.name}\n\n"
    result_text += f"**ID**: `{dataset_id}`\n"
    result_text += f"**Version**: {attrs.dataset_version}\n\n"
    result_text += f"## Description\n\n{attrs.description}\n\n"
    result_text += f"## Attribution\n\n{attrs.attribution}\n\n"
    result_text += f"## Coverage\n\n"
    result_text += f"- **Spatial**: {attrs.spatial_domain} at {attrs.spatial_resolution}\n"
    result_text += f"- **Temporal**: {attrs.time_domain}, {attrs.time_resolution}\n"

    if attrs.forecast_domain:
        result_text += f"- **Forecast**: {attrs.forecast_domain}, {attrs.forecast_resolution}\n"

    result_text += f"\n## Dimensions\n\n"
    for dim in template_config.dims:
        is_append = " (append dimension)" if dim == template_config.append_dim else ""
        result_text += f"- `{dim}`{is_append}\n"

    result_text += f"\n## Variables\n\n"
    result_text += f"Total: {len(template_config.data_vars)} variables\n\n"

    return [{"type": "text", "text": result_text}]


async def _get_dataset_implementation(dataset_id: str) -> list[dict[str, Any]]:
    """Show how a dataset is implemented."""
    logger.info(f"Getting implementation for dataset: {dataset_id}")

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

    template_class = dataset.template_config.__class__
    region_job_class = dataset.region_job_class

    result_text = f"# Implementation: {dataset_id}\n\n"
    result_text += f"## Classes\n\n"
    result_text += f"- **TemplateConfig**: `{template_class.__module__}.{template_class.__name__}`\n"
    result_text += f"- **RegionJob**: `{region_job_class.__module__}.{region_job_class.__name__}`\n"
    result_text += f"- **DynamicalDataset**: `{dataset.__class__.__module__}.{dataset.__class__.__name__}`\n\n"

    result_text += f"## Storage\n\n"
    result_text += f"- **Primary**: {dataset.primary_storage_config.__class__.__name__}\n"
    if dataset.replica_storage_configs:
        result_text += f"- **Replicas**: {len(dataset.replica_storage_configs)}\n"

    return [{"type": "text", "text": result_text}]
