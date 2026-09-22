"""Insert actual team/GitHub facts and measured outside-user results into session04.md."""
import argparse
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.model import load, DEFAULT_MODEL
from clauses.study import summarize

PEOPLE = [('Ameer','Product'),('Hemanth','Engineering'),('Jayakrishna','Data&Eval'),
          ('Niveda','Users&Research'),('Ankan','Operations')]


def require(value, label):
    if not isinstance(value, str) or not value.strip() or re.search(r'TODO|PENDING|REPLACE', value):
        raise ValueError(f'Provide an actual value for {label}.')
    return value.strip()


def replace_section(text, heading, body):
    pattern = r'(^## '+re.escape(heading)+r'\n).*?(?=^## |\Z)'
    return re.sub(pattern, lambda m: m.group(1)+'\n'+body.strip()+'\n\n', text, flags=re.M|re.S)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--facts', default='submission_facts.json')
    a=p.parse_args()
    try:
        facts=json.loads(Path(a.facts).read_text(encoding='utf-8'))
        repo=require(facts.get('repo_url'), 'repo_url').rstrip('/')
        if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):
            raise ValueError('repo_url must be your GitHub repository URL.')
        for flag in ('branch_protection_verified','outside_user_evidence_reviewed','contributions_verified'):
            if facts.get(flag) is not True:
                raise ValueError(f'{flag} must be true only after a person verifies it.')
        def links(values, label):
            if not isinstance(values,list) or not values:
                raise ValueError(f'{label} requires actual issue/PR/commit links.')
            for value in values:
                if not isinstance(value,str) or not re.fullmatch(re.escape(repo)+r'/(issues/\d+|pull/\d+|commit/[0-9a-f]{7,40})',value):
                    raise ValueError(f'{label}: expected issue, PR or commit URL in your repository.')
            return ', '.join(f'[evidence {i+1}]({u})' for i,u in enumerate(values))
        ship=links(facts.get('shipped_evidence_urls'),'shipped_evidence_urls')
        change_links=links(facts.get('user_change_evidence_urls'),'user_change_evidence_urls')
        csv_path=ROOT/'evidence/session04/tasks.csv'
        if not csv_path.exists():
            raise ValueError('Record actual outside-user trials into evidence/session04/tasks.csv first.')
        summary=summarize(csv_path)
        model_id=load(DEFAULT_MODEL)['model_id']
        groups=[g for g in summary['groups'] if g['condition']=='clauseguard']
        if len(groups)!=1 or groups[0]['model_id']!=model_id or groups[0]['limit_seconds']!=180 or groups[0]['protocol_version']!='sep22_v1':
            raise ValueError('Use one ClauseGuard model, 180-second limit, sep22_v1 protocol for this first report.')
        group=groups[0]
        text=(ROOT/'reports/session04.md').read_text(encoding='utf-8')
        contributions=[]
        for name,hat in PEOPLE:
            member=facts.get('members',{}).get(name,{})
            handle=require(member.get('github'), name+' GitHub handle')
            if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?',handle):
                raise ValueError(f'Invalid GitHub handle for {name}; omit @.')
            text=re.sub(r'(- name: '+re.escape(name)+r'\n    github: )[^\n]+',lambda m:m.group(1)+handle,text)
            work=require(member.get('completed_work'),name+' completed_work')
            proof=links(member.get('evidence_urls'),name+' evidence_urls')
            contributions.append(f'- {name} ({hat}): {work} (evidence: {proof})')
        text=re.sub(r'^  value: .*$',f"  value: {group['success_percent']:.2f}",text,flags=re.M)
        text=re.sub(r'^> DRAFT.*$', '> Prepared with AI assistance. Technical claims are backed by local artifacts; team members supplied and verified the user and repository evidence below.',text,flags=re.M)
        text=text.replace('**Repository status: PENDING team merge and approving review.** No remote repository has been inspected. Before submission, add the real issue, approved PR and merge-commit links here.',f'**Repository evidence:** {ship}. The team confirms the linked work was merged through teammate-approved PRs and main requires one approving review.')
        observation=require(facts.get('user_observation'),'user_observation')
        change=require(facts.get('change_from_user'),'change_from_user')
        text=replace_section(text,'User evidence',f'''- {observation}
- **Raw artifact**: [timestamped task records](../evidence/session04/tasks.csv), companion trial JSON files in [evidence/session04/](../evidence/session04/), and [summary](../evidence/session04/summary.json). The team must include these in this week's approved merge.
- ClauseGuard: {group['successful_tasks']}/{group['tasks']} tasks correct within 180 seconds ({group['success_percent']:.2f}%), across {group['participants']} outside participant(s).
- Resulting change or documented next action: {change} (evidence: {change_links}).
- This is a small pilot on fictional documents, not a population estimate or validation of legal correctness.''')
        text=text.replace('**Product north-star:** not measured; current `null`, previous `null`. No outside-user trial has been supplied. Do not substitute model F1 for this product metric.',f"**Product north-star:** {group['success_percent']:.2f}% ({group['successful_tasks']}/{group['tasks']} ClauseGuard tasks correct within 180 seconds); previous `null` because this is the first recorded week. Same-session manual comparison, if collected, is in the raw summary; it is not last week's metric.")
        text=replace_section(text,'Individual contributions','\n'.join(contributions))
        text=replace_section(text,'Challenges / blockers',require(facts.get('current_blockers'),'current_blockers')+'\n\n- A teammate must verify the final report and evidence are merged into main before 5:00 p.m. Eastern. This local script does not inspect GitHub or submit anything.')
        if re.search(r'TODO|PENDING|DRAFT',text):
            raise ValueError('Unresolved placeholders remain in the report; inspect before writing.')
        path=ROOT/'reports/session04.md'
        (path.parent/'session04.before-finalization.txt').write_text(path.read_text(encoding='utf-8'),encoding='utf-8')
        path.write_text(text,encoding='utf-8')
        (csv_path.parent/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
        print('Updated reports/session04.md from supplied facts and measured task records. Review every claim; merge through an approved PR.')
    except (OSError,ValueError,KeyError,TypeError) as e:
        p.exit(2,f'Not finalized: {e}\n')


if __name__=='__main__':
    main()
