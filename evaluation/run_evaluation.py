"""Evaluate live local Gemma; writes results.json. Run with server stopped or separately."""
import json
import os
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
cases=json.loads((ROOT/'cases.json').read_text())
base=os.getenv('SCOPEGUARD_URL','http://127.0.0.1:8001').rstrip('/')
results=[]
for i,case in enumerate(cases,1):
    data=json.dumps({'agreement':case['agreement'],'requests':case['requests']}).encode()
    try:
        req=urllib.request.Request(base+'/api/analyze',data=data,headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=240) as response: result=json.load(response)
        classes=[x['classification'] for x in result['items']]
        # A case with multiple findings passes only if at least one item matches
        # and no item is tagged as the opposite billable/nonbillable outcome.
        expected=case['expected']
        correct=bool(classes) and expected in classes
        if expected=='included' and any(c=='potential_extra' for c in classes):correct=False
        if expected=='needs_review' and any(c=='potential_extra' for c in classes):correct=False
        results.append({'id':case['id'],'expected':expected,'actual':classes,'pass':correct})
        print(f"{i:02}/{len(cases)} {case['id']}: {'PASS' if correct else 'FAIL'} {classes}")
    except Exception as exc:
        results.append({'id':case['id'],'expected':case['expected'],'error':str(exc),'pass':False})
        print(f"{i:02}/{len(cases)} {case['id']}: ERROR {exc}")
(ROOT/'results.json').write_text(json.dumps({'cases':len(results),'passing':sum(bool(r['pass']) for r in results),'results':results},indent=2))
print('Evaluation saved to evaluation/results.json. These are scenario-level checks, not a scientific accuracy estimate.')
