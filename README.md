# OSRS Market Data Analysis

An exploratory study of Old School RuneScape Grand Exchange prices and observed trading volume for eight items. This repository develops a school project through public revisions. The original runnable version is preserved in the `school-project-baseline` tag.

The historical snapshot contains **2,920 daily observations**, with **365 observations per item**, from **August 26, 2025 through August 25, 2026 (UTC)**. It includes no missing values or duplicate item/timestamp pairs.

## What the analysis does

The scripts inspect raw market observations, construct a midpoint of the reported high and low transaction averages, combine the two reported volume categories, and compare indexed price and volume histories. Price indices begin at 100 for each item. Volume indices use the mean of each item's first seven observations as 100.

The report discusses market changes alongside anti-cheat enforcement. The current scripts do not incorporate enforcement statistics into a statistical model, and the results do not establish that enforcement caused the observed changes. The selected items are a small sample of the economy, and the API observations are not a complete census of Grand Exchange transactions.

## Read the analysis

- [Original school report, converted to Markdown](docs/original_report.md)
- [Public revision roadmap](ROADMAP.md)

![Indexed prices for members-only items](figures/p2p_indexed_price_time_series.png)

![Indexed observed volume for free-to-play-accessible items](figures/f2p_indexed_volume_time_series.png)

The midpoint is an unweighted average of two reported transaction-price averages, rather than a volume-weighted market price. Indices depend on the chosen baseline period. The daily lines are intentionally preserved here; clearer charts and sensitivity checks are planned revisions.

## Reproduce the historical analysis

Use Python 3.11 or newer and run the commands from the repository directory.

```sh
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

Install dependencies and reproduce the historical analysis with one command:

```sh
python -m pip install -r requirements.txt
python run_analysis.py
```

This command inspects the saved raw data, rebuilds the processed CSV, and saves all five charts in `figures/` without opening windows or accessing the network. Paths are anchored to the project directory, so the script also works when called by its full path from another folder.

To display the charts while saving them:

```sh
python run_analysis.py --show
```

Close each plot window to continue. The historical raw snapshot is left unchanged; the processed CSV and figures are regenerated.

## Optional live data collection

```sh
python collect.py
```

This separate command requires internet access and saves new data to `data/snapshots/<UTC timestamp>/osrs_market_data_raw.csv`. It leaves the historical study unchanged. The API returns currently available observations rather than the fixed dates of the study.

You can supply a new output path explicitly:

```sh
python collect.py --output data/my_new_snapshot.csv
```

The collector refuses an existing output file before making requests and creates its CSV exclusively to avoid accidental replacement. `run_analysis.py` continues to use the historical snapshot; analysis of new snapshots is a future extension.

The collector identifies itself with a User-Agent. Update that identifier for your own use in accordance with the API's documentation. Live requests were not run during this revision; snapshot handling was checked with fixture data.

## Repository files

| File | Purpose |
| --- | --- |
| `run_analysis.py` | Reproduce the complete historical analysis |
| `config.py` | Shared paths, item groups, and API URL |
| `collect.py` | Collect a separate new market snapshot |
| `inspect_data.py` | Inspect raw data and save the price distribution chart |
| `process.py` | Construct dates, midpoint prices, total volume, and indices |
| `plot.py` | Save indexed price and volume charts |
| `data/` | Fixed raw snapshot and reproducible processed data |
| `figures/` | Five generated charts |

The original numbered scripts are available in the `school-project-baseline` tag. The Word submission and contextual enforcement workbook remain local; they are not runtime dependencies.

## Sources and reproducibility

Market data were collected from the [OSRS Wiki real-time price API](https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices), using its `/mapping` and `/timeseries` endpoints with `timestep=24h`. The stored timestamps establish the observation period; the original collection time and original dependency versions were not recorded. Third-party data retain their source terms.

The original report contains its own references and an acknowledgment of ChatGPT assistance. That acknowledgment is preserved in the Markdown version. The public baseline preparation verified all four offline scripts, reproduced the processed CSV within floating-point tolerance, and regenerated five figures. The dependency list is not an exact lockfile of the original school environment.

The first workflow revision was verified from outside the project directory with network requests disabled. It reproduced the processed CSV within floating-point tolerance and all five figures pixel for pixel. Separate fixture checks verified that collection refuses existing files and defaults to a new snapshot directory.
