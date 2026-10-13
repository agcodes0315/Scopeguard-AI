from io import BytesIO
import pytest
from docx import Document
import fitz
from fastapi.testclient import TestClient
from backend.main import app
from backend.documents import extract_document

AGREEMENT='A website agreement with five pages and two rounds of included revisions.'

def test_txt_extraction():
    result=extract_document('agreement.txt',AGREEMENT.encode())
    assert result['text']==AGREEMENT and result['stored'] is False

def test_docx_extraction():
    doc=Document();doc.add_paragraph(AGREEMENT)
    buf=BytesIO();doc.save(buf)
    assert AGREEMENT in extract_document('agreement.docx',buf.getvalue())['text']

def test_pdf_extraction():
    pdf=fitz.open();page=pdf.new_page();page.insert_text((72,72),AGREEMENT)
    result=extract_document('agreement.pdf',pdf.tobytes())
    assert 'five pages' in result['text'] and result['pages']==1

def test_bad_files():
    with pytest.raises(ValueError):extract_document('agreement.exe',b'dummy')
    with pytest.raises(ValueError):extract_document('agreement.txt',b'x'*(3*1024*1024+1))
    with pytest.raises(ValueError):extract_document('agreement.pdf',b'not a pdf')

def test_endpoint_upload():
    client=TestClient(app)
    response=client.post('/api/documents/extract',files={'file':('agreement.txt',AGREEMENT.encode(),'text/plain')})
    assert response.status_code==200
    assert response.json()['stored'] is False

def test_24_distinct_eval_cases():
    import json
    from pathlib import Path
    cases=json.loads((Path(__file__).parents[1]/'evaluation/cases.json').read_text())
    assert len(cases)>=20
    assert len({x['id'] for x in cases})==len(cases)
    assert all(x['expected'] in ('included','potential_extra','needs_review') for x in cases)
