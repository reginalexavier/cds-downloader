"""Build CDS download tasks from CLI options."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .config import (
    DAILY_ACCUMULATED_VARIABLES,
    DAILY_AGGREGATED_VARIABLES,
    DAILY_DATASET,
    DEFAULT_DAILY_FREQUENCY,
    DEFAULT_DAILY_STATISTICS_BY_VARIABLE,
    DEFAULT_TIME_ZONE,
    HOURLY_DATASET,
    HOURLY_VARIABLES,
)

TIME_PARTS_WITHOUT_SECONDS = 2
TIME_PARTS_WITH_SECONDS = 3
HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
SECONDS_PER_MINUTE = 60


@dataclass(frozen=True)
class DownloadTask:
    """A single CDS request and the file where its response should be saved."""

    dataset: str
    request: dict[str, Any]
    target: Path


@dataclass(frozen=True)
class CommonRequestOptions:
    """Options shared by daily and hourly CDS requests."""

    year: int
    months: Iterable[int | str]
    days: Iterable[int | str]
    area: Iterable[float]
    output_dir: Path
    data_format: str
    download_format: str


@dataclass(frozen=True)
class DailyRequestOptions:
    """Options for the composed daily workflow."""

    common: CommonRequestOptions
    daily_statistics: Iterable[str] | None
    accumulated_time: str
    daily_variables: Iterable[str] = DAILY_AGGREGATED_VARIABLES
    accumulated_variables: Iterable[str] = DAILY_ACCUMULATED_VARIABLES
    time_zone: str = DEFAULT_TIME_ZONE
    frequency: str = DEFAULT_DAILY_FREQUENCY


@dataclass(frozen=True)
class HourlyRequestOptions:
    """Options for the hourly workflow."""

    common: CommonRequestOptions
    variables: Iterable[str] = HOURLY_VARIABLES
    hours: Iterable[str] | None = None


def normalize_numbers(values: Iterable[int | str], *, minimum: int, maximum: int) -> list[str]:
    normalized = []
    for value in values:
        number = int(value)
        if number < minimum or number > maximum:
            raise ValueError(f"Value {number} must be between {minimum} and {maximum}.")
        normalized.append(f"{number:02d}")
    return normalized


def normalize_time(value: str) -> str:
    parts = value.split(":")
    if len(parts) not in {TIME_PARTS_WITHOUT_SECONDS, TIME_PARTS_WITH_SECONDS}:
        raise ValueError("Time must be in HH:MM or HH:MM:SS format.")

    hour = int(parts[0])
    minute = int(parts[1])
    second = int(parts[2]) if len(parts) == TIME_PARTS_WITH_SECONDS else 0
    if (
        hour not in range(HOURS_PER_DAY)
        or minute not in range(MINUTES_PER_HOUR)
        or second not in range(SECONDS_PER_MINUTE)
    ):
        raise ValueError("Time must be a valid 24-hour time.")

    if second:
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    return f"{hour:02d}:{minute:02d}"


def all_days() -> list[str]:
    return [f"{day:02d}" for day in range(1, 32)]


def all_hours() -> list[str]:
    return [f"{hour:02d}:00" for hour in range(24)]


def file_extension(data_format: str, download_format: str) -> str:
    if download_format == "zip":
        return "zip"
    if data_format == "netcdf":
        return "nc"
    return "grib"


def daily_statistics_for_variable(variable: str, statistics: Iterable[str] | None) -> tuple[str, ...]:
    if statistics is not None:
        return tuple(statistics)
    return DEFAULT_DAILY_STATISTICS_BY_VARIABLE.get(variable, ("daily_mean",))


def build_daily_tasks(options: DailyRequestOptions) -> list[DownloadTask]:
    common = options.common
    months = normalize_numbers(common.months, minimum=1, maximum=12)
    days = normalize_numbers(common.days, minimum=1, maximum=31)
    area = list(common.area)
    accumulated_time = normalize_time(options.accumulated_time)
    accumulated_extension = file_extension(common.data_format, common.download_format)

    tasks: list[DownloadTask] = []
    for variable in options.daily_variables:
        for statistic in daily_statistics_for_variable(variable, options.daily_statistics):
            # The CDS process for post-processed daily statistics exposes neither
            # data_format nor download_format. The retrieved asset is NetCDF/HDF5
            # for the one-variable-per-request pattern used by this CLI.
            request = {
                "variable": variable,
                "year": str(common.year),
                "month": months,
                "day": days,
                "daily_statistic": statistic,
                "time_zone": options.time_zone,
                "frequency": options.frequency,
                "area": area,
            }
            target = common.output_dir / f"daily_{variable}_{statistic}_{common.year}.nc"
            tasks.append(DownloadTask(DAILY_DATASET, request, target))

    for variable in options.accumulated_variables:
        request = {
            "variable": variable,
            "year": str(common.year),
            "month": months,
            "day": days,
            "time": accumulated_time,
            "data_format": common.data_format,
            "download_format": common.download_format,
            "area": area,
        }
        target = common.output_dir / f"daily_{variable}_accumulated_{common.year}.{accumulated_extension}"
        tasks.append(DownloadTask(HOURLY_DATASET, request, target))

    return tasks


def build_hourly_tasks(options: HourlyRequestOptions) -> list[DownloadTask]:
    common = options.common
    months = normalize_numbers(common.months, minimum=1, maximum=12)
    days = normalize_numbers(common.days, minimum=1, maximum=31)
    area = list(common.area)
    hours = list(options.hours) if options.hours is not None else all_hours()
    hours = [normalize_time(hour) for hour in hours]
    extension = file_extension(common.data_format, common.download_format)

    tasks = []
    for variable in options.variables:
        request = {
            "variable": variable,
            "year": str(common.year),
            "month": months,
            "day": days,
            "time": hours,
            "data_format": common.data_format,
            "download_format": common.download_format,
            "area": area,
        }
        target = common.output_dir / f"hourly_{variable}_{common.year}.{extension}"
        tasks.append(DownloadTask(HOURLY_DATASET, request, target))

    return tasks
