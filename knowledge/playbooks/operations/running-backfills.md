# Running Backfills - Operations Playbook

**Category**: Operations
**Last Updated**: 2026-01-15

## Overview

Step-by-step guide for running dataset backfills safely and efficiently, from planning through validation.

## Prerequisites

- [ ] Dataset implementation complete and tested
- [ ] Template generated and committed
- [ ] Local test successful with `backfill-local`
- [ ] AWS credentials configured
- [ ] Kubernetes cluster access
- [ ] Target storage bucket accessible

## Phase 1: Planning

### Step 1: Determine Scope

```bash
# Identify date range
START_DATE="2020-01-01"
END_DATE="2024-12-31"

# Identify dataset
DATASET_ID="noaa-gfs-forecast"

# Estimate workload
# For daily data: days = (end - start)
# For 6-hourly data: samples = days × 4
```

### Step 2: Estimate Resources

**Calculate expected dataset size:**
```python
# Example calculation
variables = 50
time_steps = 365 * 4  # Daily × 4 per day × 1 year
lat_points = 361
lon_points = 720
bytes_per_value = 4  # float32

uncompressed_size = variables × time_steps × lat_points × lon_points × bytes_per_value
compressed_size = uncompressed_size × 0.3  # Assume 3:1 compression

print(f"Estimated size: {compressed_size / 1e9:.2f} GB")
```

**Estimate runtime:**
- Small dataset (< 100 GB): 2-6 hours
- Medium dataset (100-500 GB): 6-24 hours
- Large dataset (> 500 GB): 1-7 days

**Choose parallelism level:**
```bash
# Conservative: Start with 10-50 parallel jobs
# Standard: 50-200 parallel jobs
# Aggressive: 200-500+ parallel jobs

# Trade-off: More parallelism = faster completion but higher cost
```

### Step 3: Test Small Range First

```bash
# CRITICAL: Always test a small range first!
uv run main $DATASET_ID backfill-kubernetes 2024-01-01 2024-01-02 \
  --max-parallelism 5 \
  --jobs-per-pod 5
```

Monitor this test run:
```bash
# Watch jobs
kubectl get jobs -w

# Check pod status
kubectl get pods | grep $DATASET_ID

# View logs
kubectl logs -f job/<job-name>
```

## Phase 2: Execution

### Step 4: Run Full Backfill

Once test is successful:

```bash
# Set environment to production
export DYNAMICAL_ENV=prod

# Run backfill with chosen parameters
uv run main $DATASET_ID backfill-kubernetes $END_DATE \
  --max-parallelism 100 \
  --jobs-per-pod 10 \
  --start-date $START_DATE  # If supported
```

**Command breakdown:**
- `backfill-kubernetes`: Uses Kubernetes jobs for parallelization
- `$END_DATE`: The last date to process (append dimension end)
- `--max-parallelism`: Number of parallel pods
- `--jobs-per-pod`: Regions processed per pod

### Step 5: Monitor Progress

**Watch job completion:**
```bash
# Overall progress
kubectl get jobs | grep $DATASET_ID

# Shows: COMPLETIONS (e.g., 45/100)
```

**Monitor pod status:**
```bash
# Active pods
kubectl get pods | grep $DATASET_ID | grep Running

# Failed pods
kubectl get pods | grep $DATASET_ID | grep Error

# Completed pods
kubectl get pods | grep $DATASET_ID | grep Completed
```

**Check logs:**
```bash
# Logs from specific pod
kubectl logs <pod-name>

# Logs from all pods in job
kubectl logs -l job-name=<job-name>

# Follow logs
kubectl logs -f <pod-name>
```

**Monitor resource usage:**
```bash
# Pod resource consumption
kubectl top pods | grep $DATASET_ID

# Node resource consumption
kubectl top nodes
```

### Step 6: Handle Failures

**Identify failed pods:**
```bash
# Get failed pods
kubectl get pods --field-selector=status.phase=Failed | grep $DATASET_ID

# Check failure reason
kubectl describe pod <failed-pod-name>

# View logs
kubectl logs <failed-pod-name>
```

**Common failure patterns:**
- **OOMKilled**: Reduce `--jobs-per-pod`, see [Memory Issues Playbook](../troubleshooting/memory-and-resource-issues.md)
- **403 Forbidden**: Check credentials, see [AWS Credentials Playbook](../troubleshooting/aws-credentials-errors.md)
- **Timeout**: Increase `pod_active_deadline` or reduce work per pod

**Retry failed regions:**
```bash
# Identify failed region indices from logs
# Re-run with specific date range or reduced parallelism

uv run main $DATASET_ID backfill-kubernetes <end-date> \
  --max-parallelism 50 \
  --jobs-per-pod 5  # Reduced workload
```

## Phase 3: Validation

### Step 7: Verify Backfill Completion

```bash
# All jobs should show COMPLETIONS = 100%
kubectl get jobs | grep $DATASET_ID

# Check for any remaining failed/pending pods
kubectl get pods | grep $DATASET_ID | grep -v Completed
```

### Step 8: Run Validators

```bash
# Run validation suite
JOB_NAME=test uv run main $DATASET_ID validate
```

**Validators check:**
- Data completeness
- No excessive NaN values
- Expected shards present
- Metadata consistency

If validation fails, see [Validation Failures Playbook](../troubleshooting/validation-failures.md).

### Step 9: Manual Spot Checks

```python
import xarray as xr
import zarr

# Open dataset
store = zarr.storage.FSStore('s3://bucket/path/dataset.zarr')
ds = xr.open_zarr(store)

# Check time coverage
print(f"Start: {ds.init_time[0].values}")
print(f"End: {ds.init_time[-1].values}")
print(f"Total times: {len(ds.init_time)}")

# Check for gaps
time_diffs = ds.init_time.diff('init_time')
gaps = time_diffs[time_diffs > expected_interval]
print(f"Gaps found: {len(gaps)}")

# Sample data values
sample = ds.temperature_2m.isel(init_time=-1, lead_time=0)
print(f"Recent data sample:\n{sample}")
print(f"NaN percentage: {sample.isnull().sum() / sample.size * 100:.2f}%")

# Check dataset size
print(f"Variables: {len(ds.data_vars)}")
print(f"Dimensions: {ds.dims}")
```

## Phase 4: Cleanup

### Step 10: Clean Up Kubernetes Resources

```bash
# Delete completed jobs (optional, saves clutter)
kubectl delete jobs -l dataset=$DATASET_ID,status=completed

# Delete failed pods after investigating
kubectl delete pods --field-selector=status.phase=Failed

# Completed pods are auto-deleted after TTL (usually 24 hours)
```

### Step 11: Document Results

Create a record of the backfill:

```markdown
# Backfill Record: <dataset-id>

**Date**: 2024-01-15
**Date Range**: 2020-01-01 to 2024-12-31
**Duration**: 8 hours
**Parallelism**: 100 pods, 10 regions/pod
**Final Size**: 250 GB (compressed)
**Status**: ✅ Complete

## Issues Encountered
- Initial OOMKilled errors → reduced jobs-per-pod from 20 to 10
- 5 failed pods due to network timeout → reran successfully

## Validation
- All validators passed
- Spot checks confirmed complete time coverage
- No data gaps found

## Notes
- Used 8Gi memory per pod
- Total cost: ~$50 (8 hours × 100 pods × $0.0625/pod-hour)
```

## Phase 5: Operational Setup

### Step 12: Set Up Operational Updates

```bash
# Deploy update CronJob
kubectl apply -f <generated-cronjob-yaml>

# Verify CronJob created
kubectl get cronjob $DATASET_ID-update

# Check schedule
kubectl describe cronjob $DATASET_ID-update | grep Schedule
```

### Step 13: Set Up Validation CronJob

```bash
# Deploy validation CronJob (runs after updates)
kubectl apply -f <generated-validation-cronjob-yaml>

# Verify
kubectl get cronjob $DATASET_ID-validate
```

### Step 14: Configure Monitoring

Set up alerts for:
- Failed update jobs
- Failed validations
- Stale data (no updates in 24h)
- High error rates

## Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| OOMKilled | Reduce `--jobs-per-pod` |
| 403 Forbidden | Check AWS credentials |
| Disk full | Increase ephemeral storage |
| Timeout | Increase `pod_active_deadline` |
| Slow progress | Increase `--max-parallelism` |
| Failed pods | Check logs, see playbooks |

## Best Practices

### Do's
- ✅ Always test small date range first
- ✅ Monitor first hour of large backfills closely
- ✅ Start with conservative parallelism
- ✅ Run validation after completion
- ✅ Document parameters and issues

### Don'ts
- ❌ Don't start large backfill without testing
- ❌ Don't max out cluster resources
- ❌ Don't ignore failed pods
- ❌ Don't skip validation
- ❌ Don't run backfills during peak hours

## Optimization Tips

### Speeding Up Backfills

1. **Increase parallelism** if cluster has capacity
2. **Reduce compression level** for faster writes (trade-off: larger files)
3. **Process variables separately** to parallelize further
4. **Use faster storage** (e.g., SSD-backed)

### Reducing Costs

1. **Use spot instances** for Kubernetes nodes
2. **Lower parallelism** (takes longer but cheaper)
3. **Compress more aggressively** (slower but smaller storage)
4. **Run during off-peak hours** if applicable

## Checklist

### Pre-Backfill
- [ ] Implementation tested locally
- [ ] Template generated and committed
- [ ] Credentials configured
- [ ] Storage bucket accessible
- [ ] Small test run successful
- [ ] Resource requirements estimated

### During Backfill
- [ ] Monitor job progress
- [ ] Watch for failures
- [ ] Check resource usage
- [ ] Handle errors promptly

### Post-Backfill
- [ ] All jobs completed
- [ ] Validators pass
- [ ] Manual spot checks done
- [ ] Kubernetes resources cleaned up
- [ ] Operational CronJobs deployed
- [ ] Monitoring configured
- [ ] Results documented

## Related Documentation

- [Backfill Failures Playbook](../troubleshooting/backfill-failures.md)
- [Memory Issues Playbook](../troubleshooting/memory-and-resource-issues.md)
- [Dataset Integration Guide](../../guides/dataset-integration-guide.md)

## Notes

- Backfills are idempotent - safe to re-run
- Failed regions can be reprocessed without affecting completed ones
- Metadata is written last to ensure atomicity
- Large backfills can be expensive - optimize carefully
