# CLI Cheatsheet

Quick reference for common reformatters CLI commands.

## Table of Contents

- [Setup and Installation](#setup-and-installation)
- [Dataset Management](#dataset-management)
- [Local Development](#local-development)
- [Kubernetes Operations](#kubernetes-operations)
- [Validation](#validation)
- [Debugging](#debugging)
- [AWS/S3 Operations](#awss3-operations)

---

## Setup and Installation

### Install reformatters
```bash
git clone https://github.com/dynamical/reformatters.git
cd reformatters
uv sync
```

### Update dependencies
```bash
uv sync --upgrade
```

### Install with optional dependencies
```bash
uv sync --all-extras
```

---

## Dataset Management

### List all datasets
```bash
uv run main --help
```

### Initialize new dataset
```bash
uv run main initialize-new-integration <provider> <model> <variant>

# Example
uv run main initialize-new-integration noaa hrrr analysis
```

### Generate template
```bash
uv run main <dataset-id> update-template

# Example
uv run main noaa-gfs-forecast update-template
```

### Commit template
```bash
git add src/reformatters/<provider>/<model>/<variant>/templates/
git commit -m "Add template for <dataset-id>"
```

---

## Local Development

### Test with one date
```bash
uv run main <dataset-id> backfill-local <date>

# Example
uv run main noaa-gfs-forecast backfill-local 2024-01-15
```

### Test with date range
```bash
uv run main <dataset-id> backfill-local <end-date> \
  --start-date <start-date>

# Example (if supported)
uv run main noaa-gfs-forecast backfill-local 2024-01-20 \
  --start-date 2024-01-15
```

### Test single variable
```bash
uv run main <dataset-id> backfill-local <date> \
  --filter-variable-names <variable>

# Example
uv run main noaa-gfs-forecast backfill-local 2024-01-15 \
  --filter-variable-names temperature_2m
```

### Test multiple variables
```bash
uv run main <dataset-id> backfill-local <date> \
  --filter-variable-names temperature_2m wind_u_10m wind_v_10m
```

---

## Kubernetes Operations

### Small test backfill
```bash
uv run main <dataset-id> backfill-kubernetes <end-date> \
  --max-parallelism 5 \
  --jobs-per-pod 5

# Example
uv run main noaa-gfs-forecast backfill-kubernetes 2024-01-02 \
  --max-parallelism 5 \
  --jobs-per-pod 5
```

### Production backfill
```bash
export DYNAMICAL_ENV=prod

uv run main <dataset-id> backfill-kubernetes <end-date> \
  --max-parallelism 100 \
  --jobs-per-pod 10

# Example
DYNAMICAL_ENV=prod uv run main noaa-gfs-forecast backfill-kubernetes 2024-12-31 \
  --max-parallelism 100 \
  --jobs-per-pod 10
```

### Backfill with specific variables
```bash
uv run main <dataset-id> backfill-kubernetes <end-date> \
  --filter-variable-names temperature_2m \
  --max-parallelism 50
```

### Monitor Kubernetes jobs
```bash
# Watch all jobs
kubectl get jobs -w

# Get jobs for specific dataset
kubectl get jobs | grep <dataset-id>

# Watch pods
kubectl get pods -w

# Get pods for specific job
kubectl get pods --selector=job-name=<job-name>
```

### View logs
```bash
# Logs from specific pod
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>

# Logs from previous container (if crashed)
kubectl logs <pod-name> --previous

# Logs from all pods in a job
kubectl logs -l job-name=<job-name>
```

### Delete resources
```bash
# Delete specific job
kubectl delete job <job-name>

# Delete all completed jobs for dataset
kubectl delete jobs -l dataset=<dataset-id>,status=completed

# Delete failed pods
kubectl delete pods --field-selector=status.phase=Failed
```

---

## Validation

### Run all validators
```bash
JOB_NAME=test uv run main <dataset-id> validate

# Example
JOB_NAME=test uv run main noaa-gfs-forecast validate
```

### Production validation
```bash
DYNAMICAL_ENV=prod JOB_NAME=validation-$(date +%s) \
  uv run main <dataset-id> validate
```

---

## Debugging

### Check dataset info
```bash
# Via Python
uv run python -c "
from reformatters.__main__ import DYNAMICAL_DATASETS
for ds in DYNAMICAL_DATASETS:
    if ds.dataset_id == '<dataset-id>':
        print(ds.template_config.dataset_attributes)
"
```

### Test import
```bash
uv run python -c "
from reformatters.<provider>.<model>.<variant> import <ClassName>
print('Import successful')
"
```

### Run tests
```bash
# All tests
uv run pytest

# Specific dataset tests
uv run pytest tests/<provider>/<model>/<variant>/

# Specific test file
uv run pytest tests/<provider>/<model>/<variant>/template_config_test.py

# With verbose output
uv run pytest -v

# With print statements
uv run pytest -s
```

### Check Python version
```bash
uv run python --version
```

### Check installed packages
```bash
uv pip list
```

---

## AWS/S3 Operations

### Configure AWS credentials
```bash
aws configure
```

### List bucket contents
```bash
# Public bucket (no credentials needed)
aws s3 ls s3://noaa-gfs-bdp-pds/ --no-sign-request

# Private bucket
aws s3 ls s3://your-bucket/

# List with prefix
aws s3 ls s3://your-bucket/path/to/files/
```

### Download file
```bash
# Public file
aws s3 cp s3://noaa-gfs-bdp-pds/path/to/file . --no-sign-request

# Private file
aws s3 cp s3://your-bucket/path/to/file .
```

### Upload file
```bash
aws s3 cp local-file.txt s3://your-bucket/path/to/
```

### Sync directory
```bash
# Upload directory
aws s3 sync ./local-dir s3://your-bucket/remote-dir/

# Download directory
aws s3 sync s3://your-bucket/remote-dir/ ./local-dir
```

### Check file metadata
```bash
aws s3api head-object \
  --bucket your-bucket \
  --key path/to/file
```

### Test credentials
```bash
# Check who you are
aws sts get-caller-identity

# Test bucket access
aws s3 ls s3://your-bucket/ || echo "Access denied"
```

---

## Kubernetes Secrets

### Create secret from literals
```bash
kubectl create secret generic <dataset>-aws-credentials \
  --from-literal=AWS_ACCESS_KEY_ID="your-key" \
  --from-literal=AWS_SECRET_ACCESS_KEY="your-secret"
```

### Create secret from file
```bash
# Create env file
cat > aws-creds.env << EOF
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
EOF

# Create secret
kubectl create secret generic <dataset>-aws-credentials \
  --from-env-file=aws-creds.env

# Clean up
rm aws-creds.env
```

### View secret
```bash
kubectl get secret <dataset>-aws-credentials -o yaml
```

### Delete secret
```bash
kubectl delete secret <dataset>-aws-credentials
```

---

## Resource Monitoring

### Pod resource usage
```bash
# Current usage
kubectl top pods

# Sort by memory
kubectl top pods --sort-by=memory

# Sort by CPU
kubectl top pods --sort-by=cpu

# Specific pod
kubectl top pod <pod-name>
```

### Node resource usage
```bash
# All nodes
kubectl top nodes

# Node details
kubectl describe node <node-name>
```

### Check pod status
```bash
# Get pod details
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check pod resource limits
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'
```

---

## CronJobs

### List CronJobs
```bash
kubectl get cronjobs
```

### Describe CronJob
```bash
kubectl describe cronjob <dataset>-update
```

### Suspend CronJob
```bash
kubectl patch cronjob <dataset>-update -p '{"spec":{"suspend":true}}'
```

### Resume CronJob
```bash
kubectl patch cronjob <dataset>-update -p '{"spec":{"suspend":false}}'
```

### Manually trigger CronJob
```bash
kubectl create job <job-name> --from=cronjob/<cronjob-name>

# Example
kubectl create job manual-update --from=cronjob/noaa-gfs-forecast-update
```

### Delete CronJob
```bash
kubectl delete cronjob <dataset>-update
```

---

## Data Inspection

### Inspect Zarr metadata
```bash
# Download and view
aws s3 cp s3://bucket/path/dataset.zarr/zarr.json -

# Pretty print
aws s3 cp s3://bucket/path/dataset.zarr/zarr.json - | python -m json.tool
```

### Inspect variable metadata
```bash
aws s3 cp s3://bucket/path/dataset.zarr/<variable>/zarr.json - | python -m json.tool
```

### Check GRIB file info
```bash
# Using gdalinfo
gdalinfo file.grib2

# Using wgrib2 (if installed)
wgrib2 file.grib2

# List variables
gdalinfo file.grib2 | grep "SUBDATASET"
```

### Quick data check with Python
```bash
uv run python << 'EOF'
import xarray as xr
import zarr

# Open dataset
store = zarr.storage.FSStore('s3://bucket/path/dataset.zarr')
ds = xr.open_zarr(store)

# Print info
print(ds)
print(f"\nTime range: {ds.init_time[0].values} to {ds.init_time[-1].values}")
print(f"Variables: {list(ds.data_vars)}")

# Check for NaNs
for var in ds.data_vars:
    nan_pct = ds[var].isnull().sum() / ds[var].size * 100
    print(f"{var}: {nan_pct:.2f}% NaN")
EOF
```

---

## Git Operations

### Create feature branch
```bash
git checkout -b feature/<dataset-name>
```

### Commit changes
```bash
git add src/reformatters/<provider>/<model>/<variant>/
git commit -m "Add <dataset-id> dataset"
```

### Push branch
```bash
git push -u origin feature/<dataset-name>
```

### Create pull request
```bash
# Using GitHub CLI
gh pr create --title "Add <dataset-id>" --body "Description here"
```

---

## Common Workflows

### Complete dataset addition workflow
```bash
# 1. Initialize
uv run main initialize-new-integration <provider> <model> <variant>

# 2. Implement classes
# (Edit template_config.py, region_job.py, dynamical_dataset.py)

# 3. Register dataset
# (Edit __main__.py)

# 4. Generate template
uv run main <dataset-id> update-template

# 5. Test locally
uv run main <dataset-id> backfill-local 2024-01-01 \
  --filter-variable-names <variable>

# 6. Run tests
uv run pytest tests/<provider>/<model>/<variant>/

# 7. Test on Kubernetes (small range)
uv run main <dataset-id> backfill-kubernetes 2024-01-02 \
  --max-parallelism 5

# 8. Validate
JOB_NAME=test uv run main <dataset-id> validate

# 9. Commit
git add .
git commit -m "Add <dataset-id>"
git push
```

### Quick troubleshooting workflow
```bash
# 1. Check job status
kubectl get jobs | grep <dataset>

# 2. Find failed pods
kubectl get pods | grep Error

# 3. Check logs
kubectl logs <failed-pod>

# 4. Describe pod
kubectl describe pod <failed-pod>

# 5. Check recent events
kubectl get events --sort-by='.lastTimestamp' | head -20
```

---

## Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Reformatters shortcuts
alias rf='cd ~/reformatters && uv run main'
alias rftest='uv run pytest'
alias rflocal='uv run main'

# Kubernetes shortcuts
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgj='kubectl get jobs'
alias klogs='kubectl logs'
alias kdesc='kubectl describe'

# Combined
alias rflogs='kubectl logs -l app=reformatters'
```

---

## Environment Variables

Useful environment variables:

```bash
# Set environment
export DYNAMICAL_ENV=prod  # or 'dev', 'staging'

# AWS configuration
export AWS_PROFILE=your-profile
export AWS_DEFAULT_REGION=us-east-1

# Kubernetes context
export KUBECONFIG=~/.kube/config

# Python
export PYTHONUNBUFFERED=1  # Don't buffer stdout
```

---

## Quick Reference

| Task | Command |
|------|---------|
| List datasets | `uv run main --help` |
| Test locally | `uv run main <id> backfill-local <date>` |
| K8s backfill | `uv run main <id> backfill-kubernetes <date>` |
| Validate | `JOB_NAME=test uv run main <id> validate` |
| Watch jobs | `kubectl get jobs -w` |
| Pod logs | `kubectl logs <pod>` |
| Run tests | `uv run pytest` |

---

## Tips and Tricks

1. **Use tab completion**: Most shells support tab completion for kubectl
2. **Set up aliases**: Save time with common commands
3. **Use watch**: `watch kubectl get pods` for live updates
4. **Save frequently used commands**: Create shell scripts for complex workflows
5. **Use stern for logs**: `stern <pod-prefix>` to tail logs from multiple pods

---

## Related Documentation

- [Getting Started Guide](getting-started.md)
- [Dataset Integration Guide](dataset-integration-guide.md)
- [FAQ](faq.md)
- [Common Errors](common-errors.md)
