# News

## v0.2.0 - 2026-05-19

- Add variable-specific default daily statistics:
  - `2m_dewpoint_temperature`: `daily_minimum`, `daily_maximum`
  - `2m_temperature`: `daily_minimum`, `daily_maximum`
  - `10m_u_component_of_wind`: `daily_mean`
  - `10m_v_component_of_wind`: `daily_mean`
- Add `--no-daily-variables` and `--no-accumulated-variables` to let users run only one daily subworkflow.
- Document daily precipitation totals using accumulated `total_precipitation` from `reanalysis-era5-land`.
- Keep explicit `--daily-statistics` overrides for users who need custom statistics.

## v0.1.0 - 2026-05-16

- Initial public release.
- Add daily and hourly CDS download workflows.
- Add dry-run support, configurable area, output directory, formats, and parallel workers.
- Add tests, Ruff checks, pre-commit hooks, and GitHub Actions CI.
