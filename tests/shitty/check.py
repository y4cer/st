#!/usr/bin/env python3
"""Strict regression gate: no new failures, changed failures, skips or XPASS."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def normalize(text):
    text=text.replace(str(ROOT),'<repo>')
    return re.sub(r'/tmp/tmp[\w-]+','<temporary>',text)


def signature(record):
    if record['status']=='failure':
        problems=record.get('problems') or [{'type':record.get('error_type','AssertionError'),'reason':record.get('reason','')}]
        value={'problems':sorted((p['type'],normalize(p['reason'])) for p in problems)}
        if record.get('output'):value['output']=normalize(record['output'])
        if record.get('coverage'):value['coverage']=record['coverage']
    elif record['status']=='excluded':value=normalize(record.get('reason',''))
    else:value={'status':record['status'],'coverage':record.get('coverage')}
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def verify_sources():
    for path,expected in json.loads((HERE/'sources.json').read_text()).items():
        actual=hashlib.sha256((HERE/path).read_bytes()).hexdigest()
        if actual!=expected:raise RuntimeError('modified pinned reference source: '+path)


def compare(actual,expected):
    errors=[]
    if actual.keys()!=expected.keys():
        errors.append('inventory changed: added='+str(sorted(actual.keys()-expected.keys()))+' removed='+str(sorted(expected.keys()-actual.keys())))
    for id,result in actual.items():
        # Baselines may record conformance assertions, never process failures.
        if result['status'] not in ('pass','failure','excluded'):
            errors.append(f'{id}: unacceptable result status {result["status"]}')
        if result['status']=='failure':
            problems=result.get('problems') or [{'type':result.get('error_type',''), 'reason':result.get('reason','')}]
            for problem in problems:
                kind,reason=problem['type'],problem['reason']
                allowed=kind=='AssertionError'
                allowed |= id.startswith('esctest/') and (kind=='TestFailure' or (kind=='InternalError' and reason=="Missing terminal response: wanted 1 bytes, have b''"))
                allowed |= id=='kitty/transaction/simple_parsing' and kind=='RuntimeError' and reason=='UTF-8 encoded C1 codepoints differ'
                if not allowed:errors.append(f'{id}: unacceptable failure {kind}: {reason}')
        if id not in expected:continue
        want=expected[id]
        if result['status']!=want['status']:
            errors.append(f'{id}: expected {want["status"]}, got {result["status"]}: {result.get("reason","")}')
        elif signature(result)!=want['signature']:
            errors.append(f'{id}: changed {result["status"]}: {result.get("reason","")}')
    return errors


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sanitize',action='store_true');parser.add_argument('--reports',action='store_true',help='verify existing reports without re-running');args=parser.parse_args()
    verify_sources()
    suffix='-asan' if args.sanitize else ''
    env=dict(os.environ,PYTHONHASHSEED='0')
    env['ASAN_OPTIONS']=env.get('ASAN_OPTIONS','')+':detect_leaks=1:halt_on_error=1'
    env['UBSAN_OPTIONS']=env.get('UBSAN_OPTIONS','')+':halt_on_error=1:print_stacktrace=1'
    paths=[]
    for name,script in [('python','run.py'),('corpora','corpora.py')]:
        path=ROOT/'tests/bin'/f'reference-{name}{suffix}.json';paths.append(path)
        if not args.reports:
            if name=='python':
                for test in ('test_adapter.py','test_gate.py'):
                    subprocess.run([sys.executable,str(HERE/test)],check=True,env=env)
            log=path.with_suffix('.log')
            with log.open('w') as output:
                subprocess.run([sys.executable,str(HERE/script),'--audit','--output',str(path)],stdout=output,stderr=subprocess.STDOUT,check=True,env=env)
    actual={}
    for path in paths:actual.update(json.loads(path.read_text()))
    baseline=json.loads((HERE/'baseline.json').read_text())['cases']
    errors=compare(actual,baseline)
    counts=Counter(r['status'] for r in actual.values())
    print(f'Shitty reference: {counts["pass"]} PASS, {counts["failure"]} documented XFAIL, {counts["excluded"]} excluded; {len(actual)} inventoried cases')
    if errors:
        for error in errors[:30]:print(error)
        print(f'{len(errors)} unexpected results; full reports: '+', '.join(str(p.relative_to(ROOT)) for p in paths))
        return 1
    print('No new/changed failures, unexpected passes, or unaccounted cases.')
    return 0
if __name__=='__main__':raise SystemExit(main())
