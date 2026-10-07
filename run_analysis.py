"""Reproduce the saved historical study without accessing the network."""
import argparse
import pandas as pd
from config import ROOT, RAW_FILE, PROCESSED_FILE, ITEMS, HISTORICAL_START, HISTORICAL_END

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
    from compare import generate_comparisons
    from enforcement import generate_enforcement, align_months
    df = pd.read_csv(RAW_FILE)
    try:
        processed = process_data(df, expected_items=ITEMS, expected_start=HISTORICAL_START, expected_end=HISTORICAL_END)
        bans = pd.read_csv(ROOT / 'data' / 'enforcement_monthly.csv')
        align_months(processed, bans)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    inspect_structure(df)
    inspect_data_quality(df)
    descriptive_statistics(df)
    plot_price_distribution(df, show=args.show)
    processed.to_csv(PROCESSED_FILE, index=False)
    plot_all(processed, show=args.show)
    generate_comparisons(processed, show=args.show)
    generate_enforcement(processed, show=args.show, bans=bans)
    print(f'Analysis complete: {len(processed):,} observations; eight figures, four comparison tables, and two analysis reports saved.')

if __name__ == '__main__':
    main()
