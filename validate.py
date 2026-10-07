"""Validation for complete daily market snapshots; never impute or drop rows."""
import numpy as np
import pandas as pd

NUMERIC_FIELDS = ('timestamp', 'avgHighPrice', 'avgLowPrice', 'highPriceVolume', 'lowPriceVolume', 'item_id')
REQUIRED_FIELDS = (*NUMERIC_FIELDS, 'item_name')


def validate_market_data(df, expected_items=None, expected_start=None, expected_end=None):
    """Require finite measurements, consistent identifiers and aligned daily coverage."""
    if df.empty:
        raise ValueError('Market data is empty.')
    if not df.columns.is_unique:
        raise ValueError('Market data contains duplicate column names.')
    missing = set(REQUIRED_FIELDS) - set(df.columns)
    if missing:
        raise ValueError(f'Missing required fields: {", ".join(sorted(missing))}.')
    for field in NUMERIC_FIELDS:
        values = df[field]
        if not pd.api.types.is_numeric_dtype(values) or pd.api.types.is_bool_dtype(values):
            raise ValueError(f'{field} must be numeric.')
        if values.isna().any() or not np.isfinite(values.to_numpy()).all():
            raise ValueError(f'{field} contains missing or non-finite values.')
        if field in ('timestamp', 'item_id', 'highPriceVolume', 'lowPriceVolume') and (values % 1 != 0).any():
            raise ValueError(f'{field} must contain whole numbers.')
        if field in ('avgHighPrice', 'avgLowPrice', 'item_id') and (values <= 0).any():
            raise ValueError(f'{field} must be strictly positive.')
        if field in ('timestamp', 'highPriceVolume', 'lowPriceVolume') and (values < 0).any():
            raise ValueError(f'{field} cannot be negative.')
    if not df['item_name'].map(lambda value: isinstance(value, str) and bool(value.strip())).all():
        raise ValueError('item_name must contain nonempty names.')
    if df.groupby('item_id')['item_name'].nunique().gt(1).any() or df.groupby('item_name')['item_id'].nunique().gt(1).any():
        raise ValueError('Item IDs and names must have a one-to-one mapping.')
    if expected_items is not None and set(df['item_name']) != set(expected_items):
        raise ValueError('Snapshot items do not match the configured item selection.')
    if df.duplicated(['item_id', 'timestamp']).any():
        raise ValueError('Duplicate item/timestamp observations detected.')
    try:
        dates = pd.to_datetime(df['timestamp'], unit='s', utc=True, errors='coerce')
    except (OverflowError, ValueError) as error:
        raise ValueError('timestamp contains out-of-range dates.') from error
    if dates.isna().any():
        raise ValueError('timestamp contains out-of-range dates.')
    if not dates.eq(dates.dt.normalize()).all():
        raise ValueError('Daily timestamps must fall at midnight UTC.')
    coverage = []
    for name, group in df.groupby('item_name'):
        ordered = group.sort_values('timestamp')
        if len(ordered) < 7:
            raise ValueError(f'{name} needs at least seven daily observations for its volume baseline.')
        if not ordered['timestamp'].diff().dropna().eq(86400).all():
            raise ValueError(f'{name} has gaps or irregular daily intervals.')
        if ordered.iloc[:7][['highPriceVolume', 'lowPriceVolume']].to_numpy(dtype=float).sum() <= 0:
            raise ValueError(f'{name} has a zero first-seven-day volume baseline.')
        coverage.append((ordered['timestamp'].iloc[0], ordered['timestamp'].iloc[-1], len(ordered)))
    if len(set(coverage)) != 1:
        raise ValueError('Items must share the same observation period and daily coverage.')
    start = dates.min().strftime('%Y-%m-%d')
    end = dates.max().strftime('%Y-%m-%d')
    if expected_start is not None and start != expected_start:
        raise ValueError(f'Historical start date must be {expected_start}; received {start}.')
    if expected_end is not None and end != expected_end:
        raise ValueError(f'Historical end date must be {expected_end}; received {end}.')
    return {'observations': len(df), 'items': df['item_name'].nunique(), 'start_date_utc': start, 'end_date_utc': end, 'observations_per_item': coverage[0][2]}


def validate_baselines(values, label):
    if values.isna().any() or not np.isfinite(values.to_numpy()).all() or values.le(0).any():
        raise ValueError(f'{label} baseline must be finite and strictly positive.')
