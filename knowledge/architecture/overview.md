# Reformatters Architecture Overview

## High-Level Architecture

Reformatters uses a **three-phase processing model** to convert weather datasets into cloud-optimized Zarr format.

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Template Phase │ --> │  Backfill Phase  │ --> │ Operational Phase  │
│  (Define)       │     │  (Bulk Process)  │     │  (Ongoing Updates) │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

### Phase 1: Template Phase

**Purpose**: Define the dataset structure as Zarr metadata

**Key Component**: `TemplateConfig`

**Process**:
1. Define dimensions, coordinates, and data variables
2. Specify chunking and compression
3. Generate Zarr metadata template
4. Commit template to git for version control

**Output**: `templates/latest.zarr/` directory with Zarr metadata

### Phase 2: Backfill Phase

**Purpose**: Process historical data in parallel

**Key Components**: `RegionJob`, Kubernetes Indexed Jobs

**Process**:
1. Split work into regions (time slices)
2. Distribute regions across Kubernetes pods
3. Each pod:
   - Downloads source files
   - Reads and transforms data
   - Writes to Zarr store
4. Metadata updated last (ensures consistency)

**Parallelism**: Configurable via `--max-parallelism` and `--jobs-per-pod`

### Phase 3: Operational Phase

**Purpose**: Keep datasets up-to-date with latest data

**Key Components**: Kubernetes CronJobs, Validators

**Process**:
1. **Update CronJob**: Runs on schedule (e.g., every 6 hours)
   - Fetches latest data
   - Writes new chunks
   - Updates metadata atomically
2. **Validation CronJob**: Runs after updates
   - Checks data freshness
   - Validates no recent NaNs
   - Verifies shard integrity

## Core Abstractions

### 1. TemplateConfig

Defines **what** the dataset looks like.

**Key Attributes**:
- `dims`: Dimension names (e.g., init_time, lead_time, latitude, longitude)
- `append_dim`: Which dimension grows over time
- `coords`: Coordinate definitions
- `data_vars`: Data variable definitions

**Key Methods**:
- `dimension_coordinates()`: Generate coordinate arrays
- `derive_coordinates()`: Compute derived coordinates
- `get_template()`: Create xarray Dataset with structure

### 2. RegionJob

Defines **how** to process a region of data.

**Key Attributes**:
- `region`: Slice of append dimension to process
- `data_vars`: Variables to process
- `tmp_store`: Temporary Zarr store

**Key Methods**:
- `generate_source_file_coords()`: List source files needed
- `download_file()`: Fetch a source file
- `read_data()`: Parse file and return numpy array
- `apply_data_transformations()`: Transform data (rounding, deaccumulation)
- `process()`: Execute full pipeline

### 3. DynamicalDataset

Orchestrates the entire dataset lifecycle.

**Key Attributes**:
- `template_config`: Instance of TemplateConfig
- `region_job_class`: RegionJob subclass
- `primary_storage_config`: Where to write data
- `replica_storage_configs`: Additional copies

**Key Methods**:
- `update_template()`: Generate template
- `backfill_local()`: Process locally
- `backfill_kubernetes()`: Process on cluster
- `update()`: Operational update
- `validate_dataset()`: Run validators

## Data Flow

```
Source Data (S3/HTTP)
        ↓
    Download
        ↓
    Read & Parse
        ↓
  Transform (deaccumulate, round)
        ↓
   Write to Zarr (sharded)
        ↓
  Primary Store (SourceCoop)
        ↓
  Replica Stores (AWS Open Data)
```

## Storage Architecture

### Zarr Format

- **Chunks**: Sub-arrays for parallel I/O
- **Shards**: Groups of chunks for efficient cloud storage
- **Compression**: Blosc with Zstd
- **Metadata**: JSON files describing structure

### Multi-Store Strategy

1. **Primary**: SourceCoop S3 (Zarr v3)
2. **Replicas**: AWS Open Data, etc.
3. **Formats**: Zarr3 and Icechunk (transactional Zarr)

### Atomic Updates

Updates write data chunks first, then metadata last. This ensures:
- Readers always see consistent data
- No partial updates visible
- Failures don't corrupt the dataset

## Kubernetes Architecture

### Indexed Jobs

```
Job: backfill-noaa-gfs
├── Pod 0: Regions [0:100)
├── Pod 1: Regions [100:200)
├── Pod 2: Regions [200:300)
└── ...
```

Each pod processes multiple regions sequentially.

### CronJobs

- **Update CronJob**: Schedules like `30 5,11,17,23 * * *` (6-hourly)
- **Validation CronJob**: Runs 1 hour after updates

### Resource Management

- CPU/memory limits per pod
- Ephemeral storage for temporary files
- Pod active deadline prevents infinite runs

## Validation Framework

**Protocol**: `DataValidator`

**Built-in Validators**:
- `check_forecast_current_data`: Verify recent data exists
- `check_forecast_recent_nans`: Check for excessive NaNs
- `check_for_expected_shards`: Verify Zarr structure

**Custom Validators**: Each dataset can define specific checks

## Extensibility

### Adding a New Dataset

1. Subclass `TemplateConfig` (structure)
2. Subclass `RegionJob` (processing)
3. Subclass `DynamicalDataset` (orchestration)
4. Register in `DYNAMICAL_DATASETS`

### Adding a New Provider

Create provider directory: `src/reformatters/<provider>/`

### Adding a New Storage Backend

Implement `StorageConfig` subclass

## Performance Optimizations

1. **Shared Memory**: Reduce inter-process communication
2. **Parallel Downloads**: Concurrent file fetching
3. **Parallel Reads**: Multi-threaded data loading
4. **Chunking Strategy**: Optimized for cloud access patterns
5. **Compression**: Blosc Zstd for fast compression/decompression

## Security

- Credentials via Kubernetes secrets
- No hardcoded secrets in code
- Sanitized error messages in production
- Path validation prevents traversal attacks
