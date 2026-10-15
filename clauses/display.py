"""Text shown for each sentence in the desktop app's result list.

Session 07 user-driven change. In the Session 06 sessions every participant who used the
app clicked a result to read its source sentence before answering, and nobody used the
Category filter (evidence/session06/session_notes.md). The list therefore shows the start
of each sentence next to its tags, so the sentence can be recognised without a click.
The full sentence is still highlighted in the document when a result is selected.
"""
import re

NO_FLAG = 'No category flagged'


def snippet(text, width=60):
    """The first `width` characters of a sentence, cut at a word boundary, with '…' if shortened."""
    if width < 10:
        raise ValueError('width must be at least 10 characters.')
    clean = re.sub(r'\s+', ' ', text).strip()
    if len(clean) <= width:
        return clean
    cut = clean[:width - 1]
    space = cut.rfind(' ')
    if space >= width // 2:
        cut = cut[:space]
    return cut.rstrip(' ,;:') + '…'


def result_label(row, width=60):
    """'3. Unilateral change | We may change these terms at any time…' for one analysed sentence."""
    tags = ', '.join(row['labels']) if row['labels'] else NO_FLAG
    return f"{row['sentence_id'] + 1}. {tags} | {snippet(row['text'], width)}"
