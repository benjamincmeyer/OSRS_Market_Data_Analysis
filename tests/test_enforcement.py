import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from enforcement import align_months, correlations, validate_enforcement


def fixture_bans(months=('2026-02','2026-03')):
    return pd.DataFrame({'month':months, 'macro_bans':[10]*len(months), 'rwt_bans':[2]*len(months), 'wealth_removed_gp':[100]*len(months), 'period_basis':'monthly', 'verification_status':'verified_archived_jagex', 'source_url':'https://example.org/fixture'})


class EnforcementTests(unittest.TestCase):
    def test_complete_month_alignment_excludes_partial_months(self):
        dates = pd.date_range('2026-02-01','2026-03-15')
        data = pd.DataFrame({'date':dates, 'item_name':'Test', 'midpoint_price':10, 'total_volume':100})
        result = align_months(data, fixture_bans(('2026-02',)))
        self.assertEqual(result['observed_days'].tolist(), [28])
        self.assertEqual(result['mean_daily_volume'].tolist(), [100])
        with self.assertRaisesRegex(ValueError, 'complete market coverage'):
            align_months(data, fixture_bans())

    def test_bad_periods_and_sources_rejected(self):
        for column,value in [('period_basis','year_to_date'), ('verification_status','unverified'), ('source_url',np.nan), ('macro_bans',np.inf), ('rwt_bans',-1), ('month','2026-13')]:
            with self.subTest(column=column):
                frame = fixture_bans().astype({column:object if isinstance(value,str) else float}) if column not in ('month','source_url') else fixture_bans()
                frame.loc[0,column] = value
                with self.assertRaises(ValueError): validate_enforcement(frame)
        with self.assertRaisesRegex(ValueError,'unique'):
            validate_enforcement(fixture_bans(('2026-02','2026-02')))
        with self.assertRaisesRegex(ValueError,'consecutive'):
            validate_enforcement(fixture_bans(('2026-02','2026-04')))

    def test_correlations_count_changes_and_handle_constants(self):
        x = np.array([1,2,4,7,11,16])
        data = pd.DataFrame({'item_name':'Test','month':pd.period_range('2026-02',periods=6,freq='M').astype(str), 'macro_bans':x,'rwt_bans':np.ones(6),'mean_daily_volume':x*3,'mean_midpoint_price':x*2})
        result = correlations(data)
        macro = result[result['enforcement_metric'].eq('macro_bans')]
        self.assertTrue(np.allclose(macro['pearson_r'],1))
        self.assertEqual(set(result.loc[result['transform'].eq('levels'),'n_months_or_changes']),{6})
        self.assertEqual(set(result.loc[result['transform'].eq('first_differences'),'n_months_or_changes']),{5})
        self.assertTrue(result.loc[result['enforcement_metric'].eq('rwt_bans'),'pearson_r'].isna().all())


if __name__ == '__main__': unittest.main()
