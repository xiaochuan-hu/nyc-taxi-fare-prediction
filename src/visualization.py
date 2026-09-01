"""Generate Week 1 report figures from the cleaned NYC taxi dataset."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "nyc-taxi-fare-matplotlib"),
)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DPI = 320
NYC_LAT_MIN = 40.5
NYC_LAT_MAX = 41.0
NYC_LON_MIN = -74.3
NYC_LON_MAX = -73.7

VISUALIZATION_COLUMNS = [
    "fare_amount",
    "pickup_longitude",
    "pickup_latitude",
    "dropoff_longitude",
    "dropoff_latitude",
    "passenger_count",
]

BLUE = "#356A8A"
TEAL = "#4F8582"
ORANGE = "#B87545"
GRID = "#D9DEE3"
TEXT = "#263238"


def _configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
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
            "grid.color": GRID,
            "grid.linewidth": 0.7,
            "grid.alpha": 0.7,
        }
    )


def discover_cleaned_dataset(project_root: Path) -> Path:
    """Find a processed CSV containing all columns required for the figures."""
    processed_dir = project_root / "data" / "processed"
    if not processed_dir.is_dir():
        raise FileNotFoundError(f"Processed data directory not found: {processed_dir}")

    candidates: list[Path] = []
    required = set(VISUALIZATION_COLUMNS)
    for path in processed_dir.rglob("*.csv"):
        try:
            columns = set(pd.read_csv(path, nrows=0).columns)
        except (OSError, pd.errors.ParserError, UnicodeDecodeError):
            continue
        if required.issubset(columns):
            candidates.append(path)

    if not candidates:
        raise FileNotFoundError(
            f"No cleaned CSV with the required columns was found under {processed_dir}"
        )

    candidates.sort(
        key=lambda path: ("clean" in path.stem.lower(), path.stat().st_size),
        reverse=True,
    )
    return candidates[0]


def load_cleaning_stats(stats_path: Path) -> dict[str, int]:
    """Load and validate exact full-dataset cleaning statistics."""
    if not stats_path.is_file():
        raise FileNotFoundError(
            "Cleaning statistics were not found. Run "
            "`python src/cleaning.py --stats-only` first."
        )

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    required = {
        "input_rows",
        "invalid_fares",
        "invalid_coordinates",
        "outside_nyc",
        "zero_passengers",
        "output_rows",
        "removed_rows",
    }
    missing = required.difference(stats)
    if missing:
        raise ValueError(
            f"Cleaning statistics are missing fields: {', '.join(sorted(missing))}"
        )

    validated = {name: int(stats[name]) for name in required}
    stage_total = sum(
        validated[name]
        for name in (
            "invalid_fares",
            "invalid_coordinates",
            "outside_nyc",
            "zero_passengers",
        )
    )
    if validated["input_rows"] - validated["output_rows"] != stage_total:
        raise ValueError("Cleaning statistics are internally inconsistent")
    if validated["removed_rows"] != stage_total:
        raise ValueError("Cleaning statistics contain an invalid removed_rows total")
    return validated


def load_visualization_data(
    cleaned_path: Path,
    total_rows: int,
    sample_size: int = 500_000,
    chunksize: int = 1_000_000,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.Series]:
    """Collect a reproducible bounded sample and exact passenger frequencies."""
    if sample_size <= 0 or chunksize <= 0:
        raise ValueError("sample_size and chunksize must be greater than zero")
    if total_rows <= 0:
        raise ValueError("total_rows must be greater than zero")

    rng = np.random.default_rng(random_state)
    sampling_probability = min(1.0, (sample_size * 1.25) / total_rows)
    sampled_chunks: list[pd.DataFrame] = []
    passenger_counts = pd.Series(dtype="int64")
    rows_seen = 0

    chunks = pd.read_csv(
        cleaned_path,
        usecols=VISUALIZATION_COLUMNS,
        chunksize=chunksize,
    )
    for chunk_number, chunk in enumerate(chunks, start=1):
        rows_seen += len(chunk)
        counts = chunk["passenger_count"].value_counts(dropna=False)
        passenger_counts = passenger_counts.add(counts, fill_value=0)

        selected = rng.random(len(chunk)) < sampling_probability
        if selected.any():
            sampled_chunks.append(chunk.loc[selected])

        print(
            f"Visualization scan chunk {chunk_number}: "
            f"processed {rows_seen:,} rows",
            flush=True,
        )

    if rows_seen != total_rows:
        raise ValueError(
            f"Cleaned dataset contains {rows_seen:,} rows, but cleaning statistics "
            f"report {total_rows:,}"
        )
    if not sampled_chunks:
        raise ValueError("No rows were sampled from the cleaned dataset")

    sample = pd.concat(sampled_chunks, ignore_index=True)
    if len(sample) > sample_size:
        sample = sample.sample(n=sample_size, random_state=random_state)
    sample = sample.reset_index(drop=True)

    passenger_counts = passenger_counts.astype("int64").sort_index()
    return sample, passenger_counts


def _save_figure(fig: plt.Figure, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=FIGURE_DPI,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)
    print(f"Saved: {output_path}", flush=True)
    return output_path


def plot_fare_distribution(
    sample: pd.DataFrame,
    total_rows: int,
    output_path: Path,
) -> dict[str, float]:
    """Plot the cleaned fare distribution using a bounded display range."""
    fares = sample["fare_amount"].dropna()
    if fares.empty:
        raise ValueError("The cleaned sample contains no fare_amount values")

    percentile_99 = float(fares.quantile(0.99))
    upper_limit = max(20.0, min(100.0, math.ceil(percentile_99 / 5.0) * 5.0))
    displayed = fares[fares <= upper_limit]
    weight = total_rows / len(fares)
    median = float(fares.median())
    mean = float(fares.mean())

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.hist(
        displayed,
        bins=70,
        range=(0, upper_limit),
        weights=np.full(len(displayed), weight),
        color=BLUE,
        edgecolor="white",
        linewidth=0.25,
    )
    ax.axvline(
        median,
        color=ORANGE,
        linewidth=1.8,
        linestyle="--",
        label=f"Median: ${median:.2f}",
    )
    ax.set_title("Fare Amount Distribution After Cleaning", pad=12)
    ax.set_xlabel("Fare Amount (USD)")
    ax.set_ylabel("Number of Trips")
    ax.set_xlim(0, upper_limit)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper right")
    ax.text(
        0.99,
        0.88,
        f"Display range: 0-{upper_limit:.0f} USD (sample p99: {percentile_99:.2f} USD)",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        color="#5F6B73",
    )
    fig.tight_layout()
    _save_figure(fig, output_path)
    return {
        "mean": mean,
        "median": median,
        "percentile_99": percentile_99,
        "display_upper_limit": upper_limit,
    }


def plot_geographic_distribution(
    sample: pd.DataFrame,
    output_path: Path,
    sample_size: int = 100_000,
    random_state: int = 42,
) -> Path:
    """Plot pickup and drop-off density within the NYC cleaning bounds."""
    if sample_size <= 0:
        raise ValueError("sample_size must be greater than zero")
    geo_sample = sample.sample(
        n=min(sample_size, len(sample)),
        random_state=random_state,
    )

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(10.4, 4.7),
        sharex=True,
        sharey=True,
    )
    extent = (NYC_LON_MIN, NYC_LON_MAX, NYC_LAT_MIN, NYC_LAT_MAX)
    plots = []
    for ax, longitude, latitude, panel_title in (
        (
            axes[0],
            "pickup_longitude",
            "pickup_latitude",
            "Pickup Locations",
        ),
        (
            axes[1],
            "dropoff_longitude",
            "dropoff_latitude",
            "Drop-off Locations",
        ),
    ):
        density = ax.hexbin(
            geo_sample[longitude],
            geo_sample[latitude],
            gridsize=80,
            extent=extent,
            mincnt=1,
            cmap="Blues",
            linewidths=0,
        )
        plots.append(density)
        ax.set_title(panel_title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Longitude")
        ax.set_xlim(NYC_LON_MIN, NYC_LON_MAX)
        ax.set_ylim(NYC_LAT_MIN, NYC_LAT_MAX)
        ax.grid(False)

    axes[0].set_ylabel("Latitude")
    maximum_density = max(float(plot.get_array().max()) for plot in plots)
    shared_norm = LogNorm(vmin=1, vmax=max(2, maximum_density))
    for plot in plots:
        plot.set_norm(shared_norm)
    fig.subplots_adjust(left=0.08, right=0.87, bottom=0.13, top=0.86, wspace=0.10)
    colorbar_axis = fig.add_axes((0.90, 0.18, 0.018, 0.64))
    colorbar = fig.colorbar(plots[-1], cax=colorbar_axis)
    colorbar.set_label("Trips per Hexagon")
    fig.suptitle("NYC Taxi Pickup and Drop-off Distribution", y=0.99)
    return _save_figure(fig, output_path)


def plot_cleaning_summary(
    cleaning_stats: dict[str, int],
    output_path: Path,
) -> Path:
    """Plot exact rows removed by each cleaning stage."""
    labels = [
        "Invalid Fare",
        "Invalid\nCoordinates",
        "Outside NYC",
        "Zero\nPassengers",
    ]
    values = [
        cleaning_stats["invalid_fares"],
        cleaning_stats["invalid_coordinates"],
        cleaning_stats["outside_nyc"],
        cleaning_stats["zero_passengers"],
    ]

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    bars = ax.bar(labels, values, color=[BLUE, TEAL, ORANGE, "#708090"], width=0.65)
    ax.set_yscale("log")
    ax.set_title("Rows Removed by Cleaning Rule", pad=12)
    ax.set_ylabel("Rows Removed")
    ax.set_ylim(min(values) * 0.70, max(values) * 1.70)
    ax.grid(axis="y", which="major")
    ax.grid(axis="x", visible=False)
    ax.text(
        0.02,
        0.96,
        "Log scale",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
        color="#5F6B73",
    )
    for bar, value in zip(bars, values, strict=True):
        ax.annotate(
            f"{value:,}",
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.tight_layout()
    return _save_figure(fig, output_path)


def plot_passenger_count_distribution(
    passenger_counts: pd.Series,
    output_path: Path,
) -> dict[str, int]:
    """Plot exact frequencies for reasonable taxi passenger counts."""
    numeric_index = pd.to_numeric(passenger_counts.index, errors="coerce")
    reasonable = passenger_counts[(numeric_index >= 1) & (numeric_index <= 6)].copy()
    reasonable.index = pd.to_numeric(reasonable.index).astype(int)
    reasonable = reasonable.groupby(level=0).sum().sort_index()
    if reasonable.empty:
        raise ValueError("No passenger counts between 1 and 6 were found")

    total = int(passenger_counts.sum())
    plotted_total = int(reasonable.sum())
    excluded_total = total - plotted_total

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    bars = ax.bar(
        reasonable.index.astype(str),
        reasonable.values,
        color=TEAL,
        width=0.68,
    )
    ax.set_title("Passenger Count Distribution After Cleaning", pad=12)
    ax.set_xlabel("Passenger Count")
    ax.set_ylabel("Number of Trips")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, reasonable.values, strict=True):
        percentage = value / total
        ax.annotate(
            f"{percentage:.1%}",
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
        )
    ax.margins(y=0.13)
    fig.tight_layout()
    _save_figure(fig, output_path)
    return {"plotted_rows": plotted_total, "excluded_rows": excluded_total}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Week 1 report figures from cleaned taxi data."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root (default: inferred from this script)",
    )
    parser.add_argument(
        "--cleaned-data",
        type=Path,
        default=None,
        help="Optional cleaned CSV; otherwise discovered under data/processed",
    )
    parser.add_argument(
        "--stats",
        type=Path,
        default=None,
        help="Cleaning statistics JSON (default: reports/cleaning_stats.json)",
    )
    parser.add_argument("--sample-size", type=int, default=500_000)
    parser.add_argument("--geo-sample-size", type=int, default=100_000)
    parser.add_argument("--chunksize", type=int, default=1_000_000)
    parser.add_argument("--random-state", type=int, default=42)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    project_root = args.project_root.resolve()
    figures_dir = project_root / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = (
        args.cleaned_data.resolve()
        if args.cleaned_data is not None
        else discover_cleaned_dataset(project_root)
    )
    if not cleaned_path.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found: {cleaned_path}")

    stats_path = (
        args.stats.resolve()
        if args.stats is not None
        else project_root / "reports" / "cleaning_stats.json"
    )
    cleaning_stats = load_cleaning_stats(stats_path)
    _configure_style()

    print(f"Cleaned dataset: {cleaned_path}")
    print(f"Cleaning statistics: {stats_path}")
    sample, passenger_counts = load_visualization_data(
        cleaned_path=cleaned_path,
        total_rows=cleaning_stats["output_rows"],
        sample_size=args.sample_size,
        chunksize=args.chunksize,
        random_state=args.random_state,
    )
    print(f"Visualization sample: {len(sample):,} rows")

    fare_metrics = plot_fare_distribution(
        sample,
        cleaning_stats["output_rows"],
        figures_dir / "fare_distribution.png",
    )
    plot_geographic_distribution(
        sample,
        figures_dir / "geographic_distribution.png",
        sample_size=args.geo_sample_size,
        random_state=args.random_state,
    )
    plot_cleaning_summary(
        cleaning_stats,
        figures_dir / "cleaning_summary.png",
    )
    passenger_metrics = plot_passenger_count_distribution(
        passenger_counts,
        figures_dir / "passenger_count_distribution.png",
    )

    print(
        "Fare sample metrics: "
        f"mean=${fare_metrics['mean']:.2f}, "
        f"median=${fare_metrics['median']:.2f}, "
        f"p99=${fare_metrics['percentile_99']:.2f}"
    )
    if passenger_metrics["excluded_rows"]:
        print(
            "Passenger-count note: "
            f"{passenger_metrics['excluded_rows']:,} cleaned rows have values "
            "outside the report display range of 1-6."
        )


if __name__ == "__main__":
    main()
