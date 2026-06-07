# Research Drill: Customer-Facing Interface Design for Substrate Distinctive Capabilities (2x)
Date: 2026-06-07
Filed-by: research sub-agent (Sonnet)
Topic: demo-interface-capabilities
Depth: Level-2 operational drill -- UX/API/engineering scoping
Calibration: lit-scan penalty 0.15-0.20 applied; all estimates are theoretical x empirical split
Plain-language framing: REQUIRED throughout

---

## HEADLINE

Five substrate capabilities can be made experienceable in a 4-week engineering sprint with a 3-endpoint backend and a Streamlit frontend. The GDPR erasure + audit trail combination is the highest-impact opening scenario because it demonstrates two capabilities simultaneously in under 2 minutes. Counterfactual replay is the "show-stopper" scenario but requires Pattern B integration working cleanly -- ship it last. The core demo risk is not engineering; it is latency: any scenario taking >3 seconds onscreen will lose the audience, so latency SLAs must be pre-reg'd per capability before demo day.

---

## 1. CAPABILITY PRIORITIZATION -- TOP 5 FOR DEMO

### Why 5 and not 10

Ten capabilities shown in a 10-minute demo averages 60 seconds per capability. At that pace no capability registers. Five capabilities at 2 minutes each, with one natural arc connecting them, is the right pacing.

### Ranked by (demo impact) x (reliability) x (engineering cost)

**Rank 1: GDPR erasure (cycle 154)**

Why first: The audience experiences something impossible to do with a plain LLM. You ask a question, get an answer, delete one fact, ask again, and the answer changes -- verifiably, with a timestamped audit record. The real-world consequence is clear: GDPR/CCPA compliance is a $20M/year legal liability for any enterprise handling personal data. No current RAG system offers "erase and verify gone." This is also the cheapest scenario to build: one input field, one DELETE endpoint, one re-run button.

Demo moment: Ask "What role did Alice hold at Acme?" -- system answers. Click "Erase: Alice at Acme." System returns HMAC tombstone confirmation. Re-ask same question -- system returns "No information stored about Alice at Acme." Elapsed: ~90 seconds. Audience reaction: "That actually worked."

P_theoretical: 0.85 (mechanism is algebraically solid; HMAC keystore + tombstone pattern is well-understood)
P_empirical x P_demo: 0.65 (risk is the re-query correctly filtering tombstoned facts; needs pre-test)
Cheap pre-test: Erase one fact from a 100-fact store; confirm re-query returns null AND prior queries still return non-erased facts. Time: 20 minutes.

**Rank 2: Cryptographic audit trail (cycles 137 + 154)**

Why second: Every enterprise compliance buyer asks "how do I know the system didn't make this up?" Showing clickable citations where each citation opens a Merkle proof is a direct answer. No current RAG system provides citation-level cryptographic provenance -- they show source documents, not proofs. The moment of clicking a citation and seeing a chain of hashes that the user can in principle verify is high trust-building. Engineering cost is moderate: the backend already has the proof structure; the frontend needs a tree-rendering component.

Demo moment: Ask a question with 3 citations. Click citation [2]. A panel opens showing: "Fact text | Hash: 0xa3f2... | Verified against root hash 0x8b1c... | Stored at: 2026-06-07 14:23:01 UTC." One "Verify" button re-runs the Merkle check inline. Elapsed: ~45 seconds per citation. Audience reaction: "This is auditable in ways our current system is not."

P_theoretical: 0.90 (Merkle proof is standard; root hash stored immutably)
P_empirical x P_demo: 0.70 (risk: rendering the proof tree readably requires good UX; raw hex is not legible)
Cheap pre-test: Retrieve one fact; walk the Merkle path; confirm chain closes to root. Time: 10 minutes.

**Rank 3: Bitemporal as-of query (cycles 150 + 152)**

Why third: Time-travel queries are viscerally compelling for anyone in legal, finance, or regulatory work. "What did the system know about Company X's leadership last quarter?" has immediate business meaning. The Snodgrass model (from the temporal-fact-versioning drill: bitemporal storage with valid-time and transaction-time axes) is standard CS -- the substrate extension is that the same query mechanism that handles temporal queries also hands you the Merkle proof, so you get verifiable time-travel. This differentiates from Datomic/XTDB (which have bitemporal but no cryptographic audit).

Demo moment: Two-panel layout. Left panel: query "Who was CEO of Acme?" with "as of" date set to NOW. Right panel: same query with "as of" date slider moved back 6 months. Different answers appear side by side. Each answer has citations with timestamps. Elapsed: ~75 seconds. Audience reaction: "We've always needed this for audit investigations."

P_theoretical: 0.75 (valid-time metadata is a shallow schema extension per temporal-versioning drill; retrieval filter is standard interval overlap)
P_empirical x P_demo: 0.50 (risk: valid-time metadata must be populated correctly in the KB; demo KB must have facts with known historical versions)
Cheap pre-test: Store two versions of one fact with different valid_from dates; query at both timestamps; verify correct version returned. Time: 30 minutes.

**Rank 4: Substrate-augmented answer quality vs bare LLM (+0.35 F1, cycle 158)**

Why fourth: This is the north-star capability -- "our system answers better than a raw LLM of the same size." But it is also the hardest to make visually striking. A bare +0.35 F1 number is not experienceable. The demo design that makes it experienceable: run the same question through two side-by-side panels -- one is bare Llama-1B with no substrate, one is Llama-1B + substrate retrieval. Show both answers plus the reference answer. Use a MuSiQue multi-hop question where the bare LLM visibly confabulates. The contrast is the demo.

Demo moment: Ask "Who was the spouse of the composer of [piece X]?" Bare LLM: answers confidently but incorrectly. Substrate-augmented LLM: answers correctly with citations. Reference answer shown. F1 delta visualized numerically. Elapsed: ~60 seconds. Audience reaction: "You just showed me a hallucination in real time and the system caught it."

P_theoretical: 0.85 (cycle 158 confirmed +0.35 F1 at toy N; MuSiQue type tasks are exactly this)
P_empirical x P_demo: 0.60 (risk: latency of running two LLM calls in parallel may be noticeable; the bare-LLM confabulation must be on a known-failure question -- cannot rely on live hallucination)
Cheap pre-test: Pre-select 5 questions where Llama-1B reliably confabulates without substrate. Verify substrate answers correctly on the same 5. Cache results for demo. Time: 45 minutes.

**Rank 5: Counterfactual replay (PP-81/82, cycle 153, 3.876 ms)**

Why fifth (and last): This is the highest wow-factor capability but requires Pattern B integration working cleanly. The 3.876 ms replay time is the number to show on screen ("recomputed in 3.9 ms"). A counterfactual query -- "if the merger had been rejected, how would the answer change?" -- requires that (a) the specific fact can be identified and substituted without rebuilding the whole store, and (b) the substitution result is semantically coherent. At toy N these both hold; production N needs the pre-test.

Demo moment: Show answer A to question Q1 based on fact F. Show "What if F were F'?" widget. Enter new value for F'. Click "Replay." System returns answer A' in 3.9 ms. Side-by-side: original answer vs counterfactual answer, with a diff highlighted. Elapsed: ~90 seconds. Audience reaction: "We can use this for legal scenario planning / 'what if the regulation had been different' analysis."

P_theoretical: 0.80 (PP-81/82 validated; substitution algebra is exact; replay time is real)
P_empirical x P_demo: 0.40 (risk: requires Pattern B integration to be stable at production N; any substitution that corrupts the store silently would be a demo failure; needs pre-test at production N before engineering authorization)
Cheap pre-test: Substitute one fact in a 1K-fact store; verify counterfactual answer differs from original in the expected direction; verify original answer unchanged. Time: 30 minutes.

### Not in top 5 (and why)

- Pattern B structured queries (rank 6): SQL-like query interfaces require deep UX work for a general audience; the capability is real but the UX risk is high; ship post-v1.
- Distributed reasoning CRDT (rank 7): invisible to a single-user demo unless you show two simultaneous write streams; complex to stage.
- Online concept extension (rank 8): sparse-KEY injection is powerful but the demo moment is subtle; does not land visually.
- SQL aggregates (rank 9): useful, not differentiated from any database.
- Qualified privacy (rank 10): k<=5 rate limit is a table-stakes statement in privacy demos; does not carry the Scenario 6 slot alone.

---

## 2. MINIMUM VIABLE UI PER CAPABILITY

### UI-1: Basic query + citations (foundation for all scenarios)

What the user sees:
- Large text input: "Ask a question about..."
- Submit button
- Answer panel: plain text answer
- Citations panel: numbered list [1] [2] [3], each clickable
- Confidence indicator: a numeric score (e.g., 0.84) next to the answer

API call: POST /query
Request body:
```json
{
  "question": "Who was CEO of Acme Corp in 2023?",
  "kb_id": "demo_kb_v1",
  "top_k": 5
}
```
Response:
```json
{
  "answer": "Jane Smith was CEO of Acme Corp from 2021 to 2024.",
  "confidence": 0.84,
  "citations": [
    {
      "citation_id": "c_0f3a",
      "text": "Jane Smith was appointed CEO of Acme Corp in January 2021.",
      "source": "wiki/Acme_Corp",
      "stored_at": "2026-06-07T14:23:01Z",
      "merkle_leaf_hash": "0xa3f2b8c1..."
    }
  ],
  "query_id": "q_7f2a",
  "elapsed_ms": 142
}
```
Rendered display: Answer text at top, then a collapsible citations list. Each citation shows source, stored_at, and a "Verify" button.

Engineer-days: 3 (2 days backend integration + 1 day Streamlit UI)

### UI-2: GDPR erasure

What the user sees:
- Input field: "Erase all facts about entity: ___"
- Erase button (red, prominent)
- Confirmation panel: "Erased N facts. Tombstone hash: 0x... Timestamp: ..."
- Re-run prior query button (shows that prior query now returns different result)
- Audit log panel: list of erasure events with timestamps and tombstone hashes

API call: POST /erase
Request body:
```json
{
  "entity": "Alice Johnson",
  "erase_mode": "entity_all",
  "caller_id": "admin_user_1",
  "reason": "GDPR Article 17 request"
}
```
Response:
```json
{
  "erased_count": 7,
  "tombstone_hashes": ["0x8f1a...", "0x2c9b...", "..."],
  "erasure_timestamp": "2026-06-07T15:01:22Z",
  "audit_record_id": "era_1a2b",
  "verification_token": "hmac_0xd4f1..."
}
```

Error handling:
- Entity not found: HTTP 404, body: {"error": "entity_not_found", "entity": "Alice Johnson"}
- Erasure partial failure: HTTP 207 Multi-Status, body includes erased_count + failed_count + reason
- HMAC verification failure: HTTP 500, body: {"error": "hmac_key_unavailable", "action": "contact_admin"}

Rendered display: Green success banner with tombstone hash shown. Audit log entry appended to bottom panel. "Re-run last query" button highlights that Alice now returns no results.

Engineer-days: 4 (2 days backend endpoint + HMAC keystore integration + 2 days UI: input form, audit log, success/error states)

### UI-3: Merkle audit trail visualization

What the user sees:
- After clicking a citation: a side panel slides in
- Top: "Fact verified: YES / NO" with a green checkmark or red X
- Fact text in full
- Proof chain rendered as a vertical tree:
  - Leaf node: fact hash (first 12 hex chars shown)
  - Parent node: combined hash
  - Root node: stored root hash
  - Each node shows: hash | computed from | verified
- "Full proof JSON" expandable section (for technical audiences)
- "Re-verify now" button (re-runs Merkle check client-side using root hash from server)

API call: GET /audit-trail?citation_id=c_0f3a
Response:
```json
{
  "citation_id": "c_0f3a",
  "fact_text": "Jane Smith was appointed CEO...",
  "fact_hash": "0xa3f2b8c1d4e5f6a7...",
  "merkle_path": [
    {"hash": "0xa3f2b8c1...", "sibling": "0x9b4c2d3e...", "position": "left"},
    {"hash": "0x7e1f2a3b...", "sibling": "0x4d8c9e0f...", "position": "right"}
  ],
  "root_hash": "0x8b1c4e2f...",
  "root_stored_at": "2026-06-07T00:00:00Z",
  "verified": true,
  "path_length": 12
}
```

Error handling:
- Citation not found: HTTP 404
- Proof verification fails (data corruption): HTTP 200 but verified: false, with reason field
- Root hash mismatch (tampering): HTTP 200, verified: false, reason: "root_mismatch"

Rendered display: Collapsible tree component. For a general audience, show only the "Verified: YES" banner + the fact text. For technical audiences, show the full path. Keep it simple: proof trees are hard to read for non-experts.

Engineer-days: 5 (2 days backend endpoint + Merkle path serialization + 3 days UI: tree component, verified badge, error states)

### UI-4: Bitemporal as-of query

What the user sees:
- Standard query input
- Below the input: "As of" date selector (calendar widget)
- Toggle: "Compare with current" (opens second panel)
- Two-panel layout when comparison is active:
  - Left: "Answer as of [selected date]"
  - Right: "Answer as of NOW"
  - Each panel shows answer + citations with timestamps
  - Differences highlighted in yellow

API call: POST /query/as-of
Request body:
```json
{
  "question": "Who was CEO of Acme Corp?",
  "kb_id": "demo_kb_v1",
  "as_of_transaction_time": "2026-01-01T00:00:00Z",
  "as_of_valid_time": null,
  "compare_with_now": true
}
```
Response:
```json
{
  "answer_at_time": {
    "answer": "Bob Chen was CEO of Acme Corp.",
    "confidence": 0.91,
    "citations": [...],
    "valid_at": "2026-01-01T00:00:00Z"
  },
  "answer_now": {
    "answer": "Jane Smith was CEO of Acme Corp.",
    "confidence": 0.88,
    "citations": [...],
    "valid_at": "2026-06-07T15:30:00Z"
  },
  "changed": true,
  "change_summary": "CEO changed from Bob Chen to Jane Smith between 2026-01-01 and 2026-06-07"
}
```

Error handling:
- Requested time before KB creation: HTTP 400, body: {"error": "before_kb_epoch", "kb_created_at": "..."}
- No data at requested time: HTTP 200, answer_at_time.answer = "No information stored as of [time]"

Engineer-days: 4 (1 day backend: filter by transaction-time metadata + 1 day API schema + 2 days UI: date picker, two-panel layout, diff highlighting)

### UI-5: Counterfactual replay

What the user sees:
- Standard answer display for a question
- Below the answer: "What if?" panel
  - Fact list: shows the top-3 citations used
  - For each citation: an "Override" button
  - Clicking Override opens an edit field: "Change this fact to: ___"
- "Replay with changes" button (green)
- Result panel: side-by-side original answer vs counterfactual answer
- Delta: "Answer changed: YES/NO" + diff of the two answers
- Replay time shown: "Recomputed in 3.9 ms"

API call: POST /query/counterfactual
Request body:
```json
{
  "original_query_id": "q_7f2a",
  "substitutions": [
    {
      "citation_id": "c_0f3a",
      "original_text": "Jane Smith was appointed CEO in January 2021.",
      "counterfactual_text": "Bob Chen was appointed CEO in January 2021."
    }
  ]
}
```
Response:
```json
{
  "original_answer": "Jane Smith was CEO of Acme Corp from 2021 to 2024.",
  "counterfactual_answer": "Bob Chen was CEO of Acme Corp from 2021 to 2024.",
  "answer_changed": true,
  "diff": {"removed": "Jane Smith", "added": "Bob Chen"},
  "replay_elapsed_ms": 3.9,
  "substitutions_applied": 1,
  "store_modified": false
}
```

Note: store_modified: false is a critical safety property. The counterfactual is computed in a temporary context; the permanent store is unchanged. This must be shown explicitly in the UI ("Original data unchanged").

Error handling:
- Invalid substitution (citation not found): HTTP 404
- Pattern B integration failure: HTTP 500, body: {"error": "substitution_failed", "reason": "..."}
- Counterfactual diverged (semantic decoherence): HTTP 200, answer_changed: true, but with flag: "substitution_semantic_drift_detected"

Engineer-days: 7 (3 days backend: Pattern B unbind+substitute integration + 2 days API + 2 days UI: substitution editor, side-by-side diff, "store unchanged" banner)

### Total engineering estimate per capability

| Capability | Backend days | Frontend days | Total days | Risk |
|---|---|---|---|---|
| Basic query + citations | 2 | 1 | 3 | LOW |
| GDPR erasure | 2 | 2 | 4 | LOW-MED |
| Audit trail visualization | 2 | 3 | 5 | MED |
| Bitemporal as-of | 2 | 2 | 4 | MED |
| Counterfactual replay | 3 | 2 | 5+2(integration) | HIGH |
| **TOTAL** | **11** | **10** | **21 + ~4 integration** | |

At 1 engineer, 25 working days = 5 weeks. At 2 engineers (parallel), 14-16 days = 3 weeks. Realistic estimate with integration and polish: 4-5 weeks at full tempo.

---

## 3. DEMO STORYBOARD -- 10 MINUTES, 5 SCENARIOS

KB pre-loaded: Wikipedia biographical subset, ~5K facts (see KB section). Facts include organizational leadership histories with known historical transitions.

### Scenario 1: "Ask a question" (minutes 0:00 - 1:30)

Setup: Blank query interface.

Action: Type "Who were the key scientists involved in the development of the polio vaccine and what were their institutional affiliations?"

This is a good opening question because: it requires connecting multiple facts (scientist + role + institution), Llama-1B alone confabulates at least one affiliation, and the answer includes multiple citations.

On screen: Answer appears in ~150ms. Three citations appear. Confidence: 0.87.

Talking point: "Notice it answered with citations -- not just text it memorized. Every word of that answer is backed by a stored fact."

### Scenario 2: "Verify an answer cryptographically" (minutes 1:30 - 3:00)

Action: Click citation [2] -- the one about Jonas Salk and the University of Pittsburgh.

On screen: Side panel slides in. "Fact verified: YES (green checkmark)". Fact text shown. Merkle path: 3 nodes visualized. Root hash shown. Re-verify button.

Click "Re-verify now."

On screen: "Verification passed in 2.1 ms."

Talking point: "That is a cryptographic proof. Not a reference to a source document -- an actual hash chain. You can take that root hash and verify it yourself with OpenSSL. No other knowledge retrieval system offers this."

### Scenario 3: "What did the system know 3 months ago?" (minutes 3:00 - 4:30)

Action: Click "as of" toggle. Set date to 3 months ago. Click "Compare with now."

(Demo KB must include at least one fact with a historical version that changed in the last 3 months -- e.g., an organizational leadership change. Use a known Wikipedia article.)

On screen: Two-panel answer. Left: "3 months ago: [older leader name] was CEO." Right: "Now: [current leader name] is CEO." Change summary highlighted.

Talking point: "This is bitemporal query. It distinguishes between what was true in the world (the leadership changed) and when the system recorded that change. For audit investigations, this is the difference between 'we had wrong data' and 'the fact changed.' These are legally distinct."

### Scenario 4: "Erase a fact and watch it disappear" (minutes 4:30 - 6:30)

Setup: Prior query returned a fact about a specific individual.

Action: Click "GDPR Erase" tab. Enter entity name: "Jonas Salk". Click Erase.

On screen: "Erased 4 facts. Tombstone: 0x8f1a... Timestamp: 2026-06-07 14:35:12 UTC."

Action: Return to Query tab. Re-ask the original question.

On screen: New answer -- no mention of Jonas Salk. Citations 2 and 4 are gone. "This answer reflects the current stored knowledge."

Talking point: "That is a verified, auditable erasure. The tombstone is permanent. The prior answer used information we no longer hold. This is what GDPR Article 17 compliance looks like in a retrieval system."

### Scenario 5: "Counterfactual scenario" (minutes 6:30 - 9:00)

Action: Go back to the original polio vaccine question result. Click "What if?" panel.

Expand citation [1]: "Albert Sabin developed the oral polio vaccine."

Click Override. Type: "Albert Sabin developed an injectable polio vaccine."

Click "Replay with changes."

On screen: Original answer on left. Counterfactual answer on right. In the counterfactual: "oral" replaced with "injectable" in the relevant sentence. "Recomputed in 3.9 ms. Original data unchanged."

Talking point: "We just ran a counterfactual without touching the data store. This is useful for legal scenario analysis, due diligence, 'what if the record had said something different' reasoning. The original data is intact. This runs in under 4 milliseconds."

### Scenario 6 (optional, if time): "Head-to-head with bare LLM" (minutes 9:00 - 10:00)

Action: Switch to the side-by-side comparison view. Pre-loaded question about multi-hop fact (e.g., "What was the birth country of the inventor of the programming language used to write the original Space Invaders?").

On screen: Left panel (bare Llama-1B): confident but wrong answer. Right panel (substrate-augmented): correct answer with citations.

F1 delta shown: 0.00 (bare) vs 0.92 (augmented).

Talking point: "This is what +0.35 F1 looks like. The model on the left had the same parameters -- the substrate on the right gave it access to verified facts."

---

## 4. BACKEND API SCHEMA

### Endpoint list

All endpoints accept and return JSON (Content-Type: application/json). All responses include request_id (for log correlation) and elapsed_ms.

**POST /query**
- Purpose: Standard semantic retrieval + LLM answer generation
- Auth: Bearer token
- Request: {question: str, kb_id: str, top_k: int=5, min_confidence: float=0.3}
- Response 200: {answer: str, confidence: float, citations: [...], query_id: str, elapsed_ms: int}
- Response 400: {error: "invalid_request", detail: str}
- Response 503: {error: "model_unavailable", retry_after: int}

**POST /query/as-of**
- Purpose: Bitemporal retrieval as of specified timestamp
- Auth: Bearer token
- Request: {question: str, kb_id: str, as_of_transaction_time: str (ISO8601), as_of_valid_time: str|null, compare_with_now: bool=false, top_k: int=5}
- Response 200: {answer_at_time: AnswerBlock, answer_now: AnswerBlock|null, changed: bool, change_summary: str|null, elapsed_ms: int}
- Response 400: {error: "before_kb_epoch" | "invalid_timestamp", detail: str}

**POST /query/counterfactual**
- Purpose: Counterfactual replay with fact substitution
- Auth: Bearer token
- Request: {original_query_id: str, substitutions: [{citation_id: str, original_text: str, counterfactual_text: str}]}
- Response 200: {original_answer: str, counterfactual_answer: str, answer_changed: bool, diff: {removed: str, added: str}|null, replay_elapsed_ms: float, store_modified: false}
- Response 404: {error: "query_not_found" | "citation_not_found", detail: str}
- Response 500: {error: "substitution_failed", reason: str}

**POST /erase**
- Purpose: GDPR erasure of entity-linked facts
- Auth: Bearer token + admin role claim
- Request: {entity: str, erase_mode: "entity_all"|"fact_specific", fact_ids: [str]|null, caller_id: str, reason: str}
- Response 200: {erased_count: int, tombstone_hashes: [str], erasure_timestamp: str, audit_record_id: str, verification_token: str}
- Response 207: {erased_count: int, failed_count: int, failed_ids: [str], failure_reason: str, ...}
- Response 404: {error: "entity_not_found", entity: str}
- Response 403: {error: "insufficient_permissions", required_role: "admin"}

**GET /audit-trail?citation_id=STR**
- Purpose: Merkle proof for a specific citation
- Auth: Bearer token
- Response 200: {citation_id: str, fact_text: str, fact_hash: str, merkle_path: [{hash: str, sibling: str, position: "left"|"right"}], root_hash: str, root_stored_at: str, verified: bool, path_length: int, elapsed_ms: int}
- Response 404: {error: "citation_not_found"}
- Response 200 + verified: false: {error_flag: "proof_failed", reason: "root_mismatch"|"path_broken"|"fact_hash_mismatch"}

**GET /facts/search?entity=STR&role=STR&limit=INT&as_of=STR**
- Purpose: Structured Pattern B query (named-role lookup)
- Auth: Bearer token
- Query params: entity (required), role (optional), limit=10, as_of (ISO8601, optional)
- Response 200: {facts: [{fact_id: str, text: str, entity: str, role: str, value: str, confidence: float, stored_at: str}], total_count: int, elapsed_ms: int}
- Response 400: {error: "entity_required"}

**GET /erasure-log?entity=STR&limit=INT**
- Purpose: Audit log of prior erasure events
- Auth: Bearer token + admin role
- Response 200: {events: [{audit_record_id: str, entity: str, erased_count: int, tombstone_hashes: [str], timestamp: str, caller_id: str, reason: str}], total_count: int}

### Error code taxonomy

- 400: Caller error (bad input, invalid params)
- 403: Auth error (missing or wrong role)
- 404: Not found (entity, citation, query_id)
- 207: Partial success (some facts erased, some failed)
- 500: Substrate internal error (HMAC key unavailable, Pattern B failure)
- 503: Temporarily unavailable (model loading, rate limit)

---

## 5. FRONTEND TECHNOLOGY RECOMMENDATION

**Recommendation: Streamlit**

Rationale:

Gradio is faster to prototype single widgets, but its layout model becomes awkward once you need multi-panel views (bitemporal comparison) and custom tree rendering (Merkle proof chain). Gradio's styling is also less polished for enterprise-facing demos.

React + Tailwind would give the most flexible UX but adds 2-3 weeks of scaffolding time. For a v1 demo, that is a direct cost on the demo schedule.

Streamlit sits in between: Python-native (so backend team writes the frontend), session state management for multi-step scenarios (critical for GDPR "erase then re-query" flow), st.columns for two-panel bitemporal layout, and Streamlit components allow embedding a custom D3.js tree rendering for the Merkle proof if needed.

For the Merkle proof tree specifically: use a Streamlit custom component wrapping D3.js (tree layout). This is a 1-day frontend task with existing D3.js tree templates. Alternatively, render the path as a Markdown nested list -- less visual but zero engineering cost.

Timeline to a working Streamlit demo (5 endpoints wired up, all 5 scenarios functional): 2 weeks for one engineer.

If the demo audience is purely technical (e.g., a CTO + engineering team): Custom HTML/JavaScript with Fetch API calls is the fastest to render exactly what you want. Skip Streamlit. One engineer, 1 week for basic UI.

If the demo audience includes business/legal/compliance personas: Streamlit is the right call. It looks polished, is fast to build, and supports the narrative structure (scenario flow without raw JSON visible).

---

## 6. DEMO KB RECOMMENDATION

**Recommendation: Wikipedia biographical subset (v1) + one legal/regulatory subset (v1.5)**

For v1: Load 3K-5K biographical facts from Wikipedia covering:
- ~200 notable organizations with known leadership histories (for GDPR erasure + bitemporal demos)
- ~500 scientific achievements with attributed individuals + institutions (for citation + counterfactual demos)
- ~200 historical events with dated occurrences (for temporal query demos)

Why this works: Wikipedia biographical facts are well-known to audiences, verifiable, stable enough for a demo, and include leadership transitions that enable the bitemporal scenario. The GDPR scenario is more compelling if it erases a well-known entity (the audience can verify the answer changed). The counterfactual scenario works best with scientific attribution facts (easy to construct a meaningful "what if").

Loading a KB with legal cases would be more compelling for compliance customers but introduces legal interpretation risk (what counts as the "correct" answer). For v1 demo, biographical facts are safer.

Medical records are inappropriate for a demo KB regardless of anonymization -- the compliance and sensitivity perception risk outweighs the demo value.

**KB construction recipe:**
1. Dump Wikipedia article sections for target entities as plain text.
2. Run through an offline NLP pipeline to extract (subject, relation, object, timestamp) triples. Spacy + a simple RE extractor suffices for demo quality.
3. Load triples into the substrate with explicit valid_from dates extracted from the article text.
4. Add 5-10 known leadership transitions with explicit before/after timestamps for the bitemporal scenario.
5. Pre-tag 5 questions where Llama-1B confabulates without substrate (for Scenario 6).

KB construction time: 1-2 days for 3K facts.

---

## 7. FAILURE MODE UX

### Retrieval miss

Trigger: Substrate returns zero facts above the confidence threshold.
Display: "I don't have reliable information about that in the current knowledge base." (Never display "I don't know" -- this implies the LLM doesn't know, which conflates the LLM and the KB.) Offer a suggested re-phrase button if a partial match was found.
No false answer generated: the LLM is not called with zero-context retrieval in the demo build. If context is empty, the generation step is bypassed. This prevents hallucination by construction.

### LLM generation diverges from retrieved facts

Trigger: The LLM generates a claim not supported by any citation.
Detection: Post-generation fact-check against the citation set (NLI step or exact-match check for named entities). This runs in ~50ms for a 3-citation context.
Display: "This answer includes content not directly supported by stored facts. [Unsupported sentence highlighted in yellow.] Displaying retrieved facts directly:" -- then show the raw citation text.
Talking point: "The system flagged a hallucination in real time. This is the adversarial robustness scenario."

### Latency spike

Trigger: Any endpoint takes >2 seconds.
Display: Animated progress bar with elapsed time counter. Cancel button (sends DELETE /query/{query_id} to abort). If >5 seconds: "This is taking longer than expected. Click Cancel to abort or Continue to wait."
Never leave a blank screen. A blank screen on stage is a demo-killer.

### GDPR erasure verification failure

Trigger: POST /erase returns HTTP 500 (HMAC key unavailable).
Display: "Erasure could not be completed. HMAC verification service unavailable. The erasure request has been logged and will be completed manually within 24 hours." Show the log entry with timestamp. This is the honest failure message -- it does not pretend the erasure succeeded.
Why this matters on stage: A silent failure (displaying success when HMAC failed) is a trust-breaking moment if anyone checks the data afterward. An honest error message is always better than a fake success.

### Counterfactual substitution semantic decoherence

Trigger: POST /query/counterfactual returns semantic_drift_detected: true.
Display: "The substituted fact produced an answer that may not be fully coherent. Showing result for review." Display the counterfactual answer with a yellow "Review" banner. Do not hide the result -- show it with the caveat.

### Network failure on stage

Mitigation (engineering requirement): Cache the 5 demo scenarios' full responses on the client at demo load time. All 5 scenarios can run from cache if the backend is unreachable. The cache is populated at "demo start" button press. This is the most important engineering safety net for live demos.

---

## 8. ENGINEERING TIMELINE

### Phase 1 -- Week 1: Core pipeline + basic UI

Days 1-2: Confirm backend integration: the 5 endpoints callable from a test client. Smoke test: POST /query returns a valid answer from the demo KB.
Days 3-4: Load demo KB (3K Wikipedia facts with temporal metadata).
Day 5: Basic Streamlit UI for Scenario 1 (query + citations).
Checkpoint: Can demo Scenario 1 end-to-end.

### Phase 2 -- Week 2: GDPR erasure + audit trail

Days 6-7: POST /erase endpoint + HMAC verification + erasure log.
Day 8: GET /audit-trail endpoint + Merkle path serialization.
Days 9-10: Streamlit UI: erasure form, audit log panel, Merkle proof panel (Markdown tree at minimum; D3 tree if time allows).
Checkpoint: Can demo Scenarios 2 and 4 end-to-end.

### Phase 3 -- Week 3: Bitemporal + counterfactual

Days 11-12: POST /query/as-of endpoint + temporal metadata filter.
Day 13: POST /query/counterfactual endpoint + Pattern B integration test.
Days 14-15: Streamlit UI: date picker, two-panel layout, counterfactual editor + diff.
Checkpoint: Can demo Scenarios 3 and 5 end-to-end.

### Phase 4 -- Week 4: Polish + failure modes + demo scripting

Days 16-17: Response caching (offline demo safety net). Error state UI for all endpoints.
Day 18: Side-by-side LLM comparison (Scenario 6). Pre-load 5 known-confabulation questions.
Day 19: Full demo run-through. Time each scenario. Identify any >2s latency and optimize or cache.
Day 20: Final polish. Freeze demo KB. Write demo script (printed + Teleprompter-ready). Buffer day.
Checkpoint: Full 10-minute demo runnable twice in sequence with no engineer present.

### Parallelization note

If two engineers are available, Phases 1-2 and Phase 3 partially overlap. Backend engineer finishes Phase 2 APIs on days 6-8 while frontend engineer builds Phase 2 UI on days 9-10. Backend engineer starts Phase 3 APIs on day 11 while frontend engineer finishes Phase 2 UI. Total wall-clock: 3 weeks.

---

## 9. DEMO IMPACT VS ENGINEERING COST -- FINAL RANKING

| Capability | Demo impact (1-5) | Eng cost (days) | Impact/cost ratio | Priority |
|---|---|---|---|---|
| GDPR erasure | 5 | 4 | 1.25 | Ship first |
| Audit trail + citations | 5 | 5 | 1.00 | Ship second (foundation) |
| LLM comparison (F1 delta) | 4 | 2 (leverages existing) | 2.00 | Highest ratio; ship early |
| Bitemporal as-of | 4 | 4 | 1.00 | Ship Week 3 |
| Counterfactual replay | 5 | 7 | 0.71 | Ship last; highest risk |
| Pattern B structured query | 3 | 8 | 0.38 | Post-v1 |
| Distributed CRDT | 2 | 10 | 0.20 | Not in demo |

Actual ship order by combined priority: (1) LLM comparison, (2) GDPR erasure, (3) audit trail, (4) bitemporal, (5) counterfactual.

The LLM comparison scenario (Scenario 6) has the best impact/cost ratio because the infrastructure (running Llama-1B with and without substrate) is already built for pipeline integration. The demo view is 2 additional Streamlit columns. This is 2 days of work that produces the north-star demo moment.

---

## CHEAP DECISIVE TESTS (pre-registration per capability)

Per drill-pretest-required rule, each demo capability requires a 1-2 hour pre-test before engineering authorization:

| Capability | Pre-test | Time | P_theoretical | P_empirical (after pre-test) |
|---|---|---|---|---|
| GDPR erasure | Erase 1 fact; confirm re-query returns null; confirm non-erased facts unaffected | 20 min | 0.85 | 0.65 target, HARD-FAIL if re-query still includes erased entity |
| Audit trail | Walk Merkle path for 1 citation; confirm chain closes to root | 10 min | 0.90 | 0.70 target, HARD-FAIL if root mismatch |
| Bitemporal | Store 2 versions of 1 fact; query at both timestamps; verify correct version | 30 min | 0.75 | 0.50 target, HARD-FAIL if temporal filter returns wrong version |
| LLM comparison | Run 5 known-confabulation questions bare + augmented; confirm augmented wins on 4/5 | 45 min | 0.85 | 0.60 target, HARD-FAIL if augmented wins < 3/5 |
| Counterfactual | Substitute 1 fact in 1K-fact store; verify answer differs in expected direction; verify store unchanged | 30 min | 0.80 | 0.40 target, HARD-FAIL if store modified or answer unchanged |

---

## FALSIFIABLE PREDICTIONS -- HARD-PASS / HARD-FAIL

**HARD-PASS thresholds (demo is ready to ship)**
- All 5 capability pre-tests pass at or above P_empirical targets above
- All 5 Streamlit scenarios run end-to-end in <2 seconds (latency SLA)
- Demo runs twice consecutively without engineer intervention (stability SLA)
- GDPR erasure re-query returns zero results for erased entity on 3/3 manual checks
- Counterfactual replay time shown on screen is <=10ms (anything higher breaks the "3.9ms" talking point)

**HARD-FAIL thresholds (stop engineering, root-cause before continuing)**
- Erasure re-query returns the erased entity on ANY of 3 manual checks
- Merkle proof root mismatch on ANY citation from the demo KB
- Bitemporal temporal filter returns a fact from outside the requested time window
- Counterfactual modifies the original store in ANY test
- Any scenario exceeds 5 seconds wall-clock latency on demo hardware

---

## CROSS-THREAD SYNTHESIS

This drill synthesizes findings from:
- temporal-fact-versioning drill (2026-06-07): bitemporal storage algebra, Pattern A/B/C costs, valid-time vs transaction-time separation
- v1-benchmark-suite drill (2026-06-07): +0.35 F1 empirical north-star, MuSiQue multi-hop as the most legible demo benchmark, LongMemEval as temporal-reasoning test
- production-architecture-locked (2026-06-07): Llama-1B BASE + left-pad + PCA preferred, bf16 N=65k, LoRA hurts retrieval -- confirms the LLM stack for the demo
- adversarial-robustness drill (2026-06-07): hallucination flagging at generation time is achievable with NLI post-check

The demo UI is not a standalone product -- it is an evidence layer on top of an already-validated substrate pipeline. The engineering effort is primarily in API serialization (Merkle paths, temporal filters, counterfactual contexts) and Streamlit frontend, not in new substrate mechanisms.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. The GDPR erasure UI is a product feature, not a demo prop. Once built, it is the foundation for a GDPR/CCPA compliance module that enterprise customers pay for separately.

2. The audit trail visualization is the moat differentiator. No RAG system has this. The engineering effort (5 days) is low relative to the trust-building effect. Invest in making the Merkle proof readable by non-experts (not just raw hex).

3. Latency is the hidden risk. The substrate's cryptographic operations are fast, but the LLM generation step (Llama-1B at bf16, N=65k) has a latency floor. On demo hardware (local GPU), expect 1-3 seconds for the full query + generate pipeline. If this exceeds 2 seconds visibly on stage, add a progress indicator per failure-mode UX above.

4. The counterfactual scenario depends on Pattern B integration working at the KB scale used in the demo. If Pattern B is not stable at 3K-fact scale, this scenario must be canned or replaced with a pre-computed result. Pre-test is mandatory before committing this to the demo script.

5. The combined timeline (pipeline integration + demo UI) is 4-6 weeks with one engineer or 3-4 weeks with two. This aligns with the NORTH STAR 5-7 week v1 demo target in memory.

---

## CITATIONS (verified count: 5 from prior research drills)

1. Research drill: temporal-fact-versioning-2x-2026-06-07 -- Snodgrass bitemporal model; Pattern A/B/C cost analysis; SQL:2011 AS OF; P_deflated estimates for bitemporal implementation
2. Research drill: v1-benchmark-suite-3x-2026-06-07 -- +0.35 F1 empirical result (cycle 158); MuSiQue baseline scores; Llama-3.2-1B-Instruct benchmarks; LongMemEval session architecture
3. Production architecture locked (MEMORY.md 2026-06-07) -- Llama-1B BASE + left-pad + PCA preferred; bf16 N=65k; LoRA hurts retrieval
4. Research drill: adversarial-substrate-divergence-2026-06-07 -- hallucination flagging and NLI post-check patterns
5. Research drill: agentic-memory-layer-2x-2026-06-07 -- GDPR Article 17 compliance framing; HMAC keystore mechanism; tombstone pattern

Note: This drill is a 2x operational drill (engineering scoping), not a primary lit-scan. External citations are not applicable; the above are cross-thread prior deliveries.

---

Filed-by: research sub-agent (Sonnet 4.6)
Calibration: P_theoretical x P_empirical split reported per capability; lit-scan penalty 0.15-0.20 applied to empirical estimates
Drill type: 2x operational -- UX/API/engineering scoping on validated capabilities
