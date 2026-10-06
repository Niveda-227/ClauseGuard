"""Build the Session 06 presentation from committed evidence.

    python scripts/build_slides.py

1. Re-runs scripts/midpoint_facts.py, so every number is fresh from the files on this branch.
2. Reads the hand-written sources in reports/midpoint/src/:
       slides.md          the deck (slides separated by a line containing only ---)
       speaker_notes.md   what the presenter says, slide by slide
       qa_prep.md         likely questions and who answers them
3. Refuses to build while any <<...>> placeholder is left, any {{AUTO_...}} token is unknown,
   any image or relative link points at a missing file, the deck runs over 5:00, or the
   Decision slide does not say Pivot or Persevere.
4. Writes reports/midpoint/slides.md (renders on GitHub), slides.html (a self-contained deck:
   open it in a browser, arrow keys to move, F for full screen, T for a timer),
   speaker_notes.md and qa_prep.md.

Use --final for the build you commit: it also requires reports/midpoint/rehearsal_log.md
to be filled with real, timed run-throughs.

Slide timing: put <!-- time: 40 --> (seconds) on each slide. Appendix slides use <!-- time: 0 -->.
Links and images are written relative to reports/midpoint/ (for example figures/x.svg or
../../evidence/session06/README.md).
"""
import argparse
import base64
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'reports/midpoint'
REPO_URL = 'https://github.com/Niveda-227/ClauseGuard/blob/main/'
LIMIT_SECONDS = 300
SOURCES = ('slides.md', 'speaker_notes.md', 'qa_prep.md')
PLACEHOLDER = re.compile(r'<<[^>]*>>')
TOKEN = re.compile(r'\{\{AUTO_([A-Z0-9_]+)\}\}')
LINK = re.compile(r'(!?)\[([^\]]*)\]\(([^)\s]+)\)')
TIME = re.compile(r'<!--\s*time:\s*(\d+)\s*-->')


class BuildError(ValueError):
    pass


# ------------------------------------------------------------------ checks
def check_placeholders(name, text):
    problems = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in PLACEHOLDER.findall(line):
            problems.append(f'{name} line {i}: unfilled placeholder {m[:70]}')
    return problems


def fill(name, text, tokens):
    problems = [f'{name}: unknown token {{{{AUTO_{t}}}}}' for t in TOKEN.findall(text) if t not in tokens]
    return TOKEN.sub(lambda m: tokens.get(m.group(1), m.group(0)), text), problems


def check_links(name, text, base=OUT):
    problems = []
    for bang, _, target in LINK.findall(text):
        if re.match(r'^(https?:|mailto:|#)', target):
            continue
        path = (base / target.split('#')[0]).resolve()
        if not path.exists():
            problems.append(f'{name}: {"image" if bang else "link"} target not found: {target}')
        elif ROOT.resolve() not in path.parents and path != ROOT.resolve():
            problems.append(f'{name}: {target} points outside the repository')
    return problems


def split_slides(text):
    return [s.strip() for s in re.split(r'^---\s*$', text, flags=re.M) if s.strip()]


def check_deck(slides):
    problems, timing = [], []
    for i, s in enumerate(slides, 1):
        m = TIME.search(s)
        title = next((l.lstrip('# ').strip() for l in s.splitlines() if l.startswith('#')), f'slide {i}')
        if not m:
            problems.append(f'slides.md slide {i} ({title}): no <!-- time: N --> comment')
            continue
        timing.append((title, int(m.group(1))))
    total = sum(t for _, t in timing)
    if total > LIMIT_SECONDS:
        problems.append(f'slides.md: planned time {total} s is over the {LIMIT_SECONDS} s limit')
    decision = [s for s in slides if re.search(r'^#+ .*decision', s, flags=re.I | re.M)]
    if not decision:
        problems.append('slides.md: no slide with "Decision" in its title')
    else:
        heading = re.search(r'^#+ .*decision.*$', decision[0], flags=re.I | re.M).group(0)
        if not re.search(r'\b(pivot|persevere)\b', heading, flags=re.I):
            problems.append('slides.md: the Decision slide title must say Pivot or Persevere')
    if not any('live demo' in s.lower() for s in slides):
        problems.append('slides.md: no "Live demo" slide (the course requires the product running, not slides about it)')
    if not re.search(r'\.\./\.\./evidence/session0[56]/', '\n'.join(slides)):
        problems.append('slides.md: the user-evidence slide must link the raw evidence in evidence/session05 or session06')
    return problems, timing, total


# ------------------------------------------------------------------ HTML
def inline(text, base):
    parts = []
    last = 0
    for m in LINK.finditer(text):
        parts.append(html.escape(text[last:m.start()]))
        bang, label, target = m.groups()
        if bang:
            parts.append(image(target, label, base))
        else:
            parts.append(f'<a href="{html.escape(to_url(target, base))}">{html.escape(label)}</a>')
        last = m.end()
    parts.append(html.escape(text[last:]))
    s = ''.join(parts)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s


def to_url(target, base):
    if re.match(r'^(https?:|mailto:|#)', target):
        return target
    rel = (base / target).resolve().relative_to(ROOT.resolve()).as_posix()
    return REPO_URL + rel


def image(target, alt, base):
    path = (base / target).resolve()
    kind = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}.get(path.suffix.lower())
    if not kind:
        raise BuildError(f'Unsupported image type: {target}')
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<img src="data:{kind};base64,{data}" alt="{html.escape(alt)}">'


def slide_html(md, base=OUT):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        h = re.match(r'^(#{1,3})\s+(.*)', line)
        if h:
            n = len(h.group(1))
            out.append(f'<h{n}>{inline(h.group(2), base)}</h{n}>')
            i += 1
        elif line.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c, base)}</th>' for c in head) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{inline(c, base)}</td>' for c in r) + '</tr>' for r in body)
                       + '</tbody></table>')
        elif re.match(r'^\s*([-*]|\d+\.)\s+', line):
            ordered = bool(re.match(r'^\s*\d+\.', line))
            tag = 'ol' if ordered else 'ul'
            items = []
            while i < len(lines) and re.match(r'^\s*([-*]|\d+\.)\s+', lines[i]):
                indent = len(lines[i]) - len(lines[i].lstrip())
                text = re.sub(r'^\s*([-*]|\d+\.)\s+', '', lines[i])
                items.append(f'<li class="{"sub" if indent >= 2 else ""}">{inline(text, base)}</li>')
                i += 1
            out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
        elif re.fullmatch(r'\s*!\[[^\]]*\]\([^)]+\)\s*', line):
            out.append(f'<figure>{inline(line.strip(), base)}</figure>')
            i += 1
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|\s*\||\s*([-*]|\d+\.)\s)', lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f'<p>{inline(" ".join(para), base)}</p>')
    return '\n'.join(out)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ClauseGuard: mid-semester presentation</title>
<style>
:root{--ink:#1d1d1f;--muted:#5b6470;--accent:#2f6fb2;--bg:#ffffff;--page:#e9ecef}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--page);font-family:Helvetica,Arial,sans-serif;color:var(--ink)}
.deck{height:100%;display:flex;align-items:center;justify-content:center}
.slide{display:none;width:min(100vw,177.78vh);height:min(56.25vw,100vh);background:var(--bg);padding:4.2% 5.5%;
  position:relative;overflow:hidden;font-size:min(2.25vw,4vh);line-height:1.35}
.slide.active{display:flex;flex-direction:column}
h1{font-size:2.6em;margin:0 0 .3em;color:var(--accent)}
h2{font-size:1.65em;margin:0 0 .5em;border-bottom:3px solid var(--accent);padding-bottom:.2em}
h3{font-size:1.15em;margin:.4em 0 .2em;color:var(--muted)}
p{margin:.3em 0}
ul,ol{margin:.2em 0 .2em 1.1em;padding:0}
li{margin:.25em 0}
li.sub{margin-left:1.2em;font-size:.9em;color:var(--muted)}
table{border-collapse:collapse;margin:.4em 0;font-size:.9em}
th,td{border:1px solid #cfd6dd;padding:.25em .7em;text-align:left}
th{background:#f1f5f9}
figure{margin:.3em 0;flex:1 1 auto;min-height:0;display:flex;justify-content:center}
figure img{max-width:100%;max-height:100%;object-fit:contain}
code{font-size:.85em;background:#f1f3f5;padding:0 .25em;border-radius:3px}
a{color:var(--accent)}
.split{display:grid;grid-template-columns:1.35fr 1fr;gap:3%;flex:1 1 auto;min-height:0;font-size:.88em}
.split .col{min-height:0;display:flex;flex-direction:column}
.split .pics figure{flex:1 1 auto}
.split .pics img{border:1px solid #cfd6dd}
.num{position:absolute;right:2.5%;bottom:2.5%;font-size:.6em;color:var(--muted)}
#timer{position:fixed;left:10px;bottom:10px;font:16px monospace;background:#000;color:#fff;padding:4px 8px;border-radius:4px;display:none}
@media print{html,body{background:#fff}.deck{display:block}.slide{display:flex!important;flex-direction:column;width:100%;height:auto;
  aspect-ratio:16/9;page-break-after:always;font-size:14pt}#timer{display:none!important}@page{size:landscape;margin:0}}
</style></head><body>
<div class="deck">
__SLIDES__
</div>
<div id="timer">0:00</div>
<script>
const s=[...document.querySelectorAll('.slide')];let i=0;
function show(n){i=Math.max(0,Math.min(s.length-1,n));s.forEach((x,k)=>x.classList.toggle('active',k===i));location.hash=i+1}
show((parseInt(location.hash.slice(1))||1)-1);
let t0=null,tick=null;const tm=document.getElementById('timer');
document.addEventListener('keydown',e=>{
 if(['ArrowRight','PageDown',' '].includes(e.key)){show(i+1);e.preventDefault()}
 if(['ArrowLeft','PageUp'].includes(e.key)){show(i-1);e.preventDefault()}
 if(e.key==='Home')show(0); if(e.key==='End')show(s.length-1);
 if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
 if(e.key==='t'||e.key==='T'){if(tick){clearInterval(tick);tick=null;tm.style.display='none'}else{t0=Date.now();tm.style.display='block';
  tick=setInterval(()=>{const d=Math.floor((Date.now()-t0)/1000);tm.textContent=Math.floor(d/60)+':'+String(d%60).padStart(2,'0');
  tm.style.background=d>=300?'#b00020':(d>=270?'#b26a00':'#000')},250)}}
});
document.addEventListener('click',e=>{if(e.target.tagName!=='A')show(i+1)});
</script></body></html>
"""


IMAGE_LINE = re.compile(r'^\s*!\[[^\]]*\]\([^)]+\)\s*$')


def split_html(md):
    """<!-- layout: split -->: text on the left, image lines on the right."""
    lines = md.splitlines()
    pics = '\n'.join(l for l in lines if IMAGE_LINE.match(l))
    text = '\n'.join(l for l in lines if not IMAGE_LINE.match(l))
    head = re.match(r'^(?:\s*<!--.*?-->\s*\n)*\s*(#+ .*)$', text, flags=re.M)
    title = ''
    if head:
        title = slide_html(head.group(1))
        text = text.replace(head.group(1), '', 1)
    return (f'{title}<div class="split"><div class="col">{slide_html(text)}</div>'
            f'<div class="col pics">{slide_html(pics)}</div></div>')


def deck_html(slides):
    body = []
    for n, s in enumerate(slides, 1):
        split = re.search(r'<!--\s*layout:\s*split\s*-->', s) and any(IMAGE_LINE.match(l) for l in s.splitlines())
        inner = split_html(s) if split else slide_html(s)
        body.append(f'<section class="slide">{inner}<div class="num">{n} / {len(slides)}</div></section>')
    return PAGE.replace('__SLIDES__', '\n'.join(body))


# ------------------------------------------------------------------ main
def build(final=False, regenerate=True):
    from scripts import midpoint_facts
    if regenerate and midpoint_facts.main([]) != 0:
        raise BuildError('scripts/midpoint_facts.py stopped; fix that first.')
    facts_path = OUT / 'facts.json'
    import json
    tokens = json.loads(facts_path.read_text(encoding='utf-8'))['tokens']
    src = OUT / 'src'
    problems, outputs = [], {}
    for name in SOURCES:
        path = src / name
        if not path.exists():
            problems.append(f'missing source reports/midpoint/src/{name}')
            continue
        text = path.read_text(encoding='utf-8')
        problems += check_placeholders(f'src/{name}', text)
        filled, p = fill(f'src/{name}', text, tokens)
        problems += p
        problems += check_links(f'src/{name}', filled)
        outputs[name] = filled
    rehearsal = OUT / 'rehearsal_log.md'
    if final:
        if not rehearsal.exists():
            problems.append('--final: reports/midpoint/rehearsal_log.md is missing')
        else:
            log = rehearsal.read_text(encoding='utf-8')
            problems += check_placeholders('rehearsal_log.md', log)
            if not re.search(r'\|\s*\d+:\d{2}\s*\|', log):
                problems.append('--final: rehearsal_log.md has no measured run time (m:ss) in its table')
    timing, total = [], 0
    if 'slides.md' in outputs:
        slides = split_slides(outputs['slides.md'])
        p, timing, total = check_deck(slides)
        problems += p
    if problems:
        raise BuildError('\n'.join(problems))
    header = ('<!-- Generated by scripts/build_slides.py from reports/midpoint/src/. Edit the source, not this file. -->\n\n')
    for name, text in outputs.items():
        (OUT / name).write_text(header + text, encoding='utf-8')
    (OUT / 'slides.html').write_text(deck_html(slides), encoding='utf-8')
    return timing, total, tokens


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--final', action='store_true',
                   help='Also require a filled rehearsal_log.md (use for the commit you open the PR with)')
    a = p.parse_args(argv)
    try:
        timing, total, tokens = build(final=a.final)
    except BuildError as e:
        print('\nNOT BUILT. Fix these and run again:\n', file=sys.stderr)
        for line in str(e).splitlines():
            print(f'  - {line}', file=sys.stderr)
        return 1
    print('\nPlanned timing:')
    for title, secs in timing:
        print(f'  {secs:4d} s  {title[:70]}')
    print(f'  {total:4d} s  TOTAL ({total // 60}:{total % 60:02d} of 5:00)')
    print(f"\nRule outcome shown on the Decision slide: {tokens['RULE_OUTCOME']}")
    print('Wrote reports/midpoint/slides.md, slides.html, speaker_notes.md, qa_prep.md')
    print('Open reports/midpoint/slides.html in a browser: arrow keys move, F = full screen, T = timer.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
