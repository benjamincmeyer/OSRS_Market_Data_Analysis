"""Collect a new dated market snapshot without replacing the historical study."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time
import json
import hashlib
import platform
from importlib.metadata import version
import pandas as pd
import requests
from config import BASE_URL, ITEMS, DATA_DIR
from validate import validate_market_data

HEADERS = {'User-Agent': 'OSRS-Market-Data-Analysis (github.com/benjamincmeyer/OSRS_Market_Data_Analysis)'}

def get_item_mapping():
    """
    Retrieve item metadata from the OSRS Wiki API.
    """
    url = f'{BASE_URL}/mapping'
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    mapping = response.json()
    if not isinstance(mapping, list) or not mapping:
        raise ValueError('API mapping must be a nonempty list.')
    for item in mapping:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str) or not item['name'].strip() or type(item.get('id')) is not int or item['id'] <= 0:
            raise ValueError('API mapping contains an invalid item name or ID.')
    return mapping

def resolve_item_ids(mapping, item_names):
    """
    Match selected item names to their OSRS item IDs.
    """
    name_to_id = {item['name']: item['id'] for item in mapping}
    for name in item_names:
        if sum(item['name'] == name for item in mapping) > 1:
            raise ValueError(f'API mapping contains ambiguous entries for {name}.')
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
    if not isinstance(data, dict) or not isinstance(data.get('data'), list) or not data['data']:
        raise ValueError(f'API timeseries for item {item_id} must contain a nonempty data list.')
    required = {'timestamp', 'avgHighPrice', 'avgLowPrice', 'highPriceVolume', 'lowPriceVolume'}
    if any(not isinstance(row, dict) or not required.issubset(row) for row in data['data']):
        raise ValueError(f'API timeseries for item {item_id} contains malformed observations.')
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
            all_rows.append({**observation, 'item_id': item_id, 'item_name': item_name})
        time.sleep(0.5)
    df = pd.DataFrame(all_rows)
    validate_market_data(df, expected_items=items)
    return df

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Output CSV path; default is a new timestamped snapshot directory.')
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = args.output or DATA_DIR / 'snapshots' / stamp / 'osrs_market_data_raw.csv'
    metadata_path = output.with_suffix('.metadata.json')
    if output.exists() or metadata_path.exists():
        parser.error(f'Refusing to replace existing snapshot data or metadata: {output}')
    started = datetime.now(timezone.utc).isoformat()
    try:
        df = collect_market_data(ITEMS)
        coverage = validate_market_data(df, expected_items=ITEMS)
    except (ValueError, requests.RequestException) as error:
        parser.error(f'Collection failed: {error}')
    metadata = {
        'collection_started_utc': started,
        'collection_completed_utc': datetime.now(timezone.utc).isoformat(),
        'api_base_url': BASE_URL,
        'endpoints': ['/mapping', '/timeseries'],
        'timestep': '24h',
        'item_ids': dict(zip(df['item_name'], df['item_id'].map(int))),
        'coverage': coverage,
        'python_version': platform.python_version(),
        'dependencies': {name: version(name) for name in ('pandas', 'requests', 'numpy')},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8', newline='') as stream:
        df.to_csv(stream, index=False)
    metadata['csv_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    with metadata_path.open('x', encoding='utf-8') as stream:
        json.dump(metadata, stream, indent=2)
    print(f'Saved new snapshot: {output.resolve()}')

if __name__ == '__main__':
    main()
