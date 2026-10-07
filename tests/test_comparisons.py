import unittest
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare import period_comparisons, endpoint_sensitivity


class ComparisonTests(unittest.TestCase):
    def test_unequal_periods_compare_daily_means(self):
        dates = pd.date_range('2025-09-01', '2026-07-31')
        prices = np.where(dates.year == 2025, 10, np.where(dates.month <= 6, 15, 20))
        volumes = np.where(dates.year == 2025, 100, np.where(dates.month <= 6, 50, 25))
        data = pd.DataFrame({'item_name': 'Yew logs', 'date': dates, 'midpoint_price': prices, 'total_volume': volumes})
        row = period_comparisons(data).iloc[0]
        self.assertEqual(row['early_days'], 122)
        self.assertEqual(row['first_half_2026_days'], 181)
        self.assertEqual(row['late_days'], 31)
        self.assertEqual(row['first_half_2026_midpoint_price_change_pct'], 50)
        self.assertEqual(row['late_total_volume_change_pct'], -75)
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            period_comparisons(data.iloc[1:])

    def test_endpoint_windows_are_sorted_and_averaged(self):
        data = pd.DataFrame({'item_name': 'Yew logs', 'date': pd.date_range('2025-01-01', periods=56), 'midpoint_price': [10] * 28 + [20] * 28, 'total_volume': [1] * 28 + [3] * 28})
        results = endpoint_sensitivity(data.iloc[::-1])
        self.assertTrue(results.loc[results.metric.eq('midpoint_price'), 'change_pct'].eq(100).all())
        self.assertTrue(results.loc[results.metric.eq('total_volume'), 'change_pct'].eq(200).all())
        with self.assertRaisesRegex(ValueError, 'nonoverlapping'):
            endpoint_sensitivity(data.iloc[:55])


if __name__ == '__main__':
    unittest.main()
