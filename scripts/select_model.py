"""Choose among already evaluated models using validation macro-F1 only."""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
records=[]
for name in ['baseline','balanced','hybrid']:
    p=ROOT/f'experiments/initial/{name}/metrics.json'
    if p.exists():
        r=json.loads(p.read_text());records.append((r['macro_f1_8'],name,r))
if not records:raise SystemExit('No validation results available.')
_,name,best=max(records,key=lambda x:x[0])
shutil.copyfile(ROOT/f'artifacts/{name}.joblib',ROOT/'artifacts/selected.joblib')
shutil.copyfile(ROOT/f'artifacts/{name}.json',ROOT/'artifacts/selected.json')
(ROOT/'experiments/initial/selection.json').write_text(json.dumps({'criterion':'validation macro_f1_8, fixed 0.5 thresholds',
 'selected':name,'model_id':best['model_id'],'test_used_for_selection':False,
 'candidates':[{k:r[k] for k in ('variant','macro_f1_8','lexglue_macro_f1_9','lexglue_micro_f1_9','model_id')} for _,_,r in records]},indent=2)+'\n')
print('Selected',name,'validation macro_f1_8',best['macro_f1_8'])
