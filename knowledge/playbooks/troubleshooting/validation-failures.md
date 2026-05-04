# Troubleshooting Validation Failures

**Category**: Troubleshooting
**Severity**: Medium
**Last Updated**: 2026-01-15

## Overview

This playbook helps diagnose and resolve dataset validation failures that occur after backfills or operational updates.

## Common Symptoms

- Validation CronJob failing
- `check_forecast_current_data` fails
- `check_forecast_recent_nans` fails
- `check_for_expected_shards` fails
- Custom validators failing

## Validator Types

Reformatters includes three standard validators:

1. **check_forecast_current_data**: Verifies recent data exists
2. **check_forecast_recent_nans**: Checks for excessive NaN values
3. **check_for_expected_shards**: Validates Zarr structure

## Troubleshooting Steps

### Step 1: Run Validation Locally

```bash
# Run all validators
JOB_NAME=test uv run main <dataset-id> validate

# The output will show which validators passed/failed
```

### Step 2: Check Kubernetes Validation Logs

```bash
# List validation jobs
kubectl get jobs | grep validate

# Get logs from most recent validation
kubectl logs job/<dataset>-validate-<timestamp>

# Check validation CronJob status
kubectl get cronjob <dataset>-validate
kubectl describe cronjob <dataset>-validate
```

### Step 3: Inspect the Data

```python
import zarr
import xarray as xr

# Open the dataset
store = zarr.storage.FSStore('s3://bucket/path/to/dataset.zarr')
ds = xr.open_zarr(store)

# Check dimensions
print(ds.dims)

# Check latest time coordinate
print(ds.init_time[-10:].values)

# Check for NaN values
print(ds['temperature_2m'].isel(init_time=-1).isnull().sum())
```

## Common Failures and Solutions

### Failure 1: Data Not Current

**Error:**
```
ValidationError: Dataset is stale. Latest data is from 2024-01-01, expected recent data.
```

**Causes:**
- Update CronJob not running
- Update CronJob failing silently
- Source data not available

**Solutions:**

1. Check update CronJob:
```bash
kubectl get cronjob <dataset>-update
kubectl logs job/<dataset>-update-<latest>
```

2. Check source data availability:
```bash
# Example for NOAA GFS
aws s3 ls s3://noaa-gfs-bdp-pds/gfs.$(date +%Y%m%d)/ --no-sign-request
```

3. Manually trigger update:
```bash
kubectl create job <dataset>-manual-update --from=cronjob/<dataset>-update
```

### Failure 2: Recent NaN Values

**Error:**
```
ValidationError: Found excessive NaN values in recent data
```

**Causes:**
- Upstream data quality issue
- Processing error
- Variable not available for recent dates

**Solutions:**

1. Verify it's an upstream issue:
```bash
# Download source file directly
aws s3 cp s3://source-bucket/latest-file.grib2 . --no-sign-request

# Check with gdalinfo or wgrib2
gdalinfo latest-file.grib2
```

2. If upstream issue, wait for reprocessing:
```bash
# Temporarily disable validation
kubectl patch cronjob <dataset>-validate -p '{"spec":{"suspend":true}}'

# Re-enable later
kubectl patch cronjob <dataset>-validate -p '{"spec":{"suspend":false}}'
```

3. If processing error, re-run update:
```bash
# Delete recent data chunks (carefully!)
# Then re-run update for that date range
uv run main <dataset-id> backfill-local <date>
```

### Failure 3: Missing Shards

**Error:**
```
ValidationError: Expected shard not found: chunk-0-100.zarr
```

**Causes:**
- Incomplete backfill
- Failed upload to S3
- Corrupted shard

**Solutions:**

1. List actual shards:
```bash
aws s3 ls s3://bucket/path/to/dataset.zarr/<variable>/ --recursive
```

2. Identify missing date range:
```python
import zarr
store = zarr.storage.FSStore('s3://bucket/path/to/dataset.zarr')
ds = xr.open_zarr(store)

# Try to load data and see where it fails
try:
    ds['temperature_2m'].load()
except Exception as e:
    print(f"Failed to load: {e}")
```

3. Re-run backfill for missing range:
```bash
uv run main <dataset-id> backfill-local <start-date> <end-date>
```

### Failure 4: Incorrect Metadata

**Error:**
```
ValidationError: Dataset metadata doesn't match template
```

**Causes:**
- Template updated but data not regenerated
- Manual metadata modification
- Concurrent writes

**Solutions:**

1. Compare template to actual:
```bash
# Check template
ls src/reformatters/<provider>/<model>/<variant>/templates/latest.zarr/

# Check actual dataset metadata
aws s3 ls s3://bucket/path/to/dataset.zarr/zarr.json
aws s3 cp s3://bucket/path/to/dataset.zarr/zarr.json -
```

2. Regenerate dataset if template changed:
```bash
# This requires re-running the entire backfill
DYNAMICAL_ENV=prod uv run main <dataset-id> backfill-kubernetes <end-date>
```

## Custom Validator Failures

If you've implemented custom validators:

1. **Review validator logic**:
```python
# Location: src/reformatters/<provider>/<model>/<variant>/dynamical_dataset.py

def custom_validator(ds: xr.Dataset) -> None:
    """Your custom validation logic."""
    # Add debugging prints
    print(f"Checking: {ds}")
```

2. **Test validator locally**:
```bash
# Run with test job name for debugging
JOB_NAME=test uv run main <dataset-id> validate
```

3. **Adjust validator thresholds** if too strict

## Prevention

1. **Monitor validation CronJobs**:
```bash
# Set up alerts for failed validations
kubectl get events --field-selector type=Warning
```

2. **Run validation after every update**:
```yaml
# Validation CronJob should run 1 hour after update CronJob
schedule: "30 6,12,18,0 * * *"  # If update runs at 5,11,17,23
```

3. **Test validators during development**:
```bash
# Always run validators before production deployment
JOB_NAME=test uv run main <dataset-id> validate
```

4. **Set up monitoring dashboards** to track:
   - Data freshness
   - NaN percentages
   - Validation success rate

## Validation Checklist

After fixing validation issues:

- [ ] Validators pass locally: `JOB_NAME=test uv run main <dataset-id> validate`
- [ ] Data is current (check latest timestamps)
- [ ] No excessive NaN values
- [ ] All expected shards present
- [ ] Metadata matches template
- [ ] Validation CronJob re-enabled
- [ ] Monitoring alerts configured

## Related Documentation

- [Backfill Failures Playbook](backfill-failures.md)
- [Architecture Overview](../../architecture/overview.md)
- [Getting Started Guide](../../guides/getting-started.md)

## Notes

- Validation failures often indicate upstream data issues, not code problems
- Always check source data before assuming processing errors
- Some NaN values are expected (e.g., land/ocean masks, forecast cutoffs)
- Validation thresholds may need tuning for different datasets
