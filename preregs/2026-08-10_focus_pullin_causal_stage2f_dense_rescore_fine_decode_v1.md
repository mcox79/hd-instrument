# Pre-reg: focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1

## Question
Stage-2E (MIDDLE_BAND, `data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json`)
SOLVED storage+skew (relevant_in_shortlist_rate=0.853 @ 1,213,912; max leaf occupancy 51,873 <
SAFE_LEAF_SIZE_SPARSE=57,000) but the FINE-DECODE step (DG-space `iterative_attractor` settle among the
~50-candidate DG-space shortlist, admission gated by DG-space cosine tau) only converts that 0.853
shortlist-hit into 0.213 final `relevant_recall` -- the answer is present but the crowded 2048-dim/2%-sparse
DG space cannot cleanly disambiguate it from the other ~49 candidates
(MEASURED@data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json:
per_scale.1213912.hierarchical_sparse: in_set_mean=0.205 vs out_set_mean=0.123, barely separated).
Does re-scoring the SAME (unchanged) DG-space shortlist in the DENSE, un-projected 1024-dim entity space
(E, i.i.d. random, never Hebbian-written, always available at full fidelity) recover
relevant_recall>=0.50 at BOTH 100K and 1,213,912 with scramble margin>=0.30 and false_pull_in<=0.20 at
both, without regressing Stage-2E's already-working 100K point (0.613)?

## Prior-work check (mandatory, USER-locked 2026-07-01)
`bash tools/substrate_query.sh` run this session. Top hit cosine=0.2979 (BELOW the 0.30 threshold) --
`coarse_to_fine_selective_depth_retrieval_..._JL_coarse_shortlist_..._dense_condenser_fine_read_...`
(cert_ledger). Conceptually adjacent (coarse-shortlist -> dense-fine-read two-stage pattern) but a
DIFFERENT substrate/mechanism entirely (JL random-projection over BGE-distilled codes at V=40000, not
KGStore/DG-CA3 hierarchical-shard triples). Below cosine=0.30 -- per rule this is NOT flagged as a
rediscovery; proceeding as genuinely novel within this substrate's KGStore/DG-CA3 lineage. No other hit
above 0.28.

## Mechanism (brain-fidelity framed)
DG/CA3 pattern-separated coarse retrieval narrows ~1.2M candidates to ~50 (hippocampal coarse recall --
UNCHANGED from Stage-2E, works: 0.853 shortlist-hit-rate). The brain does NOT then disambiguate among
those ~50 using the SAME lossy sparse code that did the coarse narrowing -- final identification recruits
neocortical reinstatement / pattern-completion against the FULL-fidelity item representation (hippocampal
index -> cortical content, per pattern-separation-then-pattern-completion two-stage retrieval theory).
Here: the query's dense (s,p) key `E[s]*R[p]*sqrt(N)` already exists (computed en route to the DG
projection, thrown away in Stage-2E); re-use it. A SECOND, per-shard dense Hebbian store
(`DenseShardStore`, already-built/certified Stage-2D infra, SAME hierarchical shard layout/routing as the
sparse store -- ZERO new routing/storage code) is ingested in the un-projected 1024-dim entity space.
At WRITE time this store has the identical crosstalk-capacity problem dense stores always have at this
scale (leaf-capacity-sweep MEASURED dense recall=0.000 at every point 57K-696K under FULL-VOCAB argmax --
this is why DG/sparse coding was adopted in Stage-2D in the first place, and this cell does NOT reopen
that). But the fine-decode READOUT here never does full-vocab argmax against the dense store -- it
compares the dense probe against ONLY the ~50 DG-shortlisted candidates' dense embeddings via cosine
similarity. SNR-vs-candidate-count is what fails at full-vocab (50K+ candidates) and may still succeed at
50 candidates, since dense-store noise variance is governed by write COUNT (unchanged either way) while
discriminability among a fixed small candidate set depends on comparison-set SIZE, not the store's
absolute SNR margin. This is the ONE thing this cell measures -- it does NOT assume the answer.

## Diagnose-first (mandatory, one variable, measured not hypothesized)
Before/alongside the fix, split Stage-2E's 0.853->0.213 loss (among relevant queries where the true
answer IS in the DG shortlist) into:
- WRONG_ARGMAX: DG-space `iterative_attractor` settles on a shortlist candidate != true answer
- CORRECT_REFUSED: settle picks the true answer, but its DG-space cosine score < tau (admission gate
  refuses)
- CORRECT_ADMITTED: settle picks the true answer AND score >= tau (the only case Stage-2E counted as
  `relevant_recall`)

Computed from the SAME per-query results the new eval function already produces for the reproduced
DG-decode path (no separate re-run) -- see `diagnose_split_dg_decode` field, at both scales.
HYPOTHESIZED (task prompt, pre-measurement): wrong-argmax dominates given Stage-2E's in_set_accept~0.89
(most in-shortlist relevant queries that ARE admitted, are admitted correctly at a HIGHER rate than the
0.213 recall suggests -- implying most of the loss is the settle never reaching the true candidate at
all, not refusing it after correctly reaching it). MEASURED value reported in the completion, not assumed.

## Compute architecture
- Storage/routing: BIT-IDENTICAL to Stage-2E (imported, not re-transcribed): `K_FAMILY`,
  `build_family_shard_layout`, `compute_ingest_shard_ids_real/scrambled`, `compute_query_shard_ids`,
  `_vectorized_entity_hash`, `SAFE_LEAF_SIZE_SPARSE`. The coarse DG-space shortlist retrieval
  (`store.probe_batch_in_shard` + top-k over `dg_val_codebook`) is ALSO bit-identical -- the ONE new
  variable is what happens AFTER the shortlist is formed.
- NEW: a second per-shard `DenseShardStore` (Stage-2D infra, unmodified class, imported not
  re-transcribed) ingested with the SAME shard labels as the sparse store (composed arm: real tier-2
  hash labels; scrambled arm: the tier-2-scrambled labels) -- this is a WRITE-SIDE-IDENTICAL companion
  store, not a new routing mechanism.
- NEW: `eval_gate_hierarchical_dense_rescore` computes, in ONE pass per (scale, arm): the DG-space
  shortlist (unchanged), the OLD DG-argmax decode + calibration (reproduces Stage-2E's own arm, used for
  the repro-check gate + diagnose split), AND the NEW dense-rescore decode + its own separately-calibrated
  admission gate (dense-space in-set/out-set scores are a DIFFERENT distribution than DG-space scores;
  reusing Stage-2E's DG-calibrated tau on dense scores would be a category error).
- Batched GPU: NOT used (CPU numpy/torch, matches Stage-2D/2E precedent) -- per-shard batched matmuls
  (dg_probe, dense_probe) are the expensive step and are already vectorized across the ~150 queries per
  shard per arm; wall-time is dominated by the O(n_edges) Hebbian ingest passes (both stores), not the
  eval loop. Estimated total wall <= ~700s (see Runtime estimate below); GPU-batching would not
  materially change this (CPU numpy matmuls of this size are not the bottleneck; disk I/O + Python loop
  overhead in the small per-query fine-decode step is). Sequential-CPU justified per exp_dev discipline
  clause (b): genuine sequential per-scale checkpoint dependency + inherited from certified Stage-2D/2E
  infra.
- Storage strategy: sharded (hierarchical, Stage-2E's tier-1 x tier-2 layout, unchanged) for BOTH the
  sparse coarse store and the new dense fine-rescore store.

## Runtime estimate (HYPOTHESIZED, from Stage-2E's measured per-arm ingest/eval times)
Stage-2E's sparse ingest at 1,213,912: composed=112.6s, scrambled=120.6s (dg_dim=2048).
DenseShardStore ingest is the SAME Hebbian-accumulate math at n_dim=1024 -- FLOP count scales with
n_dim^2 per edge, so THEORETICAL@ratio=(1024/2048)^2=0.25x sparse-ingest time: composed_dense~28s,
scrambled_dense~30s. Eval overhead for the extra dense rescore step is a vectorized [k_eff=50, 1024]
matvec per query (~150 queries/arm) -- negligible (<5s/arm). 100K scale scales down proportionally
(~1/12 of 1.2M's edge count). Total full run (both scales, both arms, sparse+dense ingest+eval, plus data
load ~90s per Stage-2E's own breakdown) HYPOTHESIZED ~500-600s. Smoke (100K only, real-data pipeline
check) HYPOTHESIZED ~40s.

## Discriminator-must-survive-scale (mandatory declaration)
Full-N smoke-at-1213912 (option A) is NOT used here to avoid ~330s of compute that would be fully
REDONE by --full's own 1213912 unit (checkpointed, inspected immediately upon landing). Instead this
cell uses a HYBRID of options B+C:
- (B) analytical: the crowded-shortlist disambiguation problem is DIMENSIONALITY-driven (DG=2048-dim/
  2%-sparse vs dense=1024-dim/100%-dense with a FIXED k_eff=50 comparison set), not sample-size driven --
  the mechanism this cell tests (compare probe against ~50 known candidates) does not get MORE crowded
  as N grows past the shortlist-formation step; only shortlist FORMATION (which stays unchanged from
  Stage-2E) is N-sensitive, and Stage-2E already proved that stays at 0.853 at 1.2M.
- (C) discriminator-preview substitute: `self_test()` runs the tiny BIGFAM/SMALLFAM synthetic corpus
  through BOTH the OLD DG-decode and NEW dense-rescore decode and asserts the dense-rescore mechanism
  activates (produces a genuinely different decode from DG-only, verified via `arms_differ` hash-diff)
  and degrades under scramble (mechanism sanity), at real-code-path (real `KGStore`/`SparseHeteroShardStore`/
  `DenseShardStore` objects, N=48 tiny).
- `--smoke` mode itself runs REAL CSKG data at scale=100,000 ONLY -- this is a RUN-SAFETY / pipeline-crash
  gate (does the real-data loader + real dense-ingest + real dense-rescore-eval pipeline run end-to-end
  without crashing, at a cheap scale), explicitly NOT a discriminator-preview (100K is not the crowded
  regime; Stage-2E's OLD decode already works fine at 100K, 0.613). The true discriminator evidence
  is measured directly by `--full`'s own 1,213,912 unit, inspected immediately upon landing
  (checkpointed, not blind-dispatched).

## HARD-PASS / HARD-FAIL bands (declared BEFORE running, per task contract)
- **HARD-PASS**: `relevant_recall` (dense-rescore path) >= 0.50 at BOTH 100,000 AND 1,213,912, AND
  scramble margin (`relevant_recall` composed - scrambled, dense-rescore path) >= 0.30 at both scales,
  AND `false_pull_in_rate` (dense-rescore path) <= 0.20 at both scales, AND no regression at 100K
  (composed dense-rescore recall @ 100K >= Stage-2E's landed composed recall @ 100K [0.6133] -
  NO_REGRESSION_TOLERANCE=0.05), AND `arms_differ_verified`, AND `cardinality_ok`, AND the DG-decode
  REPRO-CHECK passes (see below).
- **HARD-FAIL**: `relevant_recall` (dense-rescore path) < 0.30 at 1,213,912 (decode fix insufficient --
  task-contract-specified ceiling, DELIBERATELY set above Stage-2E's own HARD_FAIL_RECALL_CEILING=0.10
  since this cell's entire purpose is fixing decode, a sub-0.30 result at the hardest point means the fix
  did not meaningfully move the needle), OR scramble margin < HARD_FAIL_TIE_GAP=0.10 at EITHER scale
  (mechanism isn't discriminating -- a "tie"), OR the DG-decode repro-check fails at either scale
  (indicates routing/storage was NOT actually held bit-identical -- invalidates the cell's central
  compute-proportionality claim).
- Anything else (clears some but not all HARD-PASS gates, no HARD-FAIL trigger) = MIDDLE_BAND.

## DG-decode repro-check (mandatory, gate F.1-adjacent -- validates "storage unchanged" claim for free)
This cell's `eval_gate_hierarchical_dense_rescore` computes the OLD DG-argmax decode path as a byproduct
(needed for the diagnose-split anyway). At BOTH 100,000 and 1,213,912, for BOTH the composed and
scrambled-tier2 arms, compare the reproduced `relevant_recall_dg_decode` against Stage-2E's OWN landed
`relevant_recall` for the matching arm+scale
(MEASURED@data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json:per_scale).
`REPRO_TOLERANCE=0.05` absolute (same constant Stage-2D/2E already use). Since routing/storage/seeding
are declared bit-identical, this SHOULD reproduce near-exactly (not just within a loose tolerance) --
tolerance is retained only for float non-associativity / library version drift, not as an escape hatch.
If out of tolerance: HARD_FAIL (see above) -- means this cell accidentally changed something in the
"unchanged" storage/routing path, and NOTHING downstream can be trusted until that's fixed.

## Bands table (feasibility declared, not just asserted)
| gate | floor | measured-band-check |
|---|---|---|
| recall @ 100K, @ 1.2M (dense-rescore) | >=0.50 | strictly above floor requires clearing by >=5% of [0.50,1.0] band width = 0.525; report exact value, flag MIDDLE_BAND if within [0.50,0.525) per META_RULE_L |
| scramble margin @ both scales | >=0.30 | band width [0.30,1.0]; floor-hug flag if within [0.30, 0.335) |
| false_pull_in @ both scales | <=0.20 | this is an UPPER bound gate; floor-hug flag if within (0.165,0.20] |
| HARD-FAIL recall @ 1.2M | <0.30 | task-contract-specified, not re-derived |
| HARD-FAIL margin (either scale) | <0.10 | Stage-2E's own tie-gap constant, reused |

`crlb_n/a`: empirical two-store (sparse-coarse + dense-fine) capacity diagnostic; the dense store's
write-side capacity ceiling was already empirically measured (leaf_capacity_sweep_v1, cited, NOT
re-derived) and is EXPECTED to still be near-zero for full-vocab argmax at this scale -- this cell's
claim is specifically about restricted-comparison-set (k_eff=50) discriminability, which has no existing
closed-form CRLB in this codebase; empirical measurement is the only available method.

## Self-test / smoke / full contract
- `--self-test`: tiny (n_ent=48) synthetic BIGFAM(K=3)/SMALLFAM(K=1) corpus; constructs REAL `KGStore`,
  `SparseHeteroShardStore`, `DenseShardStore` (real_code_path, gate F.1); asserts (a) ingest-query tier-2
  agreement (inherited Stage-2E check), (b) dense-rescore mechanism activates + differs from DG-only
  decode (`arms_differ` hash check across {dg_decode, dense_rescore} x {composed, scrambled} = 4-way,
  META_RULE_AF), (c) scramble degrades the dense-rescore path's recall (mechanism sanity, not just the
  already-proven DG-path sanity).
- `--smoke`: real CSKG data, scale=[100000] only, run-safety pipeline check (see Discriminator section
  above for why this is not the discriminator-preview).
- `--full`: scales=[100000, 1213912], per-scale checkpointed via `tools/exp_checkpoint.py` (unit_key =
  scale), resumable. No separate Stage-2D-style spot-check-repro unit needed (the DG-decode repro-check
  above IS the repro-check, computed at BOTH full-contract scales for free as a byproduct, stronger than
  Stage-2E's own single-cheap-scale spot-check).

## ADDENDUM (mid-authoring, coordinator message): compose Stage-1.5 context-gate onto the accept step
A parallel brain-fidelity barrier-map drill (`notes/research_comprehension_barrier_map_brain_foundational_
2026-08-10.md` Section 5) independently reached the SAME 0.853->0.213 gap and proposed a second candidate
fix: the accept threshold (tau) is currently a single GLOBAL value pooled across all queries regardless of
which shard/family they route to; Stage-1.5's context-gated accept (`refuse_gate_calibrate_from_scores`,
already proven: false-admission 0.000 flat to M=100K) was validated on a coarse shortlist but never
composed onto a FINAL within-leaf accept. Per this cell's own diagnose-first design (not overridden --
"augmentation not redirect" per the coordinator), the choice between the two candidate fixes is decided
by MEASUREMENT: Stage-2E's OWN calibration numbers already provide a strong prior --
`in_set_accept=0.8933` @ 1,213,912 (MEASURED@data/exp_focus_pullin_causal_stage2e_hierarchical_subject_
tier_v1/metrics.json:per_scale.1213912.hierarchical_sparse.calibration.in_set_accept) means 89.3% of
relevant queries' CHOSEN candidate already clears tau -- the gate is already highly permissive, so
REFUSAL cannot be the dominant loss mode (only 21.3% end up correct+admitted despite 89.3% being
admitted at all -- most admitted candidates must be WRONG, i.e. wrong-argmax-dominant). This predicts
dense-rescore (fixes WHICH candidate) is the primary lever, not a sharper global threshold. Rather than
run a second separate cell, this cell COMPOSES both mechanisms as a combined, cheaply-ablatable fix
(context-gating is a free post-hoc recalibration over already-computed scores, no extra ingest/eval
compute):
- **PRIMARY reported `relevant_recall`/`false_pull_in_rate`**: dense-rescore candidate selection (as
  designed above) + PER-FAMILY-conditioned accept tau (context = the query-estimated family via the
  SAME relation-majority table `compute_query_shard_ids` already uses -- no oracle peek), calibrated
  independently per family from the calibration half of that family's dense in-set/out-set scores, WITH
  a fallback to the single global tau when a family's calibration sample is too thin
  (`MIN_FAMILY_CAL_N=4`; small families WD/FN/WN/CN|WN are expected to fall back given ~75 cal queries
  split ~proportionally to family size -- this is disclosed, not hidden, via `context_gate_diag` per
  scale/arm).
- **Ablation sidecars** (reported, not gating): `relevant_recall_dense_global_tau` (dense-rescore with
  the single pooled tau, isolates the argmax-fix's contribution alone) and `relevant_recall_dg_decode` /
  `false_pull_in_rate_dg_decode` (Stage-2E's original mechanism, reproduced -- doubles as the repro-check
  and as the diagnose-split source).
- VG's specific weakness (0.227@100K -> 0.0@1.2M per Stage-2E, flagged in the barrier map as possibly
  needing its OWN deeper tier) is explicitly OUT OF SCOPE for this cell -- the task contract requires
  routing/sharding/storage held EXACTLY as Stage-2E's (K_FAMILY unchanged); a deeper VG-specific tier
  would violate that. `per_family` results are still reported so a persistent VG-zero after the decode
  fix is visible and flaggable as a follow-up, not silently absorbed into an aggregate.

This keeps the diagnose-first design (the split is still measured, still decides prioritization framing
in the report) while making sure the context-gate-on-accept mechanism is genuinely exercised and
measured, not just discussed.

## ADDENDUM-2 (post-smoke, measured): PRIMARY metric reverts to dense-rescore ALONE (global tau)
The self-test (tiny scale, n_in_shortlist=8) and the real-CSKG `--smoke` run (100K,
n_in_shortlist_relevant=71) both MEASURED `diagnose_split_dg_decode.correct_refused_frac`:
tiny=0.25 (2/8, small-N noisy), **100K MEASURED@data/exp_focus_pullin_causal_stage2f_dense_rescore_fine_
decode_v1_smoke/metrics.json:per_scale.100000.hierarchical_dense_rescore.diagnose_split_dg_decode:
correct_refused_frac=0.0 (0/71)** -- at real-data scale, the DG-decode accept gate refuses ZERO
correctly-argmaxed candidates; ALL of the measurable loss among in-shortlist relevant queries is
wrong_argmax (35.2%, 25/71) or correct+admitted (64.8%, 46/71). This is exactly the ADDENDUM's predicted
outcome (in_set_accept=0.893 proxy) confirmed directly, not inferred.

Given zero refusal-loss to close, the context-gate-on-accept composition was measured (not skipped) and
found to REGRESS recall at 100K: `relevant_recall_context_gated=0.5733` vs
`relevant_recall` (global-tau dense-rescore alone) `=0.60` vs `relevant_recall_dg_decode=0.6133`
(MEASURED@data/exp_focus_pullin_causal_stage2f_dense_rescore_fine_decode_v1_smoke/metrics.json:
per_scale.100000.hierarchical_dense_rescore). `context_gate_diag` shows the dominant AT family (n_in=35)
gets a per-family tau of 0.389 vs the pooled global tau of ~0.175 -- a substantially STRICTER local
threshold that introduces NEW refusals for AT specifically where the permissive global gate had none.
Smaller families (WD/FN/WN=indices 3/5/6) have n_in in {0,1,4}, below `MIN_FAMILY_CAL_N=4` for most,
correctly falling back to global tau (not the source of the regression).

**Decision (per this cell's own diagnose-first design + the coordinator's explicit "use whichever your
diagnosis supports" instruction): PRIMARY `relevant_recall`/`false_pull_in_rate` gating metric = dense-
rescore ALONE (global tau).** `relevant_recall_context_gated` remains COMPUTED and REPORTED at every
scale/arm as an honest ablation/negative-finding sidecar (the context-gate-on-accept hypothesis was
tested, not assumed or silently dropped) -- it does not gate HARD-PASS/HARD-FAIL. All HARD-PASS/HARD-FAIL
band numeric thresholds declared above are UNCHANGED; only which computed quantity is compared against
them changed (dense-rescore-global-tau instead of dense-rescore+context-gated).

This also means dense-rescore's OWN lift over dg_decode at 100K is essentially a wash (0.60 vs 0.6133,
-0.013) -- consistent with the prereg's own analytical prediction that 100K is NOT the crowded regime
(Stage-2E's OLD decode already works fine there) and the real test of the argmax-fix is at 1,213,912,
where DG-space crowding is severe (in_set_mean=0.205 vs out_set_mean=0.123, MEASURED@Stage-2E). The
100K smoke's job (run-safety pipeline check) is satisfied; it was never meant to demonstrate the fix.

## Mandatory fields (per exp_dev canonical instructions)
- `arms_differ_verified: bool` (4-way hash: dg_decode x dense_rescore x composed x scrambled at
  self-test; digest-diff at full/smoke over {composed, scrambled} x {relevant_recall, relevant_recall_dg_decode})
- `cardinality_ok: bool` (EXPECTED_N_UNITS = len(SCALES))
- `final_metrics_atomicity: "tmp_replace"` (top-level) + per-scale unit via `record_unit`/`tools/exp_checkpoint.py`
- `cell_chunked: false` (single-seed-shaped, sweep axis = scale not seed)
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: true`
- `deterministic_seeding: true` (all seeds inherited from Stage-2B/2E constants, no `hash()`-derived
  ordering; new dense-store ingest uses the SAME shard-label arrays already computed deterministically)
- `calibration_check_dense_rescore: "adaptive_with_discriminator_gate"` (dense-space tau via
  `refuse_gate_calibrate_from_scores`, per-scale per-arm, 50/50 internal split -- SEPARATE calibration
  from the DG-path's tau, since the two score distributions are not comparable)
- `progress_logging: "print_flush_true"` (full run likely exceeds 300s per scale-pair combined)
- `hp_scope`: `{hierarchical_dense_rescore: [relevant_recall, false_pull_in_rate, scramble_margin,
  no_regression_100k, dg_decode_repro_check]}`
