from cds_downloader.cli import main, tasks_from_args
from cds_downloader.downloader import print_dry_run

EXPECTED_HOURLY_TASKS = 2


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


def test_print_dry_run_outputs_target(capsys):
    parser = __import__("cds_downloader.cli", fromlist=["build_parser"]).build_parser()
    args = parser.parse_args(["hourly", "--year", "2025", "--months", "10"])
    tasks = tasks_from_args(args)

    print_dry_run(tasks[:1])

    assert "data" in capsys.readouterr().out
