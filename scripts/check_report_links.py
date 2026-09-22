"""Check inline Markdown paths and flag unresolved report fields; no network or Git operations."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
ROOT=Path(__file__).resolve().parents[1]


def check_report(report, root):
    root=Path(root).resolve();report=Path(report).resolve()
    if not report.is_relative_to(root):raise ValueError('Report must be inside the repository.')
    raw=report.read_text(encoding='utf-8')
    # This covers the supplied report's inline Markdown, not every Markdown extension.
    text=re.sub(r'^\s*```.*?^\s*```\s*$', '', raw, flags=re.M|re.S)
    text=re.sub(r'<!--.*?-->', '', text, flags=re.S)
    issues=[];links=[];external=[]
    for target in re.findall(r'!?\[[^\]]*\]\(([^\n)]*)\)', text):
        target=target.strip()
        if not target:issues.append('Empty link target');continue
        if target.startswith('<') and target.endswith('>'):target=target[1:-1]
        if target.startswith('#'):continue
        parsed=urlsplit(target)
        if parsed.scheme or parsed.netloc:
            external.append({'url':target,'checked_online':False});continue
        path=unquote(parsed.path)
        resolved=(report.parent/path).resolve()
        if not resolved.is_relative_to(root):
            issues.append('Path escapes repository: '+target);continue
        exists=resolved.exists()
        links.append({'target':target,'exists':exists,'repo_path':str(resolved.relative_to(root))})
        if not exists:issues.append('Missing local evidence: '+target)
    unresolved=bool(re.search(r'\b(?:TODO|PENDING|DRAFT)\b',raw) or re.search(r'^\s+value:\s*null\s*$',raw,re.M))
    return {'report':str(report.relative_to(root)),'local_links':links,'external_links':external,
            'path_checks_passed':not issues,'issues':issues,'unresolved_submission_fields':unresolved,
            'limitations':'Checks inline local file/directory paths only, not anchors, legal/user claims, GitHub reviews, remote merges or real-user authenticity.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',default='reports/session04.md')
    p.add_argument('--root',default=str(ROOT))
    p.add_argument('--ready',action='store_true',help='Also fail on unresolved report fields.')
    p.add_argument('--output')
    a=p.parse_args()
    try:
        result=check_report(Path(a.root)/a.report,a.root)
        result['requested_checks_passed']=result['path_checks_passed'] and (not a.ready or not result['unresolved_submission_fields'])
        payload=json.dumps(result,indent=2)+'\n'
        if a.output:
            out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(payload,encoding='utf-8')
        print(payload)
        return 0 if result['requested_checks_passed'] else 1
    except (ValueError,OSError) as e:p.exit(2,f'Link check failed: {e}\n')


if __name__=='__main__':raise SystemExit(main())
