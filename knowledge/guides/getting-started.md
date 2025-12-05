# Getting Started with Reformatters

Welcome to the reformatters project! This guide will help you get started with using and contributing to reformatters datasets.

## What is Reformatters?

Reformatters is a Python system that converts weather and climate datasets from various meteorological agencies (NOAA, ECMWF, DWD, NASA) into **Zarr v3**, a cloud-optimized data format.

## Why Reformatters?

- **Cloud-Optimized**: Zarr format enables efficient streaming and lazy loading
- **Standardized**: All datasets follow the same structure and conventions
- **Scalable**: Kubernetes-based processing for massive datasets
- **Open**: Data available via AWS Open Data and SourceCoop

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/dynamical/reformatters.git
cd reformatters

# Install with uv
uv sync
```

### 2. Explore Available Datasets

```bash
# List all datasets
uv run main --help

# See available datasets in the code
# They're registered in src/reformatters/__main__.py
```

### 3. Generate a Template

```bash
# Example: NOAA GFS Forecast
uv run main noaa-gfs-forecast update-template
```

### 4. Run a Local Backfill (Small Test)

```bash
# Backfill a small date range locally
uv run main noaa-gfs-forecast backfill-local 2024-01-02 \\
  --filter-variable-names temperature_2m

# This will:
# 1. Download source files
# 2. Process and reformat them
# 3. Write to a local Zarr store
```

### 5. Validate the Dataset

```bash
# Run validators
JOB_NAME=test uv run main noaa-gfs-forecast validate
```

## Key Concepts

### Three-Phase Processing

1. **Template Phase**: Define dataset structure as Zarr metadata
2. **Backfill Phase**: Process historical data (parallelized)
3. **Operational Phase**: Ongoing updates via CronJobs

### Three Core Classes

1. **TemplateConfig**: Defines dataset structure (dimensions, variables, metadata)
2. **RegionJob**: Implements processing logic (download → read → write)
3. **DynamicalDataset**: Orchestrates deployment and operations

## Common Tasks

### Adding a New Dataset

See the [dataset integration guide](dataset-integration-guide.md) for detailed steps.

### Troubleshooting

See our [troubleshooting playbooks](../playbooks/troubleshooting/) for common issues.

## Next Steps

- Read the [Dataset Integration Guide](dataset-integration-guide.md)
- Explore [example implementations](../examples/)
- Check out [architecture documentation](../architecture/overview.md)
- Join the discussion on GitHub

## Getting Help

- **Documentation**: Browse this knowledge base
- **Issues**: https://github.com/dynamical/reformatters/issues
- **Discussions**: https://github.com/dynamical/reformatters/discussions
