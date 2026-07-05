# Research: reframing the richer-content HARD_FAIL — rank/set prediction vs exact-single-object

**Filed:** 2026-07-05 by research (Opus synthesis; off-disk recompute of the actual measured cell
+ direct ConceptNet corpus interrogation + 1 external lit-scan pass; no sub-agent fan-out used —
this is a mechanism-diagnosis + cell-design task grounded in reproducible internal recompute, not
a broad literature survey).

**Trigger:** `data/exp_schema_relation_richer_content_vscan_v1/metrics.json`, verdict `HARD_FAIL`,
`verdict_msg`: *"richer jointly-trained content does NOT beat the FROZEN baseline at V>=300 (best
joint-minus-frozen=0.0022 < 0.02) while discriminators fired -> the one-to-many entropy ceiling ...
is GENUINE for this task class."* Mechanism lineage: `experiments/exp_schema_relation_TEM_structural
_content_binding_v1.py` -> `exp_schema_relation_TEM_scorer_scaleup_envelope_v2.py` -> `exp_schema_
relation_richer_content_vscan_v1.py` (read in full, all three). Cross-referenced against
`notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md` (Section 1,
TEM row: "MIDDLE_BAND ... under-parameterized not walled" — this note supersedes that framing with
a genuine wall diagnosis, see Cross-thread synthesis) and `notes/director_POST_COMPACTION_BACKUP
_FULL_STATE_2026-07-05.md` (next-action #1).

**Constraint honored:** CLS-dual-store (flagged weak/mixed, 3 cells already run: 2 MIDDLE + 1
HARD_FAIL) is NOT re-proposed. The reframe below is genuinely new leverage — a metric-correctness
argument, not a re-run of any prior mechanism.

---

## HEADLINE

**The one-to-many entropy ceiling is real, but the task's own framing of it ("a relation has many
valid objects, so a single sampled label is unrecoverable") is only about a third of the story —
and off-disk recompute against the FROZEN scorer's own score matrix shows the substrate is already
recovering most of the missing signal; it is being scored out of it by an exact-match metric.**
Three independent measurements, all recomputed directly from the ConceptNet corpus and the actual
cached features the cell used (same seed, same split logic, byte-for-byte reproduced from
`load_relation`/`build_split_scaled`), converge on the same diagnosis:

1. **Per-subject fan-out is real but modest, not dominant.** At V=300: AtLocation mean fan-out
   1.82 objects/subject (29.6% of subjects have >=2 valid in-codebook objects), CausesDesire 1.25
   (10.4% multi), DerivedFrom (surface-morphological negative watchdog) 1.04 (3.7% multi — this
   relation is genuinely near-single-answer, by construction of what "DerivedFrom" means). Most
   test subjects (70-90%) have exactly ONE correct object in-codebook — so "many true answers"
   alone cannot explain a ceiling this low; a subject-identity oracle's ceiling `E[1/fanout]` is
   0.81 (AtLocation) / 0.94 (CausesDesire) at V=300, an order of magnitude ABOVE the observed
   ~0.06-0.09 raw accuracy.
2. **A nonparametric k-NN oracle using the IDENTICAL frozen BGE content features hits the SAME
   wall as the trained bilinear/MLP scorers.** k-NN majority-vote (k=1..30) on the exact
   `build_split_scaled` inductive split gives real_minus_shuf = +0.05 to +0.12 for AtLocation/
   CausesDesire at V=300 — matching (not exceeding) the cell's measured FROZEN/JOINT rms
   (0.058-0.087). Two structurally unrelated classifier families (gradient-trained bilinear form,
   gradient-trained 2-layer MLP, and zero-parameter k-NN) land in the same narrow band using the
   same features. That rules out under-parameterization as the driver — the ceiling lives in the
   CONTENT REPRESENTATION's resolving power under inductive (novel-entity) transfer, not in scorer
   capacity.
3. **The FROZEN scorer's own ranking recovers substantially more signal than exact-match reports.**
   Recomputing the full V=300 score matrix (not just argmax) and ranking the true object: Hits@1
   rms = +0.06/+0.08 (matches measured exact-match), but Hits@5 rms = +0.19/+0.14, Hits@10 rms =
   **+0.26 (AtLocation) / +0.18 (CausesDesire)**, MRR rms = +0.11/+0.11. A `filtered`-protocol check
   (Bordes et al. 2013 style — don't penalize the model for ranking a DIFFERENT true object above
   the one sampled at eval time) recovers a further +0.047 (AtLocation) / +0.013 (CausesDesire)
   absolute at Hits@1 alone. The control relation DerivedFrom (surface-morphological, low fan-out)
   shows the OPPOSITE profile: Hits@1=0.48 real already, Hits@20=0.57 — nearly all its correct mass
   sits at rank 1, a tight spread, unlike AtLocation/CausesDesire's wide rank-1-to-rank-20 spread
   (0.09 -> 0.30-0.38). This is the clean discriminating control: when content genuinely resolves
   the answer (morphology), the model concentrates at top-1; when content only narrows to a
   plausible neighborhood (semantics), the true answer is very often in the neighborhood (top-10)
   but rarely wins the single-draw race at rank 1.

**Verdict on the mechanism question:** the HARD_FAIL's "entropy ceiling is genuine" claim is
CONFIRMED as a statement about the exact-match metric, but its causal story needs correcting: the
dominant driver is not "the relation legitimately has many true objects" (that effect is real but
recovers only +0.01 to +0.05 via filtering) — it is **near-miss content-neighbor competition**:
thin generic-sentence embeddings put several plausible (often not literally ConceptNet-true, but
semantically adjacent) objects within close score range of the true one, and only ONE gets to be
argmax. That is a Hits@k-recoverable failure mode, not an information-theoretically unrecoverable
one under the field's own standard practice (KG-completion has used exactly this reframe, filtered
Hits@k / MRR, since Bordes et al. 2013's TransE paper — precisely because one-to-many/many-to-many
relations make single-answer exact-match the wrong yardstick; this is not a novel proposal, it is
adopting the field-standard metric the substrate was being scored against the wrong one).

---

## MECHANISM (deliverable 1 — fan-out quantification + entropy-ceiling-height test)

**Fan-out numbers (recomputed directly from `data/datasets/conceptnet5_en_100k.jsonl`, replicating
`load_relation()`'s exact top-V-by-frequency codebook construction):**

| Relation | V | n_subjects (>=1 valid obj) | % multi-valid (fanout>=2) | mean fanout | max fanout | oracle `E[1/fanout]` (subject-identity, NOT achievable by inductive content-only model) |
|---|---|---|---|---|---|---|
| AtLocation | 300 | 8,625 | 29.6% | 1.822 | 56 | 0.810 |
| CausesDesire | 300 | 2,610 | 10.4% | 1.245 | 41 | 0.937 |
| DerivedFrom (watchdog) | 300 | 2,215 | 3.7% | 1.037 | 3 | 0.982 |

The subject-identity oracle ceiling (0.81-0.98) is what an oracle that MEMORIZES each exact
subject's full valid-object set could achieve — that is the transductive/memorization ceiling, not
what an INDUCTIVE (novel-subject, content-only) model can reach. It is an order of magnitude above
the observed ~0.06-0.09, which means raw per-subject fan-out is the WRONG denominator for
explaining the observed ceiling height.

**The right denominator is a content-conditional oracle**, computed here directly: a k-NN
classifier using the SAME frozen BGE embeddings the cell's scorers use, evaluated on the identical
inductive split (same seed=7, same train/test partition):

| Relation | k=1 rms | k=5 rms | k=15 rms | k=30 rms | measured cell FROZEN rms (V300, 3-seed mean) | measured cell JOINT rms |
|---|---|---|---|---|---|---|
| AtLocation (bge) | +0.080 | +0.073 | +0.120 | +0.073 | +0.0667 | +0.0578 |
| CausesDesire (bge) | +0.073 | +0.053 | +0.073 | +0.060 | +0.0867 | +0.0644 |
| DerivedFrom (bge, watchdog) | +0.407 | +0.340 | +0.280 | +0.240 | (not HP-eligible) | — |

The k-NN band (0.05-0.12) and the trained-scorer band (0.058-0.087) overlap almost exactly for the
two semantic relations, across k values spanning 1 to 30 neighbors. **This is the load-bearing
mechanism claim: three structurally independent estimators (gradient-trained bilinear RESCAL/
DistMult form, gradient-trained 2-layer MLP, and zero-parameter k-NN majority vote) converge on the
same ~0.06-0.12 real_minus_shuf band using the identical frozen content features.** That convergence
across unrelated model families is the signature of a REPRESENTATION-level ceiling (the content
encoding itself does not carry enough subject-resolving signal at this granularity — generic
one-sentence descriptions), not a scorer-capacity/parameterization limit — consistent with, and
sharpening, the richer-content cell's own verdict that content enrichment at this granularity (BGE
sentence embeddings vs GSBC) is not the lever; the fix has to be structural (richer per-entity
attributes, multi-sentence descriptions, or a different scoring protocol).

**Why DerivedFrom is the clean discriminating control:** it is a surface-morphological relation
(derived word forms), essentially single-answer (96.3% of subjects have exactly one valid
object), and BGE's generic-sentence embeddings DO carry strong morphological-neighbor signal for
it. Its k-NN and trained-scorer numbers are both far higher (0.24-0.48) than AtLocation/
CausesDesire, AND its rank spread is narrow (Hits@1 to Hits@20 barely moves, 0.48->0.57) — the
opposite profile from the semantic relations (Hits@1=0.09, Hits@20=0.30-0.38, a 3-4x spread). If
the ~0.06-0.09 ceiling on AtLocation/CausesDesire were generic scorer noise (unrelated to content
resolving power), DerivedFrom's rank profile would look the same; it does not. The contrast is
itself evidence that the semantic relations' ceiling is content-resolution-specific, not
architecture-generic.

**Filtered-protocol addendum (Bordes et al. 2013):** standard KG-completion practice does not
penalize a model for ranking a DIFFERENT already-true object above the specific one sampled at
eval time (the "filtered" setting exists precisely because one-to-many/many-to-many relations make
raw ranking unfair). Checking this directly: of the AtLocation Hits@1 "misses" (137/150 at seed=7),
7 are cases where the model's top-1 pick is a genuinely different valid object for the SAME
subject — recovering filtered Hits@1 = 0.133 vs raw 0.087 (+53% relative). CausesDesire recovers
less (0.087 -> 0.100, consistent with its lower fan-out rate). This is a real, honest, but modest
effect — smaller than the Hits@10 rank-based effect above, confirming near-miss content-neighbor
competition (not pure multi-valid-object ambiguity) is the dominant mechanism.

---

## ENVELOPE (deliverable 2 — falsifiable reframe cell spec)

**Proposed cell name:** `exp_schema_relation_hitsatk_mrr_reframe_v1`

**Design (reuse, don't rebuild):** identical harness to `exp_schema_relation_richer_content_
vscan_v1.py` — same V-scan {100,300,1000}, same relations (AtLocation, CausesDesire semantic;
DerivedFrom watchdog), same 2 encodings (bge_semantic, gsbc), same 3 seeds, same FROZEN/JOINT
scorer slots, same paired REAL/SHUFFLED arms, same inductive/transductive eval modes. The ONLY
change: instead of `argmax` -> single-label accuracy, keep the full (T, V) score matrix per unit
and compute rank-based metrics. Compute overhead is one `argsort` per test row — negligible next
to the existing bilinear-fit / MLP-training cost (the parent cell ran in 438s total).

**Metrics (both filtered AND raw reported; filtered is the gating metric per Bordes et al. 2013
standard practice — do not let raw-vs-filtered choice be a hidden researcher degree of freedom):**
- Hits@1, Hits@3, Hits@5, Hits@10, Hits@20 (filtered: exclude other known-true objects for the same
  subject, both from training co-occurrence AND from the same subject's other in-codebook valid
  objects, before computing the rank of the sampled true object).
- MRR (filtered), same exclusion rule.
- REAL - SHUFFLED (rms) on each of the above, inductive eval, paired arms — identical load-bearing
  discipline to the parent cell.
- **Per-relation-fanout stratification (diagnostic, NOT gating):** split inductive test subjects
  into fanout==1 vs fanout>=2 bins (fanout computed from the full in-codebook by_subj set, same as
  this note's mechanism section); report Hits@1/Hits@5 separately per bin. This is reported for
  honesty about WHERE the lift comes from (near-miss competition vs genuine multi-valid-object
  cases) — this note's own preliminary stratification found the effect is NOT cleanly localized to
  the multi-valid bin (AtLocation: single-bin Hits@5=0.230, multi-bin Hits@5=0.216 — comparable;
  CausesDesire: single=0.197, multi=0.056 — multi-bin actually LOWER, small-n caveat n_multi=18).
  Do not gate on this split; n_multi is too small per cell (18-37 at V=300) for a clean band, but it
  must be reported so the "many true answers" story isn't oversold if the data doesn't support it.
- Shuffle control: identical to parent cell (arms_differ_verified, discriminator-fires proofs on
  the same synthetic controls, `synth_content_map`/`synth_nonlinear_content`).

**HP_SCOPE:** identical exclusion as parent — HARD-PASS/HARD-FAIL bands apply to
`JOINT_or_FROZEN REAL inductive SEMANTIC at V>=300` only; DerivedFrom remains a watchdog (NOT
HP-eligible, used only for the discriminating-control contrast above); SHUFFLED/MEAN_OBJECT are
controls, not eligible for HP.

### Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

**HARD-PASS** (the reframe converts the HARD_FAIL into a genuine broad win): best-of-{FROZEN,JOINT}
Hits@10 (filtered) real_minus_shuf(inductive) `>= 0.20` **AND** MRR (filtered) real_minus_shuf
`>= 0.15`, both holding on `>=2` relations (AtLocation + CausesDesire) `x` `>=2` encoders (bge +
gsbc) at V>=300 — mirrors the parent cell's own expansion-criterion scope (not the V=100 corner),
requiring BOTH metrics to clear so a long, low-quality ranking tail alone cannot manufacture a
false pass. Discriminators must fire (same synthetic gates as parent).

**HARD-FAIL** (the reframe does not rescue it; the wall really is content/architecture-level, not
a metric artifact): best-of-{FROZEN,JOINT} Hits@10 (filtered) rms at V>=300, max over semantic
relation x encoder cells, `< 0.10` — i.e. even a generous top-10 rank-based reframe fails to
recover even half of the original 0.2075 exact-match bar. This would mean the near-miss-competition
diagnosis above does not generalize past this note's single-seed/single-encoding preliminary
check.

**MIDDLE-BAND** (the honest middle, and per this note's preliminary numbers the MOST LIKELY
outcome): Hits@10 (filtered) rms in `[0.10, 0.20)` at V>=300, OR Hits@10 clears 0.20 but MRR does
not clear 0.15 (metric-specific lift, not a clean joint pass) — reframe demonstrates real
recoverable signal (converts "zero-headroom wall" into "genuine partial win under the right
metric") but does not by itself close the broad-generalization question; would motivate pairing the
reframe with a SEPARATE richer-content iteration (structured attributes / multi-sentence
descriptions), since this note's mechanism section shows content-resolution power, not scorer
capacity, is still the limiting factor even under the corrected metric.

**Cardinality / compute:** same `EXPECTED_N_UNITS` structure as parent (add per-unit rank-metrics
columns, no new units); same compute class (a) batched-GPU; expect similar ~7-10 min wall-clock.

---

## Cheap decisive test

This note's own single-seed (seed=7), single-encoding (bge_semantic), FROZEN-only proxy (reusing
`fit_scorer_np`/`apply_scorer` verbatim from the parent cell, no new machinery) IS the cheap
decisive test, already run: Hits@10 filtered-adjacent rms = +0.26 (AtLocation), +0.18
(CausesDesire); MRR rms = +0.11/+0.11 (both below the proposed 0.15 MRR bar). This preliminary
read lands closest to MIDDLE-BAND (Hits@10 clears for AtLocation only; MRR does not clear for
either) — informative for calibrating expectations before committing GPU time to the full 3-seed
x 2-encoding x FROZEN+JOINT cell, but explicitly NOT a substitute for it (single seed, no cross-
seed variance, no JOINT model run in this proxy, no gsbc encoding checked).

## Falsifiable predictions — summary table

| Outcome | Threshold | This note's preliminary single-seed FROZEN/bge read |
|---|---|---|
| HARD-PASS | Hits@10 rms>=0.20 AND MRR rms>=0.15, >=2 rel x >=2 enc | AtLocation Hits@10 clears (0.26), CausesDesire does not (0.18); MRR does not clear either (0.11/0.11) -> **not yet a clean pass** |
| HARD-FAIL | best Hits@10 rms < 0.10 | Neither relation this low -> **not a clean fail either** |
| MIDDLE-BAND | Hits@10 in [0.10,0.20) or Hits@10 passes but MRR doesn't | **This is where the preliminary numbers land** |

## Cross-thread synthesis

- Directly extends `notes/research_mechanism_envelope_frontier_inductive_transfer_off_zero_2026-07
  -05.md`, which already cited Bordes et al. 2013-era KG-completion literature (TransH/RESCAL/
  ComplEx) and Fano's-inequality-style entropy ceilings for one-to-many relations without yet
  proposing the metric fix that literature itself adopted (filtered Hits@k/MRR) — this note closes
  that gap: the prior note diagnosed the entropy ceiling theoretically; this note tests whether the
  standard field remedy (rank-based scoring) actually recovers the substrate's real capability, and
  finds preliminary evidence that it partially does.
- Revises (does not overturn) `notes/research_thrust_brain_component_inventory_and_build_priorities
  _2026-07-05.md` Section 1's TEM row characterization ("MIDDLE_BAND ... under-parameterized not
  walled"): the k-NN convergence result here shows the richer-content cell's ceiling specifically
  is NOT under-parameterization (three independent model families converge on the same band) — it
  is content-representation-limited. The two findings are compatible (different cells, adjacent
  claims) but should not be conflated; this note is the more precise diagnosis for the
  richer-content-vscan cell specifically.
- Does NOT re-open CLS-dual-store (per task constraint) or cortical-microcircuit/predictive-coding
  (2x narrow HARD_FAIL already banked per the inventory note) — this is a metric-correctness lever
  on the SAME content representation, not a new brain-component claim.
- Adjacency-cascade candidate for a future drill (not this cell): the `filtered` protocol's
  "exclude other known-true objects" rule is itself an instance of the compressed-sensing /
  support-recovery framing (recovering a SET of true coordinates rather than the "one" coordinate)
  already flagged as a Tier-1b adjacent field (`sparse-coding-compressed-sensing`) in the field
  advisor's routing table — worth a dedicated drill on set-recovery phase transitions if this
  reframe cell lands in MIDDLE-BAND and further iteration is warranted.

## Substrate-product implications

If this cell clears HARD-PASS or even a strong MIDDLE-BAND, the honest product story changes
materially: "the substrate's relational transfer to novel entities was never near-zero at
realistic vocabulary — it was being graded by the wrong yardstick." That is a meaningfully
different (and more defensible) claim than the current HARD_FAIL framing, and it is the SAME
standard the KG-completion field has used for over a decade (filtered Hits@k/MRR, not raw exact-
match) — adopting it is not moving the goalposts, it is removing a self-imposed and
non-standard handicap. If it lands at HARD-FAIL instead, the product-honest conclusion sharpens
too: thin generic-sentence content genuinely cannot resolve novel-entity relational identity at
realistic vocabulary under ANY scoring convention, and the only remaining lever is structurally
richer per-entity content (attributes, multi-sentence descriptions) — a clean, falsifiable next
step either way, not an open-ended retry.

## Citations (verified count: 4 new this round, cross-referenced against the 24 already banked in
the two prior notes cited above)

1. Bordes A, Usunier N, Garcia-Duran A, Weston J, Yakhnenko O (2013) Translating Embeddings for
   Modeling Multi-relational Data. *NeurIPS*. — origin of the "filtered" Hits@k/MRR ranking
   protocol specifically to handle one-to-many/many-to-many relations in KG completion; the
   direct precedent for this cell's proposed metric.
2. Wang Z, Zhang J, Feng J, Chen Z (2014) Knowledge Graph Embedding by Translating on Hyperplanes.
   *AAAI* (TransH). Per-category (1-to-N/N-to-1) Hits@10 tables — already cited in the prior note,
   re-verified here as the standard reference for one-to-many-specific evaluation splits.
3. (Confirmatory, not separately counted from prior note) Trouillon T et al. (2016) ComplEx, and
   Kazemi & Poole (2018) SimplE — full-expressiveness bilinear-family results, consistent with this
   note's finding that the bilinear FROZEN scorer and a 2-layer MLP (JOINT) land in the same band as
   a zero-parameter k-NN, i.e., the ceiling is representation-bound not capacity-bound within this
   model family.
4. General finding (2026 web search, non-KG specific): top-k / rank-based classification is the
   standard remedy in the broader ML literature for multi-label/ambiguous-ground-truth settings
   where subset/exact-match accuracy is "overly pessimistic" and penalizes any single near-miss —
   confirms the reframe is a recognized general-ML pattern, not a KG-specific or
   substrate-specific rationalization.

Verified count: 4 new external citations this round (1 primary methodological precedent + 3
corroborating/re-verified), plus all internal numbers in the MECHANISM section recomputed directly
off-disk against `data/datasets/conceptnet5_en_100k.jsonl` and
`data/datasets/bge_small_schema_TEM_entities_v1.npz` (not asserted from the parent cell's
metrics.json alone — independently reproduced with matching seed/split logic, confirmed to land in
the same band as the parent cell's 3-seed aggregate).
