# Atlas graph model and Cypher

This is an additive extension to the existing FalkorDB data model.

Nodes: `Project` (id), `Agreement` (id, version, body), `Clause` (id, text), `Request` (id, text), `Decision` (classification, status), `Exception` (id, request_hash, request_text, effect, reason, reviewer, customer_approved, agreement_version, status).

Relationships: `Project-[:HAS_AGREEMENT]->Agreement`, `Agreement-[:CONTAINS]->Clause`, `Project-[:RECEIVED]->Request`, `Request-[:BASED_ON]->Agreement`, `Request-[:HAS_DECISION]->Decision`, `Agreement-[:HAS_EXCEPTION]->Exception`, `Project-[:RECORDED_EXCEPTION]->Exception`.

Load the active version:
```cypher
MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)
RETURN a.id,a.version,a.body ORDER BY a.version DESC LIMIT 1
```

Find exceptions spanning agreement versions:
```cypher
MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)-[:HAS_EXCEPTION]->(e:Exception)
RETURN a.id,a.version,e.id,e.request_text,e.request_hash,e.effect,e.reason,e.customer_approved,e.status
ORDER BY a.version DESC
```

A confirmed exception is accepted only for an exact normalized request, the active agreement version, and a checked customer-approval flag. Conflicts and old-version exceptions return `needs_review`. This is deliberate conservative logic, not semantic multi-hop agent planning.

For a real multi-tenant production deployment, add authentication/authorization, genuine client signature records, versioning API, audit logging, stronger key isolation, and a security review.
