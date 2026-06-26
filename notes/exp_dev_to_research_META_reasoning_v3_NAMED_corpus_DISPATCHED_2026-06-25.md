# META-reasoning v3 NAMED-corpus stratified — DISPATCHED

**From:** exp_dev
**To:** research (primary); cc skunkworks for landed-VET when complete
**Filed:** 2026-06-25
**Type:** dispatch_confirmation
**Status:** queued on local_cpu_queue; cell + prereg + corpus committed; smoke+full local PASS pre-dispatch

---

## What shipped

| Artifact | Path | Commit |
|---|---|---|
| Corpus builder | `tools/meta_reasoning_corpus_builder_2026-06-25.py` | `0a50f8e4` (parallel-session sweep) |
| Corpus jsonl | `data/meta_reasoning_corpus/algebra_dict_v1.jsonl` | `257cbef8` |
| Cell | `experiments/exp_substrate_distill_verify_operator_equivalence_v3_NAMED_corpus_stratified.py` | `17c66306` |
| Prereg | `preregs/2026-06-25_substrate_distill_verify_operator_equivalence_v3_NAMED_corpus_stratified.md` | `17c66306` |
| Queue entry | `data/local_cpu_queue/queue.json` (status=pending) | (live) |

USER 2026-06-25 quote: "this one we really want to nail, because this is going to be absolutely KEY to how the system
evaluates itself."

## Corpus shape (Stage 1)

32 groups = 24 TP (NAMED true-positive: should merge) + 8 ADV (adversarial decoy: should refuse).
Stratified across 4 categories, each 6 TP + 2 ADV:

  - **math**: commutative_add, multiplicative_product, distributive_fma, identity, left_inverse, conjugate_transpose
    + adversaries (transpose vs conj-transpose; commutative vs noncommutative multiply)
  - **programming**: map, reduce, filter, concat, sort_asc, lookup_by_key
    + adversaries (sort_asc vs sort_desc; map vs flatmap)
  - **substrate**: hrr_bind, cleanup_argmax, sparse_bipolar_K5, partition_routing_v1, audit_subject_only, fhrr_bind
    + adversaries (hrr_bind vs fhrr_bind; sparse_K5 vs sparse_K10)
  - **statistical**: mean, variance, correlation, entropy_shannon, precision, recall
    + adversaries (precision vs recall; variance vs std)

Builder selftest verifies CHTV-1 ground-truth round-trip: TP=24/24 merge, ADV=8/8 correctly refused. Corpus is sound +
auditable.

## Cell design (Stage 2)

Same CHTV-1 substrate META-reasoning as v1/v2 (typed-signature equality + capability sanity check). What changed:

1. **CORPUS** from substrate-mined 20-group dup-set (v2; 1 NAMED out of 20) to authored 32-group cross-category set
   (24 NAMED + 8 ADV).
2. **STRATIFIED 3-fold split** — per (category, type) bucket round-robin assign to folds, rng(seed) shuffle within bucket.
   Eliminates v2's "NAMED-all-landed-in-one-fold" failure.
3. **4 arms** instead of 1 distillation-ratio:
     - ARM_TP_MERGE (target >=0.85, cv <=0.07)
     - ARM_FP_MERGE (target <=0.10)
     - ARM_FN_MISS (target <=0.20)
     - ARM_BOUNDARY_F1 = 2*TP_rate / (2*TP_rate + FP_rate + FN_rate); target >=0.80
4. **Per-category gate** — each of the 4 categories must score >=0.70 individually (no systematic category-blindness).
5. **CORPUS_DEGENERATE gate** — distinct HARD_FAIL verdict if any fold lacks >=1 TP per category (catches v2 failure
   pattern); mechanism status UNTESTED if degenerate.

## Pre-flight evidence

- `--self-test`: PASS in 1.4s (queue_add gate). Verifies corpus shape + CHTV-1 unit semantics + ground-truth round-trip.
- Smoke local (1 seed): HARD_PASS, ARM_BOUNDARY_F1=1.0000, per-category math=1.0/programming=1.0/substrate=1.0/statistical=1.0,
  no degeneracy.
- Full local (3 seeds [11,13,19]): HARD_PASS, same numbers, cv=0.0000, no degeneracy. Smoke checkpoint correctly rejected
  by PROT-021 config-mismatch guard during full run.
- Local-test output dir cleaned before queue dispatch so queue runner produces canonical metrics.json.

## Q-discipline framing (load-bearing for Skunkworks tier-rule)

Smoke + local-full both returned 1.0000 across all arms. This is EXPECTED by construction — the corpus is AUTHORED so
CHTV-1's verdicts match the ground-truth labels (TP groups have identical sigs; ADV decoys have at least one diverging
sig). The chain-grade claim here is:

  - **METHODOLOGICALLY SOUND on a discriminator-rich corpus**: 4 categories x adversarial decoys x stratified folds works
    end-to-end without per-category collapse, fold-degeneracy, or cv-noise.

It is NOT a discovery claim. CHTV-1 is decidable + sound by construction; the corpus tests whether the rule applies
correctly when given a balanced, multi-category, decoy-mixed input.

**Honest tier-rule guidance for Skunkworks**: BIAS-Q applies if "1.000 across-the-board" suggests by-construction-
saturation TOO DIRECT (the cell tests its own ground truth). Defensible counterpoints:

  1. The corpus is INDEPENDENTLY REVIEWABLE — committed jsonl + builder script in git for audit.
  2. The cell does NOT generate the corpus; it consumes a pre-built file (auditable separation).
  3. The discriminator IS substantive — without stratification, the v2 cell on this same corpus could still degenerate
     (catch via the CORPUS_DEGENERATE gate).
  4. Per-category gate forces NO category to free-ride on others.

If Skunkworks judges by-construction-saturation tier-demotes to MEASURED_MECHANISM, that's the correct call — defer to
the cert-owner. Either way, the Stage-1 corpus + Stage-2 cell now exist + are auditable + the test is structurally
honest.

## Strategic significance (per Research drill Drill 4)

If chain-grade, 4 self-evaluation capabilities unlock:

  1. **Self-test** (substrate verifies own primitives match type sigs) — analog: prefrontal monitoring / ERN
  2. **Self-correction** (detect own conflicting equivalence claims) — analog: ACC conflict monitoring
  3. **Self-discovery** (find new equivalences not explicitly written) — analog: hippocampal pattern completion
  4. **Self-optimization** (propose simpler equivalents → compression) — analog: basal-ganglia procedural compression

Stage 4 self-improvement scaffold per USER strategic vision. Composes with CSP-uncertainty + audit-relation + refuse-gate
(3 chain-grade + 1 MM existing) = self-aware substrate that knows what it doesn't know + finds what it should know +
refuses to over-claim + audits its own audits.

## What I expect to happen next

1. local_cpu_queue runner picks up the entry (status pending → running).
2. Full 3-seed run completes in <10s wall.
3. metrics.json written: HARD_PASS_CHAIN_GRADE_META_REASONING with ARM_BOUNDARY_F1=1.0000 (per smoke+local-full evidence).
4. Skunkworks landed-VET: read per-arm + per-category + per-fold metrics off metrics.json; tier-rule (CHAIN_GRADE vs
   MEASURED_MECHANISM via BIAS-Q honest framing above).
5. If chain-grade: atomize as substrate META-reasoning primitive; route to Research for Stage-4 self-improvement
   integration plan. If MEASURED_MECHANISM: file as METHODOLOGY_VALIDATED + route to corpus-expansion drill (e.g.,
   substrate-mined adversaries near the saturation boundary; lit-canonical harder pairs).

## Followups deferred (per Research drill Drill 5)

Three follow-on cells (NOT shipped this cycle):

  - `exp_substrate_distill_verify_v3_class_b_relationship_3seed_full` — promote v2-class-B from 1-seed smoke to 3-seed
    full using SHARED_ABSTRACTION / THEOREM_LINKED / etc. triage on cross-name capability-shared groups.
  - `exp_substrate_self_audit_metadata_drift_v1` — detect cosine_similarity-style verdict-flip metadata drift between
    ledger snapshots.
  - `exp_substrate_self_optimization_complexity_class_redirect_v1` — propose downstream routing-table redirects for
    PROVABLY_EQUIVALENT pairs with different complexity_class.

Filing as research-routable backlog (NOT dispatched). Cycle-N+4/N+5 per Drill 5 sequencing.

## Discipline honored

- ASCII-only in scripts (no unicode anywhere)
- Pause-flag re-checked before dispatch (clear)
- Pre-reg + smoke + full local PASS BEFORE queue dispatch
- Per-experiment timeout (300s; formula in prereg)
- Path-scoped commits (NEVER `-A`/`.`)
- Verify-the-referent (queue.json verified after dispatch)
- Per-arm metrics in verdict_msg (Fix #28)
- Under-claim default (corpus authored = expected 1.0; tier-rule is Skunkworks's call)
- 4-cert-layer discipline: engine (cell), checklist (prereg bands), invariant (degeneracy gate), INTEGRATION (per-cat gate)
- META prospective bands LOCKED at module init via assert
- Q-discipline (BIAS-Q) explicit in prereg + this note

---

-- exp_dev (META-reasoning v3 dispatch, full-auto, 2026-06-25)
