# Enforcement Source Audit

The workbook is a working transcription, not the authoritative input to the published comparisons. Its original entries are preserved in [enforcement_workbook_transcription.csv](../data/enforcement_workbook_transcription.csv). The analysis uses [enforcement_monthly.csv](../data/enforcement_monthly.csv), checked against archived Jagex monthly tables.

| Month | Verification | Source |
| --- | --- | --- |
| 2026-01 | Unavailable during review; excluded | [Archived source](https://archive.ph/jh8Qu) |
| 2026-02 | Monthly OSRS figures checked | [Archived source](https://web.archive.org/web/20260304165243/https://support.runescape.com/hc/en-gb/articles/34686319959441-Player-Support-Anti-Cheating-Statistics) |
| 2026-03 | Monthly OSRS figures checked | [Archived source](https://web.archive.org/web/20260410185304/https://support.runescape.com/hc/en-gb/articles/34686319959441-Player-Support-Anti-Cheating-Statistics) |
| 2026-04 | Monthly OSRS figures checked | [Archived source](https://web.archive.org/web/20260509025717/https://support.runescape.com/hc/en-gb/articles/34686319959441-Player-Support-Anti-Cheating-Statistics) |
| 2026-05 | Monthly OSRS figures checked | [Archived source](https://web.archive.org/web/20260608011747/https://support.runescape.com/hc/en-gb/articles/46608582202001-Anti-Cheating-Statistics) |
| 2026-06 | Monthly OSRS figures checked | [Archived source](https://web.archive.org/web/20260715140434/https://support.runescape.com/hc/en-gb/articles/46608582202001-Anti-Cheating-Statistics) |
| 2026-07 | Monthly OSRS figures checked | [Archived source](https://web.archive.org/web/20260813140026/https://support.runescape.com/hc/en-gb/articles/46608582202001-Anti-Cheating-Statistics) |

## Reconciliation notes

- January remains unverified: its linked archive returned HTTP 429. It is not inferred from later cumulative totals.
- Wealth figures in the workbook are roughly one thousand times smaller than the sources: February 2.4 billion versus 2.43 trillion, March 3.7 billion versus 3.67 trillion, April 8.8 billion versus 8.79 trillion, May 4.8 billion versus 4.76 trillion, June 3.4 billion versus 3.37 trillion, and July 4.7 billion versus 4.68 trillion GP. The verified CSV stores GP units and preserves the reported T suffix in a separate field.
- Macro totals for February–April are rounded in the source (1.41M, 2.25M, 1.19M), not exact account counts. Expanded numbers retain that reporting precision. Wealth figures are also rounded. Account subtotals may not sum exactly to rounded totals.
- RWT and macro categories are analyzed separately; their counts are not summed as unique accounts. Missing account-category breakdowns remain blank, not zero.
- Monthly tables are used directly. Year-to-date values across archived publications do not reconcile exactly with sums of their monthly values; potential revisions and rounding are not resolved by forcing the totals to match.
- For example, the workbook January–July RWT total is 135,141, while the July source reports 120,014 year to date. These are not treated as interchangeable series.
- F2P and members ban categories describe banned accounts. Item accessibility describes goods; it does not identify which account types traded them.
- The removal metric changes labels from GP Removed / Gold Removed to Wealth Removed. Continuity of its underlying definition is not established here. It is retained as reported context and excluded from association calculations.

Sources were inspected October 7, 2026. The reviewed archive URLs and source-response checksums are recorded in [enforcement_sources.json](../data/enforcement_sources.json). Historical publication labels are preserved; this review does not establish the publishers' underlying counting methodology.
