"""
Minimal RegionJob Example

This example shows how to implement a simple RegionJob that:
1. Downloads source files from S3
2. Reads data using xarray
3. Writes to Zarr format
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator
import numpy as np
import xarray as xr
import boto3
from botocore import UNSIGNED
from botocore.client import Config

from reformatters.base.region_job import RegionJob, SourceFileCoord
from reformatters.base.types import Region


class MinimalRegionJob(RegionJob):
    """Minimal region job for processing forecast data."""

    # ============================================================================
    # REQUIRED: Generate Source File Coordinates
    # ============================================================================

    def generate_source_file_coords(self) -> Iterator[SourceFileCoord]:
        """
        List all source files needed for this region.

        Yields:
            SourceFileCoord for each source file to download
        """
        # Get the region we're processing (slice of init_time)
        region = self.region

        # Parse region start and end dates
        # Region format: "init_time:2024-01-01:2024-01-10"
        start_str, end_str = region.split(":")[1:3]
        start_date = datetime.fromisoformat(start_str)
        end_date = datetime.fromisoformat(end_str)

        # Generate one source file coord per day
        current_date = start_date
        while current_date < end_date:
            # Create a coordinate for this date
            yield SourceFileCoord(
                # Coordinates that identify this file
                coord_dict={
                    "date": current_date.strftime("%Y%m%d"),
                },
                # S3 key or URL for the file
                url=f"s3://example-bucket/forecasts/{current_date:%Y/%m/%d}/forecast.grib2",
            )
            current_date += timedelta(days=1)

    # ============================================================================
    # REQUIRED: Download File
    # ============================================================================

    def download_file(self, source_file_coord: SourceFileCoord) -> Path:
        """
        Download a source file.

        Args:
            source_file_coord: The file to download

        Returns:
            Path to downloaded file
        """
        url = source_file_coord.url
        date = source_file_coord.coord_dict["date"]

        # Create local path for temporary storage
        local_path = self.tmp_dir / f"forecast_{date}.grib2"

        # Skip if already downloaded
        if local_path.exists():
            return local_path

        # Parse S3 URL
        # Format: s3://bucket/key
        if url.startswith("s3://"):
            parts = url[5:].split("/", 1)
            bucket = parts[0]
            key = parts[1]

            # Download from S3
            # Use unsigned for public buckets
            s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))

            print(f"Downloading: {url}")
            s3_client.download_file(bucket, key, str(local_path))

        else:
            # For HTTP URLs, use requests
            import requests

            print(f"Downloading: {url}")
            response = requests.get(url)
            response.raise_for_status()

            local_path.write_bytes(response.content)

        return local_path

    # ============================================================================
    # REQUIRED: Read Data
    # ============================================================================

    def read_data(self, source_file_coord: SourceFileCoord) -> dict[str, np.ndarray]:
        """
        Read data from a source file.

        Args:
            source_file_coord: The file to read

        Returns:
            Dictionary mapping variable names to numpy arrays
        """
        # Download file first
        file_path = self.download_file(source_file_coord)

        # Open with xarray
        # Use cfgrib engine for GRIB files
        # Use engine='netcdf4' for NetCDF files
        ds = xr.open_dataset(
            file_path,
            engine="cfgrib",
            backend_kwargs={"indexpath": ""},  # Don't save index file
        )

        # Extract data for requested variables
        result = {}
        for var_name in self.data_vars:
            if var_name == "temperature_2m":
                # Map source variable name to our variable name
                source_var = "t2m"  # Temperature at 2m in source file

                if source_var in ds:
                    data = ds[source_var].values

                    # Ensure correct shape: (lead_time, latitude, longitude)
                    # Might need to transpose or reshape depending on source format
                    result[var_name] = data
                else:
                    raise ValueError(f"Variable {source_var} not found in {file_path}")

        ds.close()

        # Clean up temporary file
        file_path.unlink()

        return result

    # ============================================================================
    # OPTIONAL: Operational Update Jobs
    # ============================================================================

    def operational_update_jobs(self) -> list[Region]:
        """
        Define regions for operational updates.

        Returns:
            List of regions to process for keeping dataset up-to-date
        """
        # Update the last 2 days
        # This handles late-arriving data and corrections
        now = datetime.utcnow()
        start_date = now - timedelta(days=2)
        end_date = now

        return [
            Region(
                region=f"init_time:{start_date.isoformat()}:{end_date.isoformat()}",
                data_vars=self.data_vars,
            )
        ]


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """Test the region job."""
    from reformatters.base.storage import LocalStorageConfig
    from .minimal_template_config import MinimalTemplateConfig

    # Set up configuration
    template_config = MinimalTemplateConfig()
    storage_config = LocalStorageConfig(base_path=Path("./test-output"))

    # Define a region to process
    region = Region(
        region="init_time:2024-01-01:2024-01-03",
        data_vars=["temperature_2m"],
    )

    # Create region job
    job = MinimalRegionJob(
        template_config=template_config,
        region=region,
        primary_storage_config=storage_config,
        replica_storage_configs=[],
        tmp_dir=Path("./tmp"),
    )

    # Process the region
    print("Processing region...")
    job.process()
    print("Done!")

    # Verify output
    output_path = storage_config.base_path / template_config.dataset_id / "dataset.zarr"
    if output_path.exists():
        ds = xr.open_zarr(output_path)
        print(f"\nOutput dataset:\n{ds}")
        print(f"\nTemperature shape: {ds.temperature_2m.shape}")
