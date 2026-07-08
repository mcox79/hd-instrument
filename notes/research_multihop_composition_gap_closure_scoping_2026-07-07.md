# Research: can we CLOSE the substrate's multi-hop composition gap (N8 re-VET honest weak spot)?

Author: research (Sonnet lit-scan x3 breadth + Opus-role synthesis). Date: 2026-07-07.
Drill type: go/no-go scoping (no cell built, no dispatch). Triggered by main-thread ask to synthesize
3 fresh session results against the standing June-19/N8 ConceptNet HARD_FAIL.

---

## HEADLINE

**Hypothesis #1 (the gap is closable by "adding per-hop re-cleaning") is REFUTED by a direct code
read, not merely untested.** `experiments/exp_substrate_conceptnet_kg_inference_transfer_cpu_v1.py`
(the cell that produced the June-19 HARD_FAIL, substrate Hits@10=0.451 < BGE 0.502) **already**
performs a hard argmax cleanup against the full entity codebook at every hop
(`substrate_scores()`: `best = argmax(E @ cur)` then re-queries `W @ (E[best]*R[r]*sq)`) —
structurally the identical "regenerative repeater" primitive that makes reasoning-depth chains
survive to depth-15. The mechanism this task hypothesizes as the fix is not missing; it was already
running when the substrate lost to BGE. So "re-clean each hop" is not a fresh lever here — it is
already-spent ammunition.

**What actually differs, on the evidence:** two INDEPENDENT, compounding disanalogies between
reasoning-depth's synthetic chain and ConceptNet's open KG, both fresh-lit-scan-confirmed as
known failure regimes in the literature, neither of which the June-19 cell addresses:

1. **Branching factor / multi-valued relations ("to-many" edges).** Reasoning-depth's codebook is a
   small, closed, near-single-valued KEY_SLOTS set with only accidental hash-style collisions.
   ConceptNet relations (IS_A, PART_OF, ...) are exactly the high-out-degree "to-many" relation type
   the multi-hop-KG-QA literature (MINERVA/Das et al. 2018, MultiHopKG/Lin-Socher-Xiong 2018) shows is
   the known failure regime for HARD single-path argmax decoding — and reports the standard fix is
   BEAM SEARCH / soft multi-hypothesis carry-through, not harder cleanup. The June-19 cell's per-hop
   step is a single hard argmax (`best = argmax(...)`, one candidate carried forward) — exactly the
   brittle configuration the literature flags, with no beam/soft-marginalization at all.
2. **Representational asymmetry (semantic content vs. arbitrary codes).** The substrate's entity
   codebook `E = bipolar(len(ents), N_DIM, g)` is **pure random noise per entity, zero semantic
   content**. BGE's embeddings carry pretrained distributional semantics. The lit-scan confirms this
   is a well-established, decade-old distinction in the KG-completion literature (Guu, Miller & Liang
   2015 "Traversing Knowledge Graphs in Vector Space," EMNLP; Lao & Cohen 2011 PRA/random-walk
   inference) — path/structural methods hard-fail when the exact supporting structure is sparse or
   missing, while embedding similarity degrades smoothly because it generalizes via latent semantic
   proximity even to never-seen edges. The June-19 result's own internal breakdown supports this
   exactly: substrate loses WORSE on non-trivial (deeper, no exact same-rel path) edges
   (`nontrivial_lift_hits10 = -0.720`) than on trivial ones (`-0.405`) — the substrate has nothing to
   fall back on when structure runs out; BGE does.

**Verdict: the gap is a compound TWO-CAUSE engineering problem, not a proven fundamental VSA limit
and not a one-lever fix.** Both causes are independently well-precedented as fixable (beam-style
decoding; semantic-content entity seeding), but neither alone is likely sufficient, and the specific
combination on this substrate is untested. Treat as a legitimate, cheap GO for a scoped exploratory
cell with a realistic MIDDLE-band expectation, not a high-confidence unlock.

---

## 1. Mechanism decomposition: WHY does substrate 2-hop underperform BGE?

Four candidate causes, each checked against on-disk code/metrics (not assumed):

**(a) Per-hop noise, fixable by adding re-cleaning to an external codebook — REFUTED.**
Verified by reading `substrate_scores()` (lines 220-232 of the June-19 cell): every hop already does
`best = int(np.argmax(E @ cur))` (hard cleanup against the FULL entity codebook `E`) before
re-querying `W @ (E[best] * R[r_idx] * sq)` for the next hop. This is not a partial or soft
cleanup — it is exactly the "hard reset to a fixed external alphabet" primitive that the
noise-compounding drill (`research_noise_compounding_bound_deep_mechanism_2026-07-07.md`) identified
as what makes reasoning-depth chains survive. It was present in the cell that produced the June-19
HARD_FAIL. Adding it again is not a new experiment.

**(b) Codebook coverage (candidates missing from the codebook) — minor factor, not the driver.**
The eval cell explicitly builds `ents` from store-edge endpoints plus all sampled classified-pool
endpoints (lines 368-373), so within-scope candidate coverage is engineered to be adequate for the
233 WITH-path rows evaluated. This is a real concern at 970K production scale (untested gap, flagged
separately in the ingest arc) but is not what explains the *measured* June-19 underperformance.

**(c) Multi-valued/branching intermediate nodes — STRONG, fresh-lit-scan-confirmed candidate.**
`cfrpe()` (the storage delta-rule, `W += (LR/n) * outer(val - W@key, key)`) has no special handling
for a key `(s, rel)` bound to MULTIPLE valid targets across training — repeated presentation of the
same key with different targets pushes `W` toward capturing several targets in superposition at that
slot. The fresh lit-scan (thread: multi-hop branching factor) independently confirms, via MINERVA
(Das et al. 2018) and MultiHopKG (Lin, Socher & Xiong 2018), that (i) KG-QA literature explicitly
distinguishes "to-one" vs "to-many" query relations, (ii) to-many relations show measurably lower
accuracy "regardless of the model," and (iii) FB15k-237-style graphs are dominated by 1-to-many
relations (~54% vs ~26% many-to-one, per the MultiHopKG analysis), cited as the reason greedy/hard
multi-hop reasoners can underperform single-hop baselines on exactly this kind of graph. The June-19
cell's per-hop step keeps only ONE candidate (`argmax`, not top-k/beam) — the precise brittle
configuration flagged. This maps directly onto ConceptNet's transitive relations (IS_A, PART_OF,
CN_HAS_A, ...), which are canonically high-branching.

**(d) Fundamental representational limit (no semantic content in entity codes) — STRONG, likely
CO-DOMINANT candidate.** The substrate's entity vectors are assigned via pure RNG (`bipolar(...)`) —
they carry no relationship to entity meaning. BGE's embeddings are pretrained on large text corpora
and encode genuine distributional semantics. The lit-scan (thread: semantic prior vs symbolic
composition) confirms this asymmetry is well-established (>10 years: Lao & Cohen 2011 on path-method
sparsity brittleness; Guu, Miller & Liang 2015 on embedding-composition's smooth-but-noisy behavior
vs path-method's hard failures on missing structure) and is an ACTIVE hybrid neuro-symbolic research
area (IterE, arXiv:1903.08948; RulE-family work) specifically because neither pure structural
composition nor pure embedding similarity alone is considered sufficient — the field's own answer is
COMBINE them, not "fix the symbolic side in isolation." This directly explains why even TRIVIAL
(single-relation, exact transitive) held-out edges still lose to BGE (`trivial_lift_hits10 = -0.405`)
— it is not purely a depth/composition effect, since a shallow, mostly-structural case still loses.

**Two supplementary internal data points, checked but not the primary evidence:**
- **N8's own "36.5x" composition ratio does NOT rescue this.** Reading
  `experiments/exp_n8_conceptnet_ingest_eval_v1.py::inference_transfer()`: the `baseline_1hop` there
  is CONSTRUCTED to be near-0 by design (direct 1-hop edges to the true target are explicitly
  excluded from the held-out chain sample — `if (s,o) in direct: leak+=1; continue` — so there is
  categorically no valid 1-hop answer to find), and the `frozen_encoder` baseline is raw MiniLM
  top-1 exact-match entity-name nearest-neighbor over the full entity set with no candidate-pool
  filtering (a near-zero baseline for almost any method by construction, not a fair proxy for BGE's
  filtered-Hits@10 comparison). This reconciles cleanly with the backup doc's own correction
  ("1hop=0 vacuous-by-construction, MiniLM baseline WEAK") — N8's ratio measures something different
  from, and weaker than, June-19's load-bearing substrate-vs-strong-BGE comparison, which remains the
  standing, undefeated HARD_FAIL.
- **The resonator verifier-readout HARD_PASS (K4 harvest=0.806, T0=0.5, +0.353 over plurality=0.453,
  `data/exp_resonator_verifier_readout_v1/metrics.json`) is a DIFFERENT sub-mechanism than hop-chaining
  re-clean.** It fixes AGGREGATION LOSS across R independent restarts of a single coupled K-way
  factorization (an "was the right answer already found but out-voted" problem), not a multi-hop
  graph-traversal problem. It is genuine evidence that "add an independent external check" is a real,
  working primitive family on this substrate — but it is not directly transplantable to ConceptNet's
  hop-chain structure without modification (see mechanism note below).

## 2. Does the reasoning-depth re-clean-each-hop mechanism TRANSFER to open-KB completion?

**Structurally: yes, it is already the same primitive (verified above). Functionally: no — and the
disanalogy is exactly what the task suspected (branching / multi-valued intermediates), plus one
more the task didn't name (semantic-content gap).**

Re-cleaning against a codebook only helps if resetting to that codebook lands you at the CORRECT
node. Reasoning-depth's codebook is small, closed, and near-single-valued, so a correct reset really
does discard accumulated noise (the regenerative-repeater property, `p_hop^D`). ConceptNet's codebook
is large, open, and high-branching, so "reset to the codebook" can cleanly and confidently reset you
to the WRONG (but locally plausible) branch of a one-to-many relation — the reset removes noise but
does not remove branching-ambiguity. This is a genuine, disk-verified extension to the
noise-compounding drill's own taxonomy: that drill's dichotomy was "reset vs. no-reset / self-
referential vs. independent-check." ConceptNet is a **third regime the taxonomy doesn't yet cover**:
reset IS present and IS independent (against the real entity codebook, not a self-referential
estimate) — but the codebook itself is (i) high-branching and (ii) semantically uninformative, so
resetting to it doesn't recover ground truth the way resetting to reasoning-depth's small closed
codebook does. **Recommend banking this as a refinement to the cross-cell law:** "reset-per-hop
survives chaining" needs an added qualifier — "...provided the thing you reset to is low-branching
AND/OR carries enough information to disambiguate branches." Neither holds for open-KB entity
codebooks built from random codes.

## 3. THE cheapest decisive experiment (spec only, NOT built, NOT dispatched)

Proposed cell: `exp_conceptnet_semantic_seeded_beam_composition_v1`. Reuses the June-19 cell's
data pipeline, held-out split, firewall, candidate-pool construction, and ALL FOUR metrics (closure,
frozen-BGE, substrate, random) **verbatim** — same bands, same held-out set, so the comparison is
apples-to-apples with the standing result. Two changes, addressing the two causes found in Section 1:

1. **Semantic-seeded entity codebook:** replace `E = bipolar(len(ents), N_DIM, g)` (pure random) with
   entity vectors derived from the now-CHAIN_GRADE-unblocked encoder (the graded-code retrieval fix,
   cross-seed MIN ret_agree10=0.432) — i.e., seed each entity's HD vector from its semantic-encoder
   embedding (via the same GSBC/graded-code binding already validated for retrieval), THEN let cf-RPE
   learn graph structure on top of that semantically-informed base, instead of on top of noise.
2. **Beam-style soft carry-through instead of single hard argmax per hop:** replace
   `best = int(np.argmax(E @ cur))` (one candidate) with a top-k (k=4-8) beam carried through each
   hop, scoring final candidates by best-over-beam similarity — directly targeting cause (c), per the
   lit-scan's confirmed standard fix (MINERVA/MultiHopKG/BeamQA/BeamAggR all use beam width
   specifically to survive high-branching hops; reported gains plateau modestly past width~4-8, so
   this is a bounded, cheap addition, not an open-ended search).

**Cheap diagnostic, free, do FIRST (before the full cell):** add per-row logging of the held-out
source's out-degree under the query relation (`len(sr.get(s, ()))`, already computable from data
already loaded in the existing cell) to the existing June-19 pipeline and re-run READ-ONLY (no new
data, no new store). This directly tests cause (c) by correlating substrate-vs-BGE lift with
branching factor on the ALREADY-LANDED 233 WITH-path rows — nearly free, and should be run
regardless of whether the fuller cell is built, since it is a near-zero-cost falsification opportunity
for the branching-factor hypothesis specifically.

**Pre-registered bands (same metric family as the June-19 cell: filtered Hits@10, AUROC,
trivial/nontrivial split):**

- **HARD-PASS:** substrate Hits@10 beats BOTH frozen-BGE AND closure by >=0.05 (the ORIGINAL
  sacrosanct band, unchanged), AND `nontrivial_lift_hits10` becomes >= 0.00 (currently -0.720) — the
  deep/hard cases must stop being the worst case, not just the aggregate improve. Also require
  AUROC >= 0.7 (unchanged band).
- **MIDDLE:** substrate closes on BGE (lift in [-0.02, +0.05)) OR `nontrivial_lift_hits10` improves
  materially (e.g. from -0.72 to inside [-0.30, 0.00)) without fully clearing HARD-PASS — an honest,
  reportable partial rescue, not force-fit to a pass.
- **HARD-FAIL:** substrate still <= BOTH baselines (Hits@10 <= max(closure, bge)) even with BOTH
  fixes applied, OR `nontrivial_lift_hits10` stays <= -0.50 — this would show the branching/
  multi-valued problem dominates independent of representational content, i.e. is the harder,
  not-yet-solved half of the compound problem.

**P estimate (calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]):**
Raw confidence that fixing ONLY cause (d) (semantic seeding, no beam) clears full HARD-PASS: LOW,
~0.20-0.25 (only one of two independently-identified causes addressed; the branching-factor
literature is explicit that hard single-path decoding remains brittle regardless of representation
quality). Raw confidence for the COMBINED fix (semantic seeding + beam): moderate, ~0.35-0.40 (both
known failure modes addressed simultaneously, each fix individually well-precedented in the general
KG-completion/KG-QA literature, but this SPECIFIC combination on this SPECIFIC substrate mechanism
is untested — novel synthesis). Applying the mandatory 0.15-0.25 deflation for uncharted-combination
risk: **P_deflated(combined fix clears full HARD-PASS) ~ 0.15-0.20.** P_deflated(clears MIDDLE or
better) is meaningfully higher, ~0.40-0.45, because semantic-seeded entities alone should push
single-hop substrate scores toward rough parity with BGE almost by construction (same underlying
encoder lineage) even before any graph-composition lift is added on top — so a MIDDLE outcome
(closing most of the gap without decisively beating BGE) is the honestly-expected base case, not a
downside surprise.

**Go/no-go read:** this is a legitimate, cheap (CPU, reuses ~everything, no new ingest) GO for
exp_dev — but should be shipped with the MIDDLE-band outcome pre-committed as the modal expectation,
not sold internally or to the user as a likely BGE-beating unlock. The free diagnostic (branching-
factor correlation re-read) should run first and independently, since a negative correlation there
would argue for prioritizing the beam-width fix over the semantic-seeding fix (or vice versa).

## 4. Honest bound: closable engineering gap, or genuine VSA limit?

**Neither extreme is supported by the evidence.** What the substrate CAN already do, proven:
depth-15 clean chain-survival on a closed, low-branching, near-single-valued codebook
(`reasoning_depth_keyslots_sharding_v1`, MIDDLE-to-CG-candidate); resonator K4 aggregation-loss
closed via independent verifier readout (0.806, matching oracle, HARD_PASS); N8 setrecall/refuse-gate
genuinely CG on the ingest side. What it CANNOT yet do, replicated across TWO corpora (WordNet
Item-1/M1/HYP-5, then ConceptNet June-19) and now TWO different storage mechanisms (serial cf-RPE
composition, and N8's multivalue-Hebbian setreadout — neither beats a strong frozen encoder on
open-KB completion): beat a strong pretrained text embedding on real-world multi-hop KG completion.
This is a genuinely stubborn, multiply-replicated negative.

Is it a WALL? The fresh lit-scan says no — hybrid neuro-symbolic KG completion (structural
composition + pretrained-embedding-seeded entities) is an active, credible, multi-year research
direction in the broader field (IterE and related rule+embedding hybrids exist specifically because
neither pure symbolic composition nor pure embedding similarity is considered sufficient alone), so
"VSA composition cannot in principle beat embeddings on open KGs" is NOT an established literature
conclusion — it would be an overclaim to assert that. But it is equally not established that THIS
substrate's specific combination (semantic-seeded entities + beam decode + cf-RPE composition) will
close the gap; that is the untested, novel-synthesis part, honestly capped at P~0.15-0.20 for full
closure.

**The defensible framing:** this is a two-cause, partially-precedented, partially-novel engineering
problem. Cheap to test, worth testing, not currently closable by any lever already in hand (re-clean
is already there and insufficient), and the honest expectation is a MEANINGFUL PARTIAL close
(MIDDLE band), not a clean win, on the first attempt.

## Cross-thread synthesis

- Directly refines `research_noise_compounding_bound_deep_mechanism_2026-07-07.md`'s reset/no-reset
  dichotomy: ConceptNet is a THIRD regime (reset present + independent, but codebook high-branching +
  semantically-empty) the prior taxonomy didn't cover. Recommend banking the qualifier described in
  Section 2 alongside the existing cross-cell law.
- Directly extends `reference_inference_transfer_eval_design_closure_perfect_bge_is_the_bar` (implicit
  via the June-19 skunkworks VET notes read this cycle) — confirms BGE remains the correctly-scoped,
  undefeated bar; this drill does not reverse that HARD_FAIL, it decomposes WHY it holds and proposes
  the first concrete, falsifiable two-cause fix.
- Reconciles with the N8 re-VET correction in the backup doc (composition scoped DOWN to MM): this
  drill independently confirms, by reading N8's own code, that its 1-hop/frozen-encoder baselines are
  constructed to be vacuous/weak, so N8's 36.5x figure cannot be read as contradicting the June-19
  HARD_FAIL — both readings are now mutually consistent from first principles, not just asserted.
- The resonator verifier-readout result (HARD_PASS, aggregation-loss fix) is genuine evidence FOR the
  general principle "add an independent external check to fix a noise/aggregation problem" but is
  mechanistically a different fix (restart aggregation, not hop-chain branching) — cited as
  encouraging precedent for the substrate's ability to build working external-check primitives, not
  as direct evidence this specific composition fix will work.

## Substrate-product implications

If the proposed cell clears MIDDLE-or-better: the substrate gains a concrete, honest story for
"knowledge_graph completion" that upgrades from "the refuse-gate is the only cert-grade value" to
"the refuse-gate plus a partially-closed completion gap, with a named, precise, two-part mechanism
(branching-factor decode brittleness + representational semantic gap) rather than an unexplained
underperformance" — a stronger glass-box narrative even without a full win. If it HARD-FAILs even
with both fixes: the honest bound sharpens further and usefully — "cf-RPE-style structural composition
over an open, high-branching, real-world KG does not currently beat a strong pretrained encoder even
with semantic seeding and beam decode," a precise, defensible, and still-informative closure that
would justify de-prioritizing further composition-mechanism levers on THIS exact task in favor of the
refuse-gate positioning already proven strong (AUROC 0.812-0.999 across the N8/June-19 cells).
Either outcome is actionable and non-parked. No overclaim either direction: this note does not
reverse the standing HARD_FAIL, and does not assert the gap is unfixable.

## Citations (verified count)

**Fresh external lit-scan (3 parallel Sonnet sub-agents, generic math/CS/networking terms only per
[[feedback-query-privacy-decomposition]], WebSearch/WebFetch):**

Thread 1 (multi-valued binding capacity in associative memory + symbolic-vs-embedding KG completion):
1. Willshaw, Buneman & Longuet-Higgins 1969-70s associative-net capacity theory (textbook,
   well-established: capacity falls as more associations share an address).
2. Palm associative-memory capacity survey (Frontiers Comput. Neurosci. 2014) — well-established.
3. Hopfield 1982 / Plate 1995/2003 HRR monograph lineage — well-established, textbook.
4. Guu, Miller & Liang, "Traversing Knowledge Graphs in Vector Space," EMNLP 2015 (arXiv:1506.01094)
   — well-established (>10 years), embedding-composition compounding-error analysis.
5. Lao & Cohen, "Random Walk Inference and Learning in a Large Scale Knowledge Base," EMNLP 2011 —
   well-established, path-method sparsity brittleness.
6. IterE (arXiv:1903.08948) — hybrid rule+embedding neuro-symbolic KG completion, active research
   area, moderate confidence (5-7 years old, established sub-field not a single contested result).
7. Two 2026 preprints surfaced by the sub-agent (arXiv:2605.05189 "Sharp Capacity Thresholds in
   Linear Associative Memory," arXiv:2606.24948 "Holographic Memory for Zero-Shot Compositional
   Reasoning in Knowledge Graphs") — **FLAGGED LOW-CONFIDENCE, not relied upon for the headline.**
   These are unreplicated, very-recent preprints whose framing is suspiciously well-tailored to this
   exact question; treated as directionally-consistent-if-real but NOT load-bearing evidence, per
   no-hallucinated-numbers discipline. The headline claims above rest on items 1-6 (decades-old,
   textbook-grade) only.

Thread 2 (branching factor / hard-decode brittleness on open-domain multi-hop graphs):
8. Das et al., "Go for a Walk and Arrive at the Answer" (MINERVA), arXiv:1711.05851 — explicit
   to-one/to-many relation-type distinction, well-established (2018, widely cited).
9. Lin, Socher & Xiong, "Multi-Hop Knowledge Graph Reasoning with Reward Shaping" (MultiHopKG),
   arXiv:1808.10568 / ACL 2018 (D18-1362) — well-established, quantifies FB15k-237's 1-to-many
   dominance (~54% vs ~26%) as the reason greedy multi-hop underperforms single-hop.
10. BeamQA, SIGIR 2023 (dl.acm.org/doi/10.1145/3539618.3591698) — beam-search-over-embeddings fix,
    established (peer-reviewed venue).
11. BeamAggR, arXiv:2406.19820 — soft-aggregation multi-hop fix, moderate confidence (2024, recent
    but peer-adjacent).

**Internal artifacts freshly re-read off-disk this cycle (load-bearing, not carried from memory):**
`experiments/exp_substrate_conceptnet_kg_inference_transfer_cpu_v1.py` (full source, the June-19
mechanism); `data/substrate_conceptnet_kg_inference_transfer_cpu_v1_metrics.json` (exact numbers
re-verified: substrate Hits@10=0.4506, BGE=0.5021, AUROC 0.733 vs 0.832, nontrivial_lift=-0.7196,
trivial_lift=-0.4048, n_with=233/n_without=233); `experiments/exp_n8_conceptnet_ingest_eval_v1.py`
(full source, confirms N8's 1-hop/frozen-encoder baselines are constructed-vacuous/weak);
`data/exp_n8_conceptnet_ingest_eval_canon_v1/metrics.json`; `data/exp_resonator_verifier_readout_v1/
metrics.json` (K4 verifier=0.806, plurality=0.453, baseline=0.133);
`research_noise_compounding_bound_deep_mechanism_2026-07-07.md`;
`research_reasoning_depth_self_margin_closed_form_2026-07-06.md`;
`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-07.md` (N8 re-VET correction context);
`skunkworks_to_all_CONCEPTNET_eval_verdict_VET_PASS_certgrade_honest_negative_2026-06-19.md`;
`exp_dev_to_skunkworks_CONCEPTNET_eval_RESULTS_factfab_PASS_inference_FAIL_verdict_VET_2026-06-19.md`.

**Total: 11 fresh external sources (9 well-established/textbook-to-established-subfield-grade + 2
explicitly flagged low-confidence recent preprints not relied upon) + 10 internal artifacts freshly
re-read off-disk this cycle (not quoted from memory).**

## P_deflated summary

- Claim (re-clean-alone hypothesis is refuted): P=0.95+ (direct code read, not inference — this is
  close to a fact, not an estimate).
- Claim (combined semantic-seed + beam fix clears full HARD-PASS on fresh dispatch): **P_deflated ~
  0.15-0.20** (novel combination, capped well below the 0.50 novel-synthesis ceiling given two
  independent well-precedented components rather than one speculative leap).
- Claim (clears MIDDLE band or better): **P_deflated ~ 0.40-0.45.**
