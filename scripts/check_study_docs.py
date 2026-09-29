"""Check that each study task is fair before a session: the answer sentence exists and
how the running model labels it. Reads the PRIVATE answer key; writes only a sanitized
summary (no answer text, no sentence position) that is safe to commit."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.model import load, analyze  # noqa: E402
from clauses.session_v2 import load_tasks  # noqa: E402


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
        matches = [s for s in analysis['sentences'] if s['text'].startswith(entry['answer_sentence_starts_with'])]
        if len(matches) != 1:
            raise ValueError(f'{task_id}: expected exactly one answer sentence, found {len(matches)}.')
        target = matches[0]
        category = entry['target_category']
        others = [s for s in analysis['sentences'] if s is not target and category in s['labels']]
        results.append({
            'task_id': task_id,
            'document': tasks[task_id]['document'],
            'target_category': category,
            'answer_sentence_flagged_with_target': category in target['labels'],
            'target_score': round(target['scores'][category], 3),
            'extra_labels_on_answer_sentence': len([l for l in target['labels'] if l != category]),
            'other_sentences_with_target_label': len(others),
            'sentences_in_document': len(analysis['sentences']),
        })
    return {'model_id': bundle['model_id'], 'tasks': results,
            'note': 'Sanitized: contains no answer text or sentence positions.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tasks', default='examples/study/tasks_v2.json')
    p.add_argument('--key', default='private/session05_answer_key.json')
    p.add_argument('--output', default='experiments/session05/study_doc_check.json')
    a = p.parse_args()
    try:
        summary = check(a.tasks, a.key, load())
    except (ValueError, OSError, KeyError) as e:
        p.exit(2, f'Check failed: {e}\n')
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    for t in summary['tasks']:
        verdict = 'FAIR' if t['answer_sentence_flagged_with_target'] else 'MODEL MISSES IT'
        print(f"{t['task_id']}: {verdict} | target score {t['target_score']} | "
              f"extra labels on answer {t['extra_labels_on_answer_sentence']} | "
              f"other '{t['target_category']}' sentences {t['other_sentences_with_target_label']}")
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()
