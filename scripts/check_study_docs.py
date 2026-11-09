"""Check that each study task is fair before a session: the answer sentence exists and
how the running model labels it. Reads the PRIVATE answer key; writes only a sanitized
summary (no answer text, no sentence position) that is safe to commit.

Session 08: also reports the review cue the app shows on the answer sentence
(clauses/cues.py): 'flagged', 'flagged, uncertain', 'possible' (not flagged, score just
below the cut-off) or 'none'.

Session 09: also reports what the "Check it yourself" panel shows for the target category
(clauses/absence.py), and supports tasks whose answer is that the document has NO such
sentence. In the private key such a task has "answer_absent": true instead of
"answer_sentence_starts_with"; the check then reports how many sentences are flagged for the
target category, how many are listed as "worth a look" for it, and how many contain its
search words at all. An optional "distractor_starts_with" names a sentence people may wrongly
give as the answer; the check reports the categories the app flags on it.

Session 10: the tasks use the fresh real Terms of Service in examples/fresh/ (task bank
tasks_v5.json), and the verdict line also names the distractor's flags for a task whose answer
is a sentence."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.absence import search_hits, worth_a_look  # noqa: E402
from clauses.model import load, analyze  # noqa: E402
from clauses.schema import LABELS  # noqa: E402
from clauses.session_v2 import load_tasks  # noqa: E402


def one_sentence(analysis, start, task_id, what):
    matches = [s for s in analysis['sentences'] if s['text'].startswith(start)]
    if len(matches) != 1:
        raise ValueError(f'{task_id}: expected exactly one {what} sentence, found {len(matches)}.')
    return matches[0]


def check(tasks_path, key_path, bundle):
    tasks = load_tasks(tasks_path)
    key = json.loads(Path(key_path).read_text(encoding='utf-8'))
    results = []
    for task_id in sorted(tasks):
        if task_id not in key:
            raise ValueError(f'No private answer key entry for {task_id}.')
        entry = key[task_id]
        doc = ROOT / tasks[task_id]['document']
        analysis = analyze(doc.read_text(encoding='utf-8'), bundle)
        category = entry['target_category']
        if category not in LABELS:
            raise ValueError(f'{task_id}: unknown target category {category!r}.')
        panel = {c['category']: c for c in worth_a_look(analysis)['categories']}[category]
        look_ids = [x['sentence_id'] for x in panel['worth_a_look']]
        row = {
            'task_id': task_id,
            'document': tasks[task_id]['document'],
            'target_category': category,
            'target_cut_off': round(float(bundle['manifest']['thresholds'][LABELS.index(category)]), 2),
            'sentences_in_document': len(analysis['sentences']),
            'worth_a_look_sentences_for_target': len(look_ids),
        }
        if entry.get('answer_absent') is True:
            if 'answer_sentence_starts_with' in entry:
                raise ValueError(f'{task_id}: an absent answer must not also name an answer sentence.')
            row.update({
                'answer': 'absent',
                'sentences_flagged_with_target': panel['flagged'],
                'sentences_with_target_search_words': sum(category in search_hits(s['text']) for s in analysis['sentences']),
            })
        else:
            target = one_sentence(analysis, entry['answer_sentence_starts_with'], task_id, 'answer')
            others = [s for s in analysis['sentences'] if s is not target and category in s['labels']]
            if category in target['labels']:
                cue = 'flagged, uncertain' if category in target.get('uncertain', []) else 'flagged'
            else:
                cue = 'possible' if category in target.get('possible', []) else 'none'
            row.update({
                'answer': 'sentence',
                'answer_sentence_flagged_with_target': category in target['labels'],
                'answer_sentence_cue': cue,
                'target_score': round(target['scores'][category], 3),
                'extra_labels_on_answer_sentence': len([l for l in target['labels'] if l != category]),
                'other_sentences_with_target_label': len(others),
                'answer_sentence_in_worth_a_look': target['sentence_id'] in look_ids,
            })
        if entry.get('distractor_starts_with'):
            distractor = one_sentence(analysis, entry['distractor_starts_with'], task_id, 'distractor')
            row['distractor_flagged_categories'] = list(distractor['labels'])
        results.append(row)
    return {'model_id': bundle['model_id'], 'tasks': results,
            'note': 'Sanitized: contains no answer text or sentence positions.'}


def verdict(t):
    if t['answer'] == 'absent':
        fair = t['sentences_flagged_with_target'] == 0 and t['worth_a_look_sentences_for_target'] == 0
        return (f"{t['task_id']}: ABSENT ANSWER{'' if fair else ' (NOT FAIR: the app points to a sentence)'} | "
                f"sentences flagged {t['target_category']}: {t['sentences_flagged_with_target']} | "
                f"worth a look: {t['worth_a_look_sentences_for_target']} | "
                f"sentences with its search words: {t['sentences_with_target_search_words']}"
                + (f" | distractor flagged as: {', '.join(t['distractor_flagged_categories']) or 'nothing'}"
                   if 'distractor_flagged_categories' in t else ''))
    name = {'flagged': 'FAIR', 'flagged, uncertain': 'FAIR (uncertain flag)',
            'possible': 'NOT FLAGGED, SHOWN AS POSSIBLE', 'none': 'MODEL MISSES IT'}[t['answer_sentence_cue']]
    return (f"{t['task_id']}: {name} | target score {t['target_score']} (cut-off {t['target_cut_off']:.2f}) | "
            f"extra labels on answer {t['extra_labels_on_answer_sentence']} | "
            f"other '{t['target_category']}' sentences {t['other_sentences_with_target_label']} | "
            f"answer listed as worth a look: {'yes' if t['answer_sentence_in_worth_a_look'] else 'no'} "
            f"({t['worth_a_look_sentences_for_target']} listed)"
            + (f" | distractor flagged as: {', '.join(t['distractor_flagged_categories']) or 'nothing'}"
               if 'distractor_flagged_categories' in t else ''))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tasks', default='examples/study/tasks_v5.json')
    p.add_argument('--key', default='private/session10_answer_key.json')
    p.add_argument('--output', default='experiments/session10/study_doc_check.json')
    a = p.parse_args()
    try:
        summary = check(a.tasks, a.key, load())
    except (ValueError, OSError, KeyError) as e:
        p.exit(2, f'Check failed: {e}\n')
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    for t in summary['tasks']:
        print(verdict(t))
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()
