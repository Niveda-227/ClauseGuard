"""Session protocol v2 (sep29_v2): fixes the two Session 04 instrumentation problems.

1. The clock stops when the observer presses Enter at the moment the participant
   states the answer. Typing the answer happens afterwards and is NOT timed.
2. The observer reads the task prompt from the task bank, and the participant
   restates it before the clock starts, so the answer can be matched to the task.

The CSV schema is unchanged (see clauses/study.py). Session 04 records made with
protocol sep22_v1 stay as they are; summaries never pool different protocols.
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .model import DEFAULT_MODEL, load
from .study import TOKEN, record

PROTOCOL = 'sep29_v2'
LIMIT_SECONDS = 180
DEFAULT_TASKS = Path(__file__).resolve().parents[1] / 'examples/study/tasks_v2.json'
INTERFACES = ('desktop', 'cli_html', 'text_editor')


def load_tasks(path):
    """Public task bank: prompts and documents only. Answer keys live in private/."""
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    tasks = data.get('tasks', {})
    if not tasks:
        raise ValueError('Task bank has no tasks.')
    for task_id, task in tasks.items():
        if not TOKEN.fullmatch(task_id):
            raise ValueError(f'Bad task ID {task_id!r}.')
        if not task.get('prompt') or not task.get('document'):
            raise ValueError(f'Task {task_id} needs a prompt and a document.')
        if 'answer' in task or 'answer_key' in task:
            raise ValueError('The public task bank must not contain answers. Keep them in private/.')
    return tasks


def run_trial_v2(output, participant, task, condition, interface, observer, model_id,
                 tasks, limit=LIMIT_SECONDS, ask=input, clock=time.perf_counter, say=print):
    for label, value in (('participant', participant), ('task', task), ('observer', observer)):
        if not TOKEN.fullmatch(value):
            raise ValueError(f'{label} must be an anonymous ID (letters, digits, _ or -).')
    if condition not in ('manual', 'clauseguard'):
        raise ValueError('Choose manual or clauseguard.')
    if interface not in INTERFACES:
        raise ValueError('Choose desktop, cli_html or text_editor.')
    if (condition == 'manual') != (interface == 'text_editor'):
        raise ValueError('Manual requires text_editor; ClauseGuard requires desktop or cli_html.')
    if task not in tasks:
        raise ValueError(f'Task {task} is not in the task bank.')
    if limit <= 0:
        raise ValueError('The time limit must be positive.')

    output = Path(output)
    transcript = output.parent / f'{participant}_{task}_{condition}_{PROTOCOL}.json'
    if transcript.exists():
        raise ValueError('This trial already exists. Do not overwrite real observations.')

    consent = ask('Participant is outside the team and consents to anonymous task logging? [yes/no] ').strip().lower()
    if consent != 'yes':
        raise ValueError('Session not started: outside-user consent was not confirmed.')

    prompt = tasks[task]['prompt']
    say('')
    say(f'Document for this trial: {tasks[task]["document"]}')
    say('READ THIS TASK ALOUD, WORD FOR WORD:')
    say(f'    "{prompt}"')
    say('Then ask the participant to say the task back in their own words.')
    attempts = 0
    while True:
        attempts += 1
        ok = ask('Did the participant restate the task correctly? [yes/no] ').strip().lower()
        if ok == 'yes':
            break
        if attempts >= 3:
            raise ValueError('Task could not be confirmed after 3 readings. Trial not recorded.')
        say('Read the task aloud again, word for word.')

    ask('Press Enter to START the clock as the participant begins. ')
    started_at = datetime.now(timezone.utc).isoformat()
    start = clock()
    ask(f'Press Enter the MOMENT the participant states their final answer (or at {int(limit)} seconds). ')
    elapsed = round(clock() - start, 3)
    stopped_at = datetime.now(timezone.utc).isoformat()
    say(f'Clock stopped at {elapsed} seconds. Answer typing below is not timed.')

    answer = ask("Type the participant's answer (or TIMEOUT): ").strip() or 'TIMEOUT'
    while True:
        correct = ask('Compare with the private answer key. Correct sentence AND correct meaning? [yes/no] ').strip().lower()
        if correct in ('yes', 'no'):
            break
    notes = ask('Observation / friction / requested change (no names or contact details): ').strip()

    row = record(output, participant, task, condition, correct == 'yes', elapsed,
                 model_id, PROTOCOL, limit)
    transcript.write_text(json.dumps({
        'started_at_utc': started_at,
        'stopped_at_utc': stopped_at,
        'record': row,
        'task_prompt': prompt,
        'document': tasks[task]['document'],
        'prompt_restated_correctly': True,
        'prompt_readings': attempts,
        'participant_answer': answer,
        'observer_notes': notes,
        'interface': interface,
        'observer_id': observer,
        'outside_team_and_consented': True,
        'capture_tool': 'clauses.session_v2',
        'timing_note': 'Clock stops when the participant states the answer; answer entry is excluded. '
                       'Answers after the limit count as unsuccessful.',
    }, indent=2) + '\n', encoding='utf-8')
    return row


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--participant', required=True, help='Anonymous code, e.g. U002')
    p.add_argument('--task', required=True, help='Task ID from the task bank, e.g. C1')
    p.add_argument('--condition', choices=['manual', 'clauseguard'], required=True)
    p.add_argument('--interface', choices=list(INTERFACES), required=True)
    p.add_argument('--observer', required=True, help='Anonymous observer code, e.g. OBS01')
    p.add_argument('--output', default='evidence/session05/tasks.csv')
    p.add_argument('--tasks', default=str(DEFAULT_TASKS), help='Public task bank JSON')
    a = p.parse_args()
    try:
        tasks = load_tasks(a.tasks)
        model_id = load(DEFAULT_MODEL)['model_id'] if a.condition == 'clauseguard' else 'manual'
        row = run_trial_v2(a.output, a.participant, a.task, a.condition, a.interface,
                           a.observer, model_id, tasks)
        print(json.dumps(row, indent=2))
        print('Saved. Check anonymity before committing.')
    except (ValueError, OSError, KeyError, KeyboardInterrupt, EOFError) as e:
        p.exit(2, f'Trial not completed: {e}\n')


if __name__ == '__main__':
    main()
