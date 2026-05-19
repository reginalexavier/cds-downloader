import pytest
from cds_downloader.cli import build_parser, main, tasks_from_args
from cds_downloader.downloader import print_dry_run

EXPECTED_HOURLY_TASKS = 2
EXPECTED_SINGLE_DAILY_TASK = 1
EXPECTED_TEMPERATURE_DEFAULT_TASKS = 2


def test_help_mentions_cds_api_token_setup(capsys):
    parser = build_parser()

    parser.print_help()

    output = capsys.readouterr().out
    assert "~/.cdsapirc" in output
    assert "https://cds.climate.copernicus.eu/how-to-api" in output


def test_daily_dry_run_does_not_call_downloader(monkeypatch, capsys):
    def fail_run_downloads(*args, **kwargs):
        raise AssertionError("run_downloads should not be called during dry-run")

    monkeypatch.setattr("cds_downloader.cli.run_downloads", fail_run_downloads)

    exit_code = main(["daily", "--year", "2025", "--months", "10", "--dry-run"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "derived-era5-land-daily-statistics" in output
    assert "reanalysis-era5-land" in output


def test_hourly_parser_builds_separate_tasks():
    parser = __import__("cds_downloader.cli", fromlist=["build_parser"]).build_parser()
    args = parser.parse_args([
        "hourly",
        "--year",
        "2025",
        "--months",
        "10",
        "--variables",
        "2m_temperature",
        "total_precipitation",
    ])

    tasks = tasks_from_args(args)

    assert len(tasks) == EXPECTED_HOURLY_TASKS
    assert tasks[0].request["variable"] == "2m_temperature"
    assert tasks[1].request["variable"] == "total_precipitation"
    assert str(tasks[0].target).startswith("data")


def test_output_dir_can_be_overridden():
    parser = __import__("cds_downloader.cli", fromlist=["build_parser"]).build_parser()
    args = parser.parse_args([
        "hourly",
        "--year",
        "2025",
        "--months",
        "10",
        "--output-dir",
        "downloads",
        "--variables",
        "total_precipitation",
    ])

    tasks = tasks_from_args(args)

    assert str(tasks[0].target).startswith("downloads")


def test_daily_can_download_only_one_aggregated_variable():
    parser = __import__("cds_downloader.cli", fromlist=["build_parser"]).build_parser()
    args = parser.parse_args([
        "daily",
        "--year",
        "2025",
        "--months",
        "10",
        "--daily-variables",
        "2m_temperature",
        "--no-accumulated-variables",
    ])

    tasks = tasks_from_args(args)

    assert len(tasks) == EXPECTED_TEMPERATURE_DEFAULT_TASKS
    assert tasks[0].dataset == "derived-era5-land-daily-statistics"
    assert tasks[0].request["variable"] == "2m_temperature"
    assert [task.request["daily_statistic"] for task in tasks] == ["daily_minimum", "daily_maximum"]


def test_daily_can_download_only_one_accumulated_variable():
    parser = __import__("cds_downloader.cli", fromlist=["build_parser"]).build_parser()
    args = parser.parse_args([
        "daily",
        "--year",
        "2025",
        "--months",
        "10",
        "--no-daily-variables",
        "--accumulated-variables",
        "total_precipitation",
    ])

    tasks = tasks_from_args(args)

    assert len(tasks) == EXPECTED_SINGLE_DAILY_TASK
    assert tasks[0].dataset == "reanalysis-era5-land"
    assert tasks[0].request["variable"] == "total_precipitation"


def test_daily_requires_at_least_one_subworkflow():
    parser = __import__("cds_downloader.cli", fromlist=["build_parser"]).build_parser()
    args = parser.parse_args([
        "daily",
        "--year",
        "2025",
        "--months",
        "10",
        "--no-daily-variables",
        "--no-accumulated-variables",
    ])

    with pytest.raises(ValueError, match="At least one daily subworkflow must be enabled."):
        tasks_from_args(args)


def test_print_dry_run_outputs_target(capsys):
    parser = __import__("cds_downloader.cli", fromlist=["build_parser"]).build_parser()
    args = parser.parse_args(["hourly", "--year", "2025", "--months", "10"])
    tasks = tasks_from_args(args)

    print_dry_run(tasks[:1])

    assert "data" in capsys.readouterr().out
