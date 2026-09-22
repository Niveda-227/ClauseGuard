"""Build a readable diagnostic table from existing validation predictions; no model training."""
import argparse
import json
import math
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from clauses.schema import LABELS


def summarize_predictions(rows):
    if not rows:
        raise ValueError('Predictions file is empty.')
    seen=set(); stats={label:Counter() for label in LABELS}; examples={label:{'fp':[],'fn':[]} for label in LABELS}
    for row in rows:
        rid=row['id']
        if not isinstance(rid,str) or not rid.startswith('validation:'):
            raise ValueError('This development report accepts validation IDs only.')
        if rid in seen:
            raise ValueError('Duplicate prediction ID: '+rid)
        seen.add(rid)
        for key in ('gold','predicted'):
            if not isinstance(row[key],list) or any(not isinstance(v,str) or v not in LABELS for v in row[key]):
                raise ValueError('Unknown label or invalid label list.')
            if len(row[key])!=len(set(row[key])):
                raise ValueError('Repeated label in one prediction.')
        gold=set(row['gold']);pred=set(row['predicted'])
        for label in LABELS:
            kind='tp' if label in gold and label in pred else 'fn' if label in gold else 'fp' if label in pred else 'tn'
            stats[label][kind]+=1
            if kind in ('fp','fn') and len(examples[label][kind])<3:
                examples[label][kind].append(rid)
    result=[]
    for label,c in stats.items():
        tp,fp,fn=c['tp'],c['fp'],c['fn']
        precision=tp/(tp+fp) if tp+fp else 0.0
        recall=tp/(tp+fn) if tp+fn else 0.0
        f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.0
        result.append({'label':label,'support':tp+fn,'tp':tp,'fp':fp,'fn':fn,
                       'precision':precision,'recall':recall,'f1':f1,'example_ids':examples[label]})
    return sorted(result,key=lambda r:(r['f1'],r['label']))


def build(predictions, metrics):
    rows=[json.loads(line) for line in Path(predictions).read_text(encoding='utf-8').splitlines() if line.strip()]
    meta=json.loads(Path(metrics).read_text(encoding='utf-8'))
    if meta.get('split')!='validation' or meta.get('n')!=len(rows):
        raise ValueError('Metrics split or sentence count does not match predictions.')
    stats=summarize_predictions(rows)
    macro=sum(r['f1'] for r in stats)/len(stats)
    if not math.isclose(macro,meta['macro_f1_8'],rel_tol=0,abs_tol=1e-10):
        raise ValueError('Recomputed macro F1 differs from the metrics file.')
    for row in stats:
        expected=meta['per_label'][row['label']]
        if expected['support']!=row['support'] or any(not math.isclose(expected[k],row[k],abs_tol=1e-10) for k in ('precision','recall','f1')):
            raise ValueError('Per-category metrics disagree for '+row['label'])
    text=['# Validation error dashboard','',f"Model SHA-256: `{meta['model_id']}`.",
          f"Sentences: {len(rows)}. Recomputed eight-category macro F1: **{macro:.4f}**.",'',
          'Development-set diagnostics, sorted by lowest F1. This is not a final-test estimate or a legal judgment.','',
          '| Category | Gold positives | TP | FP | FN | Precision | Recall | F1 |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in stats:
        text.append(f"| {r['label']} | {r['support']} | {r['tp']} | {r['fp']} | {r['fn']} | {r['precision']:.4f} | {r['recall']:.4f} | {r['f1']:.4f} |")
    text+=['','## Cases to inspect','']
    for r in stats:
        text.append(f"- **{r['label']}** — FP IDs: {', '.join(r['example_ids']['fp']) or 'none'}; FN IDs: {', '.join(r['example_ids']['fn']) or 'none'}.")
    text+=['','## Interpretation','',
           'FP means a predicted label absent from the source annotation. FN means a source label was missed. Counts do not establish why the model failed.',
           'Inspect original clauses by ID using the pinned dataset. Topic mentions and source-annotated concerning clauses may differ; review context before questioning the annotation.',
           'Add your own inspected examples and hypotheses in the PR. Do not change the final test split or count this report as outside-user evidence.']
    return '\n'.join(text)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--predictions',default='experiments/session04/hybrid/predictions.jsonl')
    p.add_argument('--metrics',default='experiments/session04/hybrid/metrics.json')
    p.add_argument('--output',default='experiments/session04/jayakrishna_error_dashboard.md')
    a=p.parse_args()
    try:
        text=build(a.predictions,a.metrics)
        out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text,encoding='utf-8')
        print('Wrote '+str(out))
    except (ValueError,KeyError,OSError,TypeError) as e:
        p.exit(2,f'Error report not written: {e}\n')


if __name__=='__main__':main()
