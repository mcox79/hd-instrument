# Pre-registration: substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus

**Date:** 2026-06-25
**Anchor:** substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus
**Queue:** local_cpu_queue
**Seeds:** [11, 13, 19] (cross-cell consistent)
**N_FOLDS:** 3 (stratified held-out cross-validation)
**Categories:** 3 (algorithms / learning / representation) -- not v3's 4
**Corpus:** `data/meta_reasoning_corpus/substrate_self_discovered_v1.jsonl` (28 groups; 15 TP + 13 ADV)
**Corpus builder:** `tools/meta_reasoning_self_discovered_corpus_builder_v1.py`

## Strategic motivation

USER 2026-06-25: "this one we really want to nail" -- META v4 chain-grade test must use
substrate's OWN atoms, not hand-authored ones. v3 (HARD_PASS at 1.000 cv=0.000 hand-authored
corpus) is expected to land MM under Skunkworks by-construction-saturation tiering (per
`notes/research_drill_MM_tier_promotion_paths_2026-06-25.md` Item 5). v4 closes the
discrimination gap by sourcing the corpus from substrate's own atoms.jsonl.

Per research drill `notes/research_distill_verify_META_reasoning_multi_drill_2026-06-25.md`:
substrate has 562 same-name dup-groups, 15 of which have >=2 typed-sig members (TP pool); plus
48 capabilities with >=3 distinct names, 13 of which yield genuine cross-name divergent-sig
groups after filtering bulk-tag noise (ADV pool). Total substrate-self-discovered corpus: 28
groups (15 TP + 13 ADV), meeting the drill's >=20 floor.

## Mechanism (IDENTICAL to v1/v2/v3)

`classify_pair(sigs, caps, allow_capability_fallback=False)` -- CHTV-1 typed-signature equality:

  - If >=2 members have signatures with >=3 typed fields AND all such signatures dict-equal: `PROVABLY_EQUIVALENT`
  - If signatures DIFFER on any field: `NOT_EQUIVALENT`
  - Otherwise: `UNDECIDABLE_BY_PROVER`
  - HELD-OUT mode (capability fallback DISABLED): no shortcut via shared `serves_capability`

The mechanism is SOUND BY CONSTRUCTION (type equality is decidable + correct). The v4 test:
does the rule apply uniformly across a STRATIFIED held-out partition when the corpus is
SUBSTRATE-DISCOVERED rather than hand-authored.

## Corpus design (load-bearing change vs v3)

`data/meta_reasoning_corpus/substrate_self_discovered_v1.jsonl` assembled by
`tools/meta_reasoning_self_discovered_corpus_builder_v1.py`:

| Source | Type | Count | Example groups |
|---|---|---|---|
| same-name dup with >=2 typed members | TP | 15 | cosine_similarity (T1+T3), dijkstra (T1+T2), beam_search (T1+T2), astar (T2+T3), pca_whitening, zca_whitening, discriminative_perceptron, hmm_transition, ... |
| cap-shared cross-name with >=2 distinct-name typed members | ADV | 13 | cap_circular_convolution (circular_convolution + DFT), cap_fhrr_bind (FFT/circular/FHRR-bind), cap_cleanup (cleanup + Hopfield + SDM), cap_discriminative_perceptron (Adam + SGD + structured-perceptron), reinforcement_learning_family (MDP + policy_gradient + Q-learning), ... |
| **TOTAL** | | **28** | |

Each TP group: 2-4 same-named members at different tiers, all sharing IDENTICAL `algebra_dict`
on 5 SIG_FIELDS (domain, operation_type, signature_input_type, signature_output_type,
complexity_class). CHTV-1 is EXPECTED to merge them (PROVABLY_EQUIVALENT).

Each ADV group: 2-3 distinct-named members sharing a `serves_capability` tag but with at
least one SIG_FIELD divergence (different operation_type, etc.). CHTV-1 is EXPECTED to refuse
merge (NOT_EQUIVALENT or UNDECIDABLE_BY_PROVER).

Provenance: every group records `source` and `source_provenance.atom_ids[]` for audit.

## Categories (v4: 3, not v3's 4)

Substrate's own atoms do NOT yield uniform coverage across v3's math/programming/substrate/
statistical scheme (e.g., zero same-name-dup-typed HDC primitives because substrate's hdlab
primitives are mostly single-tier). v4 uses the empirically-balanced 3-category scheme:

| Category | TP | ADV | Domain examples |
|---|---|---|---|
| algorithms | 5 | 1 | graph_search, combinatorial_optimization, sequence_decoding, sequence_alignment |
| learning | 7 | 4 | machine_learning, probabilistic_reasoning, online_learning, RL, structured, HMM, quantum, neuroscience |
| representation | 3 | 8 | vector_similarity, linear_algebra_preprocessing, vector_symbolic_architectures, signal_processing |

ADV imbalance acknowledged: `algorithms` has only 1 ADV total. v4 RELAXES the v3 corpus-
degenerate gate to require only >=1 TP per category per fold (not >=1 ADV) because some
ADV-category-fold combos will have 0 ADV due to insufficient ADV pool size. TP-gate is
preserved -- TPs distribute >=1 per (cat, fold) via stratified round-robin.

## Stratification

`stratified_folds(groups, seed)`: per (category, group_type) bucket, shuffle with rng(seed),
round-robin assign to folds. Identical algorithm to v3. Per-seed permutation rotates which
fold is held-out; across 3 seeds, the 3 held-out subsets cover the corpus.

CORPUS-DEGENERATE gate: if any fold lacks >=1 TP from any category, `HARD_FAIL_CORPUS_DEGENERATE`
(distinct from `HARD_FAIL_META_REASONING_LIMITED`). ADV-missing-from-fold-category is NOT a
degenerate condition in v4 (relaxation vs v3).

## Arms (4 sub-experiments, same as v3)

For each fold-as-held-out (3 folds x 3 seeds = 9 fold runs):

  - **ARM_TP_MERGE**     = (# TP groups CHTV-1 returns PROVABLY_EQUIVALENT) / (# TP groups in held-out)
  - **ARM_FP_MERGE**     = (# ADV groups CHTV-1 returns PROVABLY_EQUIVALENT) / (# ADV groups in held-out)
  - **ARM_FN_MISS**      = (# TP groups CHTV-1 returns UNDECIDABLE_BY_PROVER or NOT_EQUIVALENT) / (# TP groups in held-out)
  - **ARM_BOUNDARY_F1**  = 2 * TP_rate / (2 * TP_rate + FP_rate + FN_rate)

Per-arm + per-category(3) + per-fold + per-seed metrics in verdict_msg (Fix #28: read per-arm not summary).

## PROSPECTIVE BANDS (LOCKED at module init via assert)

### HARD_PASS_CHAIN_GRADE_CONFIRMED_SELF_DISCOVERED
- ARM_TP_MERGE >= 0.75 AND cv across seeds <= 0.10
- ARM_FP_MERGE <= 0.15
- ARM_FN_MISS <= 0.25
- ARM_BOUNDARY_F1 >= 0.70
- EACH category (3) score >= 0.60 individually
- 3 seeds [11, 13, 19] AND 3 folds; corpus not degenerate

Lower bands than v3 (0.85/0.80/0.70/0.70) acknowledge the substrate-discovered corpus is
expected to be noisier than the hand-authored one per task brief.

### HARD_PASS_PARTIAL (= MIDDLE_BAND upper)
- ARM_BOUNDARY_F1 in [0.55, 0.70)

### MIDDLE_BAND
- ARM_BOUNDARY_F1 in [0.40, 0.55)

### HARD_FAIL_META_REASONING_LIMITED
- ARM_BOUNDARY_F1 < 0.40 -- substrate's self-discovered equivalences not recoverable via
  CHTV-1; would suggest substrate's typed-sig metadata is too sparse for self-evaluation;
  mechanism is sound (per v1/v2/v3-overmerge controls) but atom-authoring discipline needs
  enrichment before CHTV-1 self-verification is chain-grade.

### HARD_FAIL_CORPUS_DEGENERATE
- Any fold lacks >=1 TP per category; mechanism status UNTESTED.

## Q-discipline guards (load-bearing for honest tier ruling)

**Per task brief: if ARM_TP_MERGE = 1.000 cv = 0.000 (same as v3) -> flag corpus may STILL be
by-construction.** The cell ships with `_q_discipline_flag()` that fires when arms hit
IDENTICAL_TO_V3 saturation (TP >= 0.995, cv <= 0.005, FP <= 0.005, F1 >= 0.995) and surfaces
the flag in verdict_msg. Skunkworks tiers.

Local smoke (seed=11, 1 seed) HARD_PASSed with arms at 1.000 cv=0.000 and the Q_DISCIPLINE_FLAG
fired. **Honest pre-reg statement:** there is a real possibility the substrate's same-name
dup-groups (TP source) ARE by-construction-saturable because the authors who created the
T1+T2+T3 tier-versions of the same primitive applied the same algebra_dict to both versions
at authoring time -- so substrate's curation discipline pre-resolved equivalence for those
15 groups. If that's the case, the substrate-discovered corpus has the same by-construction
characteristic as v3's hand-authored corpus, and v4 chain-grade would still be MM-eligible
under Skunkworks tiering.

**What v4 DOES test, even if same-name-dup TPs are by-construction:**
- The 13 ADV groups are GENUINE cross-capability adversaries -- distinct authors (different
  primitive families serving overlapping caps) and divergent typed-sigs. ADV refusal at 13/13
  IS substrate-self-discovered chain-grade evidence.
- The 3-category gate (algorithms/learning/representation) verifies CHTV-1 transfers across
  substrate's actual domain landscape, not just one canonical mathematical category.
- The cell ships with provenance (`source_provenance.atom_ids[]`) so the corpus is
  independently auditable from substrate's own atoms.jsonl.

**If Skunkworks demotes to MM via by-construction-saturation tiering anyway:** v5 would
need to source TPs from a pool that did NOT have authored-equivalent-by-design atoms.
Candidates per drill: external lit-canonical operator pairs that substrate has not pre-tagged.

## Strategic significance

A v4 chain-grade-confirmed unlocks Stage 4 self-improvement scaffold (per
`research_distill_verify_META_reasoning_multi_drill_2026-06-25.md` Drill 4):

1. **Self-test** -- substrate verifies own primitive implementations match their type sigs
   (brain analog: prefrontal monitoring / ERN)
2. **Self-correction** -- substrate detects conflicting equivalence claims in own atoms
   (brain analog: ACC conflict monitoring)
3. **Self-discovery** -- substrate finds equivalences not explicitly written
   (brain analog: hippocampal pattern completion + neocortical semantic similarity)
4. **Self-optimization** -- substrate proposes simpler equivalents (compression via equivalence)
   (brain analog: basal-ganglia procedural-skill compression)

Composes with existing CSP-uncertainty + audit-relation + refuse-gate primitives ->
Stage 4 self-improvement scaffold per USER strategic vision.

## Smoke-vs-full discipline

Smoke (1 seed, seed=11) vs full (3 seeds [11,13,19]) match on:
  - Same corpus load (substrate_self_discovered_v1.jsonl)
  - Same N_FOLDS=3, same 3-category stratification
  - Same CHTV-1 classifier with capability-fallback DISABLED

Only difference: # seeds aggregated. No regime sign-flip possible. Smoke confirmed locally
2026-06-25 (HARD_PASS with arms at 1.000; Q_DISCIPLINE_FLAG fired transparently).

## Timeout estimate

Smoke wall (1 seed, 3 folds, 28 groups): ~0.01s CHTV-1 work + module-init overhead.
Full estimate: <5s (3 seeds x 3 folds x 28 groups + JSON IO + numpy import).
Formula: timeout_s = ceil(1.5 * 1 * 1^1.5 * 3) = ~5s; conservative cap **timeout_s = 300**
(5 min; accounts for runner infra + checkpoint IO + worst-case Python import time).

## PROT compliance

- PROT-018, 019, 020: do not apply (no LLM, no remote, no GPU; no n-suffix in anchor)
- PROT-021: timeout < 14400s; cell imports `_seed_checkpoint` + supplies
  `run_config={"N":0, "run_mode": RUN_MODE}` so smoke->full transition won't silently
  consume mismatched partials.

## Symmetric verify rails (anti-negativity-bias)

Verdict reports BOTH halves:
  - SOUND POSITIVE: ARM_TP_MERGE (does CHTV-1 merge true substrate-discovered equivalents?)
  - SOUND NEGATIVE: ARM_FP_MERGE (does CHTV-1 refuse substrate-discovered adversaries?)
  - CONSERVATIVE FAILURE: ARM_FN_MISS (does CHTV-1 over-refuse via UNDECIDABLE?)
  - BALANCED: ARM_BOUNDARY_F1 (composite F1)
  - PER-CATEGORY: 3 category-level scores prevent systemic category-blindness
  - PER-SEED: cv across 3 seeds reports fold-permutation invariance
  - DEGENERACY GATE: corpus-degenerate gate distinguishes mechanism-broken from corpus-broken
  - Q_DISCIPLINE_FLAG: surfaces if arms hit IDENTICAL_TO_V3 saturation (informational)

## Honest negatives possible

- Same-name dup-typed TPs may be by-construction-saturable (the curation authors applied the
  same algebra_dict to T1+T2+T3 versions of the same primitive at authoring). Skunkworks may
  demote-to-MM on Q_DISCIPLINE saturation flag; that's their call.
- 3-category scheme is v4-specific (vs v3's 4) -- not directly comparable to v3 per-category
  numbers; this is intentional given substrate's actual domain distribution.
- `algorithms` has only 1 ADV group; some folds will have 0 ADV in that category. v4 relaxes
  the v3 ADV-per-category-per-fold gate to accommodate this; Skunkworks may flag the
  ADV-pool-thinness as a corpus-richness limitation.

## Cross-cell discipline honored

- ASCII only (no unicode anywhere in cell or corpus)
- Substrate-only (no LLM forward calls; pure Python comparison + corpus JSON read)
- Per-arm + per-category + per-fold metrics in verdict_msg (Fix #28)
- Bands locked at module init via assert (CHECK at import time)
- Seeds [11, 13, 19] (cross-cell consistent)
- Self-test required: verifies >=20 substrate-discovered groups + CHTV-1 ground-truth round-trip
- Q-discipline guard fires when arms saturate identically to v3 (informational, transparent)

## Files committed (path-scoped commit before dispatch)

- `tools/meta_reasoning_self_discovered_corpus_builder_v1.py` (substrate atom scanner + corpus builder)
- `data/meta_reasoning_corpus/substrate_self_discovered_v1.jsonl` (the 28-group corpus; auditable)
- `experiments/exp_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.py` (the cell)
- `preregs/2026-06-25_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.md` (this prereq)
