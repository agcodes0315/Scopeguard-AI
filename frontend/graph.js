'use strict';
let projectId = null, requestId = null;
const $ = id => document.getElementById(id);
async function post(path, body) {
  const res = await fetch('/api/graph'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}
function output(id, msg) { $(id).textContent = msg; }
$('create').onclick = async () => {
  try { const r = await post('/projects',{name:$('pname').value, agreement:$('agreement').value});
    projectId=r.project_id; requestId=null;
    output('project',`Created project ${projectId} · ${r.clause_count} connected clauses`);
  } catch(e) { output('project',e.message); }
};
$('analyze').onclick = async () => {
  if (!projectId) return output('decision','Create a graph project first.');
  try { const r=await post('/analyze',{project_id:projectId,request:$('request').value});
    requestId=r.request_id;
    $('classification').value=r.classification;
    output('decision',`Classification: ${r.classification} | Source: ${r.source}\n${r.reasoning}\nPrior decisions checked: ${r.prior_decisions_considered}`);
    const trace=$('trace'); trace.replaceChildren();
    const heading=document.createElement('h3'); heading.textContent='Evidence path from FalkorDB'; trace.append(heading);
    for (const step of r.evidence_path) {
      const p=document.createElement('p'); p.textContent=`${step.from} → ${step.via} → ${step.to}${step.quote ? ' | '+step.quote : ''}`;
      trace.append(p);
    }
  } catch(e) {output('decision',e.message);}
};
$('confirm').onclick = async () => {
  if (!projectId || !requestId) return output('confirmation','Analyze a request first.');
  try { const r=await post('/confirm',{project_id:projectId,request_id:requestId,classification:$('classification').value,reviewer_note:$('note').value});
    output('confirmation',`${r.status}. Click Analyze again with the same request to prove graph memory.`);
  } catch(e) { output('confirmation',e.message); }
};
