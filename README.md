# cds-downloader

CLI simples para baixar dados ERA5-Land via Copernicus Climate Data Store API.

## Autenticação

Configure o arquivo `~/.cdsapirc` antes de baixar dados:

```yaml
url: https://cds.climate.copernicus.eu/api
key: <PERSONAL-ACCESS-TOKEN>
```

Também é necessário aceitar os termos de uso dos datasets no portal CDS.

## Uso

Fluxo diário, com quatro variáveis agregáveis e duas variáveis acumuladas:

```bash
uv run cds-downloader daily --year 2025 --months 10 11 12
```

Por padrão, o fluxo diário usa `daily_mean` nas variáveis agregáveis e `00:00` nas acumuladas. Para incluir outras estatísticas:

```bash
uv run cds-downloader daily --year 2025 --months 10 --daily-statistics daily_mean daily_minimum daily_maximum
```

Para mudar o horário usado nas acumuladas:

```bash
uv run cds-downloader daily --year 2025 --months 10 --accumulated-time 00:00
```

Fluxo horário, com uma request e um arquivo por variável:

```bash
uv run cds-downloader hourly --year 2025 --months 10 11 12
```

Valide as requests sem chamar a API:

```bash
uv run cds-downloader daily --year 2025 --months 10 --dry-run
uv run cds-downloader hourly --year 2025 --months 10 --dry-run
```

Arquivos são salvos em `data/` por padrão. Use `--output-dir downloads` para escolher outro destino.

## Formatos

O subfluxo diário agregado usa o dataset `derived-era5-land-daily-statistics`. O processo da API não expõe `data_format` ou `download_format`, então esses campos não são enviados. No padrão de uma variável por request usado por esta CLI, o arquivo retornado pelo `cdsapi` é NetCDF/HDF5 e é salvo como `.nc`.

As variáveis acumuladas do fluxo diário e todo o fluxo horário usam `reanalysis-era5-land`, que aceita `--data-format` (`netcdf` ou `grib`) e `--download-format` (`unarchived` ou `zip`).

## Referências

- CDS API setup: https://cds.climate.copernicus.eu/how-to-api
- Processo API `derived-era5-land-daily-statistics`: https://cds.climate.copernicus.eu/api/retrieve/v1/processes/derived-era5-land-daily-statistics
- Processo API `reanalysis-era5-land`: https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land
- Documentação ERA5 family post-processed daily statistics: https://confluence.ecmwf.int/display/CKB/ERA5+family+post-processed+daily+statistics+documentation
