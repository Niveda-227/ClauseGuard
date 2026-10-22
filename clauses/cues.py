"""Review cues for scores close to a category's cut-off (Session 08).

The mid-semester decision memo planned, for Session 08: "show near-threshold flags as uncertain".
Session 07 showed why: task F1's answer sentence (where you must go to court) scored 0.531 for
Jurisdiction, just under its 0.55 cut-off, so the app showed "No category flagged" for it.

A sentence is flagged for a category when its score is ABOVE that category's cut-off. Scores close
to the cut-off are the least reliable, so the product now names them per category:

  uncertain  the category IS flagged, but its score is less than MARGIN above the cut-off
  possible   the category is NOT flagged, but its score is less than MARGIN below the cut-off
             (or exactly on it)

MARGIN is 0.05: the same distance the app has used since Session 04 for its general note "One
score is near its decision threshold". It was fixed before any Session 08 result and must not be
tuned on the validation or test split. So `near_threshold` keeps exactly its old meaning: it is
true when a sentence has at least one uncertain or possible category.

These cues change no flag, no score, no cut-off and no reported metric. They only add information
to what the user sees.
"""
from .schema import LABELS

MARGIN = 0.05


def review_cues(scores, thresholds, margin=MARGIN):
    """Return (uncertain, possible): two lists of category names, in LABELS order.

    scores and thresholds are sequences in LABELS order (one score and one cut-off per category).
    """
    if not 0 < margin < 0.5:
        raise ValueError('margin must be between 0 and 0.5.')
    if len(scores) != len(LABELS) or len(thresholds) != len(LABELS):
        raise ValueError(f'Expected {len(LABELS)} scores and {len(LABELS)} thresholds.')
    uncertain, possible = [], []
    for label, score, cut in zip(LABELS, scores, thresholds):
        score, cut = float(score), float(cut)
        if score > cut:
            if score - cut < margin:
                uncertain.append(label)
        elif cut - score < margin:
            possible.append(label)
    return uncertain, possible
