"""Local-only workspace for demo projects, versioned agreements and scope inbox.
No authentication: do not expose this API on a public network.
"""
import hashlib
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

DB = Path(os.getenv('SCOPEGUARD_WORKSPACE_DB', str(Path(__file__).resolve().parent.parent/'data'/'workspace.db')))
router = APIRouter(prefix='/api/workspace', tags=['Local workspace'])


def connection():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA busy_timeout=10000')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, name TEXT NOT NULL, client_label TEXT NOT NULL, created_at INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS agreements (id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id), version INTEGER NOT NULL, text TEXT NOT NULL, sha256 TEXT NOT NULL, created_at INTEGER NOT NULL, UNIQUE(project_id,version));
    CREATE TABLE IF NOT EXISTS inbox (id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id), sender TEXT NOT NULL, message TEXT NOT NULL, received_at INTEGER NOT NULL, reviewed INTEGER NOT NULL DEFAULT 0);
    ''')
    db.commit()
    return db

class ProjectIn(BaseModel):
    name: str = Field(min_length=2,max_length=120)
    client_label: str = Field(default='Client',min_length=1,max_length=120)

class AgreementIn(BaseModel):
    text: str = Field(min_length=20,max_length=30000)

class InboxIn(BaseModel):
    sender: str = Field(default='Client',min_length=1,max_length=120)
    message: str = Field(min_length=5,max_length=15000)


def require_project(db, project_id):
    row=db.execute('SELECT id FROM projects WHERE id=?',(project_id,)).fetchone()
    if not row: raise HTTPException(404,'Project not found')


def clauses_from_text(text):
    """Preserve exact source slices; paragraphs are stable only within a version."""
    import re
    paragraphs=[m.group(0).strip() for m in re.finditer(r'[^\n]+',text) if m.group(0).strip()]
    return [{'clause_id':f'C{i:03d}','quote':p,'line':i} for i,p in enumerate(paragraphs,1)]

@router.post('/projects',status_code=201)
def create_project(body:ProjectIn):
    ident=uuid.uuid4().hex
    with connection() as db:
        db.execute('INSERT INTO projects VALUES(?,?,?,?)',(ident,body.name,body.client_label,int(time.time())))
    return {'id':ident,'name':body.name,'client_label':body.client_label}

@router.get('/projects')
def list_projects():
    with connection() as db:
        rows=db.execute('''SELECT p.*, (SELECT COUNT(*) FROM agreements WHERE project_id=p.id) AS agreement_versions, (SELECT COUNT(*) FROM inbox WHERE project_id=p.id) AS messages FROM projects p ORDER BY p.created_at DESC''').fetchall()
    return {'projects':[dict(x) for x in rows]}

@router.post('/projects/{project_id}/agreements',status_code=201)
def save_agreement(project_id:str,body:AgreementIn):
    with connection() as db:
        require_project(db,project_id)
        version=db.execute('SELECT COALESCE(MAX(version),0)+1 FROM agreements WHERE project_id=?',(project_id,)).fetchone()[0]
        ident=uuid.uuid4().hex
        checksum=hashlib.sha256(body.text.encode()).hexdigest()
        db.execute('INSERT INTO agreements VALUES(?,?,?,?,?,?)',(ident,project_id,version,body.text,checksum,int(time.time())))
    return {'id':ident,'version':version,'sha256':checksum,'clauses':clauses_from_text(body.text)}

@router.get('/projects/{project_id}/agreements')
def list_agreements(project_id:str):
    with connection() as db:
        require_project(db,project_id)
        rows=db.execute('SELECT id,version,sha256,created_at FROM agreements WHERE project_id=? ORDER BY version DESC',(project_id,)).fetchall()
    return {'versions':[dict(r) for r in rows]}

@router.get('/projects/{project_id}/agreements/latest')
def latest_agreement(project_id:str):
    with connection() as db:
        require_project(db,project_id)
        row=db.execute('SELECT * FROM agreements WHERE project_id=? ORDER BY version DESC LIMIT 1',(project_id,)).fetchone()
    if not row: raise HTTPException(404,'No agreement saved')
    d=dict(row);d['clauses']=clauses_from_text(d['text']);return d

@router.post('/projects/{project_id}/messages',status_code=201)
def save_message(project_id:str,body:InboxIn):
    ident=uuid.uuid4().hex
    with connection() as db:
        require_project(db,project_id)
        db.execute('INSERT INTO inbox(id,project_id,sender,message,received_at) VALUES(?,?,?,?,?)',(ident,project_id,body.sender,body.message,int(time.time())))
    return {'id':ident,'message':body.message,'sender':body.sender}

@router.get('/projects/{project_id}/messages')
def list_messages(project_id:str):
    with connection() as db:
        require_project(db,project_id)
        rows=db.execute('SELECT * FROM inbox WHERE project_id=? ORDER BY received_at DESC,id DESC',(project_id,)).fetchall()
    return {'messages':[dict(r) for r in rows]}

@router.patch('/messages/{message_id}/reviewed')
def mark_reviewed(message_id:str):
    with connection() as db:
        result=db.execute('UPDATE inbox SET reviewed=1 WHERE id=?',(message_id,))
        if not result.rowcount: raise HTTPException(404,'Message not found')
    return {'reviewed':True}

class DraftIn(BaseModel):
    client_label:str=Field(default='Client',max_length=120)
    project_title:str=Field(min_length=2,max_length=160)
    currency:str=Field(default='INR',pattern='^(INR|USD|EUR|GBP)$')
    extra_total:float=Field(ge=0,le=100000000)
    items:list[str]=Field(default_factory=list,max_length=20)
    approval_link:str=Field(default='',max_length=400)

@router.post('/draft-reply')
def draft_reply(body:DraftIn):
    """Deterministic editable draft; no outgoing message and no invented contract clauses."""
    if not body.items or body.extra_total <= 0:
        return {'subject':f'Clarification on {body.project_title}', 'body':f'Hello {body.client_label},\n\nI reviewed the latest requests for {body.project_title}. Before quoting additional charges, could we clarify the scope and confirm which items are outside the original agreement?\n\nThank you.'}
    lines='\n'.join(f'- {item[:160]}' for item in body.items)
    link=f'\n\nYou can review the draft proposal here: {body.approval_link}' if body.approval_link else ''
    return {'subject':f'Change request for {body.project_title}', 'body':f'Hello {body.client_label},\n\nThanks for the requested additions to {body.project_title}. I have prepared a proposed scope change for your review:\n\n{lines}\n\nEstimated additional amount: {body.currency} {body.extra_total:,.2f}. This is a proposal, not an invoice or payment request. No additional work will be authorized without your agreement.{link}\n\nPlease let me know if you would like to approve, decline, or discuss the changes.\n\nBest regards'}
