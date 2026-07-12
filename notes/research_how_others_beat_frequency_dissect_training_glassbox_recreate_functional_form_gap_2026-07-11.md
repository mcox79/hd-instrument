# Research: How others beat frequency (KGE link prediction), dissected training, and the glass-box recreation gap

Date: 2026-07-11. Synthesis drill, 2 parallel Sonnet lit-scan sub-agents (functional-form expressiveness;
realistic-performance + popularity-baseline methodology) + full on-disk code read of the three CSKG fit paths
this cycle (`experiments/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py`, `experiments/_kge_anchor1_fit.py`,
`experiments/exp_course_c_oracle_capacity_ladder_v1.py` metrics, which landed `LADDER_FIT_LIMITED` while this
drill was in flight). Directly extends and does NOT duplicate three same-day notes already on disk
(`notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md`,
`notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md`,
`notes/the_last_piece_intuitive_reasoning_vs_frequency_courses_2026-07-10.md`) — those already dissected the
KGE *training-recipe* question (Ruffinelli levers, RotatE/N3 hyperparameters, the LR-mismatch and epoch-count
findings) in depth. This note's job, per the USER's mission brief, is the two things those notes did NOT yet
nail down: (A) the **functional-form** verdict — is additive TransE structurally, provably wrong for CSKG's
relation mix, independent of training recipe — and (E/F) the **glass-box translation + reframe** — what to
build instead and what to actually gate on.

---

## HEADLINE

1. **Additive TransE is doubly, provably disqualified for CSKG's dominant relation mix — this is a theorem,
   not a training problem.** RotatE's own Table 1 (Sun et al. 2019, ICLR) proves TransE cannot represent
   symmetric relations (forces the relation vector to zero, collapsing every entity pair linked by that
   relation toward the same point) and TransH's original diagnosis (Wang et al. 2014, AAAI) proves TransE
   cannot represent 1-to-N/N-to-1 relations (forces all valid targets of a fixed (h,r) toward the same point).
   CSKG's two dominant relation types are **SYNONYM (symmetric)** and **IS_A (hierarchical, 1-to-N)** — i.e.
   CSKG stresses *both* of TransE's two proven blind spots simultaneously, on the two relations that make up
   the bulk of the graph. No amount of training (more epochs, better LR, more negatives) fixes a
   representational impossibility.
2. **The CSKG fit code, read in full this cycle, uses additive-Euclidean TransE scoring in ALL THREE of its
   fit variants (`margin_fb`, `margin_mb`, `anchor1`) — none of them is a native rotation/complex fit.** The
   Anchor-1 "KGE recipe upgrade" (CE self-adversarial loss + N3 + reciprocal + minibatch) changes the LOSS
   FUNCTION and training regime but not the underlying score: `pred = X[h] + D[r]; dist = ||pred - X[t]||` is
   literally TransE's translation score in every fit function in this file. The "phase-rotation / RotatE-equivalent"
   claim in the docstring is TRUE only of the **readout** step (the FPE kernel `S(x)=exp(i x.W)` is a group
   homomorphism, so `S(x_h+delta_r) = S(x_h) (.) S(delta_r)`, an exact complex rotation) — but the **fit**
   never optimizes that complex-domain objective directly; it optimizes the real-space Euclidean surrogate,
   which inherits TransE's proven symmetric/1-to-N collapse pressure regardless of what the readout does with
   the result afterward. **This is the operator-gap finding the mission asked for: we proved a genuine
   phase-rotation/RotatE-equivalent bind primitive works elsewhere on this substrate (PP-275,
   `lap3_rotate_analogy_cpu_v1`, Hits@1=0.899, landed) — but the CSKG course-C cells do not use it. They use
   additive-TransE-fit-then-kernel-readout, a different and weaker construction that only LOOKS RotatE-shaped
   at the very last step.**
3. **The synthetic testbed that "proved the operator" (reach@1=0.972) was built out of pure grid translations
   — a relation family with NO symmetric relations and NO 1-to-N branching by construction (a grid translation
   from a fixed point has a unique target).** That testbed could not have exposed TransE's blind spots because
   it never contained the relation patterns that trigger them. The CSKG failure and the synthetic success are
   NOT in tension — they are exactly what expressiveness theory predicts: additive translation works fine on
   translation-shaped data and fails on symmetric+hierarchical data, and CSKG is the latter. **"Prove the
   operator generalizes before scaling to CSKG" (2026-07-10's own stated caution) has now, in effect, come
   back negative — the operator (as actually implemented, i.e. the additive-fit half of it) does not
   generalize to CSKG's relation-pattern mix, and there is a specific, citable reason why.**
4. **0.90 Hits@10 is not a real bar — it is above every published de-leaked transductive KGE result at this
   entity-count scale, by a wide margin.** Best tuned glass-box numbers on a comparable-density graph
   (FB15k-237, ~14.5k entities, avg-deg ~37, vs CSKG-core's ~25.7k entities avg-deg ~39.7) top out around
   0.53-0.57 Hits@10 (RotatE 0.533; ComplEx+RP 0.568); best opaque GNN (NBFNet) reaches 0.599. The ~90%+
   numbers that circulate in old KGE papers come from the leaky, since-deprecated WN18/FB15k splits, not the
   real de-leaked benchmark this substrate's task most resembles. **The 0.90 oracle-fire gate should be
   dropped as a precondition — it was never literature-grounded, and the ladder result confirms it: even the
   TRANSDUCTIVE arm (fit WITH the answers folded in) tops out at 0.424 direct Hits@10 at the largest tested
   capacity, which is not a failure to reach an achievable target so much as evidence the target itself was
   set far above what any comparable published result has ever achieved.**
5. **The recipe axis is real and not yet exhausted — the ladder's own numbers show a genuine ~3x jump from
   recipe alone** (`L1` full-batch margin, 2400 epochs: direct H@10=0.132 → `L5` Anchor-1 minibatch/CE/N3/reciprocal,
   150 epochs, larger k/dim: direct H@10=0.424) **even before fixing the two open recipe risks this cycle's
   sibling note flagged (LR ~1000x high, epochs ~2.5-3x short vs RotatE's own FB15k-237 recipe).** But this is
   recipe improving a fundamentally TransE-additive fit — Section 5 below argues the NEXT recipe improvement
   should be applied to a genuinely rotation-native fit, not another Anchor-1-style tune of the same additive
   score.

**Calibration note on this note's own central synthesis (point 2-3, the operator-gap argument):** this bridges
two independently well-established external results (RotatE's Table 1 pattern-completeness theorem; TransH's
1-to-N diagnosis) with an on-disk code read and the ladder's own empirical numbers. The bridging inference
itself — that this SPECIFIC gap (TransE-additive fit under a rotation-shaped readout) is a PRIMARY contributor
to `LADDER_FIT_LIMITED`, as opposed to pure under-training — is not independently ablated on CSKG yet. Per
lit-scan calibration discipline, capped at **P=0.50** (novel-synthesis cap), even though the supporting external
theorems themselves are well-established (not capped).

---

## A. Functional-form verdict (with citations)

**RotatE's own comparison table** (Sun, Deng, Nie, Tang, ICLR 2019, arXiv:1902.10197, Table 1; well-established,
widely reproduced):

| Model | Symmetry | Antisymmetry | Inversion | Composition |
|---|---|---|---|---|
| TransE | **No** | Yes | Yes | Yes |
| DistMult | Yes | **No** | **No** | **No** |
| ComplEx | Yes | Yes | Yes | **No** |
| RotatE | Yes | Yes | Yes | Yes |

RotatE is the only one of the four canonical forms with all four boxes checked. The paper's own framing: prior
to RotatE, "no existing approach is capable of modeling all three relation patterns simultaneously."

**TransE's proof of failure, mechanism-level** (Wang, Zhang, Feng, Chen — TransH, AAAI 2014; well-established):
for a symmetric relation, `h+r≈t` and `t+r≈h` together force `2r≈0`, collapsing the relation vector to zero and
making the model unable to distinguish ANY entity pair linked by that relation from any other. For a 1-to-N
relation (one head, many valid tails under the same relation), `h+r≈t1` and `h+r≈t2` together force `t1≈t2` —
i.e. TransE is structurally compelled to push distinct, genuinely-different entities toward the same point
whenever a relation is symmetric OR branches to multiple targets. **CSKG's own relation inventory (read this
cycle from the decisive cell's own docstrings and prior notes) is dominated by exactly SYNONYM (symmetric,
first blind spot) and IS_A (hierarchical/1-to-N, second blind spot) — the two relation types that between them
trigger BOTH of TransE's proven structural failures, on the majority of the graph's edges.** This is a sharp,
citation-backed, config-independent verdict: **additive TransE is not merely suboptimal for CSKG, it is
provably incapable of jointly satisfying CSKG's two dominant relation-type constraints, at any dimension, with
any amount of training.**

**A second-order nuance the mission specifically asked to be sharp about:** ComplEx handles symmetry AND
antisymmetry AND inversion (three of the four RotatE boxes) but **not composition**. CSKG's L2-genuine task
(the substrate's own decisive experiment) is explicitly a 2-hop **composition** test (A→B via r1, B→C via r2,
is A→C via composed relation derivable). If the substrate had picked ComplEx instead of TransE, it would have
fixed the symmetric/hierarchical failure but walked directly into the ONE pattern ComplEx cannot represent —
composition — which is the exact axis the decisive experiment measures. **RotatE (or a genuinely equivalent
rotation-native construction) is the only one of the four canonical forms that is not disqualified by either
of CSKG's two structural pressures (symmetric+hierarchical relation mix) or its own test target (2-hop
composition).** This is a clean, non-obvious reason to prefer rotation specifically, beyond "it's the newer
model" — it is the only form in the standard four-way comparison with no known disqualifying gap for this
exact combination of corpus-relation-mix and evaluation-target.

**Full-expressiveness theorems** (distinct from the qualitative Table-1 patterns — these are "can this model
class represent ANY graph exactly, given enough dimension" results, well-established, multi-paper):
- ComplEx (Trouillon et al., ICML 2016 / JMLR 2017, arXiv:1606.06357): fully expressive at dimension
  `d = n_entities × n_relations`.
- SimplE (Kazemi & Poole, NeurIPS 2018, arXiv:1802.04868): tighter bound, `d = min(n_e·n_r, γ+1)` where `γ` is
  the number of TRUE edges — i.e. for a sparse-relative-to-`n_e·n_r` graph, the sufficient dimension scales
  with edge count, not the entity×relation product. CSKG-core (25,752 entities, 29 relations, ~511k core edges)
  is sparse relative to `n_e·n_r ≈ 7.5×10^5`, so this bound is informative and not astronomically large.
- **DistMult's antisymmetry failure is dimension-independent by construction**, not merely empirical: its
  score `Σ h_i r_i t_i` is provably symmetric under swapping `h` and `t` for ANY embedding, at ANY dimension —
  no amount of capacity fixes this.
- TransE and (per a 2024/2025 survey, arXiv:2407.16326) RotatE itself are **not** proven fully-expressive in
  this strict Trouillon/SimplE sense (checking all 4 qualitative patterns in Table 1 is a different, weaker
  claim than "can represent any arbitrary graph exactly"). Flagged honestly: RotatE is the best-qualified of
  the four canonical forms for CSKG's specific pattern mix, but "best-qualified among four" is not the same
  claim as "provably sufficient for CSKG specifically" — no such proof was found for any of the four forms on
  a real-world graph this large.

**NBFNet / path-based GNN link prediction** (Zhu, Zhang, Xhonneux, Tang, NeurIPS 2021, arXiv:2106.06935):
reframes link prediction as a generalized Bellman-Ford path-aggregation problem (learned INDICATOR/MESSAGE/
AGGREGATE functions conditioned on the query relation), subsuming classical path-ranking methods. Its
structural advantage is not a Table-1-style pattern proof but an architectural one: because scores come from
aggregating actual graph paths conditioned on the relation, it naturally captures multi-hop composition and
extends to unseen entities (inductive) — something no static embedding table (TransE/DistMult/ComplEx/RotatE)
can do at all, since those require a trained vector per entity. No comparable formal completeness/incompleteness
theorem was found for NBFNet analogous to RotatE's Table 1 — treat the compositional-generalization advantage
as a strong architectural + empirical argument, not a proven theorem.

**Symmetric-vs-hierarchical interference in one embedding space** — the mission's sharpest hypothesis (does
satisfying symmetric-relation constraints actively fight satisfying hierarchical/1-to-N constraints in the
same space): no formal theorem was found proving this directly, but it is **exactly the motivation cited by
hierarchy-aware RotatE follow-ups** (HAKE-family / SHKE), which explicitly split the embedding into a
**modulus** channel (encodes hierarchy/depth as concentric shells) and a **phase** channel (encodes
symmetric/antisymmetric/compositional relation semantics), precisely because using one undifferentiated space
for both jobs was found to create conflicting pressure. One analysis cited by these follow-ups found RotatE's
own constraint structure implicitly pushes entity-embedding moduli toward similar magnitudes across entities,
which actively hurts hierarchy/type classification — direct (if narrow) empirical evidence of the interference
direction hypothesized. **Flagged as inference bridging two established results, not a citable theorem on its
own — but directly consistent with, and a plausible root cause for, why even a corrected rotation-native fit
may still need a modulus/phase split to fully separate CSKG's SYNONYM (phase-appropriate) and IS_A
(modulus-appropriate) constraint pressures.** This is a genuinely new, second-order lever this drill surfaces
that neither of today's sibling notes named: P=0.30 (newer-ground, thin direct precedent for this specific
application), worth flagging for Phase-2b (post the primary functional-form fix) rather than gating the
corrected decisive experiment on it.

---

## B. Training-recipe dissection — pointer, not re-derivation

This was already dissected in full this same day in `notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md`
(Ruffinelli et al. 2020 deltas: RESCAL untuned 0.270→tuned 0.357 MRR, +32% relative, architecture unchanged;
ComplEx untuned 0.247→tuned 0.348, +41% relative; loss-function choice alone rivals or beats the
TransE→RotatE architectural jump) and `notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md`
(RotatE's exact FB15k-237/WN18RR training exposure — ~376/~472 dataset passes at batch 1024, LR 5e-5 — vs this
substrate's current 150-epoch, LR=0.05 recipe, a ~2.5-3x pass-count shortfall and ~1000x LR deviation). Not
re-derived here per this drill's own coordination. **The one new synthesis point this note adds to that
dissection:** the recipe fixes ranked there (more epochs, correct LR, larger `n_neg`) were designed to
strengthen the SAME additive-TransE fit (`fit_transe_coords`/`fit_kge_anchor1`). Section E/F below recommends
applying that SAME recipe trio to a genuinely rotation-native fit instead — the recipe findings are not
wasted, they transfer directly (self-adversarial CE loss, N3, reciprocal augmentation, minibatch SGD are all
loss/training-loop properties, orthogonal to whether the underlying score function is additive or rotational).

---

## C. Realistic performance / bar calibration — is 0.90 winnable?

**No — confirmed by dedicated lit-scan this cycle, well-established, clear negative answer.** On the standard
de-leaked transductive benchmarks in CSKG's approximate size/density class (FB15k-237: ~14.5k entities,
avg-deg ~37; WN18RR: ~40.9k entities): RotatE reaches 0.533/0.571 Hits@10 respectively; TransE reaches
0.465/0.501; tuned ComplEx variants reach 0.43-0.57 depending on tuning; best glass-box overall (ComplEx+RP)
reaches 0.568; best opaque GNN (NBFNet) reaches 0.599. **The ~90%+ numbers that circulate in older KGE papers
come from WN18/FB15k — the original, leaky, inverse-relation-contaminated splits that were deprecated once the
leakage was discovered** (Toutanova & Chen 2015; Dettmers et al. 2018, ConvE paper) **in favor of WN18RR/FB15k-237.
A 90% Hits@10 bar is not achievable by any credible published transductive KGE result on realistically-sized,
de-leaked graphs at CSKG's scale — it is only reachable on contaminated splits or structurally trivial
regimes.** This directly and independently confirms the on-substrate ladder result (`LADDER_FIT_LIMITED`,
best 0.424 at L5) is not an anomaly — it sits BELOW but in the same broad regime as external tuned glass-box
numbers on a comparably-dense graph, for a fit that is: (a) known-wrong functional form (Section A), (b)
under-recipe'd by ~2.5-3x on training exposure and ~1000x on LR (per the sibling note), and (c) being asked to
clear a 0.90 bar that no external precedent has ever cleared on real, de-leaked, comparably-sized data.

**On ConceptNet/CSKG-specific published numbers:** the standard reference benchmark (Li et al. 2016, ACL,
CN-100k/CN-82k; Malaviya, Bhagavatula, Bosselut, Choi, AAAI 2020, arXiv:1910.02915, ConceptNet+ATOMIC
completion via GCN+LM context) confirms this is an active multi-paper benchmark, but exact Hits@10/MRR tables
could not be extracted cleanly this cycle (PDF rendering failure) — flagged as a coverage gap, not a negative
finding. **Independently important structural caveat, well-established:** ConceptNet-style graphs often have
hundreds-to-thousands of valid tails for a given (head, relation) pair (e.g. `(Water, AtLocation, ?)` →
lake/river/pool/glass/...), making raw Hits@10/MRR poorly calibrated as an absolute bar there specifically —
this is a SEPARATE, additional reason (beyond "SOTA never reaches 0.90") that an absolute Hits@10 threshold
gate is the wrong instrument for a CSKG-shaped corpus, though this substrate's own filtered-metric methodology
(masking other known-true tails) already partially addresses it.

**How papers demonstrate beating a popularity baseline — methodology, well-established, converging multi-paper
literature (2020-2023, UAI/WWW venues):** Mohamed, Nováček et al. (UAI 2020, "Popularity-Agnostic Evaluation of
Knowledge Graph Embeddings," PMLR v124) show standard test sets are power-law skewed in entity/relation
frequency and propose strat-Hits@k/strat-MRR to correct for it, explicitly stating raw Hits@k/MRR "overestimate
performance by magnifying accuracy on popular items." Shomer, Jin, Wang, Guo, Tang (WWW 2023, arXiv:2302.05044,
"Toward Degree Bias in Embedding-Based Knowledge Graph Completion") stratify test triples by head/tail degree
buckets and find a substantial, consistent gap favoring high-degree entities across TransE/DistMult/ComplEx/
RotatE-class models on standard benchmarks; propose KG-Mixup as mitigation. A related analysis interrogates
whether apparent gains are model inductive bias or data skew. **This is directly, structurally the same
apparatus this substrate already has pre-registered and unused as a gate** (`stratify_by_tail_degree`
LOW/MID/HIGH tertiles; `cross_channel_geom_vs_poprank_r` backdoor check) — the field's OWN answer to "how do
you know you beat popularity, not just rode it" is exactly degree-stratified comparison plus a
correlation-with-popularity check, which this substrate's decisive cell already implements. **Answering the
mission's CRITICAL question directly: beating POP on a fair, degree-stratified split IS a lower, more
realistic, more field-standard bar than absolute oracle-recovery at 0.90 — the field measures the FORMER, not
the latter, as its actual "did structure beat frequency" claim.** Gating on oracle-fire-at-0.90 was gating
away from the measurable, field-standard win in favor of an internal sanity-check threshold with no
external precedent at this severity.

**Training-set reconstruction/memorization framing (the substrate's ORACLE_TRANSDUCTIVE arm specifically):**
no paper was found that frames in-sample reconstruction accuracy as a deliberate capacity diagnostic in
exactly this way — flagged as a genuine methodological gap this substrate is filling, not confirming (P as
inference, not established). The closest adjacent literature (a 2025 bioRxiv data-leakage benchmarking paper
for biomedical KGE) shows that when train-test leakage/redundancy is removed, reported scores drop sharply,
implying a nontrivial fraction of "generalization" scores across this literature are close to memorization of
structurally-recoverable patterns already — indirectly suggesting that even a WELL-TUNED, CORRECT-functional-form
fit should not be expected to reach near-100% even on a see-the-answers transductive-inclusion setup, since
real KGs (CSKG included) are not perfectly representable at modest dimension even with the tightest known bound
(SimplE's `min(n_e·n_r, edges+1)` — for CSKG-core this is still potentially thousands of dimensions for exact
reconstruction, far above the 24-32 dims tested on the ladder).

---

## D. Our-own-findings gap — reconciled (see HEADLINE points 2-3 for the full argument)

Restated compactly as the mission requested: **the map-builder operator VALIDATED at reach@1=0.972 (synthetic
grid) and the CSKG FIT_LIMITED result are not contradictory — they are consistent with functional-form theory,
because the synthetic testbed's relation family (pure translations) has none of the two patterns (symmetric,
1-to-N) that CSKG's dominant relations (SYNONYM, IS_A) stress, and the CSKG fit code (read in full this cycle)
never actually switches to a native rotation/complex objective — it stays additive-Euclidean in the fit step
across all three fit variants (`margin_fb`/`margin_mb`/`anchor1`), only borrowing a rotation-shaped kernel at
the very last (readout) step.** This is the single biggest lever the mission asked to identify: **use the
win-capable operator we already validated on real substrate infrastructure (PP-275, FHRR-bind = RotatE
relation embeddings, Hits@1=0.899) directly on CSKG's fit, instead of the current additive-fit + kernel-readout
wrapper.**

---

## E. Glass-box translation

| Field mechanism | Glass-box / VSA-native construction | Status on this substrate |
|---|---|---|
| RotatE rotation (relation = unit-modulus complex rotation, applied multiplicatively to entity phasors) | **FHRR complex phase-rotation binding** — entities as complex vectors, relations as unit-modulus rotation operators, score = `\|\|h ⊙ r - t\|\|` computed directly in complex space | **Already validated elsewhere on this substrate** (PP-275, `lap3_rotate_analogy_cpu_v1`, Hits@1=0.899, landed HARD_PASS) but **NOT what the CSKG course-C fit cells actually call** — this is the single highest-EV, lowest-risk recreate-first candidate, since it reuses a proven primitive rather than building anything new. |
| ComplEx complex bilinear (Hermitian inner product, `Re(<h, r ⊙ conj(t)>)`) | Same complex-phasor substrate representation, different readout: real part of the complex inner product rather than a magnitude/distance score. Natively expressible with the SAME FHRR bind primitive, just a different similarity function at readout. | Not built; cheap to add as a second scoring head on the same complex codes once the rotation-native fit exists (shares the underlying representation, differs only in the final similarity computation). Useful cross-check given ComplEx handles 3/4 RotatE patterns but not composition — informative to compare against RotatE-native on the composition-heavy L2 test specifically. |
| NBFNet path-aggregation (generalized Bellman-Ford, conditioned message passing over graph paths) | Substrate's own HRR-bind chain-composition: binding a sequence of relation operators along a path into one HD vector, decoded via resonator/iterative-cleanup unbinding — structurally analogous to path-conditioned aggregation, but as a SINGLE bound composite rather than a learned per-step message function. | **NEWER-GROUND, bigger lift** — already flagged as lever 6 (sequential phase-coded readout) in the sibling gap-closure-prep note, P=0.35, sequenced AFTER the functional-form fix, not instead of it. |

**Highest-EV recommendation:** recreate RotatE-native FHRR binding on CSKG first. It (a) is the only one of
the four canonical forms with no disqualifying gap for CSKG's relation mix + composition test (Section A), (b)
already has a validated, landed, on-substrate implementation to reuse (PP-275) rather than being built from
scratch, and (c) is a drop-in replacement for the fit step only — the training-recipe levers already ranked in
the sibling note (CE self-adversarial loss, N3, reciprocal, minibatch, corrected LR/epochs) all transfer
directly since they are properties of the loss/training loop, not the score function.

---

## F. The reframe — measure the actual prize, not an unwinnable proxy

**Recommendation: drop `ORACLE_FIRE_MARGIN=0.90` as a gating PRECONDITION. Always measure geom-vs-POP directly
on the genuine-L2 held-out set, at whatever fit quality is actually achieved, and report the oracle-transductive
number alongside as CONTEXT/ceiling only (the "how much headroom is left" ratio), never as a precondition to
asking the question.** This is licensed by three independent findings above: (1) 0.90 has no external
precedent at this scale (Section C); (2) the field's own standard for "beat popularity" is degree-stratified
comparison, not absolute-recovery threshold (Section C); (3) this substrate's own pre-registered 7-arm harness
already computes `BASELINE_POP` vs `ONESHOT_ROTATE`/`REPLAY_CONSOLIDATED` directly — the oracle gate was an
ADDITIONAL, stricter precondition layered on top of the actual question, not the question itself.

**Fair, achievable win bar (replacing the oracle-fire gate):** geometry beats POP by `>= POP_GAP` (0.03
absolute Hits@10, already pre-registered) on the aggregate genuine-L2 stratum, **and specifically on the
LOW/MID-degree tertiles** where POP is weakest and most beatable (per the `a46eadfa` reference VET: POP scores
0.412 at HIGH degree vs only a fraction of that at LOW/MID — the low-degree arena is where a real structural
win is both most valuable and most plausible, exactly where frequency has the least signal to exploit).

**Guarding against a low-degree win being fit-noise, not a real effect — four checks, three already
pre-registered plus one new one this drill adds:**
1. Seed-flip stability: CV of the winning arm's Hits@10 across 3 seeds `< 0.15` (already a director watch-item).
2. `SCRAMBLE_REPLAY` (relation labels shuffled) must not beat the winning arm by more than `SCRAMBLE_EPS`
   (0.03) — already pre-registered.
3. Both backdoor correlations (`cross_channel_geom_vs_poprank_r`, `backdoor_coord_precision_vs_degree_r`)
   `< 0.20` — already pre-registered.
4. **NEW (this drill): stratify the win by RELATION TYPE (SYNONYM/symmetric vs IS_A/hierarchical vs other),
   not just by degree.** Given Section A's finding that additive-TransE-style fits can produce degenerate
   near-coincidence collapses specifically on symmetric relations, a "low-degree win" that turns out to be
   concentrated entirely in the SYNONYM-collapse regime would be riding a functional-form artifact, not a
   genuine relational-inference signal — this check did not exist in any of today's three sibling notes and
   should be added to the decisive cell's reporting (not necessarily a new gate threshold yet — report the
   per-relation-type breakdown first, decide a gate only once the shape of the data is seen).

---

## Cheap decisive test

**Before the next 3-seed CSKG run:** swap the fit function only (leave every other pre-registered gate,
stratification, and control untouched) from `fit_transe_coords`/`fit_kge_anchor1` (additive Euclidean,
`X_h+D_r-X_t`) to a genuinely rotation-native fit computed directly on FHRR complex phasors (reusing the
PP-275 bind primitive's construction: entities as complex vectors, relations as unit-modulus rotations, loss
computed as complex-domain distance, NOT a real-coordinate surrogate later re-encoded through an FPE kernel),
keeping the Anchor-1 training-recipe trio (CE self-adversarial + N3 + reciprocal + minibatch) and the
LR/epoch corrections from the sibling note's Branch-3 ranking. Run the ORACLE_TRANSDUCTIVE arm first, as a
single-seed preview, at the SAME capacity as the ladder's `L5` rung.

**HARD-PASS (functional-form hypothesis confirmed as a material contributor):** `oracle_direct`-equivalent
(now computed natively in complex space, no separate kernel readout needed) clears a meaningfully higher
Hits@10 than the additive-fit `L5` result (0.424) at the SAME capacity/recipe — a relative improvement
`>= 20%` would be a strong, cheap, single-seed signal the functional-form fix is real and worth the full 3-seed
run. Report per-relation-type (SYNONYM vs IS_A vs other) breakdown alongside — expect the improvement to be
concentrated specifically on SYNONYM/symmetric edges if the mechanism story (Section A) is correct.

**HARD-FAIL (functional form was not the dominant lever — recipe/capacity was closer to the true bottleneck):**
the rotation-native fit does not clear `L5`'s 0.424 by more than a training-noise margin (`<5%` relative). This
would mean the additive-vs-rotational distinction, despite the strong theoretical motivation, is not the
dominant contributor to `LADDER_FIT_LIMITED` — escalate back to the sibling note's Branch-3 recipe ladder
(more epochs, LR correction, larger n_neg) as the primary remaining lever, and treat the functional-form
hypothesis as informative-but-refuted for THIS specific graph/scale, not abandon the broader glass-box
translation program (ComplEx and NBFNet-style path-analogs remain untested).

**Must-fail control:** run the SAME rotation-native swap on `BASELINE_POP`'s own construction (i.e. confirm
POP's score, which needs no fit at all, is unchanged) — this is automatic (POP is fit-independent) and serves
as the sanity check that any observed improvement is genuinely coming from the fit-function swap, not from an
unrelated harness change.

---

## Falsifiable predictions (full corrected-decisive-experiment design)

**HARD-PASS (the corrected decisive 3-seed re-run, reusing the existing 7-arm harness verbatim, all of):**
1. `ONESHOT_ROTATE`/`REPLAY_CONSOLIDATED` (rotation-native fit) beats `BASELINE_POP` by `>= POP_GAP` (0.03) on
   aggregate genuine-L2 Hits@10, AND on the LOW and MID-degree tertiles specifically (not just aggregate or
   HIGH, where POP is hardest to beat and least informative for the "does structure help where frequency has
   no signal" question).
2. Seed-flip CV `< 0.15` across seeds {7,17,23}.
3. `SCRAMBLE_REPLAY` does not beat the winning arm by more than `SCRAMBLE_EPS` (0.03).
4. Both backdoor correlations `< 0.20`.
5. **NEW:** the per-relation-type breakdown (SYNONYM/IS_A/other) does not show the win concentrated
   >80% in a single relation type in a way inconsistent with genuine multi-relation structural inference (a
   soft, reported-not-yet-gated check per Section F).
6. The oracle-transductive number and realized/ceiling ratio are reported as CONTEXT, not as a precondition
   that must clear 0.90 before the above four criteria are even evaluated.
7. Any product/external framing of the result is paired with the calibration caveat from the sibling note
   (our absolute numbers, whatever they land at, sit in a TransE-tier-comparable band for a HARDER 2-hop task
   on a comparably-dense graph — never framed as "SOTA" or compared unqualified to easier 1-hop benchmark
   numbers).

**HARD-FAIL (any one falsifies "geometry realizes information frequency does not," even under the corrected
functional form and reframed gate):**
1. The rotation-native fit, after the recipe corrections, still does not beat `TIE_EPS` (0.02) over
   `BASELINE_POP` on aggregate — this would be the first time this substrate could ask the reasoning question
   under a THEORETICALLY well-motivated functional form and get a clean negative; still the single most
   valuable possible outcome (closes the question on solid ground rather than an artifact-confounded one).
2. Seed-flip CV `>= 0.15` — do not report a headline win off an unstable result.
3. `SCRAMBLE_REPLAY` ties or beats the winning arm.
4. Either backdoor correlation fires `>= 0.20` — matches the exact already-landed failure shape
   (`grounding_additive_geometric_degree_control_v1`, `HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT`).
5. The rotation-native fit ALSO fails to clear the ladder's `L5` capacity meaningfully (i.e. the functional-form
   fix does not even improve the FIT itself, only the reasoning-gate framing) — this would escalate the
   question beyond functional form into a genuine representational-capacity ceiling at CSKG's scale, per the
   sibling note's own Branch-3 escalation trigger.

**P_deflated summary:**
- Rotation-native fit meaningfully improves the raw fit over additive-TransE at matched capacity/recipe:
  **P=0.50** (capped; strong theoretical motivation from well-established external theorems, but no direct
  on-substrate ablation yet — this is exactly what the cheap decisive test above is designed to check first).
- Given the fit improves, geometry then beats POP on the LOW/MID-degree genuine-L2 stratum specifically:
  **P=0.30-0.35** (inherits and is capped by the pre-existing "geom vs frequency" uncertainty this program has
  carried since the map-builder design note — a better fit removes one confound but does not by itself
  guarantee the reasoning question resolves positively).
- The modulus/phase-split refinement (Section A's second-order hierarchy-interference lever) is needed as a
  FURTHER fix beyond plain rotation: **P=0.30** (newer-ground, thin direct precedent, sequence AFTER the
  primary functional-form test, not before).

---

## Anchor candidate (inline pointer, no separate routing file per USER-locked no-routing-files discipline)

**Anchor candidate — `rotation_native_cskg_fit_v1` (supersedes a plain re-run of the additive-TransE ladder at
higher capacity):** Anchor pointer: Section "Cheap decisive test" above + PP-275's own construction
(`substrate_capability_map.md` row PP-275, `lap3_rotate_analogy_cpu_v1` source if still on disk, else
reconstruct from its cap_map description: FHRR-binding = RotatE relation embeddings) + the existing decisive
cell's full 7-arm/gate/stratification harness (reuse verbatim, swap only the fit function per Section D/E).
Substrate-product reading: single-seed preview first (ORACLE_TRANSDUCTIVE arm only, at `L5`-equivalent
capacity) per the Cheap decisive test's own HARD-PASS/HARD-FAIL bands; if it clears the `>=20%` relative bar,
proceed to the full corrected 3-seed decisive re-run under the REFRAMED gate (Section F: drop 0.90 oracle
precondition, gate on `POP_GAP` at LOW/MID degree strata instead, with all four fairness checks including the
new relation-type stratification). Tier hint: remote_cpu_queue (matches existing ladder/decisive cell compute
class), no local execution. Cost: comparable to one ladder rung for the preview, comparable to the decisive
cell's own `elapsed_s` x3 seeds for the full re-run.

This is a recommendation, not a design order — exp_dev retains full autonomy over exact cell-code diffs,
compute routing, and sequencing relative to other in-flight work, per this substrate's standing
no-experiment-design-in-prompts discipline.

---

## Cross-thread synthesis

- Directly complements, does not duplicate, `notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md`
  (training-recipe deltas, Ruffinelli track record, LR/epoch findings — reused verbatim here as Section B) and
  `notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md` (the ladder's own Branch-3
  escalation trigger explicitly flagged "functional form, not recipe" as the likely explanation if a strengthened
  recipe still fails to fire the transductive oracle — **this note supplies the specific, citation-backed
  functional-form diagnosis and fix that note's Branch-3 escalation trigger called for but did not yet name**).
- The single most load-bearing NEW fact this drill adds beyond both same-day notes: **the operator-gap finding**
  (Section D) — that this substrate already has a validated, landed, genuinely rotation-native FHRR-bind
  primitive (PP-275) that the CSKG course-C cells simply never call, using an additive-fit-plus-kernel-readout
  construction instead that only superficially resembles RotatE.
- The reframe (Section F) is a direct, actionable correction to the decisive cell's own pre-registered gate
  (`ORACLE_FIRE_MARGIN=0.90`), backed by external literature showing that threshold has no precedent at this
  scale and that the field's actual "beat popularity" standard (degree-stratified comparison) is both lower and
  more measurable than what the cell currently requires as a precondition.

## Substrate-product implications

- **The honest, defensible product claim, once this fix is tried:** "we identified, via literature-grounded
  expressiveness theory, exactly which functional form our reasoning engine's relation-representation should
  use for a graph with this relation-type mix, found we were not yet using it despite already having validated
  the correct primitive elsewhere in the system, and are now testing the corrected construction under the
  field's own standard for 'beats frequency' (degree-stratified comparison) rather than an internal threshold
  with no external precedent." This is a stronger, more specific, more auditable story than "the fit needs
  more training" — it identifies a structural reason, not just a resource shortfall.
- **This changes almost nothing about compute cost or timeline** — the fix is a fit-function swap reusing an
  already-built, already-validated primitive (PP-275), not new infrastructure; the training-recipe work already
  scoped in the sibling note transfers directly onto the corrected fit.
- **The reframe (drop 0.90-gate, measure geom-vs-POP directly) is itself a durable process fix**, independent
  of whether the functional-form swap succeeds: any future capacity-ladder or decisive cell that gates a
  reasoning claim behind an absolute-recovery threshold should first check that threshold against real external
  precedent at comparable scale, per this cycle's Fix-28-adjacent discipline (verify the BAR is real, not just
  the data).

---

## Citations (verified count)

**On-disk, read in full this cycle:** `experiments/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py`
(fit_transe_coords, fit_transe_replay, make_fpe_basis, fpe_encode, fpe_kernel_scores, fit_discrete_bind — full
function bodies); `experiments/_kge_anchor1_fit.py` (fit_kge_anchor1, full body); `data/exp_course_c_oracle_capacity_ladder_v1/metrics.json`
(full, landed `LADDER_FIT_LIMITED` this cycle, all 6 ladder rungs); `notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md`;
`notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md`; `notes/the_last_piece_intuitive_reasoning_vs_frequency_courses_2026-07-10.md`;
`notes/substrate_capability_map.md` (PP-275 row, `lap3_rotate_analogy_cpu_v1`).

**External literature, this cycle (2 parallel Sonnet lit-scans, generic ML terms only, no substrate-novel
names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]], deduplicated against the
40 sources already cited in today's sibling note where overlapping):**

Sun, Deng, Nie, Tang (2019), "RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space," ICLR,
arXiv:1902.10197 (Table 1 read directly). Wang, Zhang, Feng, Chen (2014), "Knowledge Graph Embedding by
Translating on Hyperplanes" (TransH), AAAI. Trouillon et al. (2016/2017), "Complex Embeddings for Simple Link
Prediction" (ComplEx), ICML/JMLR, arXiv:1606.06357. Kazemi & Poole (2018), "SimplE Embedding for Link
Prediction in Knowledge Graphs," NeurIPS, arXiv:1802.04868. Zhu, Zhang, Xhonneux, Tang (2021), "Neural
Bellman-Ford Networks" (NBFNet), NeurIPS, arXiv:2106.06935. "On the Expressive Power of KGE Methods,"
arXiv:2407.16326. Hierarchy-aware RotatE follow-ups (HAKE-family / SHKE), arXiv:1911.09419 + ScienceDirect
SHKE. "Knowledge Graph Embeddings: A Comprehensive Survey on Capturing Relation Properties," arXiv:2410.14733.
Li et al. (2016), "Commonsense Knowledge Base Completion," ACL (CN-100k/82k origin). Malaviya, Bhagavatula,
Bosselut, Choi (2020), AAAI, arXiv:1910.02915 (ConceptNet/ATOMIC completion). Wang et al. (2021), IJCNN,
arXiv:2009.09263 (inductive CSKG completion baselines). Mohamed, Nováček et al. (2020), "Popularity-Agnostic
Evaluation of Knowledge Graph Embeddings," UAI, PMLR v124. Shomer, Jin, Wang, Guo, Tang (2023), "Toward Degree
Bias in Embedding-Based Knowledge Graph Completion," WWW, arXiv:2302.05044. Fisher/Bhardwaj et al., "Adversarial
Learning for Debiasing Knowledge Graph Embeddings," arXiv:2006.16309. bioRxiv 2025.01.23.634511 (data-leakage
benchmarking, biomedical KGE). Toutanova & Chen (2015) and Dettmers et al. (2018, ConvE) (WN18RR/FB15k-237
de-leaking origin, standard well-established reference).

**Total: 7 on-disk sources read in full this cycle + 20 external sources across 2 lit-scans = 27 verified
checks.**

---

## Intuitive summary

Other teams beat "just guess the popular answer" using a specific trick: instead of representing relationships
as simple ADDITION (walk from A in a fixed direction to reach B), the best methods represent them as ROTATION
(spin A by a fixed amount to reach B). That distinction turns out to matter enormously for exactly the kind of
facts we have most of: "these two words mean the same thing" (a symmetric fact — addition literally cannot
represent this without collapsing both words into the same point) and "this is a kind of that" (a one-to-many
fact — addition forces every "kind of X" to collapse toward the same point too, when there are many). Both
failure modes are mathematically proven, not just observed — a well-known theorem, not a training artifact.

The good news, found by actually reading our own code this cycle: **we already built the correct fix elsewhere
in the system and validated it working well (a rotation-based binding that scored 90% on a similar task) — we
just aren't using that version on this specific dataset.** The version we're using here quietly reverts to the
addition-based approach underneath, even though a rotation-flavored "reader" sits on top of it — like buying a
good camera lens but leaving the cheap sensor in the body. The fix is to plug in the good sensor: swap the
underlying math for the rotation-based version we already proved works, on this same data, keeping everything
else (the fair-test safeguards, the training improvements we found this week) exactly as they are.

Also found: our internal bar for "did the fit even work" (90% correct on nearly the first try, given every
advantage) was set far above what any published result in this entire research field has ever achieved on a
similarly-sized graph, even after decades of tuning. That's not a fair target — it's like grading a first
attempt against the current world record. We're recommending a much fairer, still-honest target: does the
smarter, geometry-based approach beat the dumb "guess the popular answer" approach on the questions where
frequency genuinely has nothing useful to say (the rare, unusual facts) — which is both the actual prize we
originally set out to win, and the standard the rest of the field itself uses to judge these systems.
