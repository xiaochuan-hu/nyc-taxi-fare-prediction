"""Full-dataset geographic density analysis for NYC taxi trips."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm

try:
    from .cleaning import NYC_LAT_MAX, NYC_LAT_MIN, NYC_LON_MAX, NYC_LON_MIN
except ImportError:
    from cleaning import NYC_LAT_MAX, NYC_LAT_MIN, NYC_LON_MAX, NYC_LON_MIN


COORDINATE_COLUMNS = [
    "pickup_longitude",
    "pickup_latitude",
    "dropoff_longitude",
    "dropoff_latitude",
]

BLUE = "#356A8A"
ORANGE = "#B87545"
GRID = "#D9DEE3"
TEXT = "#263238"


def compute_geographic_density(
    input_path: str | Path,
    grid_size: int = 250,
    chunksize: int = 1_000_000,
    lon_range: tuple[float, float] = (NYC_LON_MIN, NYC_LON_MAX),
    lat_range: tuple[float, float] = (NYC_LAT_MIN, NYC_LAT_MAX),
) -> dict[str, np.ndarray | int]:
    """Aggregate pickup and drop-off coordinates into shared spatial grids."""

    if grid_size <= 0:
        raise ValueError("grid_size must be greater than zero")
    if chunksize <= 0:
        raise ValueError("chunksize must be greater than zero")
    if lon_range[0] >= lon_range[1] or lat_range[0] >= lat_range[1]:
        raise ValueError("Geographic ranges must have increasing bounds")

    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"Feature dataset not found: {source}")

    lon_edges = np.linspace(lon_range[0], lon_range[1], grid_size + 1)
    lat_edges = np.linspace(lat_range[0], lat_range[1], grid_size + 1)
    pickup_density = np.zeros((grid_size, grid_size), dtype=np.int64)
    dropoff_density = np.zeros((grid_size, grid_size), dtype=np.int64)

    total_rows = 0
    pickup_missing = 0
    dropoff_missing = 0
    pickup_outside = 0
    dropoff_outside = 0

    chunks = pd.read_csv(
        source,
        usecols=COORDINATE_COLUMNS,
        chunksize=chunksize,
    )

    for chunk_number, chunk in enumerate(chunks, start=1):
        pickup_lon = chunk["pickup_longitude"].to_numpy(dtype=np.float64)
        pickup_lat = chunk["pickup_latitude"].to_numpy(dtype=np.float64)
        dropoff_lon = chunk["dropoff_longitude"].to_numpy(dtype=np.float64)
        dropoff_lat = chunk["dropoff_latitude"].to_numpy(dtype=np.float64)

        pickup_finite = np.isfinite(pickup_lon) & np.isfinite(pickup_lat)
        dropoff_finite = np.isfinite(dropoff_lon) & np.isfinite(dropoff_lat)

        pickup_inside = (
            pickup_finite
            & (pickup_lon >= lon_range[0])
            & (pickup_lon <= lon_range[1])
            & (pickup_lat >= lat_range[0])
            & (pickup_lat <= lat_range[1])
        )
        dropoff_inside = (
            dropoff_finite
            & (dropoff_lon >= lon_range[0])
            & (dropoff_lon <= lon_range[1])
            & (dropoff_lat >= lat_range[0])
            & (dropoff_lat <= lat_range[1])
        )

        pickup_missing += int((~pickup_finite).sum())
        dropoff_missing += int((~dropoff_finite).sum())
        pickup_outside += int((pickup_finite & ~pickup_inside).sum())
        dropoff_outside += int((dropoff_finite & ~dropoff_inside).sum())

        pickup_chunk, _, _ = np.histogram2d(
            pickup_lon[pickup_inside],
            pickup_lat[pickup_inside],
            bins=(lon_edges, lat_edges),
        )
        dropoff_chunk, _, _ = np.histogram2d(
            dropoff_lon[dropoff_inside],
            dropoff_lat[dropoff_inside],
            bins=(lon_edges, lat_edges),
        )

        pickup_density += pickup_chunk.astype(np.int64)
        dropoff_density += dropoff_chunk.astype(np.int64)
        total_rows += len(chunk)

        print(
            f"Geographic chunk {chunk_number}: "
            f"processed {total_rows:,} rows",
            flush=True,
        )

    return {
        "pickup_density": pickup_density,
        "dropoff_density": dropoff_density,
        "lon_edges": lon_edges,
        "lat_edges": lat_edges,
        "total_rows": total_rows,
        "pickup_missing": pickup_missing,
        "dropoff_missing": dropoff_missing,
        "pickup_outside": pickup_outside,
        "dropoff_outside": dropoff_outside,
    }


def validate_density_grids(
    density_data: dict[str, np.ndarray | int],
    expected_rows: int | None = None,
) -> dict[str, int]:
    """Validate grid totals against the scanned full-dataset row count."""

    pickup_density = np.asarray(density_data["pickup_density"])
    dropoff_density = np.asarray(density_data["dropoff_density"])
    total_rows = int(density_data["total_rows"])
    pickup_total = int(pickup_density.sum())
    dropoff_total = int(dropoff_density.sum())
    pickup_difference = pickup_total - total_rows
    dropoff_difference = dropoff_total - total_rows

    validation = {
        "total_rows": total_rows,
        "pickup_total": pickup_total,
        "dropoff_total": dropoff_total,
        "pickup_difference": pickup_difference,
        "dropoff_difference": dropoff_difference,
        "pickup_missing": int(density_data.get("pickup_missing", 0)),
        "dropoff_missing": int(density_data.get("dropoff_missing", 0)),
        "pickup_outside": int(density_data.get("pickup_outside", 0)),
        "dropoff_outside": int(density_data.get("dropoff_outside", 0)),
    }

    if expected_rows is not None and total_rows != expected_rows:
        raise ValueError(
            f"Scanned {total_rows:,} rows; expected {expected_rows:,}"
        )
    if pickup_difference or dropoff_difference:
        raise ValueError(f"Geographic grid validation failed: {validation}")
    if any(
        validation[name]
        for name in (
            "pickup_missing",
            "dropoff_missing",
            "pickup_outside",
            "dropoff_outside",
        )
    ):
        raise ValueError(f"Coordinate validation failed: {validation}")

    return validation


def save_density_grids(
    output_path: str | Path,
    density_data: dict[str, np.ndarray | int],
) -> Path:
    """Atomically save density grids, edges, and validation metadata."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = destination.with_suffix(destination.suffix + ".tmp")

    with temporary_output.open("wb") as handle:
        np.savez_compressed(
            handle,
            pickup_density=density_data["pickup_density"],
            dropoff_density=density_data["dropoff_density"],
            lon_edges=density_data["lon_edges"],
            lat_edges=density_data["lat_edges"],
            total_rows=int(density_data["total_rows"]),
            pickup_missing=int(density_data.get("pickup_missing", 0)),
            dropoff_missing=int(density_data.get("dropoff_missing", 0)),
            pickup_outside=int(density_data.get("pickup_outside", 0)),
            dropoff_outside=int(density_data.get("dropoff_outside", 0)),
        )

    temporary_output.replace(destination)
    return destination


def load_density_grids(input_path: str | Path) -> dict[str, np.ndarray | int]:
    """Load previously saved density grids and metadata."""

    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"Density grid cache not found: {source}")

    with np.load(source) as data:
        return {
            "pickup_density": data["pickup_density"],
            "dropoff_density": data["dropoff_density"],
            "lon_edges": data["lon_edges"],
            "lat_edges": data["lat_edges"],
            "total_rows": int(data["total_rows"]),
            "pickup_missing": int(data["pickup_missing"]),
            "dropoff_missing": int(data["dropoff_missing"]),
            "pickup_outside": int(data["pickup_outside"]),
            "dropoff_outside": int(data["dropoff_outside"]),
        }


def compute_spatial_correlation(
    pickup_density: np.ndarray,
    dropoff_density: np.ndarray,
) -> float:
    """Calculate grid-level Pearson correlation between two density maps."""

    if pickup_density.shape != dropoff_density.shape:
        raise ValueError("Pickup and drop-off grids must have matching shapes")
    return float(
        np.corrcoef(
            pickup_density.ravel(),
            dropoff_density.ravel(),
        )[0, 1]
    )


def compute_concentration(
    density: np.ndarray,
    percentages: tuple[float, ...] = (0.01, 0.05, 0.10),
) -> dict[float, float]:
    """Return trip shares contained in the densest grid-cell percentages."""

    flat_density = np.asarray(density, dtype=np.int64).ravel()
    total = int(flat_density.sum())
    if total <= 0:
        raise ValueError("Density grid must contain at least one trip")

    sorted_counts = np.sort(flat_density)[::-1]
    concentration: dict[float, float] = {}
    for percentage in percentages:
        if not 0 < percentage <= 1:
            raise ValueError("Concentration percentages must be in (0, 1]")
        cell_count = max(1, int(np.ceil(len(sorted_counts) * percentage)))
        concentration[percentage] = float(
            sorted_counts[:cell_count].sum() / total
        )
    return concentration


def extract_hotspots(
    density: np.ndarray,
    lon_edges: np.ndarray,
    lat_edges: np.ndarray,
    location_type: str,
    top_n: int = 5,
) -> pd.DataFrame:
    """Extract centers and counts for the densest individual grid cells."""

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")
    if density.shape != (len(lon_edges) - 1, len(lat_edges) - 1):
        raise ValueError("Density shape does not match the supplied grid edges")

    flat_density = density.ravel()
    top_n = min(top_n, len(flat_density))
    candidate_indices = np.argpartition(flat_density, -top_n)[-top_n:]
    ordered_indices = candidate_indices[
        np.argsort(flat_density[candidate_indices])[::-1]
    ]
    lon_centers = (lon_edges[:-1] + lon_edges[1:]) / 2
    lat_centers = (lat_edges[:-1] + lat_edges[1:]) / 2

    rows = []
    for rank, flat_index in enumerate(ordered_indices, start=1):
        lon_index, lat_index = np.unravel_index(flat_index, density.shape)
        rows.append(
            {
                "type": location_type,
                "rank": rank,
                "longitude": float(lon_centers[lon_index]),
                "latitude": float(lat_centers[lat_index]),
                "trip_count": int(density[lon_index, lat_index]),
            }
        )
    return pd.DataFrame(rows)


def save_hotspots(
    output_path: str | Path,
    pickup_density: np.ndarray,
    dropoff_density: np.ndarray,
    lon_edges: np.ndarray,
    lat_edges: np.ndarray,
    top_n: int = 5,
) -> pd.DataFrame:
    """Extract and atomically save pickup and drop-off hotspots."""

    hotspots = pd.concat(
        [
            extract_hotspots(
                pickup_density,
                lon_edges,
                lat_edges,
                "pickup",
                top_n,
            ),
            extract_hotspots(
                dropoff_density,
                lon_edges,
                lat_edges,
                "dropoff",
                top_n,
            ),
        ],
        ignore_index=True,
    )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = destination.with_suffix(destination.suffix + ".tmp")
    hotspots.to_csv(temporary_output, index=False, float_format="%.4f")
    temporary_output.replace(destination)
    return hotspots


def _configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.edgecolor": "#AAB2B9",
            "axes.labelcolor": TEXT,
            "xtick.color": TEXT,
            "ytick.color": TEXT,
            "text.color": TEXT,
        }
    )


def _geographic_aspect(lat_edges: np.ndarray) -> float:
    mean_latitude = float((lat_edges[0] + lat_edges[-1]) / 2)
    return float(1 / np.cos(np.deg2rad(mean_latitude)))


def create_density_norm(
    pickup_density: np.ndarray,
    dropoff_density: np.ndarray,
) -> LogNorm:
    maximum = int(max(pickup_density.max(), dropoff_density.max()))
    if maximum < 1:
        raise ValueError("Density grids do not contain any trips")
    return LogNorm(vmin=1, vmax=maximum)


def plot_density(
    density: np.ndarray,
    lon_edges: np.ndarray,
    lat_edges: np.ndarray,
    title: str,
    output_path: str | Path,
    norm: LogNorm,
) -> plt.Figure:
    """Plot and save one geographic density grid."""

    _configure_style()
    fig, ax = plt.subplots(figsize=(8.5, 7.0))
    image = ax.pcolormesh(
        lon_edges,
        lat_edges,
        density.T,
        cmap="viridis",
        norm=norm,
        shading="auto",
        rasterized=True,
    )
    ax.set_title(title, pad=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(lon_edges[0], lon_edges[-1])
    ax.set_ylim(lat_edges[0], lat_edges[-1])
    ax.set_aspect(_geographic_aspect(lat_edges))
    colorbar = fig.colorbar(image, ax=ax, pad=0.025)
    colorbar.set_label("Trip Density (log scale)")
    fig.tight_layout()

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=320, bbox_inches="tight", facecolor="white")
    return fig


def plot_density_comparison(
    pickup_density: np.ndarray,
    dropoff_density: np.ndarray,
    lon_edges: np.ndarray,
    lat_edges: np.ndarray,
    output_path: str | Path,
    norm: LogNorm,
) -> plt.Figure:
    """Plot pickup and drop-off density with a shared geographic scale."""

    _configure_style()
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(13.0, 6.2),
        sharex=True,
        sharey=True,
    )
    image = None
    for ax, density, title in (
        (axes[0], pickup_density, "Pickup Density"),
        (axes[1], dropoff_density, "Drop-off Density"),
    ):
        image = ax.pcolormesh(
            lon_edges,
            lat_edges,
            density.T,
            cmap="viridis",
            norm=norm,
            shading="auto",
            rasterized=True,
        )
        ax.set_title(title, pad=10)
        ax.set_xlabel("Longitude")
        ax.set_xlim(lon_edges[0], lon_edges[-1])
        ax.set_ylim(lat_edges[0], lat_edges[-1])
        ax.set_aspect(_geographic_aspect(lat_edges))

    axes[0].set_ylabel("Latitude")
    fig.suptitle(
        "NYC Taxi Pickup and Drop-off Density",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )
    colorbar = fig.colorbar(
        image,
        ax=axes,
        pad=0.025,
        shrink=0.88,
    )
    colorbar.set_label("Trip Density (log scale)")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=320, bbox_inches="tight", facecolor="white")
    return fig


def generate_density_figures(
    density_data: dict[str, np.ndarray | int],
    output_dir: str | Path,
) -> list[Path]:
    """Generate the three required comparable geographic density figures."""

    output_directory = Path(output_dir)
    pickup_density = np.asarray(density_data["pickup_density"])
    dropoff_density = np.asarray(density_data["dropoff_density"])
    lon_edges = np.asarray(density_data["lon_edges"])
    lat_edges = np.asarray(density_data["lat_edges"])
    norm = create_density_norm(pickup_density, dropoff_density)

    pickup_path = output_directory / "pickup_trip_density.png"
    dropoff_path = output_directory / "dropoff_trip_density.png"
    comparison_path = output_directory / "pickup_dropoff_density_comparison.png"

    figures = [
        plot_density(
            pickup_density,
            lon_edges,
            lat_edges,
            "NYC Taxi Pickup Density",
            pickup_path,
            norm,
        ),
        plot_density(
            dropoff_density,
            lon_edges,
            lat_edges,
            "NYC Taxi Drop-off Density",
            dropoff_path,
            norm,
        ),
        plot_density_comparison(
            pickup_density,
            dropoff_density,
            lon_edges,
            lat_edges,
            comparison_path,
            norm,
        ),
    ]
    for figure in figures:
        plt.close(figure)

    return [pickup_path, dropoff_path, comparison_path]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate and plot full-dataset NYC taxi density."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/train_features.csv"),
    )
    parser.add_argument(
        "--density-output",
        type=Path,
        default=Path("reports/geographic_density.npz"),
    )
    parser.add_argument(
        "--hotspots-output",
        type=Path,
        default=Path("reports/geographic_hotspots.csv"),
    )
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=Path("reports/figures/week2"),
    )
    parser.add_argument("--grid-size", type=int, default=250)
    parser.add_argument("--chunksize", type=int, default=1_000_000)
    parser.add_argument("--expected-rows", type=int, default=54_004_358)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    density_data = compute_geographic_density(
        args.input,
        grid_size=args.grid_size,
        chunksize=args.chunksize,
    )
    validation = validate_density_grids(density_data, args.expected_rows)
    save_density_grids(args.density_output, density_data)
    hotspots = save_hotspots(
        args.hotspots_output,
        np.asarray(density_data["pickup_density"]),
        np.asarray(density_data["dropoff_density"]),
        np.asarray(density_data["lon_edges"]),
        np.asarray(density_data["lat_edges"]),
    )
    figure_paths = generate_density_figures(density_data, args.figure_dir)

    pickup_density = np.asarray(density_data["pickup_density"])
    dropoff_density = np.asarray(density_data["dropoff_density"])
    spatial_correlation = compute_spatial_correlation(
        pickup_density,
        dropoff_density,
    )
    pickup_concentration = compute_concentration(pickup_density)
    dropoff_concentration = compute_concentration(dropoff_density)

    print("\nGeographic aggregation complete")
    print(f"Full dataset rows: {validation['total_rows']:,}")
    print(f"Pickup grid total: {validation['pickup_total']:,}")
    print(f"Drop-off grid total: {validation['dropoff_total']:,}")
    print(f"Pickup difference: {validation['pickup_difference']:,}")
    print(f"Drop-off difference: {validation['dropoff_difference']:,}")
    print(f"Grid resolution: {pickup_density.shape[0]} x {pickup_density.shape[1]}")
    print(f"Longitude range: [{NYC_LON_MIN}, {NYC_LON_MAX}]")
    print(f"Latitude range: [{NYC_LAT_MIN}, {NYC_LAT_MAX}]")
    print(f"Pickup-dropoff spatial density correlation: {spatial_correlation:.6f}")
    for percentage in (0.01, 0.05, 0.10):
        print(
            f"Top {percentage:.0%} cells: "
            f"pickup={pickup_concentration[percentage]:.2%}, "
            f"drop-off={dropoff_concentration[percentage]:.2%}"
        )
    print("\nHotspots")
    print(hotspots.to_string(index=False))
    print("\nFigures")
    for path in figure_paths:
        print(path)


if __name__ == "__main__":
    main()
