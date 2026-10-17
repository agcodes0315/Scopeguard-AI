"""Local-first workflows. Only proposal summaries are exposed via unguessable share tokens."""
import io
import json
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
ROOT=Path(__file__).resolve().parent.parent
DB=Path(os.getenv('SCOPEGUARD_DB',str(ROOT/'data'/'scopeguard.db')))
router=APIRouter(prefix='/api')
def connection():
    """Every connection gets required schema, including isolated Windows test DBs."""
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(str(DB),timeout=10)
    try:
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA busy_timeout=10000')
        db.execute("""CREATE TABLE IF NOT EXISTS proposals (token TEXT PRIMARY KEY, title TEXT NOT NULL, currency TEXT NOT NULL, rate REAL NOT NULL, items_json TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at INTEGER NOT NULL, decided_at INTEGER, customer_note TEXT)""")
        db.execute("CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, items_json TEXT NOT NULL)")
        # Commit schema immediately so tests and request handlers see it on Windows.
        db.commit()
        return db
    except Exception:
        db.close()
        raise

class LineItem(BaseModel):
    description:str=Field(min_length=3,max_length=240)
    hours:float=Field(ge=0,le=1000)
    evidence:str=Field(default='',max_length=1000)
class CreateProposal(BaseModel):
    title:str=Field(min_length=3,max_length=160)
    currency:Literal['INR','USD','EUR','GBP']= 'INR'
    hourly_rate:float=Field(gt=0,le=1000000)
    items:list[LineItem]=Field(min_length=1,max_length=20)
    analysis_id:str=Field(min_length=10,max_length=120)
    item_indices:list[int]=Field(min_length=1,max_length=20)

class Decision(BaseModel):
    decision:Literal['approved','rejected','clarification_requested']
    note:str=Field(default='',max_length=1000)
@router.post('/proposals',status_code=201)
def create_proposal(body:CreateProposal):
    with connection() as db:
        row = db.execute('SELECT items_json FROM analyses WHERE id=?', (body.analysis_id,)).fetchone()
    if not row:
        raise HTTPException(422, 'A verified analysis is required before creating a proposal.')
    analyzed = json.loads(row['items_json'])
    if len(body.item_indices) != len(body.items) or len(set(body.item_indices)) != len(body.items):
        raise HTTPException(422, 'Each proposal item needs one unique analysis index.')
    for idx, proposal_item in zip(body.item_indices, body.items):
        if idx < 0 or idx >= len(analyzed):
            raise HTTPException(422, 'Invalid analysis item index.')
        finding = analyzed[idx]
        if finding['classification'] != 'potential_extra' or not finding['agreement_evidence'] or not finding['request_evidence']:
            raise HTTPException(422, 'Included or unverified work cannot be billed as additional scope.')
        if proposal_item.description != finding['request']:
            raise HTTPException(422, 'Proposal description does not match verified finding.')
        if proposal_item.evidence != finding['request_evidence']:
            raise HTTPException(422, 'Proposal evidence does not match verified finding.')
    token=secrets.token_urlsafe(32)
    total=round(sum(x.hours*body.hourly_rate for x in body.items),2)
    with connection() as db:
        db.execute('INSERT INTO proposals(token,title,currency,rate,items_json,total,status,created_at) VALUES(?,?,?,?,?,?,?,?)', (token,body.title,body.currency,body.hourly_rate,json.dumps([x.model_dump() for x in body.items]),total,'pending',int(time.time())))
    return {'token':token,'status':'pending','total':total,'share_path':'/proposal.html?token='+token}

def get(token:str):
    if len(token)>160 or len(token)<20:raise HTTPException(404,'Proposal not found')
    with connection() as db:row=db.execute('SELECT * FROM proposals WHERE token=?',(token,)).fetchone()
    if row is None:raise HTTPException(404,'Proposal not found')
    import json
    d=dict(row);d['items']=json.loads(d.pop('items_json'))
    return d
@router.get('/proposals/{token}')
def read_proposal(token:str):return get(token)

@router.post('/proposals/{token}/decision')
def decide(token:str,body:Decision):
    with connection() as db:
        current=db.execute('SELECT status FROM proposals WHERE token=?',(token,)).fetchone()
        if current is None:raise HTTPException(404,'Proposal not found')
        if current['status']!='pending':raise HTTPException(409,'Decision already recorded; proposal is immutable')
        updated=db.execute('UPDATE proposals SET status=?,decided_at=?,customer_note=? WHERE token=? AND status=?',(body.decision,int(time.time()),body.note,token,'pending'))
        if updated.rowcount!=1:raise HTTPException(409,'Decision already recorded')
    return get(token)

@router.get('/proposals/{token}/pdf')
def proposal_pdf(token:str):
    """Generate a proposal document; not a tax invoice, and not proof of payment."""
    from reportlab.pdfgen import canvas
    data=get(token)
    mem=io.BytesIO();pdf=canvas.Canvas(mem,pagesize=(595,842))
    y=795
    def line(s):
        nonlocal y
        if y<85:pdf.showPage();y=795
        safe=str(s).encode('latin-1','replace').decode('latin-1')
        pdf.drawString(42,y,safe[:105]);y-=21
    pdf.setTitle('ScopeGuard Change Proposal')
    pdf.setFont('Helvetica-Bold',18);line('ScopeGuard - Change Proposal')
    pdf.setFont('Helvetica',11)
    line(data['title']);line('Status: '+data['status'].upper());line('Currency: '+data['currency'])
    line('Rate per hour: '+str(data['rate']))
    y-=10
    for i,item in enumerate(data['items'],1):
        line(f"{i}. {item['description']}")
        line(f"   {item['hours']} hours x {data['rate']} = {round(item['hours']*data['rate'],2)} {data['currency']}")
        if item['evidence']:line('   Evidence: '+item['evidence'][:85])
    y-=10
    pdf.setFont('Helvetica-Bold',13);line(f"PROPOSED TOTAL: {data['total']} {data['currency']}")
    pdf.setFont('Helvetica',10)
    line('Estimates require freelancer and customer review. Not an invoice or legal opinion.')
    line('Approval status is a workflow record, not a digital signature.')
    pdf.save();mem.seek(0)
    return Response(mem.getvalue(),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="scopeguard-proposal.pdf"'})

@router.get('/stats')
def stats():
    # No public counts of private projects; health signal only.
    return {'storage':'local SQLite','data_retention':'manual deletion','privacy':'share tokens act as access keys'}
