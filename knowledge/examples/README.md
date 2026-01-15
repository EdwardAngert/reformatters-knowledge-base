# Code Examples

This directory contains practical, working code examples for implementing reformatters datasets.

## Available Examples

### 1. Minimal TemplateConfig (`minimal-template-config.py`)

The simplest possible TemplateConfig implementation for a forecast dataset.

**What it demonstrates:**
- Basic dataset metadata
- Dimension definitions
- Coordinate generation
- Data variable definitions
- Chunking and sharding

**Use when:** Starting a new dataset from scratch

**Key sections:**
- Dataset attributes and metadata
- Dimension and coordinate definitions
- The critical `dimension_coordinates()` method
- Chunking strategy

### 2. Minimal RegionJob (`minimal-region-job.py`)

Simple RegionJob implementation showing the core processing logic.

**What it demonstrates:**
- Generating source file coordinates
- Downloading from S3 (public and private)
- Reading data with xarray
- Processing workflow
- Operational update patterns

**Use when:** Implementing data processing logic

**Key sections:**
- `generate_source_file_coords()` - listing files to process
- `download_file()` - fetching source data
- `read_data()` - parsing and extracting data
- `operational_update_jobs()` - defining update regions

### 3. Custom Validator (`custom-validator.py`)

Examples of custom dataset validators.

**What it demonstrates:**
- Physical bounds checking
- Spatial coverage validation
- Temporal consistency checks
- Data freshness validation
- NaN detection

**Use when:** Adding dataset-specific validation

**Key validators:**
- Temperature range check
- Spatial coverage check
- Forecast lead time check
- Data freshness check
- All-NaN timestep detection

## How to Use These Examples

### Copy and Adapt

```bash
# Copy example to your dataset directory
cp knowledge/examples/minimal-template-config.py \
   src/reformatters/your-provider/your-model/your-variant/template_config.py

# Modify for your dataset
# - Update dataset attributes
# - Adjust dimensions
# - Customize coordinate generation
# - Add your variables
```

### Learn from Structure

Study the structure and comments to understand:
- Required vs. optional methods
- Expected return types
- Common patterns
- Best practices

### Test Locally

```bash
# Test template generation
uv run main your-dataset-id update-template

# Test processing
uv run main your-dataset-id backfill-local 2024-01-01
```

## Common Patterns

### Pattern 1: Time Dimension Coordinates

```python
def dimension_coordinates(self, dim, start, end):
    if dim == "init_time":
        # Daily
        num_days = (end - start).days
        return np.array(
            [start + timedelta(days=i) for i in range(num_days)],
            dtype="datetime64[ns]"
        )
```

### Pattern 2: Downloading from S3

```python
def download_file(self, coord):
    # For public buckets
    s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))

    # For private buckets
    # s3_client = boto3.client("s3")  # Uses credentials

    s3_client.download_file(bucket, key, str(local_path))
    return local_path
```

### Pattern 3: Reading GRIB Files

```python
def read_data(self, coord):
    ds = xr.open_dataset(
        file_path,
        engine="cfgrib",
        backend_kwargs={"indexpath": ""}
    )

    data = ds["source_var_name"].values
    ds.close()

    return {"target_var_name": data}
```

## Next Steps

After understanding these minimal examples:

1. **Look at real implementations**: Browse `src/reformatters/` for production examples
2. **Read the integration guide**: See `knowledge/guides/dataset-integration-guide.md`
3. **Study advanced patterns**: (Coming soon: advanced examples)
4. **Ask questions**: GitHub discussions or team chat

## Advanced Examples (Coming Soon)

Planned advanced examples:
- Complete dataset integration (all three classes)
- Storage configurations
- Advanced template config (derived coordinates, complex chunking)
- Advanced region job (parallel processing, error handling)
- Data transformations (deaccumulation, regridding)
- Testing strategies
- Kubernetes configurations

## Related Documentation

- [Dataset Integration Guide](../guides/dataset-integration-guide.md)
- [Getting Started](../guides/getting-started.md)
- [Architecture Overview](../architecture/overview.md)
- [FAQ](../guides/faq.md)

## Tips

1. **Start simple**: Use minimal examples as starting point
2. **Add complexity gradually**: Don't try to handle all edge cases at once
3. **Test frequently**: Run locally after each change
4. **Follow existing patterns**: Look at similar datasets
5. **Document as you go**: Add comments explaining non-obvious choices
