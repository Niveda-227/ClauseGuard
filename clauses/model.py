"""Trainable baselines and identical batch/product inference."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import f1_score
from .schema import LABELS
from .data import ARCHIVE_SHA256
from .text import segment

DEFAULT_MODEL = Path(__file__).resolve().parents[1] / 'artifacts/selected.joblib'


def targets(rows):
    return np.array([[int(label in row['labels']) for label in LABELS] for row in rows], dtype=np.int8)


def make_pipeline(variant='baseline', seed=641):
    if variant not in ('baseline', 'balanced', 'hybrid'):
        raise ValueError('Unknown variant.')
    word = TfidfVectorizer(ngram_range=(1,1) if variant=='baseline' else (1,2),
                          min_df=2, max_features=30000, sublinear_tf=True, dtype=np.float64)
    features = word if variant != 'hybrid' else FeatureUnion([
        ('word', word), ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5),
                                               min_df=3,max_features=25000,sublinear_tf=True))])
    classifier = OneVsRestClassifier(LogisticRegression(
        C=1.0, class_weight=None if variant=='baseline' else 'balanced',
        solver='liblinear', max_iter=1000, random_state=seed), n_jobs=1)
    return Pipeline([('features',features),('classifier',classifier)])


def train(rows, variant='baseline', seed=641):
    if not rows or any(r['split'] != 'train' for r in rows):
        raise ValueError('Training accepts only the training split.')
    pipeline=make_pipeline(variant,seed)
    pipeline.fit([r['text'] for r in rows],targets(rows))
    manifest={'variant':variant,'seed':seed,'created_utc':datetime.now(timezone.utc).isoformat(),
              'dataset_sha256':ARCHIVE_SHA256,'labels':list(LABELS),'train_count':len(rows),
              'train_documents':sorted(set(r['document_id'] for r in rows)),
              'thresholds':[0.5]*len(LABELS),'threshold_source':'fixed_0.5',
              'python':platform.python_version(),'sklearn':sklearn.__version__,
              'test_evaluated':False}
    return {'pipeline':pipeline,'manifest':manifest}


def tune(bundle, rows):
    if not rows or any(r['split']!='validation' for r in rows):
        raise ValueError('Tune thresholds only on validation data.')
    scores=bundle['pipeline'].predict_proba([r['text'] for r in rows]); y=targets(rows)
    thresholds=[]
    for k in range(len(LABELS)):
        grid=np.arange(0.1,0.91,0.05)
        # On exact ties, prefer higher threshold to reduce unnecessary flags.
        results=[(f1_score(y[:,k],scores[:,k]>t,zero_division=0),float(t)) for t in grid]
        thresholds.append(max(results)[1])
    bundle['manifest']['thresholds']=thresholds
    bundle['manifest']['threshold_source']='validation_per_label_F1_tuned'
    return bundle


def save(bundle,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump(bundle,path,compress=3)
    model_id=hashlib.sha256(path.read_bytes()).hexdigest()
    manifest={**bundle['manifest'],'artifact_sha256':model_id}
    path.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def load(path=DEFAULT_MODEL):
    path=Path(path)
    if not path.exists():
        raise FileNotFoundError('Model missing. Train one or restore the bundled artifacts/selected.joblib.')
    # joblib is for trusted artifacts supplied with this project or trained by you.
    bundle=joblib.load(path)
    if bundle.get('manifest',{}).get('labels') != list(LABELS):
        raise ValueError('Model label order does not match this release.')
    bundle['model_id']=hashlib.sha256(path.read_bytes()).hexdigest()
    return bundle


def predict_rows(bundle,texts):
    if not texts:
        return np.empty((0,len(LABELS))), np.empty((0,len(LABELS)),dtype=int)
    scores=np.asarray(bundle['pipeline'].predict_proba(texts))
    pred=(scores>np.asarray(bundle['manifest']['thresholds'])).astype(int)
    return scores,pred


def analyze(text,bundle):
    sentences=segment(text)
    if not sentences:
        raise ValueError('Paste some text to analyze.')
    scores,pred=predict_rows(bundle,[s.text for s in sentences])
    results=[]
    for i,sentence in enumerate(sentences):
        labels=[LABELS[k] for k in range(len(LABELS)) if pred[i,k]]
        distances=np.abs(scores[i]-np.asarray(bundle['manifest']['thresholds']))
        # A review cue only; no automatic success credit in evaluation.
        uncertain=bool(np.min(distances)<0.05)
        results.append({'sentence_id':i,'start':sentence.start,'end':sentence.end,'text':sentence.text,
                        'labels':labels,'scores':{l:float(scores[i,k]) for k,l in enumerate(LABELS)},
                        'near_threshold':uncertain})
    return {'model_id':bundle.get('model_id','unsaved'), 'variant':bundle['manifest']['variant'],
            'threshold_source':bundle['manifest']['threshold_source'],
            'input_characters':len(text),'sentences':results}
