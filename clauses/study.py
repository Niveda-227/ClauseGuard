"""Manual, contemporaneous user-task records. No participant identities or document text."""
import csv
import json
import math
import re
import statistics
from datetime import datetime,timezone
from pathlib import Path

FIELDS=['recorded_at_utc','participant_id','task_id','condition','correct','seconds','limit_seconds','model_id','protocol_version']
TOKEN=re.compile(r'^[A-Za-z0-9_-]{1,64}$')


def record(path,participant_id,task_id,condition,correct,seconds,model_id,protocol_version='v1',limit_seconds=180):
    for field,value in [('participant_id',participant_id),('task_id',task_id),('protocol_version',protocol_version)]:
        if not TOKEN.fullmatch(value):raise ValueError(f'{field} must be an anonymous ID using letters, numbers, underscores or dashes.')
    if condition not in ('manual','clauseguard'):raise ValueError('Condition must be manual or clauseguard.')
    if not isinstance(correct,bool):raise ValueError('Correctness must be boolean.')
    if not math.isfinite(seconds) or seconds<0:raise ValueError('Seconds must be finite and nonnegative.')
    if not math.isfinite(limit_seconds) or limit_seconds<=0:raise ValueError('Time limit must be positive.')
    if condition=='clauseguard' and not re.fullmatch(r'[0-9a-f]{64}',model_id):raise ValueError('Use the actual model SHA-256 for ClauseGuard sessions.')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    exists=path.exists() and path.stat().st_size>0
    if exists:
        with path.open(newline='') as f:
            existing=list(csv.DictReader(f))
            f.seek(0)
            if next(csv.reader(f))!=FIELDS:raise ValueError('Evidence CSV schema mismatch.')
        key=(participant_id,task_id,condition,protocol_version)
        if any(tuple(r[k] for k in ('participant_id','task_id','condition','protocol_version'))==key for r in existing):
            raise ValueError('Duplicate participant/task/condition/protocol record. Use a new task ID for a new trial.')
    row=dict(zip(FIELDS,[datetime.now(timezone.utc).isoformat(),participant_id,task_id,condition,
                        int(correct),seconds,limit_seconds,model_id if condition=='clauseguard' else 'manual',protocol_version]))
    with path.open('a',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS)
        if not exists:writer.writeheader()
        writer.writerow(row)
    return row


def summarize(path):
    with Path(path).open(newline='') as f:rows=list(csv.DictReader(f))
    groups={}
    for row in rows:
        # Model/protocol/time-limit changes start a new group rather than silently pool results.
        key=(row['condition'],row['protocol_version'],row['limit_seconds'],row['model_id'])
        groups.setdefault(key,[]).append(row)
    output=[]
    for key,rr in groups.items():
        successes=sum(r['correct']=='1' and float(r['seconds'])<=float(r['limit_seconds']) for r in rr)
        output.append({'condition':key[0],'protocol_version':key[1],'limit_seconds':float(key[2]),'model_id':key[3],
                       'tasks':len(rr),'participants':len(set(r['participant_id'] for r in rr)),
                       'successful_tasks':successes,'success_percent':100*successes/len(rr),
                       'median_seconds_all_tasks':statistics.median(float(r['seconds']) for r in rr)})
    return {'groups':output,'note':'Descriptive task records, not proof of legal correctness or a controlled population estimate.'}
