from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------
# Configuration
# ----------------------------

DATA_FILE = Path("data") / "osrs_market_data_raw.csv"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

# ----------------------------
# Load Dataset
# ----------------------------

def load_data():
    """
    Load the raw OSRS market dataset.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Could not find dataset: {DATA_FILE.resolve()}"
        )

    df = pd.read_csv(DATA_FILE)

    return df


# ----------------------------
# Structural Exploration
# ----------------------------

def inspect_structure(df):
    """
    Review the basic structure and contents of the dataset.
    """

    print()
    print("=" * 60)
    print("DATASET STRUCTURE")
    print("=" * 60)

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nDataset information:")
    df.info()

    print("\nFirst five rows:")
    print(df.head())

    print("\nUnique items:")
    print(df["item_name"].unique())

    print("\nObservations per item:")
    print(df["item_name"].value_counts())


# ----------------------------
# Data Quality Checks
# ----------------------------

def inspect_data_quality(df):
    """
    Check the raw dataset for missing values and duplicate rows.
    """

    print()
    print("=" * 60)
    print("DATA QUALITY CHECKS")
    print("=" * 60)

    print("\nMissing values by column:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    duplicate_item_dates = df.duplicated(
        subset=["item_id", "timestamp"]
    ).sum()

    print("\nDuplicate item/timestamp combinations:")
    print(duplicate_item_dates)


# ----------------------------
# Descriptive Statistics
# ----------------------------

def descriptive_statistics(df):
    """
    Generate overall and item-level descriptive statistics.
    """

    print()
    print("=" * 60)
    print("DESCRIPTIVE STATISTICS")
    print("=" * 60)

    item_summary = (
        df.groupby("item_name")
        .agg(
            observations=("timestamp", "count"),
            high_price_mean=("avgHighPrice", "mean"),
            high_price_median=("avgHighPrice", "median"),
            high_price_std=("avgHighPrice", "std"),
            high_price_min=("avgHighPrice", "min"),
            high_price_max=("avgHighPrice", "max"),
            low_price_mean=("avgLowPrice", "mean"),
            high_volume_mean=("highPriceVolume", "mean"),
            low_volume_mean=("lowPriceVolume", "mean")
        )
        .round(2)
    )

    print("\nSummary statistics by item:")
    print(item_summary)

    return item_summary


# ----------------------------
# Visualization 1
# Price Distribution
# ----------------------------

def plot_price_distribution(df):
    """
    Create a box plot showing the distribution of
    average high prices across items.
    """

    plt.figure(figsize=(12, 6))

    df.boxplot(
        column="avgHighPrice",
        by="item_name",
        rot=45
    )

    plt.title("Distribution of Average High Prices by Item")
    plt.suptitle("")
    plt.xlabel("Item")
    plt.ylabel("Average High Price (GP)")
    plt.tight_layout()
    output_dir = Path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "price_distribution.png", dpi=300, bbox_inches="tight")
    plt.show()


# ----------------------------
# Main Program
# ----------------------------

def main():

    print()
    print("=" * 60)
    print("OSRS MARKET DATA - EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    print(f"\nLoading dataset from:")
    print(DATA_FILE.resolve())

    df = load_data()

    inspect_structure(df)

    inspect_data_quality(df)

    descriptive_statistics(df)

    print("\nCreating price distribution box plot...")
    plot_price_distribution(df)

if __name__ == "__main__":
    main()
