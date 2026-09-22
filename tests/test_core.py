import tempfile
import unittest
import numpy as np
from pathlib import Path
from clauses.text import segment
from clauses.schema import LABELS
from clauses.evaluate import metrics,with_none
from clauses.export import render_html
from clauses.study import record,summarize
from clauses.model import train,load,analyze,predict_rows,DEFAULT_MODEL
from clauses.data import load_split

class SegmentationTests(unittest.TestCase):
    def test_offsets_and_content(self):
        text='  Dr. Lin paid $3.50.\nWe may end your account!  Final clause'
        rows=segment(text)
        self.assertEqual(len(rows),3)
        for r in rows:self.assertEqual(text[r.start:r.end],r.text)
        self.assertTrue(rows[0].text.startswith('Dr. Lin'))
    def test_empty(self):self.assertEqual(segment(' \n '),[])
    def test_input_limit(self):
        with self.assertRaises(ValueError):segment('x'*100001)
    def test_unicode(self):
        text='😀 Hello. We may remove content.'
        for r in segment(text):self.assertEqual(text[r.start:r.end],r.text)
    def test_decimals_and_quoted_sentence(self):
        self.assertEqual(len(segment('Pay $12.50. "Yes!" Then leave.')),3)

class MetricTests(unittest.TestCase):
    def test_none_label(self):
        rows=np.array([[0]*8,[1]+[0]*7])
        actual=with_none(rows)
        self.assertEqual(actual[:,8].tolist(),[1,0])
    def test_perfect_all_categories(self):
        y=np.vstack([np.eye(8,dtype=int),np.zeros((1,8),dtype=int)])
        result=metrics(y,y)
        self.assertEqual(result['lexglue_macro_f1_9'],1)
        self.assertEqual(result['macro_f1_8'],1)
    def test_ordinary_sentences_can_hide_failure(self):
        y=np.zeros((100,8),dtype=int);y[0,0]=1
        result=metrics(y,np.zeros_like(y))
        self.assertEqual(result['macro_f1_8'],0)
        self.assertGreater(result['exact_match'],.98)
    def test_invalid(self):
        with self.assertRaises(ValueError):with_none(np.ones((2,7)))
        with self.assertRaises(ValueError):metrics(np.zeros((0,8)),np.zeros((0,8)))

class ExportTests(unittest.TestCase):
    def test_escape(self):
        result={'model_id':'demo','sentences':[{'sentence_id':0,'text':'<script>alert(1)</script>',
                'labels':[],'near_threshold':False}]}
        out=render_html(result)
        self.assertNotIn('<script>',out);self.assertIn('&lt;script&gt;',out)

class StudyTests(unittest.TestCase):
    def test_record_summarize_and_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tasks.csv'
            record(p,'U001','T01','manual',True,181,'manual')
            record(p,'U002','T01','manual',True,120,'manual')
            group=summarize(p)['groups'][0]
            self.assertEqual(group['success_percent'],50)
            with self.assertRaises(ValueError):record(p,'U001','T01','manual',True,100,'manual')
    def test_no_names_or_nonfinite_time(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tasks.csv'
            with self.assertRaises(ValueError):record(p,'person@example.com','T01','manual',True,3,'manual')
            with self.assertRaises(ValueError):record(p,'U1','T01','manual',True,float('nan'),'manual')
            self.assertFalse(p.exists())

class IntegrationTests(unittest.TestCase):
    def test_wrong_split_cannot_train(self):
        with self.assertRaises(ValueError):train([{'split':'validation'}])
    def test_source_split_documents_disjoint(self):
        train_docs={r['document_id'] for r in load_split('train')}
        dev_docs={r['document_id'] for r in load_split('validation')}
        self.assertFalse(train_docs & dev_docs)
    def test_saved_model_and_batch_agree(self):
        b=load(DEFAULT_MODEL)
        text='We may terminate your account at any time.'
        result=analyze(text,b)
        scores,pred=predict_rows(b,[text])
        expected=[LABELS[k] for k in range(8) if pred[0,k]]
        self.assertEqual(result['sentences'][0]['labels'],expected)
        self.assertEqual(len(result['model_id']),64)
    def test_no_input(self):
        with self.assertRaises(ValueError):analyze('',load(DEFAULT_MODEL))

if __name__=='__main__':unittest.main()
