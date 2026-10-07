"""Descriptive comparisons using mean daily measurements, not period totals."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import ROOT, FIGURES_DIR, F2P_ITEMS, P2P_ITEMS

PERIODS = {
    'early': ('2025-09-01', '2025-12-31'),
    'first_half_2026': ('2026-01-01', '2026-06-30'),
    'late': ('2026-07-01', '2026-07-31'),
}


def period_comparisons(df):
    rows = []
    for item, data in df.groupby('item_name'):
        row = {'item_name': item, 'accessibility': 'F2P-accessible' if item in F2P_ITEMS else 'Members-only'}
        for period, (start, end) in PERIODS.items():
            part = data[data['date'].between(start, end)]
            expected = len(pd.date_range(start, end))
            if len(part) != expected:
                raise ValueError(f'{item}: incomplete {period} comparison window.')
            row[f'{period}_days'] = len(part)
            for metric in ('midpoint_price', 'total_volume'):
                row[f'{period}_{metric}'] = part[metric].mean()
        for metric in ('midpoint_price', 'total_volume'):
            baseline = row[f'early_{metric}']
            if baseline <= 0:
                raise ValueError(f'{item}: unusable comparison baseline for {metric}.')
            for period in ('first_half_2026', 'late'):
                row[f'{period}_{metric}_change_pct'] = (row[f'{period}_{metric}'] / baseline - 1) * 100
        rows.append(row)
    return pd.DataFrame(rows)


def endpoint_sensitivity(df):
    rows = []
    for item, data in df.groupby('item_name'):
        data = data.sort_values('date')
        if len(data) < 56:
            raise ValueError(f'{item}: sensitivity comparison needs at least 56 observations for nonoverlapping 28-day windows.')
        for days in (7, 28):
            for metric in ('midpoint_price', 'total_volume'):
                first = data[metric].iloc[:days].mean()
                last = data[metric].iloc[-days:].mean()
                if first <= 0:
                    raise ValueError(f'{item}: unusable {days}-day sensitivity baseline.')
                rows.append({'item_name': item, 'metric': metric, 'window_days': days, 'first_window_mean': first, 'last_window_mean': last, 'change_pct': (last / first - 1) * 100})
    return pd.DataFrame(rows)


def plot_panels(df, metric, label, output, show=False):
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharex=True, sharey=True, layout='constrained')
    for ax, item in zip(axes.flat, F2P_ITEMS + P2P_ITEMS):
        data = df[df['item_name'] == item].sort_values('date')
        indexed = data[metric] / data[metric].iloc[:28].mean() * 100
        ax.plot(data['date'], indexed, color='#95a7b7', alpha=0.45, linewidth=0.8, label='Daily')
        ax.plot(data['date'], indexed.rolling(7, min_periods=7).mean(), color='#186b8c', linewidth=1.8, label='Trailing 7-day mean')
        ax.axhline(100, color='#666666', linestyle='--', linewidth=0.8)
        ax.set_title(item)
        ax.grid(alpha=0.15)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.tick_params(axis='x', labelrotation=30)
    axes[0, 0].legend(loc='upper left', fontsize=8)
    fig.suptitle(f'{label} by item | first 28-day mean = 100', fontsize=16)
    fig.supylabel('Index (shared scale)')
    fig.supxlabel('Date | top row: F2P-accessible items; bottom row: members-only items')
    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(output, dpi=180)
    if show:
        plt.show()
    plt.close(fig)


def generate_comparisons(df, show=False):
    tables = ROOT / 'tables'
    tables.mkdir(exist_ok=True)
    comparison = period_comparisons(df)
    sensitivity = endpoint_sensitivity(df)
    comparison.to_csv(tables / 'period_comparisons.csv', index=False)
    sensitivity.to_csv(tables / 'baseline_sensitivity.csv', index=False)
    plot_panels(df, 'midpoint_price', 'Midpoint price', FIGURES_DIR / 'price_small_multiples.png', show)
    plot_panels(df, 'total_volume', 'Observed daily trading volume', FIGURES_DIR / 'volume_small_multiples.png', show)
    report = ROOT / 'docs' / 'trend_comparisons.md'
    report.parent.mkdir(exist_ok=True)
    lines = ['# Quantified Market Trends', '', 'These comparisons describe the eight selected items. They do not establish effects of anti-cheat enforcement or represent the full Grand Exchange.', '', '## Comparable daily measurements', '', 'The early window is September–December 2025 (122 days), the first half of 2026 is January–June (181 days), and the late window is July 2026 (31 days). The table compares means per observed day, so longer windows do not mechanically produce larger volume totals. Partial August months are excluded. Unequal window lengths and seasonality still limit interpretation.', '', '| Item | H1 price change | July price change | H1 volume change | July volume change |', '| --- | ---: | ---: | ---: | ---: |']
    h1_count = comparison['first_half_2026_total_volume_change_pct'].lt(0).sum()
    july_count = comparison['late_total_volume_change_pct'].lt(0).sum()
    exceptions = ', '.join(comparison.loc[comparison['late_total_volume_change_pct'].ge(0), 'item_name'])
    summary = [f'Mean daily observed volume was lower than the early-window mean for {h1_count} of {len(comparison)} items in the first half of 2026 and {july_count} in July. The July exception was {exceptions}. This supports a broad decline in the selected sample rather than a decline for every item.', '']
    members = comparison[comparison['accessibility'].eq('Members-only')]
    free = comparison[comparison['accessibility'].eq('F2P-accessible')]
    summary += [f'July mean midpoint prices increased for {members["late_midpoint_price_change_pct"].gt(0).sum()} of {len(members)} members-only items. Among F2P-accessible items, {free["late_midpoint_price_change_pct"].lt(0).sum()} declined and {free["late_midpoint_price_change_pct"].gt(0).sum()} increased. The item-level results are more varied than a simple division between rising members prices and stagnant F2P prices.', '', 'These means compare levels across windows. They do not by themselves establish a steady decline within the first half of 2026, reduced volatility, or statistical significance.', '']
    lines[4:4] = ['## Main findings', '', *summary]
    for row in comparison.to_dict('records'):
        values = [row[f'{period}_{metric}_change_pct'] for metric in ('midpoint_price', 'total_volume') for period in ('first_half_2026', 'late')]
        lines.append('| ' + row['item_name'] + ' | ' + ' | '.join(f'{value:+.1f}%' for value in values) + ' |')
    lines += ['', 'All changes use the early-window mean as their reference. Full values and observation counts are in [period_comparisons.csv](../tables/period_comparisons.csv).', '', '## Baseline sensitivity', '', 'A second comparison uses the first and last seven days, then the first and last 28 days of the full snapshot. These are different windows from the calendar-period comparison; they test sensitivity to endpoint averaging rather than provide an independent replication.', '', '| Item | Price, 7 days | Price, 28 days | Volume, 7 days | Volume, 28 days |', '| --- | ---: | ---: | ---: | ---: |']
    for item in comparison['item_name']:
        values = [sensitivity[(sensitivity.item_name == item) & (sensitivity.metric == metric) & (sensitivity.window_days == days)]['change_pct'].iloc[0] for metric in ('midpoint_price','total_volume') for days in (7,28)]
        lines.append('| ' + item + ' | ' + ' | '.join(f'{value:+.1f}%' for value in values) + ' |')
    lines += ['', 'Full endpoint means are in [baseline_sensitivity.csv](../tables/baseline_sensitivity.csv).', '', '## Daily trends', '', 'Each panel uses the first 28 observations as its reference of 100. Daily observations remain visible behind a trailing seven-day mean. The first six smoothed values are omitted because a full week is not available. Shared vertical scales support comparison within each figure. Original charts retain their original normalization and remain available.', '', '![Price trends](../figures/price_small_multiples.png)', '', '![Observed volume trends](../figures/volume_small_multiples.png)', '', 'A price index above 100 is above its selected reference period, not above a market-wide average. The midpoint is an unweighted mean of the two reported transaction-price averages. F2P accessibility describes items rather than the account types of traders. Trends and associations alone cannot isolate enforcement from updates, seasonality, player activity, demand, or changes in data coverage.', '']
    report.write_text('\n'.join(lines), encoding='utf-8')
    return comparison, sensitivity
