import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("member_module", ROOT/"scripts/build_error_report.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ErrorReportTests(unittest.TestCase):
    def test_counts_and_zero_support(self):
        rows=[{'id':'validation:00001','gold':['Arbitration'],'predicted':['Arbitration']},
              {'id':'validation:00002','gold':['Arbitration'],'predicted':[]},
              {'id':'validation:00003','gold':[],'predicted':['Arbitration']}]
        stats={r['label']:r for r in m.summarize_predictions(rows)}
        a=stats['Arbitration'];self.assertEqual((a['tp'],a['fp'],a['fn']),(1,1,1));self.assertEqual(a['f1'],.5)
        self.assertEqual(stats['Content removal']['f1'],0)
    def test_duplicate_ids_rejected(self):
        r={'id':'validation:00001','gold':[],'predicted':[]}
        with self.assertRaises(ValueError):m.summarize_predictions([r,r])
    def test_final_test_and_unknown_labels_rejected(self):
        for row in [{'id':'test:00001','gold':[],'predicted':[]},
                    {'id':'validation:00001','gold':['invented'],'predicted':[]}]:
            with self.assertRaises(ValueError):m.summarize_predictions([row])
    def test_mismatched_metric_file_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'pred.jsonl').write_text(json.dumps({'id':'validation:00001','gold':[],'predicted':[]})+'\n')
            (p/'metrics.json').write_text(json.dumps({'n':1,'split':'validation','macro_f1_8':.9}))
            with self.assertRaises(ValueError):m.build(p/'pred.jsonl',p/'metrics.json')
