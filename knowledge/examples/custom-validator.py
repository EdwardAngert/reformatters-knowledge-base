"""
Custom Validator Example

This example shows how to implement custom validators for your dataset.
"""

from datetime import datetime, timedelta
import xarray as xr
from reformatters.base.validators import DataValidator, ValidationError


class ExampleCustomValidators:
    """Custom validators for example dataset."""

    @staticmethod
    def check_temperature_range(ds: xr.Dataset, max_hours_ago: int = 48) -> None:
        """
        Validate that temperature values are within physically reasonable bounds.

        Args:
            ds: The dataset to validate
            max_hours_ago: Only check data from the last N hours

        Raises:
            ValidationError: If validation fails
        """
        # Get recent data only
        recent_cutoff = datetime.utcnow() - timedelta(hours=max_hours_ago)
        recent_data = ds.sel(init_time=slice(recent_cutoff, None))

        # Check temperature_2m variable
        if "temperature_2m" not in recent_data:
            raise ValidationError("Variable 'temperature_2m' not found in dataset")

        temp = recent_data["temperature_2m"]

        # Physical bounds: -100°C to +60°C (173.15K to 333.15K)
        min_temp_k = 173.15
        max_temp_k = 333.15

        # Get min and max values (ignore NaNs)
        actual_min = float(temp.min().values)
        actual_max = float(temp.max().values)

        if actual_min < min_temp_k:
            raise ValidationError(
                f"Temperature below physical minimum: {actual_min:.2f}K "
                f"(expected >= {min_temp_k}K)"
            )

        if actual_max > max_temp_k:
            raise ValidationError(
                f"Temperature above physical maximum: {actual_max:.2f}K "
                f"(expected <= {max_temp_k}K)"
            )

        print(f"✓ Temperature range check passed: {actual_min:.2f}K to {actual_max:.2f}K")

    @staticmethod
    def check_spatial_coverage(ds: xr.Dataset) -> None:
        """
        Validate that data covers the expected spatial domain.

        Args:
            ds: The dataset to validate

        Raises:
            ValidationError: If spatial coverage is incomplete
        """
        # Check latitude coverage
        lat = ds.latitude.values
        expected_lat_min = -90.0
        expected_lat_max = 90.0

        if lat.min() > expected_lat_min or lat.max() < expected_lat_max:
            raise ValidationError(
                f"Incomplete latitude coverage: {lat.min():.1f} to {lat.max():.1f} "
                f"(expected {expected_lat_min} to {expected_lat_max})"
            )

        # Check longitude coverage
        lon = ds.longitude.values
        expected_lon_min = 0.0
        expected_lon_max = 359.0

        if lon.min() > expected_lon_min or lon.max() < expected_lon_max:
            raise ValidationError(
                f"Incomplete longitude coverage: {lon.min():.1f} to {lon.max():.1f} "
                f"(expected {expected_lon_min} to {expected_lon_max})"
            )

        print(f"✓ Spatial coverage check passed")

    @staticmethod
    def check_forecast_lead_times(ds: xr.Dataset) -> None:
        """
        Validate that all expected forecast lead times are present.

        Args:
            ds: The dataset to validate

        Raises:
            ValidationError: If lead times are missing or incorrect
        """
        lead_times = ds.lead_time.values

        # Expected: 0, 6, 12, 18, ..., 120 hours
        expected_lead_times = list(range(0, 121, 6))
        expected_count = len(expected_lead_times)
        actual_count = len(lead_times)

        if actual_count != expected_count:
            raise ValidationError(
                f"Unexpected number of lead times: {actual_count} "
                f"(expected {expected_count})"
            )

        # Check spacing
        lead_time_hours = lead_times / timedelta(hours=1)  # Convert to hours
        spacing = lead_time_hours[1:] - lead_time_hours[:-1]

        if not (spacing == 6).all():
            raise ValidationError(
                f"Irregular lead time spacing detected. Expected 6-hour intervals."
            )

        print(f"✓ Forecast lead times check passed: {actual_count} lead times")

    @staticmethod
    def check_data_freshness_strict(ds: xr.Dataset, max_age_hours: int = 6) -> None:
        """
        Strict data freshness check - requires very recent data.

        Args:
            ds: The dataset to validate
            max_age_hours: Maximum age in hours

        Raises:
            ValidationError: If data is too old
        """
        latest_init = ds.init_time[-1].values
        latest_dt = datetime.fromisoformat(str(latest_init)[:19])

        now = datetime.utcnow()
        age = now - latest_dt
        age_hours = age.total_seconds() / 3600

        if age_hours > max_age_hours:
            raise ValidationError(
                f"Data is too old: latest initialization is {age_hours:.1f} hours ago "
                f"(expected < {max_age_hours} hours). "
                f"Latest: {latest_dt.isoformat()}, Now: {now.isoformat()}"
            )

        print(f"✓ Data freshness check passed: {age_hours:.1f} hours old")

    @staticmethod
    def check_no_all_nan_timesteps(ds: xr.Dataset) -> None:
        """
        Check that no time steps are completely NaN.

        Args:
            ds: The dataset to validate

        Raises:
            ValidationError: If any time step is all NaN
        """
        for var_name in ds.data_vars:
            var = ds[var_name]

            # Check each time step
            for i, init_time in enumerate(ds.init_time):
                time_slice = var.isel(init_time=i)

                # Count NaNs
                total_values = time_slice.size
                nan_count = int(time_slice.isnull().sum().values)

                if nan_count == total_values:
                    raise ValidationError(
                        f"Variable '{var_name}' is all NaN at init_time={init_time.values}"
                    )

        print(f"✓ No all-NaN timesteps check passed")


# ============================================================================
# Integrate with DynamicalDataset
# ============================================================================

"""
To use these custom validators in your DynamicalDataset:

from reformatters.base.dynamical_dataset import DynamicalDataset
from .custom_validator import ExampleCustomValidators

class ExampleDataset(DynamicalDataset):
    def get_custom_validators(self) -> list[DataValidator]:
        return [
            ExampleCustomValidators.check_temperature_range,
            ExampleCustomValidators.check_spatial_coverage,
            ExampleCustomValidators.check_forecast_lead_times,
            ExampleCustomValidators.check_data_freshness_strict,
            ExampleCustomValidators.check_no_all_nan_timesteps,
        ]
"""


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """Test validators on a dataset."""
    import zarr

    # Open dataset
    store = zarr.storage.FSStore("s3://bucket/path/dataset.zarr")
    ds = xr.open_zarr(store)

    # Run validators
    validators = [
        ExampleCustomValidators.check_temperature_range,
        ExampleCustomValidators.check_spatial_coverage,
        ExampleCustomValidators.check_forecast_lead_times,
        ExampleCustomValidators.check_no_all_nan_timesteps,
    ]

    print("Running custom validators...\n")

    for validator in validators:
        try:
            validator(ds)
        except ValidationError as e:
            print(f"❌ Validation failed: {e}\n")
        except Exception as e:
            print(f"❌ Unexpected error: {e}\n")

    print("\nValidation complete!")
