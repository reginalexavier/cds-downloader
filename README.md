# cds-downloader

[![CI](https://github.com/reginalexavier/cds-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/reginalexavier/cds-downloader/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-46a0f5.svg)](https://docs.astral.sh/ruff/)

A small command-line tool for downloading a focused set of ERA5-Land climate variables from the Copernicus Climate Data Store (CDS) API.

The tool wraps two practical download workflows:

- `daily`: daily outputs built from daily statistics for regular variables plus daily accumulated values for accumulated variables.
- `hourly`: hourly outputs, downloaded as one request and one file per variable.

This is intentionally a CLI first, not a general-purpose Python SDK for the CDS API.

## Authentication

Before downloading data, configure your CDS API credentials in [`~/.cdsapirc`](https://cds.climate.copernicus.eu/how-to-api):

```yaml
url: https://cds.climate.copernicus.eu/api
key: <PERSONAL-ACCESS-TOKEN>
```

On Linux or macOS, you can create it from the shell without printing the token:

```bash
printf "CDS Personal Access Token: "
stty -echo
IFS= read -r CDS_TOKEN
stty echo
printf "\n"
printf "url: https://cds.climate.copernicus.eu/api\nkey: %s\n" "$CDS_TOKEN" > ~/.cdsapirc
chmod 600 ~/.cdsapirc
unset CDS_TOKEN
```

You must also accept the terms of use for each CDS dataset in the CDS portal before requesting data.

## Installation

During development, run the CLI from the project environment:

```bash
uv run cds-downloader daily --year 2025 --months 10
```

To install it as a local tool from this repository:

```bash
uv tool install .
```

After that, the command is available outside the project directory:

```bash
cds-downloader daily --year 2025 --months 10 11 12
```

To install from GitHub:

```bash
uv tool install git+https://github.com/reginalexavier/cds-downloader.git
```

For one-off usage without permanent installation:

```bash
uvx --from git+https://github.com/reginalexavier/cds-downloader.git cds-downloader daily --year 2025 --months 10
```

If the installed command is not available in your shell, run:

```bash
uv tool update-shell
```

Then reopen the terminal.

## Usage

Daily workflow, with four variables handled by daily statistics and two accumulated variables:

```bash
cds-downloader daily --year 2025 --months 10 11 12
```

By default, the daily workflow uses `daily_mean` for the daily-statistics variables and `00:00` for accumulated variables. To request more statistics:

```bash
cds-downloader daily --year 2025 --months 10 --daily-statistics daily_mean daily_minimum daily_maximum
```

To change the timestamp used for accumulated variables:

```bash
cds-downloader daily --year 2025 --months 10 --accumulated-time 00:00
```

Hourly workflow, with one request and one output file per variable:

```bash
cds-downloader hourly --year 2025 --months 10 11 12
```

Validate requests without calling the CDS API:

```bash
cds-downloader daily --year 2025 --months 10 --dry-run
cds-downloader hourly --year 2025 --months 10 --dry-run
```

Files are written to `data/` by default. Use `--output-dir downloads` or an absolute path to choose another destination.

Use `--max-workers` to run independent requests in parallel. The default is `--max-workers 1`, meaning sequential downloads. Low values such as `2` or `3` are usually safer; high values can increase queueing, slowdowns, or CDS rate-limit failures.

## Variables

CDS provides many variables. This CLI focuses on the small set used by the original workflows:

| Workflow | Dataset | Variable | Handling |
| --- | --- | --- | --- |
| `daily` | `derived-era5-land-daily-statistics` | `2m_dewpoint_temperature` | Daily statistics (`daily_mean` by default) |
| `daily` | `derived-era5-land-daily-statistics` | `2m_temperature` | Daily statistics (`daily_mean` by default) |
| `daily` | `derived-era5-land-daily-statistics` | `10m_u_component_of_wind` | Daily statistics (`daily_mean` by default) |
| `daily` | `derived-era5-land-daily-statistics` | `10m_v_component_of_wind` | Daily statistics (`daily_mean` by default) |
| `daily` | `reanalysis-era5-land` | `surface_solar_radiation_downwards` | Accumulated value at the configured timestamp (`00:00` by default) |
| `daily` | `reanalysis-era5-land` | `total_precipitation` | Accumulated value at the configured timestamp (`00:00` by default) |
| `hourly` | `reanalysis-era5-land` | All six variables above | Hourly series, one request per variable |

To request another variable that is compatible with the same dataset, use the CLI options:

```bash
cds-downloader hourly --year 2025 --months 10 --variables total_precipitation
cds-downloader daily --year 2025 --months 10 --daily-variables 2m_temperature
cds-downloader daily --year 2025 --months 10 --accumulated-variables total_precipitation
```

To make new variables part of the defaults, edit `cds_downloader/config.py`. Before adding a variable to the `daily` workflow, check the CDS dataset documentation to decide whether it belongs to `derived-era5-land-daily-statistics` or should be treated as an accumulated variable from `reanalysis-era5-land`.

## Formats

The daily-statistics subworkflow uses `derived-era5-land-daily-statistics`. That CDS API process does not expose `data_format` or `download_format`, so those fields are not sent. For the one-variable-per-request pattern used by this CLI, `cdsapi` returns a NetCDF/HDF5 file, saved as `.nc`.

The accumulated variables in the daily workflow and the entire hourly workflow use `reanalysis-era5-land`, which supports `--data-format` (`netcdf` or `grib`) and `--download-format` (`unarchived` or `zip`).

## Development

Run checks locally with:

```bash
uv run ruff format --check
uv run ruff check
uv run pytest
```

Optional pre-commit setup:

```bash
uv run task pci  # install Git hooks
uv run task pcr  # run hooks on all files
uv run task pcu  # update hook versions
```

The repository also includes a GitHub Actions workflow that runs formatting checks, linting, and tests on Linux and Windows.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).

## Data Terms

The MIT License applies only to this software. Data downloaded with this tool is provided by the Copernicus Climate Data Store and remains subject to the terms and licenses of the corresponding CDS datasets. Users are responsible for reviewing and accepting the applicable CDS dataset terms before downloading or using the data.

## References

- CDS API setup: https://cds.climate.copernicus.eu/how-to-api
- CDS terms of use: https://cds.climate.copernicus.eu/licences/terms-of-use-cds
- CDS API process `derived-era5-land-daily-statistics`: https://cds.climate.copernicus.eu/api/retrieve/v1/processes/derived-era5-land-daily-statistics
- CDS API process `reanalysis-era5-land`: https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land
- ERA5 family post-processed daily statistics documentation: https://confluence.ecmwf.int/display/CKB/ERA5+family+post-processed+daily+statistics+documentation
