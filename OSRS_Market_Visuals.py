from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------
# Configuration
# ----------------------------

DATA_FILE = Path("data") / "osrs_market_data_processed.csv"

OUTPUT_DIR = Path("figures")

F2P_OUTPUT_FILE = OUTPUT_DIR / "f2p_indexed_price_time_series.png"
P2P_OUTPUT_FILE = OUTPUT_DIR / "p2p_indexed_price_time_series.png"


F2P_ITEMS = [
    "Yew logs",
    "Swordfish",
    "Ruby necklace",
    "Pie shell",
]

P2P_ITEMS = [
    "Shark",
    "Dragon bones",
    "Zulrah's scales",
    "Blood rune",
]


# ----------------------------
# Load Processed Dataset
# ----------------------------

def load_data():
    """
    Load the processed OSRS market dataset.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Could not find dataset: {DATA_FILE.resolve()}"
        )

    df = pd.read_csv(DATA_FILE)

    # Convert the saved date column back into datetime format
    df["date"] = pd.to_datetime(df["date"])

    return df


# ----------------------------
# Time-Series Plot
# ----------------------------

def plot_indexed_prices(df, items, title, output_file):
    """
    Plot indexed price changes over time for a selected
    group of OSRS items.

    Each item begins with an indexed price of 100.
    """

    # Keep only the items assigned to this graph
    plot_df = df[
        df["item_name"].isin(items)
    ].copy()

    plt.figure(figsize=(14, 8))

    for item_name in items:

        item_df = plot_df[
            plot_df["item_name"] == item_name
        ].sort_values("date")

        plt.plot(
            item_df["date"],
            item_df["indexed_price"],
            label=item_name,
            linewidth=1.5
        )

    # Reference line representing each item's starting price
    plt.axhline(
        y=100,
        linestyle="--",
        linewidth=1
    )

    plt.title(title)

    plt.xlabel("Date")
    plt.ylabel("Indexed Price (Starting Price = 100)")

    plt.legend(
        title="Item",
        loc="best"
    )

    plt.grid(
        alpha=0.25
    )

    plt.tight_layout()

    # Save a high-resolution copy
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    # Close the figure before creating the next graph
    plt.close()


# ----------------------------
# Main Program
# ----------------------------

def main():

    print()
    print("=" * 60)
    print("OSRS MARKET DATA - TIME-SERIES VISUALIZATION")
    print("=" * 60)

    df = load_data()

    print("\nCreating F2P indexed price time series...")

    plot_indexed_prices(
        df=df,
        items=F2P_ITEMS,
        title="Indexed Grand Exchange Prices - F2P Items",
        output_file=F2P_OUTPUT_FILE
    )

    print("\nCreating P2P indexed price time series...")

    plot_indexed_prices(
        df=df,
        items=P2P_ITEMS,
        title="Indexed Grand Exchange Prices - P2P Items",
        output_file=P2P_OUTPUT_FILE
    )

    print()
    print("Figures saved to:")

    print(F2P_OUTPUT_FILE.resolve())
    print(P2P_OUTPUT_FILE.resolve())

    print()
    print("=" * 60)
    print("TIME-SERIES VISUALIZATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()