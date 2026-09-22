"""Add interface context to the existing real-user timer without changing its CSV schema."""
import argparse
import json
from pathlib import Path
from .model import DEFAULT_MODEL, load
from .study import TOKEN
from .task_timer import run_trial


def capture(output, participant, task, condition, interface, observer, runner=run_trial):
    if interface not in ('desktop','cli_html','text_editor'):
        raise ValueError('Choose desktop, cli_html or text_editor.')
    if (condition=='manual') != (interface=='text_editor'):
        raise ValueError('Manual requires text_editor; ClauseGuard requires desktop or cli_html.')
    if condition not in ('manual','clauseguard'):
        raise ValueError('Invalid condition.')
    for value in (participant,task,observer):
        if not TOKEN.fullmatch(value):raise ValueError('Use anonymous IDs only.')
    output=Path(output);protocol='sep22_v1'
    trial_path=output.parent/f'{participant}_{task}_{condition}_{protocol}.json'
    if trial_path.exists():raise ValueError('Trial already exists. Do not overwrite it.')
    model_id=load(DEFAULT_MODEL)['model_id'] if condition=='clauseguard' else 'manual'
    row=runner(output,participant,task,condition,model_id,protocol)
    # The original timer owns consent, measured duration, duplicate checks and raw evidence.
    record=json.loads(trial_path.read_text(encoding='utf-8'))
    record['interface']=interface
    record['observer_id']=observer
    record['capture_tool']='clauses.session_capture.v1'
    temp=trial_path.with_suffix('.json.tmp')
    try:
        temp.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        temp.replace(trial_path)
    finally:
        temp.unlink(missing_ok=True)
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--participant',required=True)
    p.add_argument('--task',required=True)
    p.add_argument('--condition',choices=['manual','clauseguard'],required=True)
    p.add_argument('--interface',choices=['desktop','cli_html','text_editor'],required=True)
    p.add_argument('--observer',required=True,help='Anonymous observer ID, such as OBS01.')
    p.add_argument('--output',default='evidence/session04/tasks.csv')
    a=p.parse_args()
    try:
        row=capture(a.output,a.participant,a.task,a.condition,a.interface,a.observer)
        print(json.dumps(row,indent=2))
        print('Saved the real trial with interface context. Review anonymity before committing.')
    except (ValueError,OSError,KeyError,KeyboardInterrupt,EOFError) as e:
        p.exit(2,f'Capture not completed: {e}. If a session already ran, inspect existing records before retrying.\n')


if __name__=='__main__':main()
