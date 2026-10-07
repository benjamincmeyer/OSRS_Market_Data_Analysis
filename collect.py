"""Collect a new dated market snapshot without replacing the historical study."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time
import pandas as pd
import requests
from config import BASE_URL, ITEMS, DATA_DIR

HEADERS = {'User-Agent': 'OSRS-Market-Data-Analysis (github.com/benjamincmeyer/OSRS_Market_Data_Analysis)'}

def get_item_mapping():
    """
    Retrieve item metadata from the OSRS Wiki API.
    """
    url = f'{BASE_URL}/mapping'
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()

def resolve_item_ids(mapping, item_names):
    """
    Match selected item names to their OSRS item IDs.
    """
    name_to_id = {item['name']: item['id'] for item in mapping}
    resolved = {}
    for name in item_names:
        if name not in name_to_id:
            raise ValueError(f'Item not found in API mapping: {name}')
        resolved[name] = name_to_id[name]
    return resolved

def get_timeseries(item_id):
    """
    Retrieve daily historical market data for one item.
    """
    url = f'{BASE_URL}/timeseries'
    params = {'id': item_id, 'timestep': '24h'}
    response = requests.get(url, headers=HEADERS, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data['data']

def collect_market_data(items):
    """
    Collect historical market data for all selected items
    and combine the observations into one pandas DataFrame.
    """
    mapping = get_item_mapping()
    item_ids = resolve_item_ids(mapping, items)
    print('\nResolved item IDs:')
    for item_name, item_id in item_ids.items():
        print(f'  {item_name}: {item_id}')
    print()
    all_rows = []
    for item_name, item_id in item_ids.items():
        print(f'Downloading {item_name} (Item ID: {item_id})...')
        observations = get_timeseries(item_id)
        print(f'  Retrieved {len(observations)} observations.')
        for observation in observations:
            observation['item_id'] = item_id
            observation['item_name'] = item_name
            all_rows.append(observation)
        time.sleep(0.5)
    df = pd.DataFrame(all_rows)
    return df

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Output CSV path; default is a new timestamped snapshot directory.')
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = args.output or DATA_DIR / 'snapshots' / stamp / 'osrs_market_data_raw.csv'
    if output.exists():
        parser.error(f'Refusing to replace an existing file: {output}')
    df = collect_market_data(ITEMS)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8', newline='') as stream:
        df.to_csv(stream, index=False)
    print(f'Saved new snapshot: {output.resolve()}')

if __name__ == '__main__':
    main()
