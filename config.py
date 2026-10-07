"""Shared paths and item groups for the historical analysis."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
RAW_FILE = DATA_DIR / 'osrs_market_data_raw.csv'
PROCESSED_FILE = DATA_DIR / 'osrs_market_data_processed.csv'
FIGURES_DIR = ROOT / 'figures'
F2P_ITEMS = ['Yew logs', 'Swordfish', 'Ruby necklace', 'Pie shell']
P2P_ITEMS = ['Shark', 'Dragon bones', "Zulrah's scales", 'Blood rune']
ITEMS = F2P_ITEMS + P2P_ITEMS
BASE_URL = 'https://prices.runescape.wiki/api/v1/osrs'
HISTORICAL_START = '2025-08-26'
HISTORICAL_END = '2026-08-25'
