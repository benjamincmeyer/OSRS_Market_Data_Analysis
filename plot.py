"""Save the original indexed price and volume charts."""
import matplotlib.pyplot as plt
from config import FIGURES_DIR, F2P_ITEMS, P2P_ITEMS

def plot_indexed_prices(df, items, title, output_file, show=False):
    """
    Plot indexed price changes over time for a selected
    group of OSRS items.

    Each item begins with an indexed price of 100.
    """
    plot_df = df[df['item_name'].isin(items)].copy()
    plt.figure(figsize=(14, 8))
    for item_name in items:
        item_df = plot_df[plot_df['item_name'] == item_name].sort_values('date')
        plt.plot(item_df['date'], item_df['indexed_price'], label=item_name, linewidth=1.5)
    plt.axhline(y=100, linestyle='--', linewidth=1)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Indexed Price (Starting Price = 100)')
    plt.legend(title='Item', loc='best')
    plt.grid(alpha=0.25)
    plt.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()

def plot_indexed_volumes(df, items, title, output_file, show=False):
    """
    Plot indexed trading volume changes over time for
    a selected group of OSRS items.

    Each item's indexed volume is relative to the average
    total trading volume of its first seven observations.
    """
    plot_df = df[df['item_name'].isin(items)].copy()
    plt.figure(figsize=(14, 8))
    for item_name in items:
        item_df = plot_df[plot_df['item_name'] == item_name].sort_values('date')
        plt.plot(item_df['date'], item_df['indexed_volume'], label=item_name, linewidth=1.5)
    plt.axhline(y=100, linestyle='--', linewidth=1)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Indexed Volume (First 7-Day Average = 100)')
    plt.legend(title='Item', loc='best')
    plt.grid(alpha=0.25)
    plt.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()

def plot_all(df, show=False):
    for group, items in [('F2P', F2P_ITEMS), ('P2P', P2P_ITEMS)]:
        prefix = group.lower()
        plot_indexed_prices(df, items, f'Indexed Grand Exchange Prices - {group} Items', FIGURES_DIR / f'{prefix}_indexed_price_time_series.png', show)
        plot_indexed_volumes(df, items, f'Indexed Grand Exchange Trading Volume - {group} Items', FIGURES_DIR / f'{prefix}_indexed_volume_time_series.png', show)
