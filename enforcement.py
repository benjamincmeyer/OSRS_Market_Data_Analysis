"""Align verified monthly enforcement figures with complete market months."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import ROOT, FIGURES_DIR, F2P_ITEMS, P2P_ITEMS

COUNTS = ('macro_bans', 'rwt_bans', 'wealth_removed_gp')


def validate_enforcement(df):
    required = {'month','period_basis','verification_status','source_url', *COUNTS}
    if df.empty or not required.issubset(df.columns):
        raise ValueError('Enforcement input is empty or missing required fields.')
    if not df['month'].map(lambda value: isinstance(value, str) and len(value) == 7).all():
        raise ValueError('Enforcement months must use YYYY-MM.')
    months = pd.to_datetime(df['month'], format='%Y-%m', errors='coerce')
    if months.isna().any() or df['month'].duplicated().any():
        raise ValueError('Enforcement months must be valid and unique.')
    if not df['period_basis'].eq('monthly').all():
        raise ValueError('Cumulative enforcement totals cannot be used as monthly observations.')
    if not df['verification_status'].eq('verified_archived_jagex').all() or df['source_url'].isna().any():
        raise ValueError('Enforcement observations need verified source provenance.')
    for column in COUNTS:
        if not pd.api.types.is_numeric_dtype(df[column]) or not np.isfinite(df[column]).all() or df[column].lt(0).any():
            raise ValueError(f'{column} must contain finite nonnegative values.')
    ordered = pd.PeriodIndex(months.sort_values(), freq='M').asi8
    if len(ordered) > 1 and not np.diff(ordered).tolist() == [1] * (len(ordered)-1):
        raise ValueError('Enforcement months must be consecutive for change comparisons.')


def align_months(market, bans):
    validate_enforcement(bans)
    market = market.copy()
    market['month'] = market['date'].dt.to_period('M').astype(str)
    monthly = market.groupby(['item_name','month']).agg(
        mean_midpoint_price=('midpoint_price','mean'),
        mean_daily_volume=('total_volume','mean'),
        observed_days=('date','nunique'),
    ).reset_index()
    monthly['calendar_days'] = pd.to_datetime(monthly['month']).dt.days_in_month
    complete = monthly[monthly['observed_days'].eq(monthly['calendar_days'])]
    aligned = complete.merge(bans, on='month', how='inner', validate='many_to_one')
    items = market['item_name'].unique()
    if len(aligned) != len(items) * len(bans):
        raise ValueError('Every enforcement month needs complete market coverage for every item.')
    return aligned.sort_values(['item_name','month']).reset_index(drop=True)


def correlations(aligned):
    rows = []
    for item, data in aligned.groupby('item_name'):
        data = data.sort_values('month')
        for enforcement in ('macro_bans','rwt_bans'):
            for metric in ('mean_midpoint_price','mean_daily_volume'):
                for transform in ('levels','first_differences'):
                    x, y = data[enforcement], data[metric]
                    if transform == 'first_differences':
                        x, y = x.diff().iloc[1:], y.diff().iloc[1:]
                    r = x.corr(y) if len(x) >= 3 and x.nunique() > 1 and y.nunique() > 1 else np.nan
                    rows.append({'item_name':item,'enforcement_metric':enforcement,'market_metric':metric,'transform':transform,'n_months_or_changes':len(x),'pearson_r':r})
    return pd.DataFrame(rows)


def generate_enforcement(processed, show=False, bans=None):
    if bans is None:
        bans = pd.read_csv(ROOT / 'data' / 'enforcement_monthly.csv')
    aligned = align_months(processed, bans)
    association = correlations(aligned)
    tables = ROOT / 'tables'
    tables.mkdir(exist_ok=True)
    aligned.to_csv(tables / 'monthly_enforcement_market.csv', index=False)
    association.to_csv(tables / 'enforcement_associations.csv', index=False)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), layout='constrained')
    dates = pd.to_datetime(bans['month'])
    axes[0,0].bar(dates, bans['macro_bans']/1e6, width=18, color='#196b8b')
    axes[0,0].set(title='Monthly OSRS macro bans', ylabel='Reported bans (millions)')
    axes[0,1].bar(dates, bans['rwt_bans']/1000, width=18, color='#8a4d86')
    axes[0,1].set(title='Monthly OSRS RWT bans', ylabel='Reported bans (thousands)')
    for ax, (group, items) in zip(axes[1], [('F2P-accessible',F2P_ITEMS), ('Members-only',P2P_ITEMS)]):
        for item in items:
            data = aligned[aligned['item_name'].eq(item)].sort_values('month')
            ax.plot(pd.to_datetime(data['month']), data['mean_daily_volume']/data['mean_daily_volume'].iloc[0]*100, marker='o', label=item)
        ax.axhline(100, linestyle='--', color='#666666', linewidth=0.8)
        ax.set(title=f'{group} items: observed daily volume', ylabel='Monthly mean index (February = 100)')
        ax.legend(fontsize=8)
    # Use a common vertical scale for the two market panels.
    upper = max(ax.get_ylim()[1] for ax in axes[1])
    for ax in axes[1]: ax.set_ylim(0, upper)
    for ax in axes.flat:
        ax.set_xticks(dates, labels=dates.dt.strftime('%b'), rotation=0)
        ax.grid(axis='y', alpha=0.15)
    fig.suptitle('Enforcement and observed market activity | verified months of 2026', fontsize=15)
    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(FIGURES_DIR / 'enforcement_market_timeline.png', dpi=180)
    if show: plt.show()
    plt.close(fig)
    lines = ['# Enforcement and Market Associations', '', 'The analysis aligns six verified calendar months, February–July 2026. January is excluded because its cited archive could not be verified. Each month has complete daily market coverage for all eight items; incomplete August months are excluded. No missing enforcement month is treated as zero.', '', '## Verified monthly context', '', '| Month | Macro bans | RWT bans | Wealth removed (GP) |', '| --- | ---: | ---: | ---: |']
    for row in bans.to_dict('records'):
        lines.append(f'| {row["month"]} | {row["macro_reported"]} | {row["rwt_bans"]:,} | {row["wealth_reported"]} |')
    lines += ['', 'M denotes millions and T trillions. These are monthly OSRS figures, not cumulative year-to-date totals. Rounded source values remain approximate. See the [source audit](enforcement_source_audit.md) for URLs, transcription discrepancies, and missing account-category breakdowns.', '', '![Aligned enforcement and market activity](../figures/enforcement_market_timeline.png)', '', 'Market volume is a mean per observed day, while bans are counts per calendar month. The bottom panels show each item relative to its February mean. This display supports timing comparisons rather than a direct comparison of units.', '', '## Descriptive correlations', '', 'Pearson correlations below use six monthly level observations or five consecutive month-to-month changes. First differences subtract the prior monthly value; they are not percentage changes. They reduce the influence of shared trends without controlling for other causes.', '', '| Item | Macro / volume levels | RWT / volume levels | Macro / volume changes | RWT / volume changes |', '| --- | ---: | ---: | ---: | ---: |']
    for item in sorted(aligned['item_name'].unique()):
        values = []
        for transform in ('levels','first_differences'):
            for metric in ('macro_bans','rwt_bans'):
                value = association[(association.item_name == item) & (association.market_metric == 'mean_daily_volume') & (association.enforcement_metric == metric) & (association['transform'] == transform)]['pearson_r'].iloc[0]
                values.append(f'{value:+.2f}' if pd.notna(value) else 'Unavailable')
        lines.append('| ' + item + ' | ' + ' | '.join(values) + ' |')
    lines += ['', 'Full correlations, including midpoint prices, are in [enforcement_associations.csv](../tables/enforcement_associations.csv). The aligned monthly observations and source fields are in [monthly_enforcement_market.csv](../tables/monthly_enforcement_market.csv). Wealth removal is excluded from correlations because the source label changes from GP / Gold Removed to Wealth Removed, and continuity of that definition has not been established.', '', '## Interpretation', '', 'The verified macro-ban series peaks in March and falls through July; RWT bans peak in April. Observed volume does not follow a uniform response across the eight items. A positive correlation can arise when ban counts and observed volume both decrease over time. It does not mean that bans increase trading, just as a negative correlation would not establish that bans reduce trading.', '', 'Six months provide very little evidence for a causal or predictive model. Correlations are descriptive, have no reported significance tests, and are sensitive to individual months, shared trends, time dependence, and reporting precision. No lag was selected to maximize an association. Updates, seasonality, player activity, demand, reporting coverage, and other market forces are not controlled.', '', 'Bans measure reported actions rather than the prevalence of bots or enforcement effectiveness. Macro and RWT counts may overlap and are not combined as unique accounts. Account categories must not be matched mechanically to item accessibility. The original broader volume-decline findings remain supported; the enforcement comparison adds context, not an isolated explanation.', '']
    (ROOT / 'docs' / 'enforcement_associations.md').write_text('\n'.join(lines), encoding='utf-8')
    return aligned, association
