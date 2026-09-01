"""Chunk-based cleaning pipeline for the NYC taxi fare dataset."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


NYC_LAT_MIN = 40.5
NYC_LAT_MAX = 41.0
NYC_LON_MIN = -74.3
NYC_LON_MAX = -73.7

REQUIRED_COLUMNS = {
    "fare_amount",
    "pickup_longitude",
    "pickup_latitude",
    "dropoff_longitude",
    "dropoff_latitude",
    "passenger_count",
}


@dataclass
class CleaningStats:
    """Cumulative row counts for each cleaning stage."""

    input_rows: int = 0
    invalid_fares: int = 0
    invalid_coordinates: int = 0
    outside_nyc: int = 0
    zero_passengers: int = 0
    output_rows: int = 0

    @property
    def removed_rows(self) -> int:
        return self.input_rows - self.output_rows

    def add(self, other: CleaningStats) -> None:
        self.input_rows += other.input_rows
        self.invalid_fares += other.invalid_fares
        self.invalid_coordinates += other.invalid_coordinates
        self.outside_nyc += other.outside_nyc
        self.zero_passengers += other.zero_passengers
        self.output_rows += other.output_rows

    def to_dict(self) -> dict[str, int]:
        values = asdict(self)
        values["removed_rows"] = self.removed_rows
        return values


def _validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_columns}")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the cleaning rules defined in the data-cleaning notebook."""
    cleaned, _ = _clean_dataframe_with_stats(df)
    return cleaned


def _clean_dataframe_with_stats(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, CleaningStats]:
    _validate_columns(df)
    stats = CleaningStats(input_rows=len(df))

    valid_fares = df["fare_amount"] > 0
    stats.invalid_fares = int((~valid_fares).sum())
    cleaned = df.loc[valid_fares]

    valid_coordinates = (
        cleaned["pickup_longitude"].between(-180, 180)
        & cleaned["dropoff_longitude"].between(-180, 180)
        & cleaned["pickup_latitude"].between(-90, 90)
        & cleaned["dropoff_latitude"].between(-90, 90)
    )
    stats.invalid_coordinates = int((~valid_coordinates).sum())
    cleaned = cleaned.loc[valid_coordinates]

    nyc_area = (
        cleaned["pickup_latitude"].between(NYC_LAT_MIN, NYC_LAT_MAX)
        & cleaned["pickup_longitude"].between(NYC_LON_MIN, NYC_LON_MAX)
        & cleaned["dropoff_latitude"].between(NYC_LAT_MIN, NYC_LAT_MAX)
        & cleaned["dropoff_longitude"].between(NYC_LON_MIN, NYC_LON_MAX)
    )
    stats.outside_nyc = int((~nyc_area).sum())
    cleaned = cleaned.loc[nyc_area]

    zero_passengers = cleaned["passenger_count"] == 0
    stats.zero_passengers = int(zero_passengers.sum())
    cleaned = cleaned.loc[~zero_passengers]

    stats.output_rows = len(cleaned)
    return cleaned, stats


def clean_csv(
    input_path: str | Path,
    output_path: str | Path,
    chunksize: int = 1_000_000,
) -> CleaningStats:
    """Clean a CSV in chunks and atomically publish the completed output."""
    if chunksize <= 0:
        raise ValueError("chunksize must be greater than zero")

    source = Path(input_path)
    destination = Path(output_path)
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {source}")
    if source.resolve() == destination.resolve():
        raise ValueError("Input and output paths must be different")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = destination.with_suffix(destination.suffix + ".tmp")
    temporary_output.unlink(missing_ok=True)

    totals = CleaningStats()

    try:
        chunks = pd.read_csv(source, chunksize=chunksize)
        for chunk_number, chunk in enumerate(chunks, start=1):
            cleaned_chunk, chunk_stats = _clean_dataframe_with_stats(chunk)
            totals.add(chunk_stats)

            cleaned_chunk.to_csv(
                temporary_output,
                mode="w" if chunk_number == 1 else "a",
                header=chunk_number == 1,
                index=False,
            )

            print(
                f"Chunk {chunk_number}: "
                f"read {chunk_stats.input_rows:,}, "
                f"kept {chunk_stats.output_rows:,}",
                flush=True,
            )

        temporary_output.replace(destination)
    except Exception:
        temporary_output.unlink(missing_ok=True)
        raise

    return totals


def calculate_cleaning_stats(
    input_path: str | Path,
    chunksize: int = 1_000_000,
) -> CleaningStats:
    """Calculate exact cleaning statistics without writing a cleaned dataset."""
    if chunksize <= 0:
        raise ValueError("chunksize must be greater than zero")

    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {source}")

    totals = CleaningStats()
    chunks = pd.read_csv(
        source,
        usecols=sorted(REQUIRED_COLUMNS),
        chunksize=chunksize,
    )
    for chunk_number, chunk in enumerate(chunks, start=1):
        _, chunk_stats = _clean_dataframe_with_stats(chunk)
        totals.add(chunk_stats)
        print(
            f"Statistics chunk {chunk_number}: "
            f"processed {totals.input_rows:,} rows",
            flush=True,
        )

    return totals


def save_cleaning_stats(
    stats: CleaningStats,
    output_path: str | Path,
) -> Path:
    """Save cleaning statistics as an atomically written JSON file."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = destination.with_suffix(destination.suffix + ".tmp")
    temporary_output.write_text(
        json.dumps(stats.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_output.replace(destination)
    return destination


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean the NYC taxi training data in memory-safe chunks."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/train.csv"),
        help="Raw input CSV (default: data/raw/train.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/train_clean.csv"),
        help="Clean output CSV (default: data/processed/train_clean.csv)",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=1_000_000,
        help="Rows read per chunk (default: 1,000,000)",
    )
    parser.add_argument(
        "--stats-output",
        type=Path,
        default=Path("reports/cleaning_stats.json"),
        help="Cleaning statistics JSON (default: reports/cleaning_stats.json)",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Calculate statistics without writing or replacing the cleaned CSV",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    if args.stats_only:
        stats = calculate_cleaning_stats(args.input, args.chunksize)
    else:
        stats = clean_csv(args.input, args.output, args.chunksize)
    stats_path = save_cleaning_stats(stats, args.stats_output)

    print("\nCleaning complete")
    print(f"Input rows: {stats.input_rows:,}")
    print(f"Invalid fares removed: {stats.invalid_fares:,}")
    print(f"Invalid coordinates removed: {stats.invalid_coordinates:,}")
    print(f"Trips outside NYC removed: {stats.outside_nyc:,}")
    print(f"Zero-passenger trips removed: {stats.zero_passengers:,}")
    print(f"Total rows removed: {stats.removed_rows:,}")
    print(f"Output rows: {stats.output_rows:,}")
    print(f"Statistics saved to: {stats_path}")


if __name__ == "__main__":
    main()
