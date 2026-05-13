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

Arquivos são salvos no diretório atual por padrão. Use `--output-dir data` para escolher outro destino.
