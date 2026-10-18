(()=>{'use strict';
 const body=document.body;
 if(body.classList.contains('sg-mounted')) return;
 const path=location.pathname;
 if(!/\/(atlas|graph)\.html$/.test(path))return;
 const original=document.querySelector('main'); if(!original)return;
 const panels=[...original.querySelectorAll(':scope > section.panel')];
 if(panels.length<2)return;
 // Existing controls, IDs, and handlers are NOT recreated or removed.
 const isAtlas=path.endsWith('atlas.html');
 const labels=isAtlas?['Agreement setup','Check client request','Reviewed exception']:['Graph project','Graph analysis','Confirm decision'];
 const headings=isAtlas?['Set up a project','Check a change','Record a reviewed exception']:['Create a graph project','Analyze connected context','Confirm a decision'];
 const descriptions=isAtlas?['Register the project and agreement in FalkorDB.','Check earlier promises, then use Gemma where necessary.','Store only human-reviewed decisions as agreement-bound memory.']:['Store a project and its clauses as connected nodes.','Analyze using graph agreement context.','Record a human-reviewed result for later requests.'];
 const shell=document.createElement('div');shell.className='sg-shell';
 const side=document.createElement('aside');side.className='sg-side';side.setAttribute('aria-label','ScopeGuard workspace navigation');
 const brand=document.createElement('div');brand.className='sg-brand';brand.innerHTML='<span class="sg-mark">S</span><span>ScopeGuard <span style="color:var(--sage)">AI</span><small style="display:block;font-size:11px;font-weight:400">Graph intelligence workspace</small></span>';
 const nav=document.createElement('nav');nav.className='sg-nav';
 const buttons=panels.map((panel,i)=>{const b=document.createElement('button');b.type='button';b.textContent=String(i+1).padStart(2,'0')+' · '+(labels[i]||'Step '+(i+1));b.addEventListener('click',()=>show(i));nav.appendChild(b);return b});
 const bottom=document.createElement('div');bottom.className='sg-caption-bottom';bottom.textContent='Local demonstration · FalkorDB-backed · Human review required';
 const shortcuts=document.createElement('div');shortcuts.className='sg-nav';for(const [name,uri] of [['Decision Replay','/replay.html'],['Main workflow','/'],['API docs','/docs']]){const a=document.createElement('a');a.href=uri;a.textContent=name;shortcuts.appendChild(a)}
 side.append(brand,Object.assign(document.createElement('div'),{className:'sg-caption',textContent:'Workspace'}),nav,Object.assign(document.createElement('div'),{className:'sg-caption',textContent:'Quick links'}),shortcuts,bottom);
 const slot=document.createElement('div');slot.className='sg-main';
 const descriptionsEl=panels.map((p,i)=>{const h=document.createElement('div');h.className='sg-screen-heading';const e=document.createElement('span');e.textContent='FalkorDB · Live local workflow';const title=document.createElement('h1');title.textContent=headings[i]||'Graph workflow';const d=document.createElement('p');d.textContent=descriptions[i]||'';h.append(e,title,d);const wrap=document.createElement('div');wrap.className='sg-screen';wrap.append(h,p);slot.append(wrap);return wrap});
 const before=document.createElement('div');before.className='sg-screen';
 // Keep any descriptive hero, links or notes visible on first screen without altering event targets.
 for(const child of [...original.children])if(!panels.includes(child))before.append(child);
 descriptionsEl[0].prepend(before);
 function show(i){descriptionsEl.forEach((el,n)=>{el.hidden=n!==i});buttons.forEach((b,n)=>{b.classList.toggle('active',n===i);if(n===i)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});const hash='#step-'+(i+1);if(location.hash!==hash)history.replaceState(null,'',hash);window.scrollTo(0,0)}
 shell.append(side,slot);original.replaceWith(shell);body.classList.add('sg-mounted');
 let initial=parseInt(location.hash.replace('#step-',''),10)-1;if(!Number.isInteger(initial)||initial<0||initial>=descriptionsEl.length)initial=0;show(initial);
})();