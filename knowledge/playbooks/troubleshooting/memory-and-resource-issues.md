# Memory and Resource Issues

**Category**: Troubleshooting
**Severity**: High
**Last Updated**: 2026-01-15

## Overview

This playbook addresses out-of-memory errors, CPU throttling, and disk space issues during backfills and updates.

## Common Symptoms

- Pods with status `OOMKilled`
- Python `MemoryError` exceptions
- Disk full errors: `No space left on device`
- Jobs timing out before completion
- Slow processing performance

## Error Examples

```
Pod was OOMKilled - container exceeded memory limit

MemoryError: Unable to allocate array with shape (1000, 361, 720)

OSError: [Errno 28] No space left on device

ERROR: Job exceeded activeDeadlineSeconds (3600s)
```

## Troubleshooting Steps

### Step 1: Identify the Resource Issue

**Check pod status:**
```bash
# Get pod status
kubectl get pods | grep <dataset>

# Describe the pod
kubectl describe pod <pod-name>

# Look for:
# - State: OOMKilled
# - Reason: Evicted
# - Message about resource limits
```

**Check pod resource usage:**
```bash
# Real-time resource monitoring
kubectl top pod <pod-name>

# For all pods
kubectl top pods --sort-by=memory
kubectl top pods --sort-by=cpu
```

**Check node resources:**
```bash
# Node resource usage
kubectl top nodes

# Node capacity
kubectl describe node <node-name> | grep -A 5 "Allocated resources"
```

### Step 2: Determine Resource Limits

```bash
# Check current limits
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'

# Should show something like:
# {"limits":{"cpu":"2","memory":"4Gi"},"requests":{"cpu":"1","memory":"2Gi"}}
```

## Common Issues and Solutions

### Issue 1: Out of Memory (OOM)

**Symptoms:**
- Pods killed with `OOMKilled` status
- Python `MemoryError`
- Processing stops partway through

**Root Causes:**
- Loading too much data into memory at once
- Too many regions processed per pod
- Large arrays (high spatial/temporal resolution)
- Memory leaks in processing code

**Solutions:**

**Solution A: Reduce work per pod**
```bash
# Reduce jobs-per-pod (default is often 10)
uv run main <dataset-id> backfill-kubernetes <end-date> \
  --jobs-per-pod 2 \
  --max-parallelism 200
```

**Solution B: Increase pod memory**

Edit dataset config (`src/reformatters/<path>/dynamical_dataset.py`):
```python
class YourDataset(DynamicalDataset):
    def backfill_kubernetes_spec(self, **kwargs) -> BackfillKubernetesSpec:
        return BackfillKubernetesSpec(
            pod_memory="8Gi",  # Increase from default (e.g., 4Gi)
            pod_cpu="2",
            # ...
        )
```

**Solution C: Process fewer variables at once**
```bash
# Process variables in batches
for var in temperature_2m wind_u_10m wind_v_10m; do
  uv run main <dataset-id> backfill-kubernetes <end-date> \
    --filter-variable-names $var
done
```

**Solution D: Optimize data loading**

In `region_job.py`:
```python
def read_data(self, source_file_coord: SourceFileCoord) -> dict[str, np.ndarray]:
    """Read data efficiently."""
    # Load data in chunks instead of all at once
    with xr.open_dataset(file_path, chunks={'time': 1}) as ds:
        # Process chunk by chunk
        return {var: ds[var].values for var in self.data_vars}
```

### Issue 2: Disk Space Exhausted

**Symptoms:**
- `No space left on device`
- Pod evicted due to disk pressure
- Download failures

**Root Causes:**
- Too many source files downloaded
- Temporary Zarr stores not cleaned up
- Insufficient ephemeral storage

**Solutions:**

**Solution A: Increase ephemeral storage**
```python
def backfill_kubernetes_spec(self, **kwargs) -> BackfillKubernetesSpec:
    return BackfillKubernetesSpec(
        pod_ephemeral_storage="50Gi",  # Increase from default
        # ...
    )
```

**Solution B: Clean up temporary files**
```python
def process(self):
    """Process region with cleanup."""
    try:
        # Your processing logic
        self.download_files()
        self.read_and_write()
    finally:
        # Always clean up
        self.cleanup_temp_files()
```

**Solution C: Download files one at a time**
```python
def process_region(self):
    """Process files sequentially to save disk space."""
    for source_coord in self.generate_source_file_coords():
        file_path = self.download_file(source_coord)
        data = self.read_data(source_coord)
        self.write_data(data)
        # Delete immediately after processing
        file_path.unlink()
```

### Issue 3: Job Timeouts

**Symptoms:**
- Jobs exceed `activeDeadlineSeconds`
- Pods terminated before completion

**Root Causes:**
- Too much work per pod
- Slow network downloads
- Insufficient CPU
- Inefficient processing

**Solutions:**

**Solution A: Increase timeout**
```python
def backfill_kubernetes_spec(self, **kwargs) -> BackfillKubernetesSpec:
    return BackfillKubernetesSpec(
        pod_active_deadline=7200,  # Increase to 2 hours
        # ...
    )
```

**Solution B: Increase parallelism**
```bash
# Distribute work across more pods
uv run main <dataset-id> backfill-kubernetes <end-date> \
  --max-parallelism 500 \
  --jobs-per-pod 5
```

**Solution C: Add more CPU**
```python
def backfill_kubernetes_spec(self, **kwargs) -> BackfillKubernetesSpec:
    return BackfillKubernetesSpec(
        pod_cpu="4",  # Increase from default (e.g., 2)
        # ...
    )
```

### Issue 4: CPU Throttling

**Symptoms:**
- Jobs running very slowly
- High CPU wait times
- Processing takes much longer than expected

**Root Causes:**
- CPU limit too low
- Too many pods on one node
- Inefficient compression/decompression

**Solutions:**

**Solution A: Increase CPU allocation**
```python
def backfill_kubernetes_spec(self, **kwargs) -> BackfillKubernetesSpec:
    return BackfillKubernetesSpec(
        pod_cpu="4",
        # ...
    )
```

**Solution B: Use CPU-efficient compression**
```python
# In template_config.py
def get_variable_encoding(self) -> dict:
    return {
        "compressor": {
            "codec": "blosc",
            "cname": "zstd",  # Fast compression
            "clevel": 3,      # Lower compression level = faster
            "shuffle": 1,
        }
    }
```

### Issue 5: Node Resource Exhaustion

**Symptoms:**
- Pods stuck in `Pending` state
- `Insufficient memory/cpu` events
- Pods not scheduled

**Solutions:**

**Solution A: Scale cluster**
```bash
# If using managed Kubernetes (EKS, GKE)
# Increase node count or enable auto-scaling
```

**Solution B: Reduce resource requests**
```python
def backfill_kubernetes_spec(self, **kwargs) -> BackfillKubernetesSpec:
    return BackfillKubernetesSpec(
        pod_memory_request="2Gi",  # Lower than limit
        pod_memory_limit="4Gi",
        # ...
    )
```

## Resource Sizing Guidelines

### Memory Recommendations

| Dataset Size | Variables | Resolution | Recommended Memory |
|--------------|-----------|------------|-------------------|
| Small        | 1-5       | 1°         | 2-4 GiB          |
| Medium       | 5-20      | 0.5°       | 4-8 GiB          |
| Large        | 20-50     | 0.25°      | 8-16 GiB         |
| Very Large   | 50+       | 0.1°       | 16-32 GiB        |

### CPU Recommendations

- **Light processing**: 1 CPU
- **Standard processing**: 2 CPUs
- **Heavy computation**: 4 CPUs
- **Compression-intensive**: 4-8 CPUs

### Disk Space Recommendations

**Ephemeral storage = 2x (largest source file size × files processed per pod)**

Example:
- Source file size: 500 MB
- Files per region: 10
- Ephemeral storage: 2 × (500 MB × 10) = 10 GB

## Monitoring and Prevention

### Set Up Resource Monitoring

```bash
# Install metrics-server if not present
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Monitor continuously
watch kubectl top pods
```

### Add Resource Alerts

```yaml
# Example Prometheus alert
- alert: PodMemoryUsageHigh
  expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
  annotations:
    summary: "Pod {{ $labels.pod }} memory usage is above 90%"
```

### Load Test Before Production

```bash
# Test with a small date range first
uv run main <dataset-id> backfill-kubernetes 2024-01-02 2024-01-03 \
  --jobs-per-pod 10

# Monitor resource usage
kubectl top pods --sort-by=memory

# Adjust parameters based on results
```

## Troubleshooting Checklist

- [ ] Identified resource constraint (memory/CPU/disk)
- [ ] Checked pod resource limits and requests
- [ ] Reviewed logs for memory/disk errors
- [ ] Adjusted `--jobs-per-pod` if needed
- [ ] Increased resource limits in dataset config
- [ ] Tested with smaller workload
- [ ] Verified cluster has sufficient capacity
- [ ] Set up monitoring for future runs

## Related Documentation

- [Backfill Failures Playbook](backfill-failures.md)
- [Architecture Overview](../../architecture/overview.md)
- [Dataset Integration Guide](../../guides/dataset-integration-guide.md)

## Notes

- Start conservative with resource limits and scale up as needed
- Monitor resource usage during first backfill to establish baseline
- Different datasets have very different resource requirements
- Cloud provider costs scale with resource allocation - optimize carefully
