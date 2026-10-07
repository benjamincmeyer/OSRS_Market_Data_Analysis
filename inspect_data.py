"""Inspect the historical dataset and save its price distribution chart."""
import matplotlib.pyplot as plt
from config import FIGURES_DIR

def inspect_structure(df):
    """
    Review the basic structure and contents of the dataset.
    """
    print()
    print('=' * 60)
    print('DATASET STRUCTURE')
    print('=' * 60)
    print('\nDataset shape:')
    print(df.shape)
    print('\nColumn names:')
    print(df.columns.tolist())
    print('\nData types:')
    print(df.dtypes)
    print('\nDataset information:')
    df.info()
    print('\nFirst five rows:')
    print(df.head())
    print('\nUnique items:')
    print(df['item_name'].unique())
    print('\nObservations per item:')
    print(df['item_name'].value_counts())

def inspect_data_quality(df):
    """
    Check the raw dataset for missing values and duplicate rows.
    """
    print()
    print('=' * 60)
    print('DATA QUALITY CHECKS')
    print('=' * 60)
    print('\nMissing values by column:')
    print(df.isnull().sum())
    print('\nDuplicate rows:')
    print(df.duplicated().sum())
    duplicate_item_dates = df.duplicated(subset=['item_id', 'timestamp']).sum()
    print('\nDuplicate item/timestamp combinations:')
    print(duplicate_item_dates)

def descriptive_statistics(df):
    """
    Generate overall and item-level descriptive statistics.
    """
    print()
    print('=' * 60)
    print('DESCRIPTIVE STATISTICS')
    print('=' * 60)
    item_summary = df.groupby('item_name').agg(observations=('timestamp', 'count'), high_price_mean=('avgHighPrice', 'mean'), high_price_median=('avgHighPrice', 'median'), high_price_std=('avgHighPrice', 'std'), high_price_min=('avgHighPrice', 'min'), high_price_max=('avgHighPrice', 'max'), low_price_mean=('avgLowPrice', 'mean'), high_volume_mean=('highPriceVolume', 'mean'), low_volume_mean=('lowPriceVolume', 'mean')).round(2)
    print('\nSummary statistics by item:')
    print(item_summary)
    return item_summary

def plot_price_distribution(df, show=False):
    """
    Create a box plot showing the distribution of
    average high prices across items.
    """
    plt.figure(figsize=(12, 6))
    df.boxplot(column='avgHighPrice', by='item_name', rot=45)
    plt.title('Distribution of Average High Prices by Item')
    plt.suptitle('')
    plt.xlabel('Item')
    plt.ylabel('Average High Price (GP)')
    plt.tight_layout()
    output_dir = FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / 'price_distribution.png', dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()
