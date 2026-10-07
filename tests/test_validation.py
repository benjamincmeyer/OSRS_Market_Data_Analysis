"""Offline regression and failure-case tests for the market workflow."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import collect
import config
import run_analysis
from process import process_data, normalize_prices, normalize_volumes
from validate import validate_market_data


def sample(days=7):
    return pd.DataFrame({
        'timestamp': 1756166400 + np.arange(days) * 86400,
        'avgHighPrice': np.full(days, 12),
        'avgLowPrice': np.full(days, 8),
        'highPriceVolume': np.full(days, 3),
        'lowPriceVolume': np.full(days, 7),
        'item_id': np.full(days, 1),
        'item_name': ['Test'] * days,
    })


class ValidationTests(unittest.TestCase):
    def test_historical_snapshot_regression(self):
        raw = pd.read_csv(config.RAW_FILE)
        expected = pd.read_csv(config.PROCESSED_FILE, parse_dates=['date'])
        actual = process_data(raw, expected_items=config.ITEMS, expected_start=config.HISTORICAL_START, expected_end=config.HISTORICAL_END)
        pd.testing.assert_frame_equal(actual.reset_index(drop=True), expected, check_dtype=False, check_exact=False, rtol=1e-10, atol=1e-10)
        self.assertNotIn('date', raw.columns)

    def test_invalid_measurements(self):
        cases = [('timestamp', -1), ('timestamp', 1.5), ('timestamp', 1e30), ('avgHighPrice', 0), ('avgLowPrice', -2), ('highPriceVolume', -1), ('lowPriceVolume', 0.5), ('item_id', 0), ('avgHighPrice', np.inf), ('avgHighPrice', np.nan), ('item_name', ''), ('item_name', None)]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                data = sample().astype({field: object}) if field == 'item_name' else sample().astype({field: float})
                data.loc[0, field] = value
                with self.assertRaises(ValueError):
                    validate_market_data(data)

    def test_missing_fields_and_empty_data(self):
        for data in [sample().drop(columns='timestamp'), sample().iloc[:0]]:
            with self.assertRaises(ValueError):
                validate_market_data(data)

    def test_duplicate_and_missing_days(self):
        duplicate = pd.concat([sample(), sample().iloc[:1]], ignore_index=True)
        gap = sample(8).drop(index=3)
        for data in [duplicate, gap, sample(6)]:
            with self.assertRaises(ValueError):
                validate_market_data(data)

    def test_identifier_and_coverage_mismatches(self):
        second = sample().assign(item_id=2, item_name='Other')
        bad_id = pd.concat([sample(), second.assign(item_id=1)], ignore_index=True)
        shifted = pd.concat([sample(), second.assign(timestamp=second.timestamp + 86400)], ignore_index=True)
        for data in [bad_id, shifted]:
            with self.assertRaises(ValueError):
                validate_market_data(data)
        with self.assertRaisesRegex(ValueError, 'item selection'):
            validate_market_data(sample(), expected_items=['Absent'])
        with self.assertRaisesRegex(ValueError, 'end date'):
            validate_market_data(sample(), expected_end='2026-08-25')

    def test_zero_baseline_and_zero_volume_days(self):
        data = sample().assign(highPriceVolume=0, lowPriceVolume=0)
        with self.assertRaisesRegex(ValueError, 'volume baseline'):
            process_data(data)
        data.loc[0, 'lowPriceVolume'] = 1
        self.assertTrue(np.isfinite(process_data(data)['indexed_volume']).all())

    def test_direct_normalization_rejects_invalid_baselines(self):
        data = sample().assign(date=pd.to_datetime(sample().timestamp, unit='s'), midpoint_price=0, total_volume=0)
        for operation in [normalize_prices, normalize_volumes]:
            with self.assertRaisesRegex(ValueError, 'baseline'):
                operation(data)

    def test_malformed_api_responses(self):
        for payload in [{}, {'data': []}, {'data': [{}]}, {'data': [None]}]:
            with self.subTest(payload=payload), patch('collect.requests.get', return_value=Mock(json=lambda: payload)):
                with self.assertRaisesRegex(ValueError, 'API timeseries'):
                    collect.get_timeseries(1)
        for payload in [None, {}, [], [{'name': 'Test', 'id': '1'}]]:
            with self.subTest(payload=payload), patch('collect.requests.get', return_value=Mock(json=lambda: payload)):
                with self.assertRaisesRegex(ValueError, 'API mapping'):
                    collect.get_item_mapping()

    def test_reject_invalid_data_before_output_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            raw = Path(temp) / 'raw.csv'
            processed = Path(temp) / 'processed.csv'
            sample().drop(columns='timestamp').to_csv(raw, index=False)
            processed.write_text('preserve me', encoding='utf-8')
            with patch.object(run_analysis, 'RAW_FILE', raw), patch.object(run_analysis, 'PROCESSED_FILE', processed), patch.object(sys, 'argv', ['run_analysis.py']), patch('inspect_data.plot_price_distribution') as plot:
                with self.assertRaises(SystemExit) as error:
                    run_analysis.main()
                self.assertEqual(error.exception.code, 2)
                plot.assert_not_called()
            self.assertEqual(processed.read_text(encoding='utf-8'), 'preserve me')

    def test_collection_metadata_and_collision_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            with patch.object(collect, 'DATA_DIR', directory), patch.object(collect, 'ITEMS', ['Test']), patch.object(collect, 'collect_market_data', return_value=sample()), patch.object(sys, 'argv', ['collect.py']):
                collect.main()
            output = next(directory.glob('snapshots/*/*.csv'))
            metadata = json.loads(output.with_suffix('.metadata.json').read_text())
            self.assertEqual(metadata['csv_sha256'], hashlib.sha256(output.read_bytes()).hexdigest())
            self.assertEqual(metadata['coverage']['observations'], 7)
            self.assertEqual(metadata['timestep'], '24h')
            with patch.object(sys, 'argv', ['collect.py', '--output', str(output)]), patch.object(collect, 'collect_market_data') as fetch:
                with self.assertRaises(SystemExit):
                    collect.main()
                fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
