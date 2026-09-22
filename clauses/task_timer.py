"""Observer-operated timer for real, consented task sessions. No synthetic evidence."""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from .model import DEFAULT_MODEL, load
from .study import record, TOKEN


def run_trial(output, participant, task, condition, model_id, protocol='sep22_v1',
              limit=180, ask=input, clock=time.perf_counter):
    for value in (participant, task, protocol):
        if not TOKEN.fullmatch(value):
            raise ValueError('Use anonymous IDs with letters, digits, underscore or dash.')
    if condition not in ('manual', 'clauseguard'):
        raise ValueError('Choose manual or clauseguard.')
    if limit <= 0:
        raise ValueError('The time limit must be positive.')
    output = Path(output)
    transcript = output.parent / f'{participant}_{task}_{condition}_{protocol}.json'
    if transcript.exists():
        raise ValueError('This trial already exists. Do not overwrite real observations.')
    consent = ask('Participant is outside the team and consents to anonymous task logging? [yes/no] ').strip().lower()
    if consent != 'yes':
        raise ValueError('Session not started: outside-user consent was not confirmed.')
    ask('Prepare the assigned document and product. Press Enter when the participant starts. ')
    started_at = datetime.now(timezone.utc).isoformat()
    start = clock()
    answer = ask('When the participant finishes, enter their answer (or TIMEOUT): ').strip()
    elapsed = round(clock() - start, 3)
    stopped_at = datetime.now(timezone.utc).isoformat()
    while True:
        correct = ask('Compare with the observer answer key. Correct? [yes/no] ').strip().lower()
        if correct in ('yes', 'no'):
            break
    notes = ask('Observation / friction / requested change (no names or contact details): ').strip()
    row = record(output, participant, task, condition, correct == 'yes', elapsed,
                 model_id, protocol, limit)
    transcript.write_text(json.dumps({'started_at_utc': started_at, 'stopped_at_utc': stopped_at,
                         'record': row, 'participant_answer': answer, 'observer_notes': notes,
                         'outside_team_and_consented': True,
                         'timing_note': 'Observer-operated; includes time to enter the answer. Stop at the limit; late answers are unsuccessful.'}, indent=2) + '\n', encoding='utf-8')
    return row


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--participant', required=True)
    p.add_argument('--task', required=True)
    p.add_argument('--condition', choices=['manual', 'clauseguard'], required=True)
    p.add_argument('--output', default='evidence/session04/tasks.csv')
    p.add_argument('--model', default=str(DEFAULT_MODEL))
    p.add_argument('--protocol', default='sep22_v1')
    a = p.parse_args()
    try:
        model_id = load(a.model)['model_id'] if a.condition == 'clauseguard' else 'manual'
        print('Use the study instructions and answer key. Do not use team rehearsals as user evidence.')
        print(json.dumps(run_trial(a.output, a.participant, a.task, a.condition, model_id, a.protocol), indent=2))
    except (ValueError, OSError, KeyboardInterrupt, EOFError) as e:
        p.exit(2, f'Trial not completed: {e}\n')


if __name__ == '__main__':
    main()
