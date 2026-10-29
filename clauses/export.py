"""Escaped, self-contained HTML document export; no network assets.

Session 09: the export also contains the "Check it yourself" panel (clauses/absence.py): per
category, how many sentences were flagged and which unflagged sentences contain a search word.
That panel is word matches, not model predictions.
"""
import html
from .absence import worth_a_look
from .schema import NOTICE,EXPLANATIONS


def render_check_panel(result):
    h=html.escape
    panel=worth_a_look(result)
    rows=[]
    for c in panel['categories']:
        parts=[f'<p><strong>{h(c["category"])}</strong>: Flagged: {c["flagged"]}</p>']
        if c['flagged']==0:
            parts.append(f'<p>{h(panel["zero_flags_note"])}</p>')
        if c['worth_a_look']:
            items=', '.join(f'sentence {x["sentence_id"]+1} ('+', '.join(h(f"'{w}'") for w in x['words'])+')'
                            for x in c['worth_a_look'])
            parts.append(f'<p>Not flagged, but worth a look: {items}</p>')
        rows.append('<div class="check-row">'+''.join(parts)+'</div>')
    return ('<section class="check"><h2>Check it yourself</h2>'
            f'<p class="meta">{h(panel["note"])}</p>'+''.join(rows)+'</section>')


def render_html(result):
    h=html.escape
    rows=[]
    for item in result['sentences']:
        labels=item['labels'];uncertain=item.get('uncertain',[]);possible=item.get('possible',[])
        descriptions='<br>'.join(h(label)+(' (uncertain: score close to its cut-off)' if label in uncertain else '')+': '+h(EXPLANATIONS[label]) for label in labels)
        if not descriptions:descriptions='No category flagged. Read the original context.'
        if possible:descriptions+='<br>Possible, not flagged (score just below its cut-off): '+h(', '.join(possible))
        marker=' <strong>Near a decision threshold</strong>' if item['near_threshold'] else ''
        rows.append(f'<article><p class="meta">Sentence {item["sentence_id"]+1}{marker}</p>'
                    f'<blockquote>{h(item["text"])}</blockquote><p>{descriptions}</p></article>')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+\
        '<title>ClauseGuard analysis</title><style>body{font:17px/1.6 system-ui;max-width:880px;margin:36px auto;padding:0 24px;color:#163032;background:#faf9f6}article{border-top:1px solid #ccc;padding:14px 0}blockquote{margin:10px 0;padding:12px 18px;background:#eef2ef}.meta{font-size:13px}h1{font-size:36px}h2{font-size:22px}.check{margin:18px 0 28px;padding:6px 18px 10px;border:1px solid #ccc;border-radius:8px}.check-row{border-top:1px solid #e3e3e3}.check-row p{margin:6px 0}</style>'+\
        f'<h1>ClauseGuard</h1><p>{h(NOTICE)}</p><p class="meta">Model: {h(result["model_id"])}</p>'+render_check_panel(result)+''.join(rows)+'</html>'
