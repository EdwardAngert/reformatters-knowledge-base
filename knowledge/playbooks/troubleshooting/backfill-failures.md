# Troubleshooting Backfill Failures

**Category**: Troubleshooting
**Severity**: Medium
**Last Updated**: 2024-12-04

## Overview

This playbook helps diagnose and resolve common backfill failures in reformatters datasets.

## Common Symptoms

- Backfill job fails with error messages
- Incomplete data in output Zarr store
- Download failures for source files
- Memory errors during processing
- Timeout errors

## Troubleshooting Steps

### Step 1: Check Logs

```bash
# For local backfills
# Check terminal output for error messages

# For Kubernetes backfills
kubectl logs job/<job-name>
kubectl get pods --selector=job-name=<job-name>
kubectl logs <pod-name>
```

**What to look for**: Error messages, stack traces, failed file downloads

### Step 2: Verify Source Data Availability

```bash
# Test if source files are accessible
# Example for NOAA GFS
aws s3 ls s3://noaa-gfs-bdp-pds/gfs.20241201/00/atmos/

# For HTTP sources
curl -I <source-url>
```

**Common issues**:
- Source data not yet available (too recent)
- S3 bucket permissions
- Network connectivity

### Step 3: Check Disk Space

```bash
# Local disk space
df -h

# Kubernetes ephemeral storage
kubectl describe pod <pod-name> | grep ephemeral-storage
```

**Solution**: If low on space:
- Clear temporary files
- Reduce `--filter-variable-names` to process fewer variables
- Increase ephemeral storage allocation in pod spec

### Step 4: Memory Issues

**Symptoms**: OOMKilled, MemoryError

```bash
# Check pod memory limits
kubectl describe pod <pod-name> | grep memory
```

**Solutions**:
- Reduce `--jobs-per-pod` to process fewer regions per pod
- Increase pod memory allocation
- Process fewer variables at once

### Step 5: Timeout Issues

**Symptoms**: Job exceeds `pod_active_deadline`

```bash
# Check job deadline
kubectl describe job <job-name> | grep activeDeadlineSeconds
```

**Solutions**:
- Increase `pod_active_deadline` in dataset config
- Reduce work per pod (`--jobs-per-pod`)
- Increase `--max-parallelism` to distribute work

### Step 6: Data Validation Failures

```bash
# Run validators locally
JOB_NAME=test uv run main <dataset-id> validate
```

**Common issues**:
- NaN values in recent data (upstream issue)
- Missing shards
- Incorrect chunking

## Resolution Checklist

- [ ] Identified error from logs
- [ ] Verified source data availability
- [ ] Checked disk space and memory
- [ ] Adjusted job parameters if needed
- [ ] Re-ran backfill
- [ ] Validated output data

## Prevention

- Monitor source data availability before scheduling backfills
- Set appropriate resource limits based on dataset size
- Use incremental backfills rather than processing entire archives at once
- Implement retry logic for transient failures

## Related Documentation

- [Dataset Integration Guide](../../guides/dataset-integration-guide.md)
- [Getting Started](../../guides/getting-started.md)

## Notes

For persistent issues, check GitHub issues or contact the team.
