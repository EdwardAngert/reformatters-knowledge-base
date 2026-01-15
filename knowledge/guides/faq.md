# Frequently Asked Questions (FAQ)

Quick answers to common questions about reformatters.

## Table of Contents

- [General](#general)
- [Getting Started](#getting-started)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## General

### What is reformatters?

Reformatters is a Python system that converts weather and climate datasets from various meteorological agencies (NOAA, ECMWF, DWD, NASA) into Zarr v3 format, optimized for cloud access.

### Why use reformatters instead of accessing the original data?

- **Cloud-optimized**: Zarr format enables efficient streaming and lazy loading
- **Standardized**: All datasets follow the same structure and conventions
- **Accessible**: Available via AWS Open Data and SourceCoop
- **Performant**: Optimized chunking and compression for fast access

### What data sources does reformatters support?

Currently supported:
- **NOAA**: GFS, GEFS, HRRR, NAM
- **ECMWF**: ERA5, IFS
- **DWD**: ICON
- **NASA**: MERRA-2, GEOS-FP

Check `uv run main --help` for the complete list.

### Where is the reformatted data stored?

Primary storage:
- **SourceCoop S3**: Zarr v3 format
- **AWS Open Data**: Public access

### How much does it cost to use reformatted data?

The data is freely available through AWS Open Data (requester pays for egress) and SourceCoop.

---

## Getting Started

### How do I install reformatters?

```bash
git clone https://github.com/dynamical/reformatters.git
cd reformatters
uv sync
```

### What are the minimum requirements?

- Python 3.11+
- uv package manager
- 4GB+ RAM for local testing
- For production: Kubernetes cluster

### How do I list available datasets?

```bash
uv run main --help
```

This shows all registered datasets.

### How do I test a dataset locally before deploying?

```bash
# Backfill a small date range with one variable
uv run main <dataset-id> backfill-local 2024-01-02 \
  --filter-variable-names <variable-name>
```

### What's the fastest way to add a new dataset?

```bash
# 1. Initialize
uv run main initialize-new-integration <provider> <model> <variant>

# 2. Implement the three core classes (see dataset-integration-guide.md)

# 3. Register in __main__.py

# 4. Test locally
uv run main <dataset-id> backfill-local <date>
```

---

## Development

### What are the three core classes I need to implement?

1. **TemplateConfig**: Defines dataset structure (dimensions, coordinates, variables)
2. **RegionJob**: Implements processing logic (download, read, write)
3. **DynamicalDataset**: Orchestrates deployment and operations

### How do I generate a template?

```bash
uv run main <dataset-id> update-template
```

This creates `templates/latest.zarr/` with Zarr metadata. Commit this to git!

### How do I run tests?

```bash
# All tests
uv run pytest

# Specific dataset
uv run pytest tests/<provider>/<model>/<variant>/

# Specific test file
uv run pytest tests/<provider>/<model>/<variant>/template_config_test.py
```

### How do I debug a failing backfill?

1. Check logs for error messages
2. Try with a single variable: `--filter-variable-names <var>`
3. Test locally first: `backfill-local` instead of `backfill-kubernetes`
4. Verify source data is available
5. Check disk space and memory

### Where do I find example implementations?

Look at existing datasets in `src/reformatters/`:
- `noaa/gfs/forecast/` - Good example for gridded forecast data
- `ecmwf/era5/analysis/` - Example for reanalysis data
- `dwd/icon/forecast/` - Example for rotated grid data

---

## Deployment

### How do I deploy to Kubernetes?

```bash
# Backfill historical data
DYNAMICAL_ENV=prod uv run main <dataset-id> backfill-kubernetes <end-date> \
  --max-parallelism 100

# Set up operational updates
kubectl apply -f <generated-cronjob-yaml>
```

### How many parallel jobs should I use?

Start conservative:
- Small datasets: 10-50 jobs
- Medium datasets: 50-200 jobs
- Large datasets: 200-500 jobs

Monitor resource usage and adjust.

### How long does a backfill take?

Depends on:
- Dataset size (time range, spatial resolution, number of variables)
- Parallelism level
- Network bandwidth
- Compute resources

Typical ranges:
- Small dataset (1 year, few variables): 1-4 hours
- Medium dataset (5 years, many variables): 4-24 hours
- Large dataset (30+ years): 1-7 days

### Can I pause and resume a backfill?

Yes! Backfills are idempotent. If a job fails or is stopped:
1. Identify which regions failed
2. Re-run with a narrower date range
3. Data already written is not re-processed

### How do I validate the output?

```bash
JOB_NAME=test uv run main <dataset-id> validate
```

This runs all validators to check data freshness, integrity, and quality.

---

## Troubleshooting

### Why is my backfill failing with "403 Forbidden"?

**Cause**: AWS credentials missing or incorrect

**Solution**:
```bash
# Check credentials
aws s3 ls s3://your-target-bucket

# For Kubernetes
kubectl get secret <dataset>-aws-credentials
```

### Why am I getting "OOMKilled" errors?

**Cause**: Pod ran out of memory

**Solutions**:
- Reduce `--jobs-per-pod` to process fewer regions per pod
- Increase pod memory allocation in dataset config
- Process fewer variables at once with `--filter-variable-names`

### Why does my job timeout?

**Cause**: Job exceeded `pod_active_deadline`

**Solutions**:
- Increase `pod_active_deadline` in dataset config
- Reduce work per pod (`--jobs-per-pod`)
- Increase parallelism (`--max-parallelism`)

### Source files are missing - what do I do?

**Causes**:
- Data not yet available (too recent)
- S3 bucket moved or deleted
- Network connectivity issues

**Solutions**:
- Wait if data is too recent (check provider's publication schedule)
- Verify source URL is correct
- Check network connectivity: `curl -I <source-url>`

### Validation is failing - what should I check?

Common issues:
- **Recent NaNs**: Upstream data issue, wait for reprocessing
- **Missing shards**: Backfill incomplete, check logs
- **Stale data**: Update CronJob not running, check `kubectl get cronjobs`

### How do I find the error in a failed Kubernetes job?

```bash
# List pods for the job
kubectl get pods --selector=job-name=<job-name>

# Check logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

---

## Architecture

### What is the append dimension?

The dimension that grows over time (typically `init_time` or `time`). New data is appended along this dimension during updates.

### What are regions?

A region is a slice of the append dimension to process. For example, if append dimension is `init_time`, a region might be one week of initialization times.

### How does sharding work?

Zarr v3 groups multiple chunks into shards for efficient cloud storage:
- **Chunks**: Sub-arrays for parallel I/O (e.g., 1 time × 361 lat × 720 lon)
- **Shards**: Groups of chunks (e.g., 10 time chunks per shard)
- **Benefit**: Reduces number of S3 objects, improves listing performance

### Why write metadata last?

Atomic updates! Writing metadata last ensures:
- Readers always see consistent data
- No partial updates visible
- Failures don't corrupt the dataset

### What's the difference between backfill and operational updates?

- **Backfill**: One-time processing of historical data (parallelized with Kubernetes Jobs)
- **Operational Updates**: Ongoing updates with latest data (scheduled with CronJobs)

### Can I use a different storage backend?

Yes! Implement a `StorageConfig` subclass:
- `LocalStorageConfig` - Local filesystem
- `S3StorageConfig` - Any S3-compatible storage
- `SourceCoopDatasetStorageConfig` - SourceCoop
- Custom: Subclass `StorageConfig`

### How do I optimize chunking?

Consider access patterns:
- **Time series access**: Larger time chunks
- **Spatial analysis**: Larger spatial chunks
- **General purpose**: Balance all dimensions

Rule of thumb: Aim for 10MB-100MB per chunk (compressed).

---

## Need More Help?

- **Guides**: See `knowledge/guides/` for detailed guides
- **Playbooks**: See `knowledge/playbooks/` for troubleshooting
- **Issues**: https://github.com/dynamical/reformatters/issues
- **Discussions**: https://github.com/dynamical/reformatters/discussions
