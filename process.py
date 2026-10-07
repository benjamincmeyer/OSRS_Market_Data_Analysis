"""Original feature construction and normalization formulas."""
import pandas as pd
import numpy as np
from validate import validate_market_data, validate_baselines

def convert_timestamp(df):
    """
    Convert Unix timestamps into readable datetime values.
    """
    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    return df

def construct_features(df):
    """
    Create analytical features from the raw market variables.
    """
    df['midpoint_price'] = (df['avgHighPrice'] + df['avgLowPrice']) / 2
    df['total_volume'] = df['highPriceVolume'] + df['lowPriceVolume']
    return df

def normalize_prices(df):
    """
    Normalize midpoint prices so that each item's
    first observation begins at an index value of 100.
    """
    df = df.sort_values(by=['item_name', 'date']).copy()
    starting_prices = df.groupby('item_name')['midpoint_price'].transform('first')
    validate_baselines(starting_prices, 'Price')
    df['indexed_price'] = df['midpoint_price'] / starting_prices * 100
    return df

def normalize_volumes(df):
    """
    Normalize total trading volume using the average
    volume from each item's first seven observations
    as the baseline value of 100.
    """
    df = df.sort_values(by=['item_name', 'date']).copy()
    baseline_volumes = df.groupby('item_name')['total_volume'].transform(lambda x: x.iloc[:7].mean())
    validate_baselines(baseline_volumes, 'Volume')
    df['indexed_volume'] = df['total_volume'] / baseline_volumes * 100
    return df

def process_data(df, **validation_options):
    validate_market_data(df, **validation_options)
    df = df.copy()
    for transform in (convert_timestamp, construct_features, normalize_prices, normalize_volumes):
        df = transform(df)
    features = df[['midpoint_price', 'total_volume', 'indexed_price', 'indexed_volume']]
    if not np.isfinite(features.to_numpy()).all() or features.lt(0).any().any():
        raise ValueError('Feature construction produced non-finite values.')
    return df
