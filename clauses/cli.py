"""Run `python -m clauses.cli --help`."""
import argparse
import json
import sys
from pathlib import Path
from . import data,model
from .evaluate import evaluate
from .export import render_html
from .study import record,summarize


def main(argv=None):
    parser=argparse.ArgumentParser(description='ClauseGuard: local ToS classification and reproducible evaluation.')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('data',help='Download and verify the pinned source dataset.')
    t=sub.add_parser('train');t.add_argument('--variant',choices=['baseline','balanced','hybrid'],default='baseline')
    t.add_argument('--output',required=True);t.add_argument('--tune-thresholds',action='store_true');t.add_argument('--seed',type=int,default=641)
    e=sub.add_parser('evaluate');e.add_argument('--model',default=str(model.DEFAULT_MODEL));e.add_argument('--split',choices=['validation','test'],default='validation')
    e.add_argument('--output',required=True);e.add_argument('--final-test',action='store_true',help='Explicitly expose the test set after model freeze.')
    a=sub.add_parser('analyze');a.add_argument('--input',required=True,help='UTF-8 text path or - for standard input')
    a.add_argument('--model',default=str(model.DEFAULT_MODEL));a.add_argument('--json-out');a.add_argument('--html-out')
    r=sub.add_parser('record-task');r.add_argument('--output',required=True);r.add_argument('--participant',required=True);r.add_argument('--task',required=True)
    r.add_argument('--condition',choices=['manual','clauseguard'],required=True);r.add_argument('--correct',choices=['yes','no'],required=True)
    r.add_argument('--seconds',type=float,required=True);r.add_argument('--model',default=str(model.DEFAULT_MODEL));r.add_argument('--protocol',default='v1');r.add_argument('--limit',type=float,default=180)
    s=sub.add_parser('summarize-tasks');s.add_argument('--input',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='data':
            path=data.fetch();print(json.dumps({'path':str(path),'sha256':data.digest(path)}))
        elif args.command=='train':
            bundle=model.train(data.load_split('train'),args.variant,args.seed)
            if args.tune_thresholds:bundle=model.tune(bundle,data.load_split('validation'))
            print(json.dumps(model.save(bundle,args.output),indent=2))
        elif args.command=='evaluate':
            if args.split=='test' and not args.final_test:parser.error('Test evaluation requires --final-test after configuration freeze.')
            bundle=model.load(args.model)
            result=evaluate(bundle,data.load_split(args.split),args.output)
            if args.split=='test':
                ledger=Path(__file__).resolve().parents[1]/'experiments/test_exposure.jsonl'
                ledger.parent.mkdir(exist_ok=True)
                from datetime import datetime,timezone
                with ledger.open('a') as f:f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'model_id':bundle['model_id'],'output':args.output})+'\n')
            print(json.dumps(result,indent=2))
        elif args.command=='analyze':
            text=sys.stdin.read() if args.input=='-' else Path(args.input).read_text(encoding='utf-8')
            result=model.analyze(text,model.load(args.model))
            if args.json_out:Path(args.json_out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
            if args.html_out:Path(args.html_out).write_text(render_html(result),encoding='utf-8')
            if not args.json_out and not args.html_out:print(json.dumps(result,indent=2))
            else:print(json.dumps({'sentences':len(result['sentences']),'model_id':result['model_id'],'exported':True}))
        elif args.command=='record-task':
            model_id=model.load(args.model)['model_id'] if args.condition=='clauseguard' else 'manual'
            print(json.dumps(record(args.output,args.participant,args.task,args.condition,args.correct=='yes',args.seconds,model_id,args.protocol,args.limit)))
        elif args.command=='summarize-tasks':print(json.dumps(summarize(args.input),indent=2))
    except (ValueError,FileNotFoundError,OSError) as exc:
        parser.exit(2,f'Error: {exc}\n')

if __name__=='__main__':main()
