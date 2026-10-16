import csv
from pathlib import Path
import pytest
from tools.impact_benchmark import compute, REQUIRED

def write_csv(path,rows):
    with path.open('w', newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=REQUIRED);w.writeheader();w.writerows(rows)

def trial(**kwargs):
    row=dict(participant_id='P01',scenario_id='S01',manual_seconds='600',scopeguard_seconds='120',manual_usable='1',scopeguard_usable='1',false_billable_flags='0',notes='test fixture only')
    row.update(kwargs);return row

def test_valid_calculation(tmp_path):
    p=tmp_path/'pilot.csv'; write_csv(p,[trial(),trial(participant_id='P02',manual_seconds='500',scopeguard_seconds='100')]); result=compute(p)
    assert result['trials']==2 and result['median_manual_seconds']==550
    assert result['median_scopeguard_seconds']==110 and result['median_time_change_percent']==80

def test_empty_data_refused(tmp_path):
    p=tmp_path/'pilot.csv';write_csv(p,[])
    with pytest.raises(ValueError,match='No completed trials'):compute(p)

def test_duplicate_pair_refused(tmp_path):
    p=tmp_path/'pilot.csv'; write_csv(p,[trial(),trial()])
    with pytest.raises(ValueError,match='duplicate'):compute(p)

def test_negative_time_refused(tmp_path):
    p=tmp_path/'pilot.csv';write_csv(p,[trial(scopeguard_seconds='-5')])
    with pytest.raises(ValueError,match='invalid time'):compute(p)

def test_invalid_flag_refused(tmp_path):
    p=tmp_path/'pilot.csv';write_csv(p,[trial(scopeguard_usable='yes')])
    with pytest.raises(ValueError,match='0 or 1'):compute(p)
