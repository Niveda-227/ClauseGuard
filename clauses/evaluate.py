"""Both eight-label diagnostics and LexGLUE's derived no-label convention."""
import json
import time
from pathlib import Path
import numpy as np
from sklearn.metrics import f1_score, precision_recall_fscore_support, accuracy_score
from .schema import LABELS
from .model import targets,predict_rows
from .data import ARCHIVE_SHA256


def with_none(y):
    a=np.asarray(y,dtype=np.int8)
    if a.ndim!=2 or a.shape[1]!=8:
        raise ValueError('Expected eight binary labels per row.')
    if not np.isin(a,[0,1]).all():
        raise ValueError('Labels must be binary.')
    return np.column_stack([a,(a.sum(axis=1)==0).astype(np.int8)])


def metrics(y,pred):
    y=np.asarray(y);pred=np.asarray(pred)
    if y.shape!=pred.shape or len(y)==0:raise ValueError('Nonempty matching shapes required.')
    gold9,pred9=with_none(y),with_none(pred)
    p,r,f,s=precision_recall_fscore_support(gold9,pred9,zero_division=0)
    return {'n':len(y),'scale':'0_to_1','macro_f1_8':float(f1_score(y,pred,average='macro',zero_division=0)),
            'micro_f1_8':float(f1_score(y,pred,average='micro',zero_division=0)),
            'lexglue_macro_f1_9':float(f1_score(gold9,pred9,average='macro',zero_division=0)),
            'lexglue_micro_f1_9':float(f1_score(gold9,pred9,average='micro',zero_division=0)),
            'exact_match':float(accuracy_score(y,pred)),
            'per_label':{label:{'precision':float(p[k]),'recall':float(r[k]),'f1':float(f[k]),'support':int(s[k])}
                         for k,label in enumerate((*LABELS,'No category'))}}


def evaluate(bundle,rows,out):
    split=rows[0]['split'] if rows else None
    if not rows or any(r['split']!=split for r in rows):raise ValueError('One nonempty split required.')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();scores,pred=predict_rows(bundle,[r['text'] for r in rows]);elapsed=time.perf_counter()-start
    result=metrics(targets(rows),pred)
    result.update({'split':split,'dataset_sha256':ARCHIVE_SHA256,'model_id':bundle.get('model_id','unsaved'),
                   'threshold_source':bundle['manifest']['threshold_source'],'variant':bundle['manifest']['variant'],
                   'inference_seconds':elapsed,'ms_per_sentence':1000*elapsed/len(rows),
                   'timing_note':'Single batch timing on the recorded environment; not end-to-end UI latency.'})
    (out/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    # IDs rather than original clauses keep raw source text out of experiment exports.
    with (out/'predictions.jsonl').open('w') as f:
        for i,row in enumerate(rows):
            item={'id':row['id'],'document_id':row['document_id'],'gold':row['labels'],
                  'predicted':[LABELS[k] for k in range(8) if pred[i,k]],'scores':scores[i].tolist()}
            f.write(json.dumps(item)+'\n')
    return result
