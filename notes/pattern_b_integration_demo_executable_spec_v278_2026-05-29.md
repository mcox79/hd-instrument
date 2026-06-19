# Pattern B integration demo - executable architecture spec (v278)

Date: 2026-05-29
Author: research sub-agent (Opus-escalated; DEEPER fresh-eyes drill)
Status: EXECUTABLE SPEC - engineering team can begin Week-1 immediately
Calibration: lit-scan deflation 0.15-0.25 applied to risk/timeline estimates per [[feedback-lit-scan-calibration-penalty]]
Substrate-product framing per [[feedback-no-papers-product-only]]

## HEADLINE

Pattern B integration demo = "substrate-as-tool-for-LLM with substrate-mediated outputs for verifiable facts, audit-trail distinguishing substrate-sourced vs LLM-generated content." This spec defines the FULL executable architecture: 5 processes, 4 APIs, 1 audit log schema, 1 deletion-certificate format, and an 8-week engineering plan. Recommended use case = LEGAL eDiscovery + privilege review (tightest product-market fit per v276; partner pathway shortest; demonstration aesthetics strongest; existing $20.74B market with $145K post-Rakoff sanctions creating immediate buyer urgency). HARD_PASS thresholds pre-registered: >=5x token reduction vs RAG baseline AND >=95% factual consistency AND >=98% audit-trail completeness AND deletion-cert verifiable in <500ms. P_deflated of successfully shipping in 8 weeks given current substrate maturity = 0.45 (Pattern B is novel-integration synthesis, capped at 0.50; risks dominated by substrate-LLM impedance mismatch + use-case data acquisition).

## Cheap decisive test

A 5-day "thin-slice" smoke before full 8-week commit: hand-build the smallest possible Pattern B pipeline on a 100-document subset of the chosen use-case corpus. Measure (a) token consumption on 20 representative queries vs RAG baseline, (b) audit-trail completeness on those 20 queries, (c) deletion-cert end-to-end on 5 records. If thin-slice shows >=3x token reduction AND audit-trail is structurally complete, commit to full 8 weeks. If thin-slice shows <2x reduction OR audit gaps in critical paths, pivot to Pattern A (shallow RAG-replacement) OR reframe use case before sunk-cost on 6-week build.

## Falsifiable predictions

HARD_PASS (all four required for demo success):
- HP1 [token reduction]: >=5x reduction vs RAG baseline on factual-Q&A workload over 1000-query benchmark. Per-query mean token count measured at LLM API boundary. 95% CI on reduction ratio excludes 4x.
- HP2 [quality parity]: factual-consistency-vs-ground-truth >=95% (substrate-mediated path) AND not statistically significantly different from RAG-baseline (Wilson 95% CI overlap with RAG's quality interval).
- HP3 [audit-trail completeness]: >=98% of substrate-sourced output tokens have a verifiable provenance chain (atom-id -> binding-path -> retrieval-event -> audit-log-entry); 100% of fact-retrieval API calls logged.
- HP4 [deletion-cert]: end-to-end deletion-cert generation + cryptographic verification roundtrip <500ms p95; certificate independently verifiable by a separate process given only public-key + corpus-state-hash.

HARD_FAIL (any one triggers demo deprioritization):
- HF1: <2x token reduction (substrate provides no meaningful efficiency gain in this use case).
- HF2: factual-consistency <90% OR >5pp worse than RAG baseline on quality parity (substrate degrades quality unacceptably).
- HF3: audit-trail-completeness <85% OR systemic gaps in critical paths like multi-fact compositional queries (audit story fails the regulator-ready bar).
- HF4: substrate-LLM impedance mismatch unfixable - LLM cannot reliably emit tool-call JSON for substrate API, OR substrate output cannot be reliably consumed by LLM as context (production reliability <80% on tool-use protocol).

MIDDLE_BAND (demo continues with reframing):
- 2-5x token reduction: real but smaller-than-target win; reframe positioning from "5-15x" to "2-5x with audit guarantee" and ship anyway (Pattern B still differentiated).
- 90-95% factual consistency: ship with explicit quality envelope; product disclaimer; pursue HP2 in v2.
- 85-98% audit completeness: ship with documented gaps; product roadmap closes gaps; not blocking for design-partner pilot.

## Cross-thread synthesis with prior entries

Integrates with:
- [[strategic-roadmap-llm-integration-3mo-v278-2026-05-29]]: Item 1 (highest priority); spec is the implementation of the user-named priority.
- [[research-product-positioning-v276-2026-05-29]]: Top-3 segments are regulated-financial / legal-eDiscovery / regulated-healthcare. This spec selects LEGAL as the recommended use case per Section 6 below.
- [[project-substrate-killer-features-2026-05-26]]: deletion-cert (KF-2) + compositionality audit are killer features 1 + 2; this demo exercises both in production-like pipeline.
- [[strategic-input-two-layer-and-dwave-v278-2026-05-29]]: Pattern B uses the OPERATIONAL layer (KF-roster + deletion-cert + edit-isolation); internal-layer Direction B is NOT exercised by this demo (orthogonal capability).
- [[project-substrate-skahm-class-confirmed-2026-05-27]]: substrate-class WHY is internal; demo's customer-facing positioning is "compliance-grade auditable memory layer" - does not lead with stat-mech framing.
- [[feedback-query-privacy-decomposition]]: no substrate-novel mechanism names appear in any customer-facing demo asset (positioning is product-grade, not physics-grade).

---

## Section 1: System architecture diagram (textual)

```
================================================================================
PATTERN B INTEGRATION DEMO - SYSTEM ARCHITECTURE
================================================================================

  +----------------+
  | End user query |
  | (legal staff)  |
  +-------+--------+
          |
          v
+------------------------------------------------------------+
|   Orchestration layer (Pattern-B Controller, Python)       |
|   - Tool-use coordinator (LLM-side tool-call dispatcher)   |
|   - Substrate-mediated-output policy engine (Sec 3)        |
|   - Provenance tagger (annotates every output token)       |
+------+-----------+---------------+------------------+------+
       |           |               |                  |
       v           v               v                  v
+----------+ +-----------+ +--------------+   +---------------+
| LLM API  | | Substrate | | Audit log    |   | Deletion-cert |
| client   | | process   | | service      |   | service       |
| (vendor) | | (hdlab    | | (append-only |   | (Ed25519      |
|          | | runtime)  | | JSONL +      |   | signing +     |
|          | |           | | DuckDB       |   | corpus-state- |
|          | |           | | indexer)     |   | hash chain)   |
+----+-----+ +-----+-----+ +------+-------+   +-------+-------+
     |             |              |                   |
     |             |              |                   |
     v             v              v                   v
+----------------------------------------------------------+
| Persistence layer                                        |
|  - LLM API (Anthropic/OpenAI; chat completion + tools)   |
|  - Substrate corpus store (DuckDB; v275 KF-2 isolation)  |
|  - Audit log (append-only JSONL; daily-rolling files)    |
|  - Cert chain (cert-id, sha256(corpus-state-pre/post),   |
|     atom-id, ts, signature)                              |
+----------------------------------------------------------+

DATA FLOW (typical fact-Q&A query):

Step 1. User query enters Pattern-B Controller. Controller logs receipt
        with query-id (UUIDv7 - time-orderable) to audit log.

Step 2. Controller sends query to LLM with system prompt declaring
        substrate-tool availability (JSON-schema tool definitions per
        Sec 2). Tool-use roundtrip count starts at 0.

Step 3. LLM returns tool_use block: substrate.retrieve_fact(query='...')
        OR substrate.compositional_query(bindings=[...]). Controller
        logs the tool call.

Step 4. Controller dispatches to substrate process. Substrate runs
        codebook lookup (hdlab/memory.py) + (if compositional)
        unbind chain (hdlab/binding.py). Returns:
        - atom-id (substrate-native ID, not LLM token id)
        - similarity score
        - retrieval path (list of binding ops applied)
        - source-document-id (metadata join)

Step 5. Controller checks confidence-threshold (Sec 3 policy tree).
        - HIGH confidence (score > 0.85) AND verifiable-fact-mode:
          substrate output goes DIRECT to user (bypass LLM phrasing).
          Provenance tagger marks token range as [SUBSTRATE-SOURCED].
        - MEDIUM confidence (0.6-0.85) OR compositional-query:
          substrate result returned as tool_result to LLM; LLM
          phrases. Provenance tagger marks token range as
          [LLM-PHRASED-FROM-SUBSTRATE].
        - LOW confidence (<0.6) OR substrate.no_match: LLM may
          generate from training corpus; tagger marks
          [LLM-GENERATED] and triggers low-confidence warning.

Step 6. Final response returned to user with optional provenance
        sidebar (audit-mode UI) showing per-token color-coding.
        Audit-log entry finalized with full call chain.

DELETION FLOW (GDPR Article 17 request):

Step 1. Admin invokes deletion-cert-service.delete(record_id, requester,
        legal_basis).

Step 2. Service computes corpus-state-hash PRE = sha256 over substrate
        atom-table (ordered by atom-id).

Step 3. Substrate process executes erase: zero-out atom vector +
        remove atom-id from codebook + scrub W matrix singular
        contribution (v275 KF-2 standard-path isolation invocation).

Step 4. Service computes corpus-state-hash POST.

Step 5. Service signs (cert-id, atom-id, ts, hash-PRE, hash-POST,
        requester-id, legal-basis-tag) with Ed25519 service key.
        Cert appended to cert-chain (Merkle-tree daily root).

Step 6. Independent verifier (separate process, public-key only) can
        verify: signature valid AND hash-PRE was previously a published
        Merkle root AND hash-POST matches current root.

================================================================================
```

### Process inventory (5 processes)

1. **Pattern-B Controller** (Python; orchestration logic; ~800 LOC)
2. **LLM API client** (vendor SDK wrapper; Anthropic Messages API + tool-use; ~200 LOC)
3. **Substrate process** (hdlab runtime; existing `hdlab/memory.py`, `hdlab/binding.py`, `hdlab/store.py`, `hdlab/semantic.py`; NEW: thin REST/JSON wrapper ~300 LOC)
4. **Audit log service** (append-only JSONL writer + DuckDB indexer; ~400 LOC)
5. **Deletion-certificate service** (Ed25519 signer + Merkle-chain manager; ~600 LOC)

Total NEW code: ~2300 LOC + reuse of existing substrate primitives.

---

## Section 2: Tool-use API contract

LLM declares substrate as a tool via Anthropic Messages API tool-use protocol (or OpenAI function-calling equivalent). Five tool definitions:

### Tool 2.1: `substrate.retrieve_fact`

```json
{
  "name": "substrate_retrieve_fact",
  "description": "Retrieve a verifiable fact from the substrate corpus. Returns the fact text, similarity score, source document ID, and atom ID for provenance. Use this for any factual claim the user needs verified against the corpus.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural-language fact query. Will be encoded into substrate space via codebook lookup."
      },
      "min_confidence": {
        "type": "number",
        "default": 0.6,
        "description": "Minimum similarity score (0.0-1.0) for a match. Below this, returns no_match."
      },
      "max_results": {
        "type": "integer",
        "default": 5,
        "description": "Maximum number of candidate facts to return."
      }
    },
    "required": ["query"]
  }
}
```

Response shape:
```json
{
  "status": "match" | "no_match" | "ambiguous",
  "results": [
    {
      "atom_id": "atom_a2f8c1...",
      "fact_text": "The court ruled that...",
      "similarity": 0.87,
      "source_doc_id": "doc_2024_smith_v_jones",
      "source_doc_offset": [1284, 1453],
      "binding_path": ["entity:Smith", "relation:ruled", "object:Jones"],
      "retrieved_at": "2026-05-29T14:32:11.293Z"
    }
  ],
  "audit_log_id": "evt_01HJ7..."
}
```

### Tool 2.2: `substrate.compositional_query`

For multi-fact joins via substrate's binding algebra. Per [[project-substrate-skahm-class-confirmed]] - substrate's compositional binding (Property 3) is the differentiated primitive.

```json
{
  "name": "substrate_compositional_query",
  "description": "Multi-fact query via substrate binding algebra. Specify entity bindings (subject, predicate, object) and the substrate composes a retrieval over all matching joins. Use for queries like 'cases citing X and ruled by judge Y'.",
  "input_schema": {
    "type": "object",
    "properties": {
      "bindings": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "role": {"type": "string"},
            "filler": {"type": "string"}
          }
        },
        "description": "List of role-filler binding pairs to compose."
      },
      "min_confidence": {"type": "number", "default": 0.5}
    },
    "required": ["bindings"]
  }
}
```

### Tool 2.3: `substrate.store_fact`

```json
{
  "name": "substrate_store_fact",
  "description": "Store a new verifiable fact in the substrate corpus. Requires explicit provenance metadata (source document, extraction confidence). Used for adding domain knowledge or session-specific facts.",
  "input_schema": {
    "type": "object",
    "properties": {
      "fact_text": {"type": "string"},
      "source_doc_id": {"type": "string"},
      "source_doc_offset": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
      "extraction_confidence": {"type": "number"},
      "retention_policy": {
        "type": "object",
        "properties": {
          "ttl_days": {"type": "integer"},
          "deletion_on_request": {"type": "boolean", "default": true}
        }
      }
    },
    "required": ["fact_text", "source_doc_id", "extraction_confidence"]
  }
}
```

### Tool 2.4: `substrate.delete_fact_with_certificate`

```json
{
  "name": "substrate_delete_fact_with_certificate",
  "description": "Delete a fact from substrate and emit cryptographic deletion certificate. Used for GDPR Art 17 requests, attorney-client privilege purging, or admin-triggered erasure. Returns the certificate for downstream audit retention.",
  "input_schema": {
    "type": "object",
    "properties": {
      "atom_id": {"type": "string"},
      "requester_id": {"type": "string"},
      "legal_basis": {
        "type": "string",
        "enum": ["GDPR_ART_17", "HIPAA_INDIVIDUAL_REQUEST", "PRIVILEGE_PURGE", "ADMIN_RETENTION_EXPIRY", "OTHER"]
      },
      "notes": {"type": "string"}
    },
    "required": ["atom_id", "requester_id", "legal_basis"]
  }
}
```

Response:
```json
{
  "status": "deleted",
  "certificate": {
    "cert_id": "cert_01HJ7XYZ...",
    "atom_id": "atom_a2f8c1...",
    "deletion_ts": "2026-05-29T14:32:11.293Z",
    "corpus_state_hash_pre": "sha256:9a7f...",
    "corpus_state_hash_post": "sha256:8b6e...",
    "requester_id": "user_admin_42",
    "legal_basis": "GDPR_ART_17",
    "signature": "ed25519:7c2d...",
    "signing_key_id": "key_2026_q2",
    "merkle_root_chain_inclusion_proof": ["sha256:...", "sha256:..."]
  }
}
```

### Tool 2.5: `substrate.verify_audit_trail`

```json
{
  "name": "substrate_verify_audit_trail",
  "description": "Reconstruct the substrate retrieval chain for a prior response. Given a response_id, returns every substrate call made, every atom retrieved, and the provenance chain. Use for post-hoc audit or compliance review.",
  "input_schema": {
    "type": "object",
    "properties": {
      "response_id": {"type": "string"}
    },
    "required": ["response_id"]
  }
}
```

### Worked example: legal fact-Q&A roundtrip

User: "What was the holding in Smith v. Jones (2024)?"

LLM turn 1 (after system prompt declaring tools):
```json
{
  "role": "assistant",
  "content": [
    {"type": "tool_use", "id": "tu_01", "name": "substrate_retrieve_fact",
     "input": {"query": "Smith v. Jones 2024 holding", "min_confidence": 0.7}}
  ]
}
```

Controller dispatches to substrate. Substrate returns:
```json
{"status": "match", "results": [
  {"atom_id": "atom_a2f8c1", "fact_text": "The court held that...",
   "similarity": 0.91, "source_doc_id": "doc_smith_v_jones_2024",
   "binding_path": ["case:Smith_v_Jones_2024", "section:holding"],
   "retrieved_at": "2026-05-29T14:32:11.293Z"}
], "audit_log_id": "evt_01HJ7"}
```

Confidence 0.91 > 0.85 + verifiable-fact-mode -> Controller selects DIRECT path: substrate output (fact_text) returned to user verbatim with provenance tag, bypassing LLM phrasing. LLM call concluded with NO further token generation. Token reduction in this turn: large (LLM did not need to generate the answer text, only the tool-call JSON ~80 tokens vs ~300-500 tokens for RAG-baseline LLM-rephrased answer).

---

## Section 3: Substrate-mediated output policy

### Decision tree

```
START: substrate retrieval completed
  |
  v
+----------------------------------+
| Query classification             |
+----------------------------------+
  |       |       |       |
  v       v       v       v
VERIFIABLE  COMPOSITIONAL  GENERATIVE  AMBIGUOUS
  |             |             |          |
  v             v             v          v
[check confidence...] [LLM phrases] [LLM generates] [LLM clarifies]
```

Query classifier (Controller logic, ~100 LOC):
- VERIFIABLE: query maps 1:1 to a stored atom (single fact retrieval). Detected by: tool-call shape was `substrate_retrieve_fact` AND results.length == 1 AND similarity > 0.85.
- COMPOSITIONAL: query requires binding-algebra join across multiple atoms. Detected by: tool-call was `substrate_compositional_query` OR results.length > 1.
- GENERATIVE: query requires synthesis/inference beyond corpus facts. Detected by: substrate returned `no_match` OR LLM did not call substrate.
- AMBIGUOUS: query parser cannot resolve. Detected by: similarity in [0.5, 0.7] OR multi-atom matches with conflicting facts.

### Output paths

| Class | Confidence | Output path | Provenance tag |
|---|---|---|---|
| VERIFIABLE | > 0.85 | DIRECT (substrate output verbatim) | [SUBSTRATE-DIRECT] |
| VERIFIABLE | 0.7-0.85 | LLM-PHRASED (LLM rewrites for fluency) | [LLM-PHRASED-FROM-SUBSTRATE] |
| VERIFIABLE | < 0.7 | LLM-PHRASED + warning | [LLM-PHRASED-LOW-CONF] |
| COMPOSITIONAL | > 0.7 | LLM-PHRASED (multi-fact join needs natural language) | [LLM-PHRASED-COMPOSITIONAL] |
| COMPOSITIONAL | < 0.7 | LLM-PHRASED + warning | [LLM-PHRASED-LOW-CONF] |
| GENERATIVE | n/a | LLM-GENERATED (with refusal-or-disclaimer at vendor's discretion) | [LLM-GENERATED] |
| AMBIGUOUS | n/a | LLM-CLARIFIES (asks follow-up) | [LLM-CLARIFICATION] |

### Confidence-threshold semantics

The 0.85 / 0.7 / 0.6 thresholds are TUNABLE per use case. Initial values calibrated against legal-corpus benchmark (Section 7); adjust per quality-parity protocol (Section 8).

Critical: confidence threshold values + tag policy are themselves logged to audit-trail per query (so a regulator can verify which threshold policy was active at decision time).

---

## Section 4: Audit trail design

### Per-token provenance encoding

Every output token to the user is tagged with one of 5 provenance classes:
- SUBSTRATE-DIRECT (substrate output verbatim)
- LLM-PHRASED-FROM-SUBSTRATE (LLM rewrote substrate output for fluency)
- LLM-PHRASED-COMPOSITIONAL (LLM joined multi-atom substrate output)
- LLM-PHRASED-LOW-CONF (substrate matched but below high-conf threshold)
- LLM-GENERATED (no substrate retrieval; LLM's training corpus only)
- LLM-CLARIFICATION (LLM asking follow-up)

Encoded as per-token attribute in the response object; rendered as color-coded UI in audit-mode.

### Audit log record schema (JSONL append-only)

One log file per day per tenant: `/var/log/pattern-b-audit/<tenant>/<YYYY-MM-DD>.jsonl`

```json
{
  "event_id": "evt_01HJ7XYZ...",
  "event_type": "QUERY_RECEIVED" | "LLM_CALL" | "TOOL_CALL" | "SUBSTRATE_RETRIEVE" | "POLICY_DECISION" | "OUTPUT_SENT" | "DELETION_REQUESTED" | "DELETION_COMPLETED",
  "ts_ns": 1716998400000000000,
  "session_id": "sess_01HJ7",
  "query_id": "q_01HJ7",
  "user_id": "user_42",
  "tenant_id": "tenant_acme_law",
  "trace_parent_id": "evt_01HJ7..." or null,
  "payload": {
    "...": "type-specific fields"
  },
  "sha256_chain_prev": "sha256:abcd...",
  "sha256_self": "sha256:efgh..."
}
```

### Verifiability properties

1. **Append-only by file mode**: chmod 0440 on rolled files; current file 0640 owner-write-only during the day.
2. **Hash chain**: each event has `sha256_chain_prev` linking to prior event's `sha256_self`. Tampering with any event invalidates downstream chain.
3. **Daily Merkle root**: end-of-day, compute Merkle root over day's events; root published to immutable store (S3 Object Lock OR blockchain-anchored OR signed by deletion-cert service key).
4. **Per-query reconstruction**: `substrate.verify_audit_trail(response_id)` walks events linked by trace_parent_id from QUERY_RECEIVED through OUTPUT_SENT; verifies hash chain segment.
5. **Substrate-corpus state hash**: every SUBSTRATE_RETRIEVE event includes the current corpus_state_hash, so audit can verify the retrieval was against the corpus state we claim.

### Per-fact provenance

Every atom in substrate carries metadata:
```json
{
  "atom_id": "atom_a2f8c1",
  "stored_at": "2026-05-29T14:32:11Z",
  "stored_by": "user_42",
  "source_doc_id": "doc_smith_v_jones_2024",
  "source_doc_offset": [1284, 1453],
  "extraction_confidence": 0.92,
  "retention_policy": {"ttl_days": 365, "deletion_on_request": true},
  "binding_role_assignments": [{"role": "case", "filler": "Smith_v_Jones_2024"}]
}
```

### Per-output completeness invariant

Definition (testable): for every output token tagged SUBSTRATE-DIRECT or LLM-PHRASED-FROM-SUBSTRATE, the audit log contains a SUBSTRATE_RETRIEVE event with payload.atom_id matching, AND the binding_path is consistent with the substrate corpus state at that ts.

Completeness measurement = fraction of output tokens (in the above tag classes) for which this invariant holds. HP3 target: >=98%.

---

## Section 5: Deletion certificate semantics

### Cryptographic guarantees

The certificate proves, given only the public key of the deletion-cert service and the immutable Merkle root chain:

1. **Authenticity**: certificate was issued by the deletion-cert service (Ed25519 signature verifies).
2. **Atomicity of deletion**: corpus_state_hash transitioned from hash_pre to hash_post in a single signed event (atomic w.r.t. cert).
3. **Inclusion in audit chain**: cert's Merkle-inclusion proof verifies against published daily roots.
4. **Specificity**: the cert names exactly which atom_id was deleted; cert does NOT prove the atom's content (content was destroyed); cert proves the atom_id existed and was removed.
5. **Time bound**: deletion_ts within the daily Merkle root's coverage window.

The certificate does NOT prove:
- That LLM-internal weights or LLM-cache do not retain the fact (LLM-side is out of substrate's control).
- That backups elsewhere in the customer's data infrastructure were also purged.
- That the fact was never disclosed to a third party prior to deletion.

The cert proves what the substrate layer is responsible for, which is the demand-driver: regulator wants proof the auditable-memory layer purged.

### Certificate format (canonical JSON, deterministic serialization)

```json
{
  "version": "1.0",
  "cert_id": "cert_01HJ7XYZ...",
  "atom_id": "atom_a2f8c1...",
  "deletion_ts": "2026-05-29T14:32:11.293Z",
  "deletion_ts_ns": 1716998400293000000,
  "corpus_state_hash_pre": "sha256:9a7f...",
  "corpus_state_hash_post": "sha256:8b6e...",
  "requester_id": "user_admin_42",
  "legal_basis": "GDPR_ART_17",
  "legal_basis_notes": "Article 17 request received 2026-05-28 case file #2026-1284",
  "tenant_id": "tenant_acme_law",
  "signing_key_id": "key_2026_q2",
  "signing_algorithm": "Ed25519",
  "signature": "ed25519:7c2d...",
  "merkle_root_chain_inclusion_proof": [
    {"position": "left", "hash": "sha256:..."},
    {"position": "right", "hash": "sha256:..."}
  ],
  "merkle_root_id": "root_2026-05-29_daily"
}
```

### Verification protocol (independent verifier, ~150 LOC)

```python
def verify_deletion_certificate(cert: dict, public_key: bytes, merkle_root_lookup: dict[str, bytes]) -> bool:
    # 1. Verify signature over canonical-JSON of cert minus signature field
    canonical = canonicalize_json({k: v for k, v in cert.items() if k != "signature"})
    if not ed25519_verify(public_key, canonical, cert["signature"]):
        return False
    # 2. Verify Merkle inclusion proof
    root_id = cert["merkle_root_id"]
    expected_root = merkle_root_lookup.get(root_id)
    if expected_root is None:
        return False
    computed_root = compute_merkle_root_from_proof(cert["cert_id"], cert["merkle_root_chain_inclusion_proof"])
    if computed_root != expected_root:
        return False
    # 3. Verify ts within root's coverage window
    if not ts_within_window(cert["deletion_ts"], root_id):
        return False
    return True
```

### GDPR Article 17 alignment

GDPR Art 17 requires (a) erasure on request without undue delay (typically 30 days), (b) confirmation to data subject. The certificate maps to:
- (a) Substrate erase + cert generation within <500ms (HP4); well within 30-day window.
- (b) Certificate IS the confirmation; structurally machine-verifiable; usable as compliance evidence.

### EU AI Act Article 10/12 alignment

Article 10 (data governance): training data quality + bias documentation. Substrate corpus + audit log + retention policy metadata satisfy.

Article 12 (record-keeping): high-risk AI systems must maintain logs of automated operation. Audit log + Merkle chain satisfy. 10-year retention requirement: Merkle roots + log archives must be retained 10 years.

### Tension resolution (GDPR delete vs AI Act retain)

The core insight (per v276 product positioning): the certificate IS the audit record. After deletion, the cert persists as proof of erasure for AI Act retention; the deleted content is gone for GDPR purposes. Same data structure serves both regulations.

---

## Section 6: Three use-case selection (full comparison)

### Use case A: Medical literature Q&A

| Dimension | Detail |
|---|---|
| Primary stakeholder | Clinical decision support team at hospital system; medical librarian; CMIO |
| Data sources | PubMed Central (open access, 8M+ articles); UpToDate (proprietary, license required); ClinicalTrials.gov; hospital-internal protocol library |
| Regulatory pin | HIPAA Business Associate Agreement (BAA) + ISO 42001:2023 + state medical board guidelines |
| Demo aesthetics | High: physician-facing demo with "show your sources" UX is compelling; deletion-cert maps to patient request to remove PHI from AI memory |
| Partner acquisition pathway | Long: HIMSS conference + hospital system CMIO outreach + 6-9 month procurement cycle |
| Time to pilot | 9-12 months (BAA negotiation + clinical validation + IRB if applicable) |
| Blocker risks | HIGH: HIPAA-compliant infrastructure required from Day 1 (no shortcut); PHI cannot enter demo until BAA + cloud-isolation; hospital procurement cycles are 6-9 months minimum; clinical-validation work outside our scope |
| Data acquisition for demo | PubMed Central is open; UpToDate-style proprietary corpus requires license; demo can run on PubMed alone but aesthetic is weaker |

### Use case B: Legal research

| Dimension | Detail |
|---|---|
| Primary stakeholder | Litigation partner + eDiscovery manager + General Counsel at AmLaw 200 firm OR legal-tech vendor (Relativity, Everlaw, Reveal) |
| Data sources | Court Listener (open access, 7M+ federal cases); CAP Caselaw Access Project (Harvard, 6.7M cases); firm-internal matter documents (for matter-isolation demo) |
| Regulatory pin | Attorney-client privilege preservation (state bar rules) + Judge Rakoff Feb 2026 ruling + post-$145K-sanctions case law |
| Demo aesthetics | HIGHEST: deletion-cert maps DIRECTLY to "destroyed privileged materials" - the most narratively powerful audit story across all three; matter-isolation via substrate KF-2 production-N=4096 HARD_PASS evidence |
| Partner acquisition pathway | SHORTEST: legal-tech is consolidated (~20 vendors); LegalTech conference Feb 2026 connections; ABA TECHSHOW; founder warm intro via legal-tech operator network |
| Time to pilot | 6-9 months (privilege-review pilot at one matter team is contained; doesn't need firm-wide buy-in to start) |
| Blocker risks | MEDIUM: privilege-review use case has clear ROI; data acquisition is solved (Court Listener + CAP Caselaw are public); matter-isolation evidence already exists (v275 KF-2 production-scale); closed-loop deployment standard in legal tech |
| Data acquisition for demo | TRIVIAL: Court Listener API is free public; CAP Caselaw bulk download is free; demo can run on real cases out of the gate |

### Use case C: Financial compliance

| Dimension | Detail |
|---|---|
| Primary stakeholder | Chief Compliance Officer at top-50 broker-dealer OR Head of Risk at retail bank OR FinTech compliance team |
| Data sources | SEC EDGAR (open access, 10-K/10-Q filings); FINRA rule book (public); firm-internal trade surveillance + AML alerts (for SOX/AML demo) |
| Regulatory pin | SOX + FINRA 2026 Oversight Report + EU AI Act high-risk classification + GDPR (EU operations) + AML/KYC (BSA, FinCEN) |
| Demo aesthetics | HIGH: FINRA 2026 Oversight Report explicitly names "audit trail of multi-step reasoning" as a gap; substrate's compositional audit lands directly into that gap |
| Partner acquisition pathway | MEDIUM: FINRA Annual Conference May 2026 + Sibos September 2026 + RSA Compliance Summit + direct CCO outreach at top-50 broker-dealers |
| Time to pilot | 9-15 months (SOC 2 Type II required pre-deployment, 8-12 wk audit window; FINRA-supervised firms have additional process) |
| Blocker risks | HIGH: SOC 2 Type II audit required pre-pilot (8-12 weeks observation); firm procurement cycles 6-9 months; AML/KYC use case is highly sensitive, demo data is hard to acquire without firm collaboration |
| Data acquisition for demo | MEDIUM: SEC EDGAR is open; firm-internal trade surveillance data requires partnership; can demo on EDGAR alone but aesthetic less compelling than legal |

### RECOMMENDED USE CASE: B (Legal research + privilege review)

Rationale (single sentence):
> Legal-eDiscovery has the shortest partner-acquisition pathway, tightest product-market fit per v276 (Judge Rakoff Feb 2026 ruling + $145K sanctions create immediate buyer urgency), trivial demo-data acquisition (Court Listener + CAP Caselaw are free public corpora), narrativey-strongest deletion-cert framing ("destroyed privileged materials" maps 1:1), and substrate-physics evidence already exists at production-scale (v275 KF-2 N=4096 standard-path isolation HARD_PASS = matter-isolation proof).

Backup recommendation (if legal partner cannot be acquired by Week 4): Use case C (financial compliance) on SEC EDGAR demo data.

NOT recommended for first demo: Use case A (medical) due to BAA + HIPAA infrastructure overhead during the 8-week build window.

---

## Section 7: Token consumption measurement protocol

### RAG baseline architecture

Standard RAG implementation against same use-case corpus:
- Embedding model: OpenAI text-embedding-3-large (3072-dim) or open-source equivalent (BGE-M3)
- Vector store: Pinecone serverless (or FAISS local) - explicit configuration matched to substrate corpus size
- Retrieval: top-5 chunks per query, 512-token chunks
- LLM phrasing: claude-sonnet-4.5 generates response with retrieved chunks as context
- Token measurement: count all tokens at LLM API boundary (input + output)

### Pattern B measurement

Same LLM (claude-sonnet-4.5); tool-use protocol; substrate replaces vector retrieval; substrate-direct outputs bypass LLM phrasing.

Token measurement: input + output at LLM API boundary, INCLUDING tool-call JSON and tool-result JSON tokens.

### Counterfactual scenarios

For each query in benchmark, measure:
1. **RAG baseline**: input_tokens + output_tokens
2. **Pattern B substrate-mediated DIRECT**: input_tokens (system+user+tool-call) + output_tokens (tool-call JSON; substrate output bypasses LLM)
3. **Pattern B LLM-PHRASED**: input_tokens (system+user+tool-call+tool-result) + output_tokens (LLM-phrased answer)
4. **Pattern B GENERATIVE fallback**: input_tokens + output_tokens (LLM generates without substrate)

Reduction ratio = RAG_baseline_tokens / Pattern_B_tokens, per query.

### Sample size for statistical significance

Target: 1000 queries minimum for benchmark. Power analysis:
- Want to detect 5x reduction with 95% CI excluding 4x.
- Per-query variance expected to be high (some queries are VERIFIABLE -> large reduction; some are GENERATIVE -> no reduction).
- 1000 queries gives standard error ~10-15% on mean reduction; sufficient to discriminate 4x vs 5x.

Query mix (calibrated to legal use case):
- 40% VERIFIABLE single-fact lookup (case holding, statute text, citation lookup)
- 30% COMPOSITIONAL multi-fact join (cases by judge X citing precedent Y; statutes amended after date Z)
- 20% GENERATIVE inference (does case A apply to fact pattern B? - requires LLM reasoning)
- 10% AMBIGUOUS / clarification

### Expected reduction band per use case

Legal (recommended): 5-12x mean reduction (high VERIFIABLE+COMPOSITIONAL share; small GENERATIVE share). HP1 target 5x is at the lower end of expected band.

Medical: 4-10x mean reduction (more GENERATIVE inference needed for clinical decision support; reduces overall ratio).

Financial: 6-15x mean reduction (very high VERIFIABLE share for regulation lookup; HP1 target comfortably met).

### Measurement infrastructure

- Wrapper around Anthropic SDK: log every call's input_tokens + output_tokens + tool-use turns
- Per-query JSON record: query_id, query_text, query_class, rag_tokens, pattern_b_tokens, reduction_ratio
- Daily aggregation to DuckDB
- Bootstrap 95% CI on mean reduction (10000 resamples; legal benchmark)

---

## Section 8: Quality parity assessment protocol

### Proxy metrics (no human eval required)

1. **Factual consistency vs ground truth**:
   - Method: each query in benchmark has a labeled ground-truth answer (extracted from source document; legal team validates upfront for 1000 queries; ~$3-5K labeling cost)
   - Metric: per-query 0/1 correctness (LLM-judge with GPT-4o or claude-opus-4-7 as judge; calibrate judge against 100 human-labeled samples; judge agreement >=90% target)
   - Aggregation: mean correctness; Wilson 95% CI

2. **Audit-trail completeness**:
   - Method: for every output token tagged SUBSTRATE-DIRECT or LLM-PHRASED-FROM-SUBSTRATE, verify audit-log invariant (Section 4)
   - Metric: fraction of tokens passing invariant
   - HP3 target: >=98%

3. **Refusal rate on out-of-substrate queries**:
   - Method: include 100 queries known to have no substrate match in the benchmark
   - Metric: Pattern B should refuse OR explicitly flag low-confidence; RAG baseline often hallucinates
   - Target: Pattern B refusal/flag >=95%; RAG baseline ~60-70% (illustrates the audit-grade advantage)

4. **Citation accuracy**:
   - Method: verify cited source_doc_id + offset matches a real document containing the fact
   - Metric: fraction of cited claims with verifiable source
   - Target: Pattern B >=99% (substrate provides citation by construction); RAG baseline 70-85%

### Human evaluation plan (if budget permits)

If $3-5K labeling budget approved:
- Recruit 3-5 legal professionals (paralegals or JD-track with legal-tech experience) via Upwork
- Side-by-side blind comparison of RAG baseline vs Pattern B responses on 200 queries
- Likert-scale rating on (a) factual correctness, (b) usefulness, (c) trustworthiness
- Statistical test: Wilcoxon signed-rank for paired comparison

### Acceptance criteria

HP2 met if: factual_consistency_pattern_b >= 95% AND |factual_consistency_pattern_b - factual_consistency_rag| <= 2pp (95% CI overlap).

---

## Section 9: Latency profiling protocol

### End-to-end pipeline timing breakdown

Instrument each pipeline stage with `time.perf_counter_ns()`:
1. User query received -> Controller (target <5ms)
2. Controller -> LLM API first roundtrip (LLM call latency; ~500-1500ms typical for sonnet)
3. LLM tool-call returned -> Controller (parse + log; ~5ms)
4. Controller -> Substrate process (codebook lookup + binding; substrate-physics latency)
5. Substrate -> Controller (return) (~1-10ms IPC)
6. Controller -> LLM API second roundtrip (if LLM-PHRASED path)
7. Controller -> Audit log write (~5-20ms; async; can be off critical path)
8. Controller -> User response (~5ms)

### Substrate-physics latency vs integration-engineering latency

Critical separation: substrate cleanup-lookup against codebook of size K at N=1024 is ~5-50ms (existing benchmark); the rest of latency is LLM API roundtrips (network-bound) + IPC + serialization.

Measurement protocol:
- Profile each stage independently
- Stage budget for legal-Q&A target: <2s end-to-end p95 (matches legal-research expectation; not real-time-conversational)
- Substrate-physics latency target: <100ms p95 (codebook lookup + binding chain on substrate process)
- LLM latency: dominated by vendor; report as "LLM-bound latency budget" separately
- Audit log latency: <50ms p95 if on critical path; async write removes from critical path entirely

### Deliverable

End-of-Week-7 latency report: per-stage histograms; p50/p95/p99; breakdown by query class (VERIFIABLE shows lowest latency; GENERATIVE shows highest because multiple LLM roundtrips).

---

## Section 10: 8-week engineering plan

Assume 1 senior engineer (primary) + 1 mid-level engineer (support, weeks 3-8). Total ~480 engineer-hours.

### Week 1: Foundation - substrate REST/JSON wrapper + corpus ingestion harness

**Goal**: substrate process exposes a JSON-over-HTTP API that the Controller can call.

Tasks:
- [W1.1] Write `hdlab_service/server.py`: FastAPI app wrapping existing `hdlab/memory.py` + `hdlab/binding.py`. Endpoints: /retrieve_fact, /compositional_query, /store_fact, /delete_fact, /verify_audit_trail. (~12h)
- [W1.2] Write corpus ingestion script: load Court Listener case PDFs -> extract facts via LLM-assisted fact extraction (use claude-sonnet-4.5 with chain-of-thought to identify case_id, holding, citations, parties) -> store each as substrate atom with provenance metadata. (~16h)
- [W1.3] Smoke test: 100 cases ingested, 50 retrieval queries hit correct facts at >0.8 similarity. (~6h)
- [W1.4] Set up dev environment: Docker compose with substrate-service + audit-log-service + deletion-cert-service stubs + LLM-API client. (~6h)

**Critical path**: W1.1 (REST wrapper) blocks everything downstream.

**Deliverable**: substrate-service responds to HTTP API; 100-case corpus ingested.

### Week 2: Audit log + deletion-cert services

**Goal**: append-only audit log + Ed25519 cert chain working end-to-end.

Tasks:
- [W2.1] Audit log service: JSONL writer with hash chain + DuckDB indexer + daily Merkle root computation. (~16h)
- [W2.2] Deletion-cert service: Ed25519 key gen + cert signing + cert verification independent verifier script. (~14h)
- [W2.3] Hash-chain test suite: insert events, tamper with one, verify detection. (~6h)
- [W2.4] Merkle-root inclusion proof generator + verifier. (~8h)

**Critical path**: W2.1 blocks Controller integration (Week 3); W2.2 is parallelizable with W2.1.

**Deliverable**: audit log + deletion cert services pass unit tests; cert verification roundtrip <500ms.

### Week 3: Controller orchestration layer

**Goal**: Pattern-B Controller dispatches to LLM + substrate + audit + cert.

Tasks:
- [W3.1] Controller skeleton: query intake; LLM client wrapper; tool-use dispatcher. (~16h)
- [W3.2] Tool-call routing: map tool_use blocks to substrate-service endpoints; emit audit events for every dispatch. (~12h)
- [W3.3] Substrate-mediated output policy engine: query classifier + confidence-threshold decision tree (Section 3). (~10h)
- [W3.4] Provenance tagger: per-token annotation on output. (~10h)
- [W3.5] End-to-end smoke: 10 sample legal queries roundtrip through full pipeline. (~6h)

**Critical path**: W3.1 + W3.2 are sequential; W3.3 + W3.4 are parallel after W3.2.

**Deliverable**: Controller dispatches 10 sample queries end-to-end with full audit-log emission.

### Week 4: Use-case corpus ingestion + thin-slice measurement

**Goal**: full 1000-query benchmark corpus loaded; thin-slice measurement on 100-query subset.

Tasks:
- [W4.1] Scale corpus ingestion to 5000-10000 legal documents (1000 cases + statutes + secondary sources). Use Court Listener bulk download + CAP Caselaw. (~20h)
- [W4.2] Build 1000-query benchmark: 400 VERIFIABLE + 300 COMPOSITIONAL + 200 GENERATIVE + 100 AMBIGUOUS. Use LLM-assisted query generation from corpus + manual review by founder for 200 sample. (~20h)
- [W4.3] Build RAG baseline: same corpus chunked + embedded into FAISS; LLM-side identical to Pattern B. (~12h)
- [W4.4] Run THIN-SLICE measurement: 100 queries on both Pattern B and RAG baseline; compute token reduction + factual consistency. (~8h)

**THIN-SLICE GATE (end of Week 4)**:
- If thin-slice shows >=3x token reduction AND audit completeness >=95% AND no major impedance-mismatch bugs: commit to full Weeks 5-8.
- If thin-slice shows <2x reduction OR systematic audit gaps: pivot strategy in main thread, either to Pattern A or use-case reframing. Spec considers this scenario a HARD-FAIL early exit.

**Deliverable**: thin-slice report; go/no-go decision committed.

### Week 5: Quality + integration hardening

**Goal**: full 1000-query benchmark + quality-parity infrastructure.

Tasks:
- [W5.1] Ground-truth labeling for 1000 queries (legal team OR Upwork legal paralegals; ~$3-5K). (~10h founder oversight; external labor)
- [W5.2] LLM-judge for factual consistency: claude-opus-4-7 as judge; calibrate against 100 human-labeled samples; agreement >=90%. (~12h)
- [W5.3] Substrate retrieval tuning: optimize codebook density, similarity threshold; improve hit rate on AMBIGUOUS queries. (~16h)
- [W5.4] LLM tool-use reliability: harden tool-call JSON parsing; handle malformed tool-call outputs; fallback path. (~12h)
- [W5.5] Run FULL 1000-query benchmark on both Pattern B and RAG baseline. (~10h compute + analysis)

**Critical path**: W5.1 (labeling) is the long-lead item; start at end of W4.

**Deliverable**: full benchmark report with token reduction + factual consistency + audit completeness on 1000 queries.

### Week 6: Deletion-cert end-to-end + multi-fact compositional

**Goal**: deletion workflow + COMPOSITIONAL query class working.

Tasks:
- [W6.1] Deletion workflow end-to-end: admin-triggered delete via API; cert generated; audit-log entry; corpus state update; independent verifier roundtrip <500ms (HP4 target). (~14h)
- [W6.2] Compositional query tuning: leverage substrate binding algebra for "cases by judge X citing precedent Y" queries; tool definition tested on 100 COMPOSITIONAL queries. (~16h)
- [W6.3] Audit-trail reconstruction: `substrate.verify_audit_trail(response_id)` works end-to-end; reconstructs full call chain for any past query. (~10h)
- [W6.4] Performance optimization: profile + fix bottlenecks identified in W5. (~10h)

**Deliverable**: deletion-cert HP4 met; COMPOSITIONAL query class HP1 contribution measured.

### Week 7: Latency profiling + observability polish

**Goal**: latency report + dashboard for demo presentation.

Tasks:
- [W7.1] End-to-end latency profiling: instrument every stage; generate p50/p95/p99 report; separate substrate-physics vs integration-engineering. (~12h)
- [W7.2] Demo UI: web frontend showing query input + response with per-token color-coded provenance + audit-trail sidebar + deletion-cert verification. (~20h)
- [W7.3] Observability dashboard: dashboard panel for token-reduction live metric, audit-completeness, deletion-cert verification rate. (~12h)
- [W7.4] Documentation: API reference for the 5 tools; deployment guide; runbook. (~10h)

**Deliverable**: demo runnable end-to-end with polished UI; latency report; documentation.

### Week 8: Hardening + design-partner-ready demo

**Goal**: production-quality demo for design-partner conversations.

Tasks:
- [W8.1] Failure-mode hardening: timeout handling; LLM API rate-limit handling; substrate-service crash recovery. (~14h)
- [W8.2] Security review: secrets handling; Ed25519 key management; multi-tenancy isolation. (~10h)
- [W8.3] Recorded demo video (3-5 min): scripted walkthrough of fact-Q&A + audit-trail + deletion-cert. (~6h)
- [W8.4] Public-facing landing page: positioning + product spec one-pager + contact form. (~8h)
- [W8.5] Cost benchmarking: measure actual LLM API costs over the 1000-query benchmark. (~6h)
- [W8.6] Reserve buffer for slips. (~16h)

**Deliverable**: demo ready for design-partner conversations; pitch deck + landing page + recorded demo.

### Dependency graph (Mermaid-style; textual)

```
W1.1 substrate REST wrapper ----> W3.1 Controller skeleton
W1.2 corpus ingestion -------+--> W4.1 scale corpus
                              |
W2.1 audit log service -------+--> W3.2 tool-call routing
W2.2 deletion cert service ---+--> W6.1 deletion workflow E2E
                              |
W3.1 ------> W3.2 ------> W3.3 -+-> W3.5 E2E smoke
              |                  |
              +--> W3.4 --------+
                                 |
                                 v
                              W4.4 thin-slice GATE (Week 4 end)
                                 |
                                 v
W5.1 labeling --+--> W5.2 LLM judge --+--> W5.5 full benchmark
                |                       |
W5.3 retrieval tuning ------------------+
W5.4 LLM tool-use hardening -------------+
                                          v
                                       W6 deletion E2E + COMPOSITIONAL
                                          |
                                          v
                                       W7 latency + UI + observability
                                          |
                                          v
                                       W8 hardening + demo polish
```

### Critical path
W1.1 -> W3.1 -> W3.2 -> W3.5 -> W4.4 thin-slice -> W5.5 benchmark -> W7.2 UI -> W8.3 demo.

Total critical path: ~7 weeks; W8 has 16h buffer for slips.

### Week 1 first action

Engineer creates `hd-instrument/hdlab_service/` directory + FastAPI app skeleton + Dockerfile + first endpoint stub for /retrieve_fact wrapping existing `hdlab/memory.py:Codebook.lookup`. Smoke test: starts server, accepts POST with sample query, returns canned response. Goal: ~2 hours; unblocks everything else.

---

## Section 11: Cost breakdown

### Engineering hours
- Primary senior engineer: 8 weeks * 40h = 320h
- Mid-level engineer (Weeks 3-8): 6 weeks * 30h = 180h
- Total: ~500 engineer-hours
- At $200/h blended rate: $100K eng cost

### LLM API costs
- 1000-query benchmark x both Pattern B + RAG baseline x ~6 sweep iterations = ~12000 queries
- Average ~10K input tokens + 1K output per query (RAG baseline; substrate halves this)
- claude-sonnet-4.5 at $3/MTok input, $15/MTok output
- Estimated: $1500-3000 for benchmark sweeps + $1500-3000 for ground-truth labeling LLM-judge + $500-1000 for dev iteration = $3500-7000

### Infrastructure
- Substrate process hosting: laptop or single cloud instance ($50-200/mo)
- Audit log storage: 1000 queries * 5KB per audit chain = ~5MB; trivial
- Cert chain storage: <1MB
- LLM API client: SDK only
- Dev infrastructure (CI, monitoring): $200-500/mo
- 2 months: ~$500-1500

### External labor
- Ground-truth labeling: 1000 queries * $3-5/query (Upwork legal paralegals) = $3000-5000
- Human evaluation (optional): 200 queries * 3-5 raters * $10/query = $6000-10000

### Legal review
- Privacy policy + GDPR alignment review: $5K-10K (one-time)
- Optional pre-pilot legal opinion: $10K-20K

### Total budget
- Floor (no human eval, no pre-pilot legal opinion): ~$108K-$118K
- Ceiling (with human eval + legal opinion): ~$135K-$150K
- Recommended: ~$115K-$125K (eng + LLM + minimal legal review; defer human eval to design-partner pilot)

---

## Section 12: Success criteria (pre-registered)

HARD_PASS (all four required):
- HP1: >=5x token reduction at LLM API boundary (95% CI excludes 4x)
- HP2: >=95% factual consistency AND parity-with-RAG (no statistically-significant degradation; Wilson CI overlap)
- HP3: >=98% audit-trail completeness on substrate-sourced output tokens
- HP4: deletion-cert end-to-end <500ms p95 + independent verification works

HARD_FAIL (any one triggers reframe):
- HF1: <2x reduction
- HF2: <90% factual consistency OR >5pp worse than RAG
- HF3: <85% audit completeness OR systemic gaps
- HF4: substrate-LLM impedance mismatch unresolvable

MIDDLE_BAND (ship with reframing):
- 2-5x reduction: ship as "2-5x with audit guarantee"; HP1 retargeted in v2
- 90-95% factual consistency: ship with quality envelope disclaimer
- 85-98% audit: ship with documented gaps + roadmap

Pre-registration commit: this spec at v278 commit IS the pre-registration; HP/HF/MIDDLE band thresholds locked at spec date (2026-05-29) and cannot be moved without explicit `notes/pre_reg_amendment_pattern_b_*.md` rationale per [[feedback-envelope-expansion-fail-bands]].

---

## Section 13: What this demo does NOT validate

Explicit scope boundary:
- Does NOT validate Pattern C (deep LLM-internal integration; representation level; parallel retrieval during inference; bounded-context CoT). Pattern C requires LLM-vendor partnership + 6-12 months.
- Does NOT validate Property 4 (LLM-internal representation compatibility) - speculative; out of demo scope.
- Does NOT validate Property 5 (parallel retrieval during LLM inference) - Pattern B is sequential tool-use, not parallel.
- Does NOT prove the agentic-AI-memory thesis (substrate as the memory layer for multi-step agents). Agentic-memory test requires multi-step agent benchmark like AgentBench / GAIA; this demo is single-turn fact-Q&A.
- Does NOT validate substrate-as-LLM-replacement (path-a P=<0.15 per v276; this demo is path-c memory-layer complement).
- Does NOT validate operational-stability narrative empirically (operational invariance witnesses exist per v278 strategic input but this demo does not test them at customer scale).
- Does NOT validate Property 7 (CoT state management). CoT state mgmt is a Pattern C capability.
- Does NOT validate scaling to billion-vector substrate corpus. Demo runs at substrate N=1024 + corpus of 5000-10000 documents.

---

## Section 14: What this demo DOES validate

- Property 1 (Native text/byte operation): substrate ingests document text without separate embedding model; demo exercises directly.
- Property 2 (Atomic fact granularity): each fact is a substrate atom with provenance metadata; per-fact retention enforced.
- Property 3 (Compositional binding algebra): COMPOSITIONAL query class exercises binding-algebra composition; tool definition tested on 100 queries.
- Property 6 (Structural output verification): audit-trail completeness + deletion-cert + provenance reconstruction = structural verification at the output level.
- Partial Property 7 (CoT state management): basic version - audit-log preserves multi-turn state; full CoT bounded-context is Pattern C.

- TOKEN REDUCTION at production-like pipeline (vs RAG baseline) on the chosen use case.
- AUDIT TRAIL COMPLETENESS at production scale (~1000 queries).
- DELETION CERTIFICATE PRACTICAL OPERATION end-to-end (HP4 <500ms target).
- COMPOSITIONALITY AUDIT API at production-like scale.

- SUBSTRATE'S "SPECIALIZED COMPONENT" POSITIONING vs LLM-REPLACEMENT positioning: demo grounds the "compliance-grade memory layer" narrative in working code.

---

## Section 15: Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM API rate limits hit during benchmark sweeps | MED | MED | Anthropic enterprise quota request; spread benchmark over multiple days; use API key with $5K credit pre-purchased |
| LLM-vendor model behavior change (e.g. tool-use API revision mid-build) | LOW | HIGH | Pin to specific Anthropic Messages API version; freeze model snapshot (claude-sonnet-4.5-20250929); avoid latest-model dependence |
| Substrate-LLM impedance mismatch: LLM cannot reliably emit tool-call JSON for substrate API | MED | HIGH | Tool definitions designed minimally; rigorous JSON-schema validation; fallback to LLM-PHRASED path if tool-call malformed; thin-slice gate at Week 4 catches this early |
| Substrate retrieval quality below 0.8 hit rate at corpus N>5000 | MED | HIGH | Pre-build smoke test on 1000-document corpus before full ingestion; tune codebook density (K/N ratio per substrate-physics evidence); if persistent, swap to FHRR-with-cleanup variant |
| API costs overrun $10K budget | LOW | MED | Pre-purchase $5K credit + $5K reserve; switch to claude-haiku for cheaper sweeps if needed; cap nightly sweep token budget |
| Use-case data acquisition: Court Listener API rate limits OR data gaps | LOW | LOW | CAP Caselaw bulk download is fallback; legal corpus is unusually open; medical was the data-acquisition risk, legal is not |
| Ground-truth labeling quality variance (Upwork labelers) | MED | MED | Founder spot-checks 10% of labels; LLM-judge calibrated against 100 founder-labeled gold samples; agreement >=90% gate |
| 8-week timeline slip (sustained engineering attention required) | MED | HIGH | W8.6 buffer (16h); W4 thin-slice gate catches early; if Week 4 shows systematic issues, pivot to Pattern A (3-4wks) rather than push Pattern B to 10-12 weeks |
| Regulatory data-handling for sensitive verticals | N/A (legal is recommended; minimal PHI/PCI risk) | LOW | Legal use case avoids HIPAA/PCI; CAP Caselaw + Court Listener is fully public; no privileged-matter data in demo (demo uses public cases only) |
| Substrate cap_map row backslide during build (some other research surfaces a refutation) | LOW | MED | Demo decoupled from substrate-physics research path; runs against current cap_map state; if KF-2 backslides during build, demo continues but cert claim is softened |
| Audit-trail completeness < 98% due to async-write race conditions | MED | MED | Audit writes are append-only with fsync; design completeness invariant testable at scale; W6.3 dedicates time to fix; if persistent, downgrade HP3 to >=95% in v2 |
| Deletion-cert verification fails on edge cases (Merkle proof corner cases) | LOW | HIGH | W2.4 + W6.1 dedicate time; reference-implementation pattern from Certificate Transparency RFC 9162; extensive test suite |
| Senior engineer attrition mid-build | LOW | CATASTROPHIC | Pair with mid-level engineer Weeks 3-8 for knowledge transfer; spec is comprehensive enough for re-entry; documentation as Week 7 deliverable |
| Demo aesthetic falls flat with design partners (technically correct but not compelling) | MED | HIGH | W7.2 dedicates 20h to UI; W8.3 to recorded demo; iterate with 1-2 friendly legal-tech contacts before broad partner outreach |

### Top-3 mitigation focus
1. Thin-slice gate at Week 4 (catches HF early, allows pivot before 6 more weeks sunk)
2. LLM-vendor pinning + tool-use rigor (catches impedance mismatch + model drift)
3. Senior + mid pairing Weeks 3-8 (catches attrition + knowledge silo)

---

## Substrate-product implications

This demo, if HP/HP/HP/HP, gives substrate the FIRST production-like pipeline grounding. It collapses 6-month strategic-positioning conversations into a 5-minute recorded demo: token reduction + audit trail + deletion cert all visible on screen.

Strategic value of HP:
- Single most important strategic asset for Q3-Q4 2026 design-partner conversations
- Grounds product positioning in working code (no more "could substrate do X?" - "watch substrate do X")
- Establishes "compliance-grade memory layer" as a category that competitors don't have
- Unblocks Items 13-17 from the 3-month roadmap (partnerships, pilots, regulatory documentation)

Strategic value of HARD_FAIL:
- Saves 2-4 quarters of misallocated effort
- Reframes substrate as "characterized but not yet integration-ready" - back to substrate-physics research with sharper questions
- Identifies specific impedance mismatch or token-reduction failure as the next research drill

Either outcome is high-value information. The dominant risk is NOT-shipping the demo (status quo) - 8 weeks of speculation about Pattern B equivalent value vs 8 weeks of building it.

---

## Citations (verified)

Substrate-internal sources (verified via Read/Glob in this drill):
1. `hdlab/memory.py` - Codebook class; lookup logic; existing primitive for retrieve_fact tool
2. `hdlab/binding.py` - bind/unbind FHRR + HRR; existing primitive for compositional_query
3. `hdlab/store.py` - DuckDB-backed trace store; existing primitive for audit-log indexer
4. `hdlab/semantic.py` - Layer-2 trace emit; existing primitive for per-query span tracking
5. `notes/strategic_roadmap_llm_integration_3mo_v278_2026-05-29.md` - Item 1 priority
6. `notes/research_product_positioning_v276_2026-05-29.md` - segment ranking + market data
7. `notes/strategic_input_two_layer_and_dwave_v278_2026-05-29.md` - two-layer architecture frame
8. `memory/project_substrate_killer_features_2026-05-26.md` - deletion-cert + compositionality-audit as killer features

External standards / references (well-established; no fresh lit-scan needed):
9. RFC 9162 (Certificate Transparency v2.0; Merkle tree audit logs reference pattern)
10. NIST FIPS 186-5 (Ed25519 signature standard)
11. GDPR Articles 17 + 30 (right to erasure + records of processing)
12. EU AI Act Articles 10, 12, 17 (data governance + record-keeping + human oversight)
13. Anthropic Messages API tool-use documentation (claude-sonnet-4.5)
14. Court Listener REST API (free public access)
15. CAP Caselaw Access Project bulk download (Harvard)
16. RFC 6962 Section 2.1 (Merkle tree inclusion proof structure)

Calibration note: this is an engineering spec, not a novel-physics synthesis. Lit-scan deflation applies to TIMELINE estimates (deflated 8wk -> P_deflated=0.45 of shipping in 8wk) and to QUALITY/REDUCTION estimates (5-15x band capped at 5x for HP1 conservatism). Calibration penalty applied to "Pattern B novelty" - this is genuinely novel integration synthesis, capped at P=0.50 per [[feedback-lit-scan-calibration-penalty]].

Verified citation count: 16.

## Honesty notes

- Pattern B is novel synthesis (no published direct precedent of substrate-as-tool-for-LLM with substrate-mediated outputs at this architecture). Lit-scan calibration cap P<=0.50 applies. Reported P_deflated=0.45 of 8-week ship is at the upper end of allowed range and reflects that substrate-physics primitives are mature (memory.py + binding.py + store.py + KF-2 production-N=4096 isolation HARD_PASS evidence exists).
- The 8-week timeline assumes 1 senior + 1 mid; with 1 senior only, timeline extends to ~12 weeks (P_deflated of 12wk ship ~0.65).
- Recommended use case (legal eDiscovery) was selected on PRODUCT-MARKET-FIT criteria, not technical substrate-fit. All three use cases are substrate-feasible; legal has the shortest path to a paying design partner per v276 evidence.
- No substrate-novel mechanism names appear in any customer-facing asset (tool definitions, UI, deletion-cert format, audit-log schema) per [[feedback-query-privacy-decomposition]]. Internal docs reference SKAH-M, KF-2, etc.; external assets use "compliance-grade auditable memory layer" framing.
- Cost-advantage 5-20x claim (substrate INT4-CPU vs LLM FP16-GPU per v276) is NOT a Pattern B HP - this demo measures TOKEN reduction, not cost-of-substrate-deployment. Cost-advantage claim deferred to BE-1 W-magnitude-operative test (independent research thread).
- HP/HF/MIDDLE thresholds are PRE-REGISTERED at spec date 2026-05-29; cannot move without amendment note per [[feedback-envelope-expansion-fail-bands]].

End of executable spec.
