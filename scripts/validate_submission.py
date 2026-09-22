"""Validate course paths and report structure. `--ready` additionally checks unresolved evidence."""
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATES={'04':'2026-09-22','05':'2026-09-29','07':'2026-10-20','08':'2026-10-27','09':'2026-11-03','10':'2026-11-10','11':'2026-11-17','12':'2026-11-24'}
NAMES=['Ameer','Hemanth','Jayakrishna','Niveda','Ankan']
HEADINGS=['Shipped this week','User evidence','Metrics snapshot','What did not work','Challenges / blockers',"Next week's goal",'Individual contributions','Lean canvas changes (if any)']
FINAL=['1. Problem and users','2. Product','3. NLP method and evaluation','4. User evidence','5. Ethics and limitations']

def validate(ready=False,session=None):
    errors=[];notes=[]
    sessions=[session] if session else list(DATES)
    for n in sessions:
        if n not in DATES:errors.append(f'Unknown session {n}');continue
        path=ROOT/f'reports/session{n}.md'
        if not path.exists():errors.append(f'Missing {path.relative_to(ROOT)}');continue
        text=path.read_text()
        if re.findall(r'^## (.+)$',text,re.M)!=HEADINGS:errors.append(f'{path.name}: wrong report headings/order')
        if f'date: "{DATES[n]}"' not in text:errors.append(f'{path.name}: wrong date')
        if f'session: "{n}"' not in text:errors.append(f'{path.name}: wrong session field')
        for name in NAMES:
            if f'name: {name}' not in text or f'- {name} (' not in text:errors.append(f'{path.name}: missing member {name}')
        if ready:
            if re.search(r'TODO|PENDING|NOT YET|DRAFT',text):errors.append(f'{path.name}: unresolved draft/evidence fields')
            if 'value: null' in text:errors.append(f'{path.name}: missing north-star value')
            if n!='04' and 'previous: null' in text:errors.append(f'{path.name}: missing preceding value')
    if not session:
        for name in ['README.md','slides.md','report.md']:
            path=ROOT/'reports/final'/name
            if not path.exists():errors.append(f'Missing final/{name}')
            elif ready and re.search(r'TODO|PENDING|DRAFT',path.read_text()):errors.append(f'final/{name}: unresolved draft fields')
        report=ROOT/'reports/final/report.md'
        if report.exists():
            if re.findall(r'^## (.+)$',report.read_text(),re.M)!=FINAL:errors.append('Final report headings/order incorrect')
            words=len(report.read_text().split());notes.append(f'Final report words: {words}')
            if not 1000<=words<=2500:errors.append('Final report should be roughly 1000–2500 words')
    notes.append('This script checks structure/placeholders, not whether users, PR reviews or claims are genuine. Humans must verify evidence.')
    return {'mode':'ready' if ready else 'structural','errors':errors,'notes':notes,'passed':not errors}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ready',action='store_true');p.add_argument('--session',choices=list(DATES));a=p.parse_args()
    r=validate(a.ready,a.session);print(json.dumps(r,indent=2));sys.exit(0 if r['passed'] else 1)
