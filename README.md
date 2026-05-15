# cds-downloader

CLI simples para baixar dados ERA5-Land via Copernicus Climate Data Store API.

## Autenticação

Configure o arquivo [`~/.cdsapirc`](https://cds.climate.copernicus.eu/how-to-api) antes de baixar dados:

```yaml
url: https://cds.climate.copernicus.eu/api
key: <PERSONAL-ACCESS-TOKEN>
```

Também é necessário aceitar os termos de uso dos datasets no portal CDS.

## Instalação

Durante desenvolvimento, use a CLI pelo ambiente do projeto:

```bash
uv run cds-downloader daily --year 2025 --months 10
```

Para instalar como uma ferramenta local a partir desta pasta:

```bash
uv tool install .
```

Depois disso, o comando fica disponível fora da pasta do projeto:

```bash
cds-downloader daily --year 2025 --months 10 11 12
```

Em outro computador, publique ou disponibilize este projeto em um repositório Git e instale com:

```bash
uv tool install git+https://github.com/reginalexavier/cds-downloader.git # acesso publico
uv tool install git+ssh://git@github.com/reginalexavier/cds-downloader.git # acesso atutenticado
```

Para uso pontual, sem instalação permanente:

```bash
uvx --from git+https://github.com/reginalexavier/cds-downloader.git cds-downloader daily --year 2025 --months 10
```

Se o comando instalado não aparecer no terminal, rode:

```bash
uv tool update-shell
```

e reabra o terminal.

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

Use `--max-workers` para executar múltiplas requests independentes em paralelo. O padrão é `--max-workers 1`, ou seja, download sequencial. Valores baixos como `2` ou `3` costumam ser mais seguros; valores altos podem apenas aumentar fila, lentidão ou chance de erro por limite do CDS.

## Variáveis

O CDS oferece muitas variáveis. Esta CLI foi pensada para um conjunto pequeno usado nos fluxos originais:

| Fluxo | Dataset | Variável | Tratamento |
| --- | --- | --- | --- |
| `daily` | `derived-era5-land-daily-statistics` | `2m_dewpoint_temperature` | Estatísticas diárias (`daily_mean` por padrão) |
| `daily` | `derived-era5-land-daily-statistics` | `2m_temperature` | Estatísticas diárias (`daily_mean` por padrão) |
| `daily` | `derived-era5-land-daily-statistics` | `10m_u_component_of_wind` | Estatísticas diárias (`daily_mean` por padrão) |
| `daily` | `derived-era5-land-daily-statistics` | `10m_v_component_of_wind` | Estatísticas diárias (`daily_mean` por padrão) |
| `daily` | `reanalysis-era5-land` | `surface_solar_radiation_downwards` | Valor acumulado no horário configurado (`00:00` por padrão) |
| `daily` | `reanalysis-era5-land` | `total_precipitation` | Valor acumulado no horário configurado (`00:00` por padrão) |
| `hourly` | `reanalysis-era5-land` | Todas as 6 variáveis acima | Série horária, uma request por variável |

Para baixar outra variável já compatível com o mesmo dataset, use os parâmetros da CLI:

```bash
uv run cds-downloader hourly --year 2025 --months 10 --variables total_precipitation
uv run cds-downloader daily --year 2025 --months 10 --daily-variables 2m_temperature
uv run cds-downloader daily --year 2025 --months 10 --accumulated-variables total_precipitation
```

Para tornar novas variáveis parte dos defaults, edite `cds_downloader/config.py`. Antes de adicionar uma variável ao fluxo `daily`, confira na documentação do dataset se ela pertence ao produto de estatísticas diárias ou se deve ser tratada como acumulada via `reanalysis-era5-land`.

## Formatos

O subfluxo diário agregado usa o dataset `derived-era5-land-daily-statistics`. O processo da API não expõe `data_format` ou `download_format`, então esses campos não são enviados. No padrão de uma variável por request usado por esta CLI, o arquivo retornado pelo `cdsapi` é NetCDF/HDF5 e é salvo como `.nc`.

As variáveis acumuladas do fluxo diário e todo o fluxo horário usam `reanalysis-era5-land`, que aceita `--data-format` (`netcdf` ou `grib`) e `--download-format` (`unarchived` ou `zip`).

## Referências

- CDS API setup: https://cds.climate.copernicus.eu/how-to-api
- Processo API `derived-era5-land-daily-statistics`: https://cds.climate.copernicus.eu/api/retrieve/v1/processes/derived-era5-land-daily-statistics
- Processo API `reanalysis-era5-land`: https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land
- Documentação ERA5 family post-processed daily statistics: https://confluence.ecmwf.int/display/CKB/ERA5+family+post-processed+daily+statistics+documentation
