"""Explanation check (Session 08): do participants understand ClauseGuard's category explanations?

The mid-semester decision memo planned for Session 08: "test whether users understand the category
explanations". After a participant's two timed trials, the observer runs:

    python -m clauses.explain_check --participant U008 --observer OBS01 --output evidence/session08

For each card in examples/study/explain_check_v1.json the terminal shows one category name, the
explanation the app shows for it (word for word), and three invented sentences. The participant
reads the card (or the observer reads it aloud) and picks the sentence that fits. Nothing is timed.

The scoring key is in private/explain_key_v1.json (git-ignored) and is never printed. The record
<participant>_explain_v1.json holds only codes, the letters chosen, right/wrong and an optional note.

Summary of a session folder:
    python -m clauses.explain_check --summarize evidence/session08
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .schema import EXPLANATIONS
from .study import TOKEN

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / 'examples/study/explain_check_v1.json'
KEY = ROOT / 'private/explain_key_v1.json'
VERSION = 'explain_v1'


def load_cards(path=CARDS):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    items = data.get('items', [])
    if not items:
        raise ValueError('The card file has no items.')
    for item in items:
        if not TOKEN.fullmatch(item.get('id', '')):
            raise ValueError(f"Bad card ID {item.get('id')!r}.")
        if 'answer' in item or 'correct' in item:
            raise ValueError('The public card file must not contain answers. Keep them in private/.')
        if item.get('category') not in EXPLANATIONS:
            raise ValueError(f"{item['id']}: unknown category {item.get('category')!r}.")
        if item.get('explanation') != EXPLANATIONS[item['category']]:
            raise ValueError(f"{item['id']}: the explanation must be exactly the one the app shows.")
        if sorted(item.get('options', {})) != ['a', 'b', 'c']:
            raise ValueError(f"{item['id']}: each card needs options a, b and c.")
    return items


def load_key(path, items):
    answers = json.loads(Path(path).read_text(encoding='utf-8')).get('answers', {})
    missing = [i['id'] for i in items if answers.get(i['id']) not in ('a', 'b', 'c')]
    if missing:
        raise ValueError(f'The private key has no valid answer for: {", ".join(missing)}.')
    return answers


def run_check(output_dir, participant, observer, items, key, ask=input, say=print):
    for label, value in (('participant', participant), ('observer', observer)):
        if not TOKEN.fullmatch(value):
            raise ValueError(f'{label} must be an anonymous ID (letters, digits, _ or -).')
    output_dir = Path(output_dir)
    record_path = output_dir / f'{participant}_{VERSION}.json'  # e.g. U008_explain_v1.json
    if record_path.exists():
        raise ValueError('This participant already has an explanation check. Do not overwrite real observations.')
    consent = ask('Participant agreed to a few more minutes of questions about the category explanations? [yes/no] ').strip().lower()
    if consent != 'yes':
        raise ValueError('Explanation check not started: consent was not confirmed.')

    say('')
    say('Read this aloud: "Each card shows a category name and the explanation the app gives for it.')
    say('Pick the one sentence that fits that category best. There is no time limit."')
    answers = {}
    for n, item in enumerate(items, 1):
        say('')
        say(f'Card {n} of {len(items)}')
        say(f'  Category:    {item["category"]}')
        say(f'  The app explains it as: "{item["explanation"]}"')
        say('  Which sentence fits this category best?')
        for letter in ('a', 'b', 'c'):
            say(f'    {letter}) {item["options"][letter]}')
        while True:
            choice = ask("Participant's choice [a/b/c, or skip]: ").strip().lower()
            if choice in ('a', 'b', 'c', 'skip'):
                break
        answers[item['id']] = None if choice == 'skip' else choice
    notes = ask('Anything they said about the explanations (no names or contact details): ').strip()

    correct = {i: (a == key[i]) if a is not None else None for i, a in answers.items()}
    record = {
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'participant_id': participant,
        'observer_id': observer,
        'version': VERSION,
        'outside_team_and_consented': True,
        'answers': answers,
        'correct': correct,
        'answered': sum(a is not None for a in answers.values()),
        'score': sum(bool(c) for c in correct.values()),
        'items': len(items),
        'observer_notes': notes,
        'note': 'Explanation check, not timed. Cards: examples/study/explain_check_v1.json. Key kept in private/.',
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    return record


def summarize(folder, items=None):
    items = items if items is not None else load_cards()
    records = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(Path(folder).glob('*_explain_v1.json'))]
    per_card = {}
    for item in items:
        answered = [r for r in records if r['answers'].get(item['id']) is not None]
        per_card[item['id']] = {'category': item['category'],
                                'correct': sum(bool(r['correct'][item['id']]) for r in answered),
                                'answered': len(answered)}
    return {
        'participants': [r['participant_id'] for r in records],
        'per_participant': {r['participant_id']: f"{r['score']}/{r['answered']}" for r in records},
        'per_card': per_card,
        'total_correct': sum(r['score'] for r in records),
        'total_answered': sum(r['answered'] for r in records),
        'note': 'Descriptive only: a handful of people and four cards.',
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--participant', help='anonymous code, e.g. U008')
    p.add_argument('--observer', default='OBS01')
    p.add_argument('--output', default='evidence/session08', help='the session evidence folder')
    p.add_argument('--cards', default=str(CARDS))
    p.add_argument('--key', default=str(KEY))
    p.add_argument('--summarize', metavar='FOLDER', help='print a summary of the checks in FOLDER')
    a = p.parse_args(argv)
    try:
        items = load_cards(a.cards)
        if a.summarize:
            print(json.dumps(summarize(a.summarize, items), indent=2))
            return 0
        if not a.participant:
            p.error('--participant is required (or use --summarize FOLDER)')
        record = run_check(a.output, a.participant, a.observer, items, load_key(a.key, items))
        print(f"Saved. {a.participant}: {record['score']} of {record['answered']} answered cards right. "
              'Do not tell the participant which ones.')
    except (ValueError, OSError, KeyError, KeyboardInterrupt, EOFError) as e:
        p.exit(2, f'Explanation check not completed: {e}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
