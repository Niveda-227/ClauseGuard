"""'Not flagged, but worth a look': a plain word search next to the model (Session 09).

Why: on the validation split the model misses 77 annotator labels (honest estimate, Session 07),
and the Session 08 "possible" cue points to only 6 of them (experiments/session08/cue_eval.md).
When the model misses a clause, the user sees nothing at all, so "no flags" can read as "nothing
there". This module gives the user a way to check for themselves.

For each of the 8 categories, SEARCH_WORDS lists plain words that clauses of that kind often use.
A sentence that is NOT flagged for a category but contains one of that category's words is listed
under "Not flagged, but worth a look". These are word matches, not model predictions: they change
no flag, no score, no cut-off and no reported metric.

The words were written on Oct 27, 2026, from the category definitions only, before any validation
run. They must not be edited to improve a validation result. scripts/hint_eval.py measures them on
the validation split with a rule set before its first run.

Matching rules:
  - case-insensitive, whole words only ('court' does not match 'courtesy');
  - a word ending in '*' matches any word that starts with that stem
    ('terminat*' matches 'terminate', 'terminated', 'termination');
  - a phrase matches its words in that order, with any spaces or line breaks between them.
"""
import re

from .schema import LABELS

SEARCH_WORDS = {
    'Limitation of liability': ['liable', 'liability', 'damages', 'responsible', 'losses'],
    'Unilateral termination': ['terminat*', 'suspend*', 'suspension', 'deactivat*', 'close your account',
                               'end your access'],
    'Unilateral change': ['modif*', 'amend*', 'revis*', 'change these', 'changes to', 'update these',
                          'update the terms'],
    'Content removal': ['remov*', 'delet*', 'take down', 'taken down'],
    'Contract by using': ['by using', 'by accessing', 'by signing up', 'by creating', 'you agree',
                          'you accept', 'continued use'],
    'Choice of law': ['governed by', 'laws of', 'law of', 'governing law'],
    'Jurisdiction': ['court', 'courts', 'jurisdiction', 'venue'],
    'Arbitration': ['arbitrat*', 'dispute resolution'],
}

NOTE = ('Word matches, not model predictions. A sentence is listed when it is not flagged for a '
        'category but contains one of that category\'s search words.')
ZERO_FLAGS = 'No sentence was flagged for this category. That does not mean the document has none.'


def _pattern(term):
    words = term.split()
    stem = words[-1].endswith('*')
    if stem:
        words[-1] = words[-1][:-1]
    body = r'\s+'.join(re.escape(w) for w in words)
    return body + (r'\w*' if stem else r'\b')


if set(SEARCH_WORDS) != set(LABELS):
    raise RuntimeError('SEARCH_WORDS must have exactly the 8 categories.')
_COMPILED = {label: re.compile(r'\b(?:' + '|'.join(_pattern(t) for t in SEARCH_WORDS[label]) + ')', re.IGNORECASE)
             for label in LABELS}


def search_hits(text):
    """{category: [words found, lower case, in order, no repeats]} for the categories whose words appear.

    Categories come in the dataset's label order (clauses/schema.py). An empty dict means no search
    word of any category appears in the text.
    """
    if not isinstance(text, str):
        raise TypeError('text must be a string.')
    hits = {}
    for label in LABELS:
        found = []
        for match in _COMPILED[label].finditer(text):
            word = ' '.join(match.group().lower().split())
            if word not in found:
                found.append(word)
        if found:
            hits[label] = found
    return hits


def worth_a_look(analysis):
    """For each category: what was flagged, what was 'possible', and the unflagged sentences with a search word.

    `analysis` is the output of clauses.model.analyze(). Sentence IDs count from 0, like
    analysis['sentences'][i]['sentence_id']; the app shows them as sentence_id + 1.
    """
    sentences = analysis['sentences']
    hits = [search_hits(s['text']) for s in sentences]
    categories = []
    for label in LABELS:
        flagged = [s['sentence_id'] for s in sentences if label in s['labels']]
        possible = [s['sentence_id'] for s in sentences if label in s.get('possible', [])]
        look = [{'sentence_id': s['sentence_id'], 'words': h[label]}
                for s, h in zip(sentences, hits) if label in h and label not in s['labels']]
        categories.append({
            'category': label,
            'flagged': len(flagged),
            'flagged_sentence_ids': flagged,
            'possible_sentence_ids': possible,
            'worth_a_look': look,
            'search_words': list(SEARCH_WORDS[label]),
        })
    return {'note': NOTE, 'zero_flags_note': ZERO_FLAGS, 'categories': categories}
