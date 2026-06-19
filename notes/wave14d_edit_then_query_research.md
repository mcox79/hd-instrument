# Wave 14d — Edit-then-Query: Unbiased Product Research

Date: 2026-05-19
Purpose: Map the editable-LM landscape, score axes, and pick the smallest
credible product where an HDC byte-level substrate has a real, defensible edge.
Framing rule: ask "what makes editing hard?", not "is HDC better?"

---

## 1. TL;DR

Editing inside transformer weights (ROME / MEMIT / MEND) is fundamentally a
locality-vs-ripple game the field is losing: edits beyond ~50–100 facts
deteriorate locality and beyond ~1k edits trigger gradual-then-catastrophic
forgetting (Gupta 2024, 2401.07453). Memory-based editors (SERAC, GRACE) and
RAG dominate at scale, but they pay in (a) opaque gating, (b) no atomic
audit trail, and (c) no surgical sub-fact deletion — the substrate's
decomposable atomic-bundle structure is a genuine differentiator on
*verifiability* and *targeted erasure*, weaker on retrieval coverage. The
smallest credible v1 is **GDPR-style targeted erasure with cryptographic
audit** ("which atoms were touched, when, by whom"), not Wikipedia-update
or preference-editing, because erasure is the one place the SOTA legally
cannot use RAG-only and the substrate's decompose-edit-recompose loop is
exactly what regulators ask to inspect.

---

## 2. Literature on Editable LMs (ranked by relevance to substrate)

Ranked by how much the method's failure mode is something HDC's structure
specifically addresses.

### Tier A — Direct competitors / inspirations

**ROME** (Meng et al. 2022, arxiv 2202.05262)
- Primitive: rank-one update to a single MLP layer's W, treating it as a
  key→value associative memory.
- Cost: ~1 GPU-minute per edit on GPT-J; closed-form, no training.
- Failure mode: edits bleed (Hase 2023; "But Is It Really In Rome?" on
  Alignment Forum). Sequential edits past ~50 cause locality collapse;
  past ~1k cause model collapse. r-ROME (2024) partially fixes the
  collapse artifact but not the bleed.

**MEMIT** (Meng et al. 2022, arxiv 2210.07229)
- Primitive: simultaneous rank-r update across multiple MLP layers; solves
  for `argmin ||W - W'|| s.t. W'k_i = v_i` for batch of (k,v) pairs.
- Cost: scales to ~10k edits in one shot; still GPU-bound.
- Failure mode: paraphrase and neighborhood metrics degrade above batch
  ~1024; performs best at exactly the eval distribution it was solved for.
  Ripple effects extend into hidden space even where no factual
  relationship exists (Cohen 2023, 2307.12976; "Evaluating the Ripple
  Effects").

**MEND** (Mitchell et al. 2021, arxiv 2110.11309)
- Primitive: hypernetwork that decomposes the gradient of a fine-tune step
  into a low-rank parameter delta, trained to be a good "one-shot edit".
- Cost: ~1 forward pass at edit time, but requires training the
  hypernetwork on (edit, retain) pairs.
- Failure mode: degrades badly past ~10 sequential edits (Yao 2023).
  MALMEN (2024) shows the hypernetwork is fundamentally pooling parameter
  shifts and that simple summing causes cancellation.

### Tier B — Memory-based (most product-relevant)

**SERAC** (Mitchell et al. 2022, arxiv 2206.06520)
- Primitive: external edit memory + a learned gating classifier that
  routes inputs to either (a) base model or (b) a small counterfactual
  model that reads the relevant edit.
- Cost: edit = append to memory; query = O(1) classifier call.
- Failure mode: "hard examples account for the vast majority of classifier
  errors" (paper §5); accuracy on out-of-scope-but-related queries is the
  bottleneck. The gating is a black-box neural net — you cannot audit why
  a given query was or wasn't routed to an edit.

**GRACE** (Hartvigsen et al. 2022, arxiv 2211.11031)
- Primitive: discrete codebook of (activation_key → activation_value)
  patches inserted at one chosen layer; query-time nearest-neighbor in
  activation space toggles a patch on.
- Cost: edit = add codebook entry; query = layer-hooked NN lookup.
- Failure mode: codebook epsilon-ball radius is a hyperparameter — too
  large = bleed, too small = miss paraphrases. State-of-the-art on
  sequential edits among parameter-touching methods, but still degrades
  on multi-hop (Zhong 2023).

### Tier C — Retrieval baselines

**GraphRAG** (Edge et al. 2024, arxiv 2404.16130)
- Primitive: LLM builds an entity-relation graph from corpus; queries are
  answered by retrieving community summaries.
- Cost: graph construction is expensive but one-shot; edits = patch the
  graph node.
- Failure mode: edits to the graph don't reach into the LLM's parametric
  knowledge — the LLM still "knows" the old fact and may contradict the
  retrieved patch.

**Vanilla RAG**
- Primitive: append to vector store; query = top-k retrieval + LLM read.
- Cost: trivial.
- Failure mode: documented in 2025 surveys (e.g., 2508.03860, MDPI
  Mathematics 13/5/856) — RAG still hallucinates ~5–20% on grounded
  questions because the LLM's parametric prior overrides retrieved
  context, especially when the parametric answer is high-confidence
  and the retrieved snippet is short.

### Tier D — Adjacent

- **Selective Contextual Reasoning** (2503.05212): "stop editing, just
  retrieve" — argues editing is the wrong frame.
- **FiNE / neuron-level editing** (2503.01090): more surgical than ROME
  by localizing to individual FFN neurons.
- **KELE / IRAKE** (2408.12456, 2509.07555): wrappers to fix multi-hop
  failure of editors via guided decomposition.

---

## 3. Edit-axis Evaluation

Scoring: ★★★★★ best in class, ★ unusable in practice. Anchored to
2024–2025 published evals.

| Method     | Locality | Persistence | Composability | Verifiability |
|------------|----------|-------------|---------------|---------------|
| ROME       | ★★ (bleed past 50 edits) | ★ (subsequent fine-tune erases) | ★ (collapse past ~1k) | ★ (rank-1 delta in opaque MLP) |
| MEMIT      | ★★★ at <1k; ★ above   | ★ (overwritten by training) | ★★ (batched only) | ★ (multi-layer delta) |
| MEND       | ★★ | ★ | ★ (≤10 sequential) | ★ (hypernet output) |
| SERAC      | ★★★ (gated)            | ★★★★ (external memory survives training) | ★★★ (memory grows freely) | ★★ (memory readable, gate opaque) |
| GRACE      | ★★★★ (codebook ε-ball)| ★★★★ (codebook persists) | ★★★ (sequential proven to 1k) | ★★★ (codebook entries inspectable) |
| GraphRAG   | ★★★★ (graph node)      | ★★★★★ (no model touch) | ★★★★ (graph edits) | ★★★★ (graph diff = audit log) |
| RAG        | ★★★★ (doc-level)       | ★★★★★ | ★★★★★ | ★★★★ (doc + retrieval log) |

Key empirical anchors:
- ROME/MEMIT ripple: 38–66% portability accuracy across models on
  RippleEdits (2307.12976).
- Sequential collapse: Gupta 2024 (2401.07453) shows two-phase forgetting
  for ROME and MEMIT.
- Verifiability: no parameter-touching editor produces a human-readable
  diff of what changed semantically — you get a weight delta, not "we
  replaced 'Paris' with 'Lyon' in fact F".

---

## 4. Where HDC Fits on Each Axis

### Locality — ★★★★★ (theoretically), ★★★ (demonstrated)
- Bundle `B = sum_i bind(role_i, atom_i)`. Editing one (role, atom) pair
  changes that binding only; orthogonality of random hypervectors gives
  near-zero interference with other bindings in the same bundle.
- Demonstrated: residual-and-rebind primitive works on isolated bundles.
- Not demonstrated: locality at the *query level* — i.e., does a query
  for an unedited fact still resolve correctly when it shares atoms with
  edited bundles? This is the open question.

### Persistence — ★★★ (mixed)
- Pool entries (the cleanup memory) persist indefinitely; an explicit
  edit to a pool entry survives.
- The W matrix (whatever you're using as the bundling/key transform)
  keeps drifting under continued training. If a query depends on W to
  reach the bundle, the edit can effectively rot.
- Verdict: persistence is conditional on query-side routing being
  bundle-anchored rather than W-anchored. **This is the integration
  problem of §7.**

### Composability — ★★★ (unclear in practice)
- Theory: edits on distinct bundles are non-interfering (sum of bundles
  is still well-defined). Edits on the *same* bundle compose via
  superposition.
- Risk: bundle capacity. Per the survey (2111.06077), each bundle holds
  ~D/(k log k) reliable atoms; exceeding this degrades all bindings.
  Sequential edits that add bindings will eventually saturate.
- Untested: composability across the W transform, since the LLM-side
  query has to traverse it.

### Verifiability — ★★★★★ (genuine moat)
- Decompose: `B → {(role_i, atom_i)}` is exact (modulo noise) and is a
  primitive of the substrate, not a post-hoc interpretability tool.
- Edit log: "atom at role_r in bundle B was swapped from a to a' at
  timestamp t by principal p" is naturally cryptographic — atoms are
  pool indices, roles are pool indices, the diff is a 4-tuple.
- Recompose: deterministic reverse.
- **No other editor on the list produces an edit log that a non-ML
  auditor can read.** This is the single defensible axis.

---

## 5. Real Product Use-cases vs. Current SOTA

### Use-case A — Wikipedia knowledge update for deployed LLM
- Pain: model trained on 2024 dump, world moved on.
- SOTA: RAG (vector store + retrieval). Works well enough that nobody is
  deploying ROME at scale.
- HDC advantage: marginal. RAG owns the document-level case.

### Use-case B — Customer support / outdated KB correction
- Pain: rep tells customer wrong return policy because LLM was trained
  on old docs.
- SOTA: RAG over current KB; sometimes fine-tune.
- HDC advantage: marginal. The unit of correction is a document, not a
  byte-level atom; HDC granularity is overkill.

### Use-case C — Personalized assistant preference editing
- Pain: "I'm vegan now, stop suggesting steakhouses."
- SOTA: SERAC-like external memory + system prompt; or in-context.
- HDC advantage: minor. Locality matters but the alternatives are
  acceptable. Verifiability matters little ("did the assistant note my
  veganism" is checkable by behavior).

### Use-case D — Legal/compliance: GDPR right-to-erasure, redaction
- Pain: data subject demands removal of personal info from a deployed
  model. GDPR Article 17. EU AI Act 2025 enforcement expanding.
- SOTA: **There is no satisfying SOTA.** Three options today:
  1. Retrain from scratch with the data excluded — prohibitively
     expensive at LLM scale.
  2. Machine unlearning approximations (gradient ascent, NPO, etc.) —
     no formal guarantee; courts have not blessed any specific method.
  3. Output filtering at inference — fragile, breakable by prompt
     injection, does not satisfy "erasure" under GDPR strict reading.
- Recent surveys (2507.11128, MDPI Future Internet 17/4/151) explicitly
  call out that the right to erasure in LLMs is **unsolved** and that
  regulators expect verifiable removal.
- **HDC advantage: this is the only product where the substrate's
  decompose-and-prove primitive maps directly to a regulator-readable
  artifact.** "Atom A at role R is deleted from bundle B; cleanup pool
  entry zeroed; diff signed at time t" is a legal document, not a hand-
  wave.

### Use-case E — Real-time updates (news, weather, stock)
- Pain: model has stale info.
- SOTA: RAG. The freshness/cost tradeoff is solved.
- HDC advantage: none.

---

## 6. Smallest Credible Edit-then-Query Product for the Substrate v1

**Pick: targeted erasure with verifiable audit log ("right-to-forget for
HDC-augmented LLMs").**

Why this and not the others:
- It's the one use-case where RAG can't simply win — RAG keeps the data
  in the vector store; deleting from the vector store doesn't address
  what's in the model's weights.
- It's the one use-case where verifiability is the *primary* product
  attribute, not a nice-to-have. Compliance auditors need a paper trail;
  the substrate produces one for free.
- Scope is naturally narrow: a v1 doesn't need to cover all of model
  knowledge, just the specific atoms representing redactable entities
  (names, identifiers, location strings). The byte-level substrate
  already represents these as concrete atoms.
- Failure is detectable: post-erasure probing is a well-defined test
  (does the model emit the redacted string given any prompt in the
  attack set?). Unlike "is the model still smart after the edit?", this
  has a binary answer.

What v1 looks like concretely:
1. The HDC layer holds a redactable subset of representations (e.g., a
   per-document entity bundle for documents in the model's auxiliary
   memory).
2. Erasure API: `erase(entity_id) → signed_diff`. Implementation:
   decompose the bundle, zero the entity's atom at every role, recompose,
   zero the cleanup-pool entry, write a signed entry to the audit log.
3. Query coverage: probing harness with 100+ paraphrased prompts per
   redaction, measuring leak rate. Target: zero leaks on the redacted
   atom; ≤1% behavior delta on a held-out non-redacted set.
4. Auditor-readable export: JSON diff per erasure with atom IDs, role
   IDs, pool indices, timestamp, principal, signature.

What v1 explicitly does *not* do:
- Edit the underlying LLM's weights. We are not competing with ROME.
- Cover knowledge stored only in the LLM's parameters. That's outside
  the HDC layer's reach, and we should say so to regulators.
- Promise multi-hop reasoning over edits.

---

## 7. Hardest Technical Challenge — Query-side Integration

The substrate is good at editing atoms inside bundles. The product
question is: **when the LLM is asked about the redacted entity, does
the query reach the (now-zeroed) bundle, or does it bypass the HDC
layer and recover the answer from the transformer's own parametric
memory?**

This is the integration problem. Three sub-problems:

### 7a. Routing
Some queries should go through the HDC store, others shouldn't. SERAC
solved this with a learned gating classifier and paid for it with
opacity. We need a *deterministic* router — e.g., "any prompt containing
a known PII pattern is routed through the HDC redaction check first."
This makes the audit story work but reduces the system to a structured
PII filter for the v1 product. That's fine — it's what regulators want.

### 7b. Coverage
The transformer also has the fact stored implicitly. Even if we zero
the HDC bundle, the base model can emit "John Smith lives at 123 Main
St" because that's in its training data. Two paths:
- (i) Run the model in a "retrieval-grounded only" mode where parametric
  knowledge is suppressed; HDC is the source of truth. This is restrictive
  but legally defensible.
- (ii) Combine HDC erasure with a separate weight-level unlearning step.
  HDC then serves as the audit substrate, not the only erasure mechanism.

For v1, path (i) is the honest answer. It limits the deployment surface
but keeps the claim defensible.

### 7c. Query–bundle alignment
The LLM's query has to be mappable to a bundle key. If the W matrix
(whatever projects LLM activations into HDC space) drifts, the same
query may stop hitting the right bundle. Mitigations:
- Freeze W after deployment of a redaction; treat W as part of the
  audit artifact.
- Or: re-anchor bundle keys to a hash of the entity's canonical form
  (name string), not to W's output.

**This is the load-bearing open problem.** If we cannot guarantee that
post-redaction queries route to the redacted bundle (and only to it),
the verifiability advantage is theatrical. The substrate produces a
clean audit log of an edit that the LLM may or may not actually
respect at query time.

Brutal honest read: until 7c is solved with a published, repeatable
benchmark (e.g., 0 leaks on 10k paraphrased PII probes after 1k
sequential redactions), the product claim is "auditable erasure of
the HDC-stored representation," not "auditable erasure from the
model." That's a real but narrower product. We should ship it as that.

---

## 8. RAG Comparison

What RAG does well that HDC cannot match:
- **Document-level recall at billions-of-tokens scale.** Vector stores
  with HNSW/IVF retrieve from 10^9 chunks in milliseconds. HDC bundle
  capacity is bounded by D/(k log k); we don't scale to web-corpus
  size without losing the orthogonality guarantees.
- **Zero-shot new facts.** Append a doc to the store, queries see it
  immediately. HDC requires encoding the new atoms into the pool.
- **Ecosystem maturity.** LangChain, LlamaIndex, every cloud vendor.
  We're starting from zero.
- **LLM-native.** Retrieved context is text; the LLM consumes it
  natively. HDC outputs are vectors; we have to project back to tokens
  or train the LLM to consume HDC reads.

What HDC can do that RAG cannot:
- **Sub-document atomic erasure with proof.** RAG can delete a chunk;
  it cannot prove that no other chunk encodes the same fact. HDC can
  prove that no bundle contains a given atom at any role (pool sweep).
- **Compositional edits.** "Swap atom A for atom B across all bundles
  where they appear as role R." RAG has no equivalent — chunks aren't
  decomposable.
- **No-LLM-call audit.** Asking "is the fact X removed?" is a pool
  query on the substrate, not an LLM probe. Faster, deterministic,
  cheaper.
- **Provable absence.** Cryptographic-grade audit: signed diff over a
  finite atom alphabet. RAG audit is "we deleted the doc and trust
  that no other doc said the same thing."

The honest framing: HDC is **not** a RAG replacement; it's a compliance
layer that sits *next to* a RAG/LLM stack. RAG handles knowledge
freshness, HDC handles knowledge erasure with proof.

---

## 9. Sources

Primary papers:
- ROME — Meng et al. 2022 — https://arxiv.org/abs/2202.05262
- MEMIT — Meng et al. 2022 — https://arxiv.org/abs/2210.07229
- MEND — Mitchell et al. 2021 — https://arxiv.org/abs/2110.11309
- SERAC — Mitchell et al. 2022 — https://arxiv.org/abs/2206.06520
- GRACE — Hartvigsen et al. 2022 — https://arxiv.org/abs/2211.11031
- GraphRAG — Edge et al. 2024 — https://arxiv.org/abs/2404.16130

Limitation / failure-mode literature:
- Ripple effects of knowledge editing — Cohen et al. 2023 — https://arxiv.org/abs/2307.12976
- Sequential editing collapse — Gupta et al. 2024 — https://arxiv.org/abs/2401.07453
- Pitfalls of knowledge editing — Findings of EMNLP 2024 —
  https://aclanthology.org/2024.findings-emnlp.550/
- Multi-hop edit failure — Zhong et al. 2023; IRAKE 2024 — https://arxiv.org/abs/2509.07555
- "But is it really in Rome?" — Alignment Forum 2023 —
  https://www.alignmentforum.org/posts/QL7J9wmS6W2fWpofd
- Quantifying ripple effects — https://arxiv.org/abs/2403.07825
- Should we really edit LMs? — https://arxiv.org/abs/2410.18785
- Selective contextual reasoning (anti-editing) — https://arxiv.org/abs/2503.05212
- FiNE neuron-level editing — https://arxiv.org/abs/2503.01090

RAG / hallucination:
- Hallucination mitigation for RAG-LLMs — MDPI Mathematics 2025 —
  https://www.mdpi.com/2227-7390/13/5/856
- Hallucination to truth (fact-checking review) — https://arxiv.org/abs/2508.03860

GDPR / unlearning:
- Right to be forgotten in LLMs — https://arxiv.org/abs/2307.03941
- What should LLMs forget — https://arxiv.org/abs/2507.11128
- GDPR and LLMs technical/legal obstacles — MDPI Future Internet 17/4/151 —
  https://www.mdpi.com/1999-5903/17/4/151
- Goldilocks standard, unlearning & RTBF — CEP 2025 —
  https://cep-project.org/wp-content/uploads/2025/11/Pratiksha-Ashok-THE-GOLDILOCKS-STANDARD-Machine-Unlearning-and-the-Right-to-be-Forgotten-Under-Emerging-Legal-Frameworks.pdf

HDC / VSA background:
- Kleyko et al. VSA Survey Part I — https://arxiv.org/abs/2111.06077
- Kleyko et al. VSA Survey Part II — https://dl.acm.org/doi/10.1145/3558000
