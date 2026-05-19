"""CLI entrypoint for cds-downloader."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .config import (
    DAILY_ACCUMULATED_VARIABLES,
    DAILY_AGGREGATED_VARIABLES,
    DAILY_STATISTICS,
    DEFAULT_ACCUMULATED_TIME,
    DEFAULT_AREA,
    DEFAULT_DATA_FORMAT,
    DEFAULT_DOWNLOAD_FORMAT,
    DEFAULT_OUTPUT_DIR,
    HOURLY_VARIABLES,
)
from .downloader import print_dry_run, run_downloads
from .requests import (
    CommonRequestOptions,
    DailyRequestOptions,
    HourlyRequestOptions,
    all_days,
    build_daily_tasks,
    build_hourly_tasks,
)

AUTH_HELP = (
    "Before downloading, configure your CDS API token in ~/.cdsapirc. "
    "Setup instructions: https://cds.climate.copernicus.eu/how-to-api"
)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--year", type=int, required=True, help="Year to download.")
    parser.add_argument("--months", nargs="+", required=True, help="Months to download, e.g. 10 11 12.")
    parser.add_argument("--days", nargs="+", default=all_days(), help="Days to download. Defaults to 1..31.")
    parser.add_argument(
        "--area",
        nargs=4,
        type=float,
        default=list(DEFAULT_AREA),
        metavar=("NORTH", "WEST", "SOUTH", "EAST"),
        help="Bounding box in CDS order: north west south east.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(DEFAULT_OUTPUT_DIR),
        help="Directory for downloaded files. Defaults to data/.",
    )
    parser.add_argument(
        "--data-format",
        choices=("netcdf", "grib"),
        default=DEFAULT_DATA_FORMAT,
        help="CDS data format.",
    )
    parser.add_argument(
        "--download-format",
        choices=("unarchived", "zip"),
        default=DEFAULT_DOWNLOAD_FORMAT,
        help="CDS download format.",
    )
    parser.add_argument("--max-workers", type=positive_int, default=1, help="Parallel CDS requests.")
    parser.add_argument("--timeout", type=positive_int, default=None, help="CDS API timeout in seconds.")
    parser.add_argument("--retry-max", type=positive_int, default=10, help="Maximum CDS API retries.")
    parser.add_argument("--quiet", action="store_true", help="Reduce cdsapi output.")
    parser.add_argument("--dry-run", action="store_true", help="Print requests without calling CDS.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download ERA5-Land data from the Copernicus CDS API.",
        epilog=AUTH_HELP,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily = subparsers.add_parser("daily", help="Download daily frequency outputs.")
    add_common_arguments(daily)
    daily.add_argument(
        "--daily-statistics",
        nargs="+",
        choices=DAILY_STATISTICS,
        default=None,
        help="Daily statistics for aggregated variables. Defaults are variable-specific.",
    )
    daily.add_argument(
        "--daily-variables",
        nargs="+",
        default=list(DAILY_AGGREGATED_VARIABLES),
        help="Variables handled by the daily statistics dataset.",
    )
    daily.add_argument(
        "--no-daily-variables",
        action="store_true",
        help="Skip variables handled by the daily statistics dataset.",
    )
    daily.add_argument(
        "--accumulated-variables",
        nargs="+",
        default=list(DAILY_ACCUMULATED_VARIABLES),
        help="Accumulated variables downloaded from the hourly dataset.",
    )
    daily.add_argument(
        "--no-accumulated-variables",
        action="store_true",
        help="Skip accumulated variables downloaded from the hourly dataset.",
    )
    daily.add_argument(
        "--accumulated-time",
        default=DEFAULT_ACCUMULATED_TIME,
        help="Hourly timestamp used for accumulated variables.",
    )

    hourly = subparsers.add_parser("hourly", help="Download hourly outputs.")
    add_common_arguments(hourly)
    hourly.add_argument(
        "--variables",
        nargs="+",
        default=list(HOURLY_VARIABLES),
        help="Hourly variables. Each variable is downloaded in a separate request.",
    )

    return parser


def tasks_from_args(args: argparse.Namespace):
    common = CommonRequestOptions(
        year=args.year,
        months=args.months,
        days=args.days,
        area=args.area,
        output_dir=args.output_dir,
        data_format=args.data_format,
        download_format=args.download_format,
    )

    if args.command == "daily":
        if args.no_daily_variables and args.no_accumulated_variables:
            raise ValueError("At least one daily subworkflow must be enabled.")

        return build_daily_tasks(
            DailyRequestOptions(
                common=common,
                daily_statistics=args.daily_statistics,
                accumulated_time=args.accumulated_time,
                daily_variables=[] if args.no_daily_variables else args.daily_variables,
                accumulated_variables=[] if args.no_accumulated_variables else args.accumulated_variables,
            )
        )

    if args.command == "hourly":
        return build_hourly_tasks(HourlyRequestOptions(common=common, variables=args.variables))

    raise ValueError(f"Unsupported command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        tasks = tasks_from_args(args)
        if args.dry_run:
            print_dry_run(tasks)
            return 0
        run_downloads(
            tasks,
            max_workers=args.max_workers,
            timeout=args.timeout,
            retry_max=args.retry_max,
            quiet=args.quiet,
        )
    except ValueError as exc:
        parser.error(str(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
