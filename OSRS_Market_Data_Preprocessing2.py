from pathlib import Path

import pandas as pd


# ----------------------------
# Configuration
# ----------------------------

RAW_DATA_FILE = Path("data") / "osrs_market_data_raw.csv"
PROCESSED_DATA_FILE = Path("data") / "osrs_market_data_processed.csv"

# Show all columns in console output
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


# ----------------------------
# Load Raw Dataset
# ----------------------------

def load_data():
    """
    Load the raw OSRS market dataset.
    """

    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Could not find dataset: {RAW_DATA_FILE.resolve()}"
        )

    df = pd.read_csv(RAW_DATA_FILE)

    return df


# ----------------------------
# Timestamp Conversion
# ----------------------------

def convert_timestamp(df):
    """
    Convert Unix timestamps into readable datetime values.
    """

    df["date"] = pd.to_datetime(
        df["timestamp"],
        unit="s"
    )

    return df


# ----------------------------
# Feature Construction
# ----------------------------

def construct_features(df):
    """
    Create analytical features from the raw market variables.
    """

    # Average of the high-price and low-price transaction averages
    df["midpoint_price"] = (
        df["avgHighPrice"] + df["avgLowPrice"]
    ) / 2

    # Combined trading volume
    df["total_volume"] = (
        df["highPriceVolume"] + df["lowPriceVolume"]
    )

    return df


# ----------------------------
# Price Normalization
# ----------------------------

def normalize_prices(df):
    """
    Normalize midpoint prices so that each item's
    first observation begins at an index value of 100.
    """

    # Make sure observations are ordered chronologically
    df = df.sort_values(
        by=["item_name", "date"]
    ).copy()

    # Find the first midpoint price for each item
    starting_prices = df.groupby(
        "item_name"
    )["midpoint_price"].transform("first")

    # Index each item's price relative to its starting value
    df["indexed_price"] = (
        df["midpoint_price"] / starting_prices
    ) * 100

    return df

# ----------------------------
# Volume Normalization
# ----------------------------

def normalize_volumes(df):
    """
    Normalize total trading volume using the average
    volume from each item's first seven observations
    as the baseline value of 100.
    """

    df = df.sort_values(
        by=["item_name", "date"]
    ).copy()

    baseline_volumes = (
        df.groupby("item_name")["total_volume"]
        .transform(
            lambda x: x.iloc[:7].mean()
        )
    )

    df["indexed_volume"] = (
        df["total_volume"] / baseline_volumes
    ) * 100

    return df

# ----------------------------
# Inspect Transformed Dataset
# ----------------------------

def inspect_processed_data(df):
    """
    Display basic information about the transformed dataset.
    """

    print()
    print("=" * 60)
    print("PROCESSED DATASET")
    print("=" * 60)

    print("\nFirst ten rows:")
    print(df.head(10))

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())


# ----------------------------
# Save Processed Dataset
# ----------------------------

def save_data(df):
    """
    Save the transformed dataset as a new CSV file.
    """

    PROCESSED_DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_DATA_FILE,
        index=False
    )

    print()
    print(f"Processed dataset saved to:")
    print(PROCESSED_DATA_FILE.resolve())


# ----------------------------
# Main Program
# ----------------------------

def main():

    print()
    print("=" * 60)
    print("OSRS MARKET DATA - PREPROCESSING")
    print("=" * 60)

    print("\nLoading raw dataset from:")
    print(RAW_DATA_FILE.resolve())

    df = load_data()

    print("\nConverting timestamps...")
    df = convert_timestamp(df)

    print("Constructing analytical features...")
    df = construct_features(df)

    print("Normalizing midpoint prices...")
    df = normalize_prices(df)

    print("Normalizing total trading volume...")
    df = normalize_volumes(df)

    inspect_processed_data(df)

    save_data(df)

    print()
    print("=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()