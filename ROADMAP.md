# Public Revision Roadmap

The initial public commit preserves the original analysis and historical data. Revisions should be small enough that readers can understand the purpose, inspect the changes, and reproduce the result.

## 1. Simplify the workflow — completed

- Replace the numbered script names with clear collection, inspection, processing, and plotting modules.
- Add one command to reproduce the historical analysis without accessing the network.
- Make input and output paths explicit and independent of the current working directory.
- Require an explicit option before live collection replaces an existing dataset.

Completed: `python run_analysis.py` rebuilds the historical analysis offline, paths are anchored to the project directory, `--show` controls chart windows, and collection saves to a new snapshot while refusing existing output files. Regression checks reproduced the data and all five figures.

## 2. Strengthen data validation and provenance — completed

- Validate required fields, numeric ranges, item/timestamp uniqueness, chronological coverage, and daily gaps.
- Handle missing or zero price and volume baselines explicitly rather than producing invalid indices.
- Record collection time, API parameters, observed date range, and dependency versions for new snapshots.
- Add focused tests for normalization, malformed API responses, missing intervals, and snapshot preservation.

Completed: invalid data fail before historical outputs are written, new snapshots include provenance sidecars, and ten offline tests cover regression and failure cases. The full historical run preserves the processed data and all five chart images.

## 3. Improve the visuals and written analysis

- Compare small-multiple charts with the existing four-line charts.
- Show a labeled seven-day rolling view alongside the raw daily series.
- Quantify changes using comparable windows and test sensitivity to price and volume baseline choices.
- Define observed volume, price midpoint, and item grouping clearly.
- Revise the report around supported findings, preserving the original version for comparison.

Done when every headline finding is linked to a generated table or figure and the limitations remain visible.

## 4. Explore the enforcement question

- Review the local enforcement workbook against dated official sources before incorporating it.
- Distinguish monthly counts from cumulative year-to-date figures, macro bans from RWT bans, and account categories from item accessibility.
- Align enforcement and market data at a common time interval, with an explicit treatment of partial months.
- Examine descriptive associations and alternative explanations such as updates, seasonality, player activity, and item-specific demand.
- Consider a broader item sample and a longer time window before stronger claims.

Done when source provenance and time alignment are documented and the results clearly distinguish association from causation. Ban counts alone do not establish enforcement effectiveness or an exogenous treatment.
