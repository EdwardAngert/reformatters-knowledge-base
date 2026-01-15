"""
Minimal TemplateConfig Example

This example shows the simplest possible TemplateConfig implementation
for a forecast dataset with 2D spatial grids.
"""

from datetime import datetime, timedelta
import numpy as np
from reformatters.base.template_config import TemplateConfig, DatasetAttributes
from reformatters.base.types import CoordDefinition, DataVarDefinition


class MinimalTemplateConfig(TemplateConfig):
    """Minimal forecast dataset template."""

    # ============================================================================
    # REQUIRED: Dataset Metadata
    # ============================================================================

    @property
    def dataset_attributes(self) -> DatasetAttributes:
        """Basic dataset metadata."""
        return DatasetAttributes(
            name="Example Forecast Dataset",
            description="A minimal example of a forecast dataset with temperature.",
            attribution="Example Meteorological Agency",
            spatial_domain="Global",
            spatial_resolution="1° × 1°",
            time_domain="2020-present",
            time_resolution="Daily",
            forecast_domain="0-120 hours",
            forecast_resolution="6 hours",
        )

    # ============================================================================
    # REQUIRED: Dimensions
    # ============================================================================

    @property
    def dims(self) -> list[str]:
        """Dimension names."""
        return ["init_time", "lead_time", "latitude", "longitude"]

    @property
    def append_dim(self) -> str:
        """Which dimension grows over time."""
        return "init_time"

    # ============================================================================
    # REQUIRED: Coordinates
    # ============================================================================

    @property
    def coords(self) -> dict[str, CoordDefinition]:
        """Coordinate definitions."""
        return {
            "init_time": CoordDefinition(
                dims=["init_time"],
                dtype="datetime64[ns]",
                attrs={
                    "long_name": "Forecast initialization time",
                    "description": "Time when forecast was initialized",
                },
            ),
            "lead_time": CoordDefinition(
                dims=["lead_time"],
                dtype="timedelta64[ns]",
                attrs={
                    "long_name": "Forecast lead time",
                    "description": "Time elapsed since initialization",
                },
            ),
            "latitude": CoordDefinition(
                dims=["latitude"],
                dtype="float32",
                attrs={
                    "units": "degrees_north",
                    "long_name": "Latitude",
                },
            ),
            "longitude": CoordDefinition(
                dims=["longitude"],
                dtype="float32",
                attrs={
                    "units": "degrees_east",
                    "long_name": "Longitude",
                },
            ),
        }

    # ============================================================================
    # REQUIRED: Data Variables
    # ============================================================================

    @property
    def data_vars(self) -> dict[str, DataVarDefinition]:
        """Data variable definitions."""
        return {
            "temperature_2m": DataVarDefinition(
                dims=["init_time", "lead_time", "latitude", "longitude"],
                dtype="float32",
                attrs={
                    "long_name": "Temperature at 2 meters",
                    "units": "K",
                    "description": "Air temperature at 2 meters above surface",
                },
            ),
        }

    # ============================================================================
    # REQUIRED: Generate Coordinates
    # ============================================================================

    def dimension_coordinates(
        self, dim: str, append_dim_start: datetime, append_dim_end: datetime
    ) -> np.ndarray:
        """
        Generate coordinate arrays for each dimension.

        Args:
            dim: Dimension name
            append_dim_start: Start of append dimension
            append_dim_end: End of append dimension (exclusive)

        Returns:
            Array of coordinate values
        """
        if dim == "init_time":
            # Daily initializations from start to end
            num_days = (append_dim_end - append_dim_start).days
            return np.array(
                [append_dim_start + timedelta(days=i) for i in range(num_days)],
                dtype="datetime64[ns]",
            )

        elif dim == "lead_time":
            # Forecast lead times: 0, 6, 12, ..., 120 hours
            lead_hours = np.arange(0, 121, 6)
            return lead_hours.astype("timedelta64[h]")

        elif dim == "latitude":
            # Global 1-degree grid: -90 to 90
            return np.arange(-90, 91, 1.0, dtype="float32")

        elif dim == "longitude":
            # Global 1-degree grid: 0 to 359
            return np.arange(0, 360, 1.0, dtype="float32")

        else:
            raise ValueError(f"Unknown dimension: {dim}")

    # ============================================================================
    # OPTIONAL: Chunking Strategy
    # ============================================================================

    @property
    def chunks(self) -> dict[str, int]:
        """
        Chunk sizes for each dimension.

        Optimize for your access patterns:
        - Time series access: larger time chunks
        - Spatial analysis: larger spatial chunks
        - Balanced: moderate sizes for all dimensions
        """
        return {
            "init_time": 10,     # 10 initialization times per chunk
            "lead_time": 21,     # All lead times in one chunk
            "latitude": 181,     # All latitudes in one chunk
            "longitude": 360,    # All longitudes in one chunk
        }

    # ============================================================================
    # OPTIONAL: Sharding Strategy
    # ============================================================================

    @property
    def shards(self) -> dict[str, int] | None:
        """
        Shard sizes (groups of chunks).

        For Zarr v3, sharding reduces number of S3 objects.
        """
        return {
            "init_time": 100,    # 100 chunks (1000 init times) per shard
            "lead_time": 1,
            "latitude": 1,
            "longitude": 1,
        }


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """Generate a template."""
    config = MinimalTemplateConfig()

    # Generate template for a date range
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 10)

    template = config.get_template(start_date, end_date)

    print(f"Template dimensions: {template.dims}")
    print(f"Template coordinates: {list(template.coords.keys())}")
    print(f"Template variables: {list(template.data_vars.keys())}")
    print(f"\nTemplate structure:\n{template}")
