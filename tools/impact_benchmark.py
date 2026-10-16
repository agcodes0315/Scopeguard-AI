"""ScopeGuard pilot metrics, standard-library only.
Usage: python tools/impact_benchmark.py --input evaluation/pilot_results.csv
Records are paired trials and MUST be observed, not invented.
"""
from __future__ import annotations
import argparse, csv, json, statistics
from pathlib import Path
REQUIRED = ('participant_id','scenario_id','manual_seconds','scopeguard_seconds','manual_usable','scopeguard_usable','false_billable_flags','notes')
def parse_binary(value):
    if str(value).strip().lower() not in {'0','1'}: raise ValueError('usable flags must be 0 or 1')
    return int(value)
def compute(path: Path):
    if not path.exists(): raise ValueError(f'CSV missing: {path}')
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError('Missing required columns: '+', '.join(sorted(set(REQUIRED)-set(reader.fieldnames or []))))
        rows=list(reader)
    if not rows: raise ValueError('No completed trials. Do not publish placeholder results.')
    pairs=set(); clean=[]
    for i,row in enumerate(rows, start=2):
        key=(row['participant_id'].strip(),row['scenario_id'].strip())
        if not all(key):raise ValueError(f'Row {i}: participant_id and scenario_id required')
        if key in pairs:raise ValueError(f'Row {i}: duplicate participant/scenario pair')
        pairs.add(key)
        try:
            m=float(row['manual_seconds']); a=float(row['scopeguard_seconds']); flags=int(row['false_billable_flags'])
            import math
            if not math.isfinite(m) or not math.isfinite(a) or m <= 0 or a<=0 or flags<0:raise ValueError()
        except (TypeError, ValueError):raise ValueError(f'Row {i}: invalid time or false_billable_flags') from None
        clean.append(dict(manual=m,assisted=a,manual_usable=parse_binary(row['manual_usable']),assisted_usable=parse_binary(row['scopeguard_usable']),false_flags=flags))
    medm=statistics.median(x['manual'] for x in clean); meda=statistics.median(x['assisted'] for x in clean)
    return {'label':'OBSERVED PILOT DATA — not a controlled causal study', 'trials':len(clean), 'participants':len({k[0] for k in pairs}),
       'median_manual_seconds':round(medm,2),'median_scopeguard_seconds':round(meda,2),
       'median_time_change_percent':round((medm-meda)/medm*100,2),
       'manual_usable_rate_percent':round(sum(x['manual_usable'] for x in clean)/len(clean)*100,2),
       'scopeguard_usable_rate_percent':round(sum(x['assisted_usable'] for x in clean)/len(clean)*100,2),
       'false_billable_flags':sum(x['false_flags'] for x in clean),
       'caveat':'Small convenience sample. Report protocol, dates, sample size, uncertainty and failures. Do not claim dispute prevention or recovered revenue.'}
def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',default='evaluation/pilot_results.csv');p.add_argument('--output',default='evaluation/pilot_summary.json');a=p.parse_args()
    try: result=compute(Path(a.input))
    except ValueError as e: p.error(str(e))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
