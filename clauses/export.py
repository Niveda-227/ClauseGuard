"""Escaped, self-contained HTML document export; no network assets."""
import html
from .schema import NOTICE,EXPLANATIONS


def render_html(result):
    h=html.escape
    rows=[]
    for item in result['sentences']:
        labels=item['labels']
        descriptions='<br>'.join(h(label)+': '+h(EXPLANATIONS[label]) for label in labels)
        if not descriptions:descriptions='No category flagged. Read the original context.'
        marker=' <strong>Near a decision threshold</strong>' if item['near_threshold'] else ''
        rows.append(f'<article><p class="meta">Sentence {item["sentence_id"]+1}{marker}</p>'
                    f'<blockquote>{h(item["text"])}</blockquote><p>{descriptions}</p></article>')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+\
        '<title>ClauseGuard analysis</title><style>body{font:17px/1.6 system-ui;max-width:880px;margin:36px auto;padding:0 24px;color:#163032;background:#faf9f6}article{border-top:1px solid #ccc;padding:14px 0}blockquote{margin:10px 0;padding:12px 18px;background:#eef2ef}.meta{font-size:13px}h1{font-size:36px}</style>'+\
        f'<h1>ClauseGuard</h1><p>{h(NOTICE)}</p><p class="meta">Model: {h(result["model_id"])}</p>'+''.join(rows)+'</html>'
