"""Conservative sentence splitting with original character offsets."""
import re
from dataclasses import dataclass

MAX_CHARS = 100_000
MAX_SENTENCES = 1500
ABBREVIATIONS = {'mr', 'mrs', 'ms', 'dr', 'prof', 'inc', 'ltd', 'corp', 'no', 'vs', 'etc', 'e.g', 'i.e', 'u.s'}

@dataclass(frozen=True)
class Sentence:
    start: int
    end: int
    text: str


def segment(text):
    if not isinstance(text, str):
        raise TypeError('Input must be text.')
    if len(text) > MAX_CHARS:
        raise ValueError(f'Limit input to {MAX_CHARS:,} characters.')
    sentences = []
    start = 0
    for match in re.finditer(r'[.!?]+[\"”\')\]]*(?=\s|$)|\n+', text):
        if match.group().startswith('\n'):
            end = match.start()
        else:
            end = match.end()
            token = text[start:match.start()].split()
            token = token[-1].lower() if token else ''
            if match.group().startswith('.') and (token in ABBREVIATIONS or re.fullmatch(r'(?:[a-z]\.)*[a-z]', token)):
                continue
        a, b = start, end
        while a < b and text[a].isspace(): a += 1
        while b > a and text[b-1].isspace(): b -= 1
        if a < b:
            sentences.append(Sentence(a, b, text[a:b]))
        start = match.end()
    a, b = start, len(text)
    while a < b and text[a].isspace(): a += 1
    while b > a and text[b-1].isspace(): b -= 1
    if a < b:
        sentences.append(Sentence(a,b,text[a:b]))
    if len(sentences) > MAX_SENTENCES:
        raise ValueError(f'Limit input to {MAX_SENTENCES} sentences.')
    return sentences
