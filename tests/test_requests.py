from pathlib import Path

import pytest
from cds_downloader.requests import (
    build_daily_tasks,
    build_hourly_tasks,
    file_extension,
    normalize_numbers,
    normalize_time,
)


def test_build_daily_tasks_splits_aggregated_and_accumulated_variables():
    tasks = build_daily_tasks(
        year=2025,
        months=["10", "11"],
        days=["1", "2"],
        area=[-15.36, -55.91, -17.24, -53.14],
        output_dir=Path("data"),
        data_format="netcdf",
        download_format="unarchived",
        daily_statistics=["daily_mean", "daily_maximum"],
        accumulated_time="0:00",
        daily_variables=["2m_temperature"],
        accumulated_variables=["total_precipitation"],
    )

    assert len(tasks) == 3
    assert tasks[0].dataset == "derived-era5-land-daily-statistics"
    assert tasks[0].request["daily_statistic"] == "daily_mean"
    assert tasks[0].target == Path("data/daily_2m_temperature_daily_mean_2025.nc")
    assert tasks[1].request["daily_statistic"] == "daily_maximum"
    assert tasks[2].dataset == "reanalysis-era5-land"
    assert tasks[2].request["time"] == "00:00"
    assert tasks[2].target == Path("data/daily_total_precipitation_accumulated_2025.nc")


def test_build_hourly_tasks_creates_one_request_per_variable():
    tasks = build_hourly_tasks(
        year=2025,
        months=[10],
        days=[1, 2],
        area=[-15.36, -55.91, -17.24, -53.14],
        output_dir=Path("data"),
        data_format="netcdf",
        download_format="unarchived",
        variables=["2m_temperature", "total_precipitation"],
    )

    assert len(tasks) == 2
    assert [task.request["variable"] for task in tasks] == ["2m_temperature", "total_precipitation"]
    assert tasks[0].request["time"][0] == "00:00"
    assert tasks[0].request["time"][-1] == "23:00"
    assert tasks[0].target == Path("data/hourly_2m_temperature_2025.nc")
    assert tasks[1].target == Path("data/hourly_total_precipitation_2025.nc")


def test_normalize_numbers_zero_pads_and_validates_range():
    assert normalize_numbers(["1", 12], minimum=1, maximum=12) == ["01", "12"]

    with pytest.raises(ValueError):
        normalize_numbers(["13"], minimum=1, maximum=12)


def test_normalize_time_accepts_hour_minute_and_second():
    assert normalize_time("0:00") == "00:00"
    assert normalize_time("03:00:00") == "03:00"
    assert normalize_time("03:00:30") == "03:00:30"


def test_file_extension_uses_zip_when_download_format_is_zip():
    assert file_extension("netcdf", "unarchived") == "nc"
    assert file_extension("grib", "unarchived") == "grib"
    assert file_extension("netcdf", "zip") == "zip"
