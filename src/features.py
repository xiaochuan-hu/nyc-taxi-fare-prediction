"""Feature engineering pipeline for the NYC taxi fare dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


EARTH_RADIUS_KM = 6371.0088


def haversine_distance(
    pickup_longitude: pd.Series,
    pickup_latitude: pd.Series,
    dropoff_longitude: pd.Series,
    dropoff_latitude: pd.Series,
) -> np.ndarray:
    """Calculate Haversine distance between pickup and drop-off points."""

    pickup_lon = np.radians(pickup_longitude.to_numpy())
    pickup_lat = np.radians(pickup_latitude.to_numpy())
    dropoff_lon = np.radians(dropoff_longitude.to_numpy())
    dropoff_lat = np.radians(dropoff_latitude.to_numpy())

    delta_lon = dropoff_lon - pickup_lon
    delta_lat = dropoff_lat - pickup_lat

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(pickup_lat)
        * np.cos(dropoff_lat)
        * np.sin(delta_lon / 2) ** 2
    )

    a = np.clip(a, 0.0, 1.0)

    c = 2 * np.arcsin(np.sqrt(a))

    return EARTH_RADIUS_KM * c


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features required for EDA and modelling."""

    df = df.copy()

    pickup_datetime = pd.to_datetime(
        df["pickup_datetime"],
        utc=True,
        errors="coerce",
    )

    df["trip_distance"] = haversine_distance(
        df["pickup_longitude"],
        df["pickup_latitude"],
        df["dropoff_longitude"],
        df["dropoff_latitude"],
    )

    df["pickup_hour"] = pickup_datetime.dt.hour
    df["day_of_week"] = pickup_datetime.dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype("int8")

    return df


def process_file(
    input_path: Path,
    output_path: Path,
    chunksize: int = 500_000,
    nrows: int | None = None,
) -> None:
    """Process a large CSV file in chunks."""

    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output files must be different.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        output_path.unlink()

    rows_processed = 0
    first_chunk = True

    reader = pd.read_csv(
        input_path,
        chunksize=chunksize,
        nrows=nrows,
    )

    for chunk_number, chunk in enumerate(reader, start=1):

        featured_chunk = add_features(chunk)

        featured_chunk.to_csv(
            output_path,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )

        rows_processed += len(featured_chunk)
        first_chunk = False

        print(
            f"Chunk {chunk_number}: "
            f"{len(featured_chunk):,} rows processed "
            f"(total: {rows_processed:,})"
        )

    print("\nFeature engineering complete.")
    print(f"Total rows processed: {rows_processed:,}")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Feature engineering for NYC taxi fare data."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to cleaned input CSV.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output CSV.",
    )

    parser.add_argument(
        "--chunksize",
        type=int,
        default=500_000,
        help="Number of rows processed per chunk.",
    )

    parser.add_argument(
        "--nrows",
        type=int,
        default=None,
        help="Optional maximum number of rows for testing.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    process_file(
        input_path=args.input,
        output_path=args.output,
        chunksize=args.chunksize,
        nrows=args.nrows,
    )


if __name__ == "__main__":
    main()
