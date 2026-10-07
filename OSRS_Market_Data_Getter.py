import time
from pathlib import Path

import requests
import pandas as pd


# ----------------------------
# Configuration
# ----------------------------

BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"

HEADERS = {
    "User-Agent": "DATA645 Unit 2 - @Need Herb on Discord"
}

ITEMS = [
    "Yew logs",
    "Swordfish",
    "Ruby necklace",
    "Pie shell",
    "Shark",
    "Dragon bones",
    "Zulrah's scales",
    "Blood rune",
]

OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "osrs_market_data_raw.csv"


# ----------------------------
# API Functions
# ----------------------------

def get_item_mapping():
    """
    Retrieve item metadata from the OSRS Wiki API.
    """

    url = f"{BASE_URL}/mapping"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def resolve_item_ids(mapping, item_names):
    """
    Match selected item names to their OSRS item IDs.
    """

    name_to_id = {
        item["name"]: item["id"]
        for item in mapping
    }

    resolved = {}

    for name in item_names:
        if name not in name_to_id:
            raise ValueError(
                f"Item not found in API mapping: {name}"
            )

        resolved[name] = name_to_id[name]

    return resolved


def get_timeseries(item_id):
    """
    Retrieve daily historical market data for one item.
    """

    url = f"{BASE_URL}/timeseries"

    params = {
        "id": item_id,
        "timestep": "24h"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["data"]


# ----------------------------
# Data Collection
# ----------------------------

def collect_market_data(items):
    """
    Collect historical market data for all selected items
    and combine the observations into one pandas DataFrame.
    """

    mapping = get_item_mapping()

    item_ids = resolve_item_ids(
        mapping,
        items
    )

    print("\nResolved item IDs:")

    for item_name, item_id in item_ids.items():
        print(f"  {item_name}: {item_id}")

    print()

    all_rows = []

    for item_name, item_id in item_ids.items():

        print(
            f"Downloading {item_name} "
            f"(Item ID: {item_id})..."
        )

        observations = get_timeseries(item_id)

        print(
            f"  Retrieved {len(observations)} observations."
        )

        for observation in observations:

            # Add identifying information to each API observation
            observation["item_id"] = item_id
            observation["item_name"] = item_name

            all_rows.append(observation)

        # Small courtesy delay between API requests
        time.sleep(0.5)

    df = pd.DataFrame(all_rows)

    return df


# ----------------------------
# Main Program
# ----------------------------

def main():

    print("Starting OSRS market data collection...")

    df = collect_market_data(ITEMS)

    # Create the output directory if it does not already exist
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save the raw dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("----------------------------------------")
    print("Data collection complete.")
    print("----------------------------------------")
    print(f"Total observations: {len(df):,}")
    print(f"Output file: {OUTPUT_FILE.resolve()}")

    print()
    print("First five rows:")
    print(df.head())


if __name__ == "__main__":
    main()