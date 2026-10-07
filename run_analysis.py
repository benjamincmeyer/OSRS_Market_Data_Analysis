"""Reproduce the saved historical study without accessing the network."""
import argparse
import pandas as pd
from config import RAW_FILE, PROCESSED_FILE, ITEMS, HISTORICAL_START, HISTORICAL_END

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show', action='store_true', help='Open chart windows in addition to saving figures.')
    args = parser.parse_args()
    if not args.show:
        import matplotlib
        matplotlib.use('Agg')
    from inspect_data import inspect_structure, inspect_data_quality, descriptive_statistics, plot_price_distribution
    from process import process_data
    from plot import plot_all
    df = pd.read_csv(RAW_FILE)
    try:
        processed = process_data(df, expected_items=ITEMS, expected_start=HISTORICAL_START, expected_end=HISTORICAL_END)
    except ValueError as error:
        parser.error(str(error))
    inspect_structure(df)
    inspect_data_quality(df)
    descriptive_statistics(df)
    plot_price_distribution(df, show=args.show)
    processed.to_csv(PROCESSED_FILE, index=False)
    plot_all(processed, show=args.show)
    print(f'Analysis complete: {len(processed):,} observations; five figures saved.')

if __name__ == '__main__':
    main()
