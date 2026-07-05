# Cortex re-encode prerequisite: verdict + smallest decisive experiment (2026-07-04)

Director design drill (notes memo, NO dispatch). Question from USER: before we
commit the live ~178k-atom substrate to a re-encode into the new GSBC_EXPAND2X
sparse concept code, be SURE the re-encode is the right prerequisite for the M3
cortex. Deflated-honest, good/mediocre/bad.

## TL;DR (one line)
Cortex does NOT need the re-encode; validate cortex FIRST on existing atoms. The
current parked cortex (Cortex-2 atom-consultation) reasons over atom METADATA via
a char-trigram sidecar, never touches concept-encoder vectors, and does no
bind/unbind algebra on atoms -- so the encoder's headline new property
(composable sparse codes) is not exercised by any cortex operation that exists.

## Q1 -- What the cortex actually needs from atom representations

Two "cortex" objects exist on disk; I read both end-to-end.

**A. Cortex-2 atom-consultation** (`hdlab/atom_consultation.py`; the parked
advisory -> SHADOW/WARN/LIVE dose-response -> multi-atom stack USER named).
What it consumes:
- A CURATED table of ~7 (curated subset of the 375-row `data/substrate_index/
  meta/atoms.jsonl`) METHODOLOGY atoms, each with structured fields:
  `op_class` tag, `constraint_text` (plain string), a discrete `recommendation`
  (e.g. "SHARDED"), `source_signature`, `tier`, `recommendation_priority`.
- A DELIBERATELY SEPARATE tiny `CharTrigramEncoder(n_dim=1024)` used only for
  tag similarity. The code is explicit (atom_consultation.py L372-375): "This is
  NOT the substrate n_dim; it is a tiny sidecar encoder purpose-built for tag
  similarity, orthogonal to any substrate configuration."
- Reasoning mechanism: strict-subset tag-filter by op_class -> char-trigram
  cosine rerank within the <20-atom subset -> return top atom's discrete
  `recommendation` field -> (Phase 2) write it into a downstream param slot with
  a nonce. Multi-atom "conflict resolution" (case 3 SCALE_FREE vs SHARDED) is a
  HAND-SET `recommendation_priority` constant + a locked `_PRIORITY_ALPHA=0.10`
  tie-break, NOT vector reasoning.

What it needs from representations: (i) atoms carrying a discrete actionable
recommendation, (ii) a tag-similarity channel good enough to route an operation
to the right atom at N~7-100 curated (char-trigram already clears this), (iii)
a nonce/enforcement instrumentation channel. NONE of these requires the new
sparse concept codes. There is ZERO FHRR bind/unbind on atom vectors anywhere in
the cortex path -- the cortex reasons by RETRIEVAL + DISCRETE-FIELD-READ, not by
algebra. That is the load-bearing observation.

**B. M3 Phase-1 router** (`substrate_router/api.py`, `router.py`). Also uses
`CharTrigramEncoder` for intent classification + a tiny Hebbian-bound KG fixture.
Also does NOT consume concept-encoder vectors of the 178k store. Same finding.

The original drill (notes/research_drill_cortex_2_atoms_as_active_constraints_M3
_v2_2026-07-04.md sec c) SKETCHED an AtomConsultant wrapping `DirectorKBQuery`
with a `query_vec` (i.e. semantic retrieval over the store) -- but the SHIPPED
implementation DEFERRED that ("wrapping the full DirectorKBQuery ~970k entities
~16s per cosine sweep would blow the sub-ms budget... deferred to a later phase")
and substituted the curated table + char-trigram sidecar. So the only cortex
operation that WOULD consume the concept encoder is an explicitly future,
not-yet-built phase.

## Q2 -- Is the re-encode a genuine prerequisite? NO.

The cortex can and should be validated first, for two independent reasons:
1. The parked cortex arc (atom-consultation) is fully decoupled from the concept
   encoder (Q1-A). Re-encoding the concept substrate changes nothing it reads.
2. Even the FULLER cortex (semantic retrieval over the store + composed answers)
   can be prototyped on the EXISTING representation. BGE-large gives 0.54
   semantic cosine -- mediocre but FUNCTIONAL for a retrieval prototype. You do
   not need 0.85 native codes to learn whether cortex REASONING (multi-atom
   integration, calibrated refuse, faithful provenance) works AT ALL.

Cortex-first is the SAFER order AND it de-risks the encoder investment:
- If cortex reasoning fails even on a near-oracle representation, the encoder is
  not the bottleneck and the re-encode is wasted compute committed on faith.
- If cortex reasoning works on the existing rep, you have a measured floor, and
  the encoder's 0.54 -> 0.85 gain becomes a QUANTIFIABLE cortex-accuracy lift
  (representation-quality dose-response). That measured lift is the decisive
  evidence that would actually JUSTIFY the re-encode -- which we do not have yet.

PROGRESS.md L7 asserts "everything downstream (retrieval, composition, Cortex-2
atom-consultation) inherits [the encoder's] quality." That is true in principle
for a FUTURE semantic-retrieval cortex, but FALSE for the cortex code that exists
today (char-trigram sidecar over curated metadata). The dependency is aspiration,
not current wiring. Committing the live store to a re-encode on the strength of an
unwired dependency is exactly the risk USER flagged.

## Q3 -- Smallest decisive cortex experiment (runnable on existing atoms NOW)

**Anchor idea:** `exp_cortex2_provenance_faithfulness_and_calibrated_refuse_v1`.
One experiment, three metrics, one of them decisive-and-novel.

**Capability demonstrated:** given queries that require INTEGRATING >=2 atoms,
the cortex (a) returns the correct composed answer when support exists,
(b) ABSTAINS ("I don't know") when support is absent, and -- decisively --
(c) its cited-atom trace is MECHANICALLY FAITHFUL: the answer provably depends on
exactly the atoms it cites.

**Assets, all LOCAL, zero re-encode:**
- Corpus: `data/substrate_index/meta/atoms.jsonl` (375 atoms) + the curated
  AtomConsultant table. Representation: existing `CharTrigramEncoder`.
- Held-out ANSWERABLE / UNANSWERABLE split: build from `fb15k_237_train_50k
  .jsonl` multi-hop chains (KG 1-hop r@1=1.000 chain-grade already banked at
  `data/exp_fb15k237_kg_khop_benchmark_cpu_v1/`). Unanswerable = queries whose
  supporting atom/edge is removed by construction.

**Three metrics (pre-registered):**
1. Answerable-recall: correct composed answer on answerable queries. Floor =
   single-hop top-1 retrieval baseline (the 2nd hop must ADD lift, else the
   "integration" is decorative -- same failure as the case-3 hand-priority hack).
2. Refuse-precision on unanswerable: cortex abstains. Floor = chance.
3. **Provenance-faithfulness under ablation (DECISIVE, NOVEL):** for each
   answered query, ablate each CITED atom one at a time -> fraction of answers
   that flip should be HIGH (cited atoms are load-bearing). Ablate a random
   NON-cited atom -> fraction that flips should be ~0. Faithfulness =
   flip_rate(cited) - flip_rate(non-cited).

**Pre-registered gates:**
- HARD_PASS: faithfulness >= 0.70 AND refuse-precision beats a black-box
  baseline (retrieve-top-k + concatenate, no per-hop gate, no calibrated refuse)
  AND answerable-recall within a small margin of that baseline.
- HARD_FAIL_DECORATIVE: faithfulness < 0.20 (citations don't determine the
  answer -> post-hoc rationalization, same as LLM chain-of-thought; the cortex
  adds nothing over LLM+vectorDB).
- MIDDLE_BAND: 0.20 <= faithfulness < 0.70 -> tag-vector representation may be
  the limiter; THIS is the trigger for the representation-quality 2nd arm
  (char-trigram vs BGE vs future-sparse), which is the FIRST honest evidence
  that would justify the re-encode.

**Honest failure modes:**
- Recall dominated by single-hop retrieval -> multi-atom claim decorative.
- Refuse-precision high only because the curated corpus is tiny and unanswerable
  queries are trivially far in char-trigram space -> won't survive scale; must
  smoke at the full 375-atom (and later BGE-index) density before any FULL claim.
- Faithfulness fails the ablation -> the trace is a story, not a mechanism.

**Why this and not something bigger:** provenance-faithfulness is the ONE
property that separates a glass-box cortex from LLM+vectorDB. Retrieval and
refuse are table-stakes both systems do; a mechanically-honest audit trail under
ablation is what an LLM cannot fake. Testing it costs a CPU-local smoke, needs no
GPU, and needs no re-encode.

## Q4 -- Honest: real capability or LLM+vectorDB replica? The ONE thing.

Deflated-honest read of the cortex bet:
- As CURRENTLY scoped (retrieve-atom -> read discrete recommendation ->
  advisory/enforce with SHADOW/WARN/LIVE), the cortex is LARGELY REPLICABLE by
  LLM + vectorDB + a policy engine. The retrieve-top-k-by-similarity is vectorDB.
  The recommendation field is a stored rule. SHADOW/WARN/LIVE is OPA/Gatekeeper.
  The parked-plan drill itself cites Rete (1982), CLP (1987), ASP, Self-RAG as
  the analogs and rates the whole bet P=0.45-0.50 deflated -- i.e. it already
  concedes this is a known computational motif. Case-3 conflict resolution being
  a hand-set priority constant reinforces this: the "reasoning" is engineered
  rules, not substrate reasoning.
- The ONE thing the cortex must demonstrate to be worth building over
  LLM+vectorDB: **mechanically-verifiable, substrate-native provenance +
  calibrated abstention that an LLM cannot fake** -- specifically (i)
  provenance-faithfulness under ablation, (ii) refuse tied to the substrate's OWN
  measured capacity bounds (it abstains because it knows its scaling laws, where
  an LLM confabulates), and eventually (iii) glass-box down to the vector
  algebra (unbind the answer, exhibit the constituent bindings). Property (iii)
  is the only thing that ever needs the encoder's composable codes -- and NO
  current cortex operation exercises it.

good/mediocre/bad on the cortex bet: **MEDIOCRE as currently framed** (it
replicates LLM+vectorDB+rules-engine, and today's code doesn't touch the
substrate's distinctive algebra), with a **GOOD conditional upside** IF the
decisive experiment shows provenance-faithfulness/calibrated-refuse beating a
black-box baseline. That upside is testable NOW, cheaply, with no re-encode.

## Sequencing recommendation
1. Run the decisive cortex experiment (Q3) on existing atoms + char-trigram. CPU-
   local smoke, one anchor.
2. If HARD_FAIL_DECORATIVE: the cortex is an LLM+vectorDB replica; do NOT spend
   the re-encode on its behalf; re-scope the cortex around the algebra property.
3. If MIDDLE_BAND (representation-limited): add the representation-quality arm
   (char-trigram vs BGE vs future-sparse). A measured cortex-accuracy lift from
   better codes is the FIRST real justification for the re-encode.
4. If HARD_PASS on char-trigram: the cortex works AND the re-encode is not
   urgent; finish the encoder for its OWN 4 goals (native perception, 0.85,
   sparse, algebra), not as a cortex prerequisite.

Net: the re-encode should be justified by a MEASURED cortex lift, not assumed.
Building the cortex validation first produces that measurement and costs one
CPU-local smoke.

## Evidence (paths)
- `hdlab/atom_consultation.py` (L64 char-trigram sidecar; L372-375 "NOT the
  substrate n_dim"; L246-358 curated 7-atom table; L419-519 consult() = tag-
  filter + cosine + discrete-field read; L382-392 hand-set priority tie-break)
- `experiments/exp_cortex2_atom_consultation_smoke_v1_core.py` (advisory probe)
- `experiments/exp_cortex_2_phase_2_dose_response_v1_core.py` (SHADOW/WARN/LIVE
  dose-response; case-3 exempted as structural-mismatch = hand-priority hack)
- `substrate_router/api.py`, `router.py` (Phase-1 router; char-trigram + tiny KG)
- `notes/research_drill_cortex_2_atoms_as_active_constraints_M3_v2_2026-07-04.md`
  (parked plan; sec 200-210 already flags "decorative retrieval -> needs
  different representation"; P=0.45-0.50 deflated; Rete/CLP/ASP/Self-RAG analogs)
- LOCAL prototypable-now assets: `data/substrate_index/meta/atoms.jsonl` (375),
  `hdlab/char_trigram_encoder.py`, `hdlab/director_kb_query.py`,
  `data/exp_fb15k237_kg_khop_benchmark_cpu_v1/metrics.json` (r@1=1.000),
  `fb15k_237_train_50k.jsonl`. NOT local: full 178k BGE npz (metrics-only;
  ~1.7k-item BGE indices under `data/substrate_index/cached_indices/`). The
  decisive test needs none of the missing assets.
- Substrate concept-query (mandatory pre-dispatch): "M3 cortex reasoning atom
  consultation..." returned WordNet "consultation"/"response" noise at
  cosine=0.35 -> SUBSTRATE KNOWS NOTHING of this concept (expected); prior arc
  work via substrate KB = NONE. Prior arc work via notes/code = the two cortex-2
  probes + router above.
