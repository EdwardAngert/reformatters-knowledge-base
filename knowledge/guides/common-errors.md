# Common Errors and Solutions

Quick reference for error messages you might encounter and how to fix them.

## Table of Contents

- [AWS and S3 Errors](#aws-and-s3-errors)
- [Memory and Resource Errors](#memory-and-resource-errors)
- [Python and Import Errors](#python-and-import-errors)
- [Kubernetes Errors](#kubernetes-errors)
- [Data and Processing Errors](#data-and-processing-errors)
- [Zarr and Storage Errors](#zarr-and-storage-errors)

---

## AWS and S3 Errors

### `ClientError: An error occurred (403) when calling the HeadObject operation: Forbidden`

**What it means**: No permission to access S3 bucket

**Quick fix**:
```bash
# Check credentials
aws configure list
aws s3 ls s3://bucket-name/

# For public buckets, use --no-sign-request
aws s3 ls s3://noaa-gfs-bdp-pds/ --no-sign-request
```

**See**: [AWS Credentials Playbook](../playbooks/troubleshooting/aws-credentials-errors.md)

---

### `NoCredentialsError: Unable to locate credentials`

**What it means**: AWS credentials not configured

**Quick fix**:
```bash
# Set up credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

---

### `ClientError: An error occurred (NoSuchBucket)`

**What it means**: S3 bucket doesn't exist or wrong region

**Quick fix**:
```bash
# Verify bucket name
aws s3 ls s3://bucket-name/

# Check region
aws s3api get-bucket-location --bucket bucket-name
```

---

### `EndpointConnectionError: Could not connect to the endpoint URL`

**What it means**: Network issue or wrong S3 endpoint

**Quick fix**:
```bash
# Check internet connectivity
ping s3.amazonaws.com

# Specify region explicitly
aws s3 ls s3://bucket-name/ --region us-east-1
```

---

## Memory and Resource Errors

### `Pod was OOMKilled`

**What it means**: Pod ran out of memory

**Quick fix**:
```bash
# Reduce work per pod
uv run main <dataset-id> backfill-kubernetes <end-date> \
  --jobs-per-pod 5  # Reduce from default (10)

# Or increase memory in dataset config
# Edit src/reformatters/<path>/dynamical_dataset.py
# Set pod_memory="8Gi"
```

**See**: [Memory Issues Playbook](../playbooks/troubleshooting/memory-and-resource-issues.md)

---

### `MemoryError: Unable to allocate array`

**What it means**: Python process ran out of memory

**Quick fix**:
```python
# Load data in chunks instead of all at once
ds = xr.open_dataset(file_path, chunks={'time': 1})

# Or process fewer variables
uv run main <dataset-id> backfill-local <date> \
  --filter-variable-names temperature_2m
```

---

### `OSError: [Errno 28] No space left on device`

**What it means**: Disk is full

**Quick fix**:
```bash
# Check disk usage
df -h

# Clean up temporary files
rm -rf /tmp/*

# Increase ephemeral storage in dataset config
# Set pod_ephemeral_storage="50Gi"
```

---

### `ERROR: Job exceeded activeDeadlineSeconds`

**What it means**: Job timed out

**Quick fix**:
```python
# Increase timeout in dataset config
def backfill_kubernetes_spec(self, **kwargs):
    return BackfillKubernetesSpec(
        pod_active_deadline=7200,  # 2 hours
        # ...
    )
```

---

## Python and Import Errors

### `ModuleNotFoundError: No module named 'reformatters'`

**What it means**: Package not installed

**Quick fix**:
```bash
# Install dependencies
cd reformatters
uv sync

# Verify installation
uv run python -c "import reformatters; print('OK')"
```

---

### `ModuleNotFoundError: No module named 'cfgrib'` or `'xarray'`

**What it means**: Optional dependency not installed

**Quick fix**:
```bash
# Install all dependencies
uv sync --all-extras

# Or install specific package
uv pip install cfgrib
```

---

### `AttributeError: 'NoneType' object has no attribute`

**What it means**: Expected value is None

**Quick fix**:
```python
# Add defensive checks
if value is not None:
    result = value.some_attribute
else:
    raise ValueError("Expected value is None")
```

---

### `TypeError: unsupported operand type(s)`

**What it means**: Type mismatch in operation

**Quick fix**:
```python
# Check and convert types
if isinstance(value, str):
    value = float(value)

# Or use explicit type conversion
result = int(value)
```

---

## Kubernetes Errors

### `Error: pods are not available`

**What it means**: No pods ready to run jobs

**Quick fix**:
```bash
# Check node status
kubectl get nodes

# Check pod status
kubectl get pods -A

# Check for resource constraints
kubectl describe nodes | grep -A 5 "Allocated resources"
```

---

### `Error from server (Forbidden): error when creating "job.yaml"`

**What it means**: Insufficient Kubernetes permissions

**Quick fix**:
```bash
# Check your permissions
kubectl auth can-i create jobs

# Get cluster admin to grant permissions
# Or use correct kubectl context
kubectl config get-contexts
kubectl config use-context <correct-context>
```

---

### `ImagePullBackOff` or `ErrImagePull`

**What it means**: Can't pull Docker image

**Quick fix**:
```bash
# Check image exists
docker pull <image-name>

# Check image registry credentials
kubectl get secrets

# Verify image name in job spec
kubectl describe pod <pod-name>
```

---

### `CrashLoopBackOff`

**What it means**: Container keeps crashing

**Quick fix**:
```bash
# Check logs
kubectl logs <pod-name>

# Check previous container logs
kubectl logs <pod-name> --previous

# Describe pod for events
kubectl describe pod <pod-name>
```

---

## Data and Processing Errors

### `KeyError: 'variable_name'`

**What it means**: Expected variable not found in source data

**Quick fix**:
```bash
# Check what variables are in the file
gdalinfo source-file.grib2

# Or with Python
import xarray as xr
ds = xr.open_dataset('source-file.grib2')
print(list(ds.data_vars))

# Update your variable mapping
```

---

### `ValueError: cannot reshape array`

**What it means**: Array shape mismatch

**Quick fix**:
```python
# Check shapes
print(f"Source shape: {source_array.shape}")
print(f"Expected shape: {expected_shape}")

# Reshape or transpose as needed
reshaped = source_array.reshape(expected_shape)
# or
transposed = source_array.transpose(1, 0, 2, 3)
```

---

### `ValidationError: Dataset is stale`

**What it means**: Data is too old

**Quick fix**:
```bash
# Check update CronJob
kubectl get cronjob <dataset>-update
kubectl logs job/<dataset>-update-<latest>

# Manually trigger update
kubectl create job manual-update --from=cronjob/<dataset>-update
```

**See**: [Validation Failures Playbook](../playbooks/troubleshooting/validation-failures.md)

---

### `ValidationError: Found excessive NaN values`

**What it means**: Too many missing values in data

**Quick fix**:
```bash
# Check if it's an upstream issue
aws s3 cp s3://source-bucket/latest-file .
gdalinfo latest-file

# If upstream issue, wait for reprocessing
# If processing error, re-run update
```

---

## Zarr and Storage Errors

### `zarr.errors.PathNotFoundError`

**What it means**: Zarr store doesn't exist

**Quick fix**:
```bash
# Verify path
aws s3 ls s3://bucket/path/to/dataset.zarr/

# Check if backfill completed
kubectl get jobs | grep <dataset>

# Run backfill if needed
uv run main <dataset-id> backfill-kubernetes <end-date>
```

---

### `zarr.errors.MetadataValidationError`

**What it means**: Zarr metadata is invalid

**Quick fix**:
```bash
# Check metadata file
aws s3 cp s3://bucket/path/dataset.zarr/zarr.json -

# Regenerate if corrupted
uv run main <dataset-id> update-template
```

---

### `ValueError: chunk size exceeds dimension size`

**What it means**: Chunk configuration is invalid

**Quick fix**:
```python
# In template_config.py, adjust chunks
@property
def chunks(self) -> dict[str, int]:
    return {
        "time": 10,      # Reduce if time dimension is small
        "latitude": 100,
        "longitude": 100,
    }
```

---

### `fsspec.exceptions.FSTimeoutError`

**What it means**: S3 operation timed out

**Quick fix**:
```python
# Increase timeout in storage config
import fsspec
fs = fsspec.filesystem(
    's3',
    client_kwargs={'connect_timeout': 60, 'read_timeout': 60}
)
```

---

## Environment and Configuration Errors

### `KeyError: 'DYNAMICAL_ENV'`

**What it means**: Required environment variable not set

**Quick fix**:
```bash
# Set environment
export DYNAMICAL_ENV=prod

# Or for development
export DYNAMICAL_ENV=dev
```

---

### `ValueError: Invalid date format`

**What it means**: Date string in wrong format

**Quick fix**:
```bash
# Use ISO format: YYYY-MM-DD
uv run main <dataset-id> backfill-local 2024-01-15  # Correct

# Not:
# uv run main <dataset-id> backfill-local 01/15/2024  # Wrong
# uv run main <dataset-id> backfill-local 2024-1-15   # Wrong
```

---

### `CommandNotFoundError: uv: command not found`

**What it means**: uv not installed

**Quick fix**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv

# Verify
uv --version
```

---

## Quick Troubleshooting Checklist

When encountering an error:

1. **Read the full error message** - often contains the solution
2. **Check logs** - `kubectl logs <pod-name>` for Kubernetes jobs
3. **Verify environment** - credentials, environment variables, paths
4. **Test with minimal example** - reduce scope to isolate issue
5. **Check recent changes** - did something change in code/config?
6. **Search this knowledge base** - use search tools to find relevant playbooks
7. **Check GitHub issues** - someone may have encountered this before

## Getting Help

If the error persists:

1. Check [Troubleshooting Playbooks](../playbooks/troubleshooting/)
2. Search [GitHub Issues](https://github.com/dynamical/reformatters/issues)
3. Post in [Discussions](https://github.com/dynamical/reformatters/discussions)
4. Include:
   - Full error message
   - What you were trying to do
   - What you've tried already
   - Relevant logs

## Related Documentation

- [FAQ](faq.md)
- [Backfill Failures Playbook](../playbooks/troubleshooting/backfill-failures.md)
- [AWS Credentials Playbook](../playbooks/troubleshooting/aws-credentials-errors.md)
- [Memory Issues Playbook](../playbooks/troubleshooting/memory-and-resource-issues.md)
- [Validation Failures Playbook](../playbooks/troubleshooting/validation-failures.md)
