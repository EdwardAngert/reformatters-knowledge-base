# Dataset Integration Guide

Integrate a dataset to reformat into Zarr.

## Overview

Integrating a dataset in dynamical.org `reformatters` is done by subclassing a trio of base classes, customizing their behavior based on the unique characteristics of your dataset.

There are three core base classes to subclass:

1. `TemplateConfig` defines the dataset **structure**
2. `RegionJob` defines the **process** by which a region of that dataset is reformatted: **downloading, reading, rewriting**
3. `DynamicalDataset` brings together a `TemplateConfig` and `RegionJob` and defines the compute resources to operationally update and validate a dataset

### Terminology

- **Provider** - the agency or organization that publishes the source data. e.g. ECMWF
- **Model** - the model or system that produced the data. e.g. GFS
- **Variant** - the specific subset and structure of data from the model. e.g. forecast, analysis, climatology
- **Dataset** - a specific provider-model-variant. e.g. noaa-gfs-forecast

## Integration Steps

### 1. Initialize a New Integration

```bash
uv run main initialize-new-integration <provider> <model> <variant>
```

Provider, model and variant can contain letters, numbers and dashes. Capitalization will be normalized.

This creates files in `src/reformatters/<provider>/<model>/<variant>` and `tests/<provider>/<model>/<variant>`.

### 2. Register Your Dataset

Add an instance of your `DynamicalDataset` subclass to `DYNAMICAL_DATASETS` in `src/reformatters/__main__.py`:

```python
from reformatters.provider.model.variant import ProviderModelVariantDataset

DYNAMICAL_DATASETS = [
    ...,
    ProviderModelVariantDataset(primary_storage_config=SourceCoopDatasetStorageConfig()),
]
```

### 3. Implement `TemplateConfig` Subclass

Work through `src/reformatters/$DATASET_PATH/template_config.py`, setting attributes and methods to describe your dataset structure.

**Tip**: Use an AI/LLM with:
1. Example template config code
2. Output of `gdalinfo <example source data file>`
3. Dataset documentation

Generate and track the template:

```bash
uv run main $DATASET_ID update-template
git add src/reformatters/$DATASET_PATH/templates/latest.zarr
```

Run tests:

```bash
uv run pytest tests/$DATASET_PATH/template_config_test.py
```

### 4. Implement `RegionJob` Subclass

Implement four required methods in `src/reformatters/$DATASET_PATH/region_job.py`:

- `generate_source_file_coords` - List source files to process
- `download_file` - Retrieve and save a source file
- `read_data` - Load data and return numpy arrays
- `operational_update_jobs` - Create update jobs (can skip initially)

Test your implementation:

```bash
uv run pytest tests/$DATASET_PATH/region_job_test.py
```

Run locally:

```bash
uv run main $DATASET_ID backfill-local <append_dim_end> --filter-variable-names <data_var_name>
```

### 5. Implement `DynamicalDataset` Subclass

Implement operational methods in `src/reformatters/$DATASET_PATH/dynamical_dataset.py`.

Create integration tests:

```bash
uv run pytest tests/$DATASET_PATH/dynamical_dataset_test.py
```

### 6. Deployment

**Local Backfill:**
```bash
DYNAMICAL_ENV=prod uv run main $DATASET_ID backfill-local <append-dim-end>
```

**Kubernetes Backfill:**
```bash
DYNAMICAL_ENV=prod uv run main $DATASET_ID backfill-kubernetes <append-dim-end> --max-parallelism N
kubectl get jobs  # Track progress
```

**Operational CronJobs:**
```bash
kubectl get cronjobs  # See scheduled updates
```

## Need Help?

Contact feedback@dynamical.org for deployment support.
