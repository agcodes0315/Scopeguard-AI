/* ScopeGuard Atlas: read-only, evidence-aware decision explanation. */
(function (root) {
  'use strict';
  function explain(outcome, evidenceText) {
    var heading = String(outcome || '').split('\n')[0].trim();
    var detail = String(outcome || '');
    var evidence = null;
    try { evidence = JSON.parse(evidenceText || 'null'); } catch (_) { /* no graph JSON */ }
    var version = evidence && Number.isInteger(evidence.current_version) ? evidence.current_version : null;
    var versionText = version === null ? 'the current agreement' : 'agreement version ' + version;
    var hasPath = !!(evidence && (Array.isArray(evidence) || Array.isArray(evidence.path)));
    var graphMemory = detail.includes('Source: graph_memory');
    var freshGraph = detail.includes('Source: graph_agreement_plus_gemma');
    var common = ' This is advice, not an invoice or proof of customer consent. Human review is required.';
    if (heading === 'conflict') return {title:'Conflicting previous decisions', message:'The active agreement contains different reviewer decisions for this exact request. Ask for clarification; do not automatically apply either one.' + common, tone:'review'};
    if (heading === 'stale_exception') return {title:'Old agreement — decision not reusable', message:'A matching decision exists for an earlier agreement, but it does not automatically apply to ' + versionText + '.' + common, tone:'review'};
    if (heading === 'applicable_customer_approved_exception') return {title:'Matching exception found', message:'FalkorDB found a reviewer-recorded exception for this request under ' + versionText + '. The stored customer-approved flag is not independent proof of consent; verify the supporting record before acting.' + common, tone:'match'};
    if (heading === 'reviewer_confirmed_only') return {title:'Previous reviewer decision found', message:'FalkorDB found a matching reviewed exception under ' + versionText + ', but customer approval has not been established.' + common, tone:'review'};
    if (heading === 'no_applicable_exception') return {title:'No matching previous decision', message:'FalkorDB found no exact applicable exception under ' + versionText + '. Continue with agreement-based analysis and human review.' + common, tone:'neutral'};
    if (graphMemory) return {title:'Decision replay: graph memory used', message:'The graph-backed workflow retrieved a previously human-confirmed decision for this exact request and agreement. Check the evidence path before relying on it.' + common, tone:'match'};
    if (freshGraph) return {title:'First-pass analysis from graph agreement', message:'FalkorDB supplied the current agreement and related clauses; Gemma analyzed this request because no matching confirmed decision was reused.' + common, tone:'neutral'};
    if (heading === 'included' || heading === 'potential_extra' || heading === 'needs_review') return {title:'Agreement analysis: ' + heading.replace('_',' '), message: hasPath ? 'Review the graph evidence and model reasoning. The recommendation does not itself authorize charges.' : 'Review the model reasoning and verify the evidence before taking action.' , tone:'review'};
    return null;
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {explain: explain};
  if (typeof document === 'undefined') return;
  function setup() {
    var outcome = document.getElementById('outcome');
    var evidence = document.getElementById('evidence');
    if (!outcome || !evidence || document.getElementById('decisionReplayCard')) return;
    var card = document.createElement('section');
    card.id = 'decisionReplayCard';
    card.setAttribute('aria-live','polite');
    card.style.cssText = 'padding:16px;margin:12px 0;border:1px solid #46c7b5;border-radius:12px;background:#102a35;color:#eef8f7;display:none;';
    var title = document.createElement('strong');
    var message = document.createElement('p');
    message.style.marginBottom = '0';
    card.appendChild(title);
    card.appendChild(message);
    outcome.parentNode.insertBefore(card,outcome);
    // Keep full evidence accessible to judges, rather than deleting or changing it.
    var technical = document.createElement('details');
    technical.id = 'atlasTechnicalEvidence';
    var summary = document.createElement('summary');
    summary.textContent = 'Technical evidence (FalkorDB graph path)';
    summary.style.cursor = 'pointer';
    technical.appendChild(summary);
    evidence.parentNode.insertBefore(technical,evidence);
    technical.appendChild(evidence);
    function render() {
      var result = explain(outcome.textContent,evidence.textContent);
      card.style.display = result ? 'block' : 'none';
      if (!result) return;
      title.textContent = result.title;
      message.textContent = result.message;
    }
    var observer = new MutationObserver(render);
    observer.observe(outcome,{characterData:true,childList:true,subtree:true});
    observer.observe(evidence,{characterData:true,childList:true,subtree:true});
    render();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',setup);
  else setup();
})(typeof globalThis !== 'undefined' ? globalThis : this);
