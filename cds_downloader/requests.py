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
    DEFAULT_TIME_ZONE,
    HOURLY_DATASET,
    HOURLY_VARIABLES,
)


@dataclass(frozen=True)
class DownloadTask:
    """A single CDS request and the file where its response should be saved."""

    dataset: str
    request: dict[str, Any]
    target: Path


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
    if len(parts) not in (2, 3):
        raise ValueError("Time must be in HH:MM or HH:MM:SS format.")

    hour = int(parts[0])
    minute = int(parts[1])
    second = int(parts[2]) if len(parts) == 3 else 0
    if hour not in range(24) or minute not in range(60) or second not in range(60):
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


def build_daily_tasks(
    *,
    year: int,
    months: Iterable[int | str],
    days: Iterable[int | str],
    area: Iterable[float],
    output_dir: Path,
    data_format: str,
    download_format: str,
    daily_statistics: Iterable[str],
    accumulated_time: str,
    daily_variables: Iterable[str] = DAILY_AGGREGATED_VARIABLES,
    accumulated_variables: Iterable[str] = DAILY_ACCUMULATED_VARIABLES,
    time_zone: str = DEFAULT_TIME_ZONE,
    frequency: str = DEFAULT_DAILY_FREQUENCY,
) -> list[DownloadTask]:
    months = normalize_numbers(months, minimum=1, maximum=12)
    days = normalize_numbers(days, minimum=1, maximum=31)
    area = list(area)
    accumulated_time = normalize_time(accumulated_time)
    extension = file_extension(data_format, download_format)

    tasks: list[DownloadTask] = []
    for variable in daily_variables:
        for statistic in daily_statistics:
            request = {
                "variable": variable,
                "year": str(year),
                "month": months,
                "day": days,
                "daily_statistic": statistic,
                "time_zone": time_zone,
                "frequency": frequency,
                "area": area,
                "data_format": data_format,
                "download_format": download_format,
            }
            target = output_dir / f"daily_{variable}_{statistic}_{year}.{extension}"
            tasks.append(DownloadTask(DAILY_DATASET, request, target))

    for variable in accumulated_variables:
        request = {
            "variable": variable,
            "year": str(year),
            "month": months,
            "day": days,
            "time": accumulated_time,
            "data_format": data_format,
            "download_format": download_format,
            "area": area,
        }
        target = output_dir / f"daily_{variable}_accumulated_{year}.{extension}"
        tasks.append(DownloadTask(HOURLY_DATASET, request, target))

    return tasks


def build_hourly_tasks(
    *,
    year: int,
    months: Iterable[int | str],
    days: Iterable[int | str],
    area: Iterable[float],
    output_dir: Path,
    data_format: str,
    download_format: str,
    variables: Iterable[str] = HOURLY_VARIABLES,
    hours: Iterable[str] | None = None,
) -> list[DownloadTask]:
    months = normalize_numbers(months, minimum=1, maximum=12)
    days = normalize_numbers(days, minimum=1, maximum=31)
    area = list(area)
    hours = list(hours) if hours is not None else all_hours()
    hours = [normalize_time(hour) for hour in hours]
    extension = file_extension(data_format, download_format)

    tasks = []
    for variable in variables:
        request = {
            "variable": variable,
            "year": str(year),
            "month": months,
            "day": days,
            "time": hours,
            "data_format": data_format,
            "download_format": download_format,
            "area": area,
        }
        target = output_dir / f"hourly_{variable}_{year}.{extension}"
        tasks.append(DownloadTask(HOURLY_DATASET, request, target))

    return tasks
