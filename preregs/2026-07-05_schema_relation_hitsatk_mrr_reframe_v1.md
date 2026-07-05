# Pre-registration: schema_relation_hitsatk_mrr_reframe_v1

**Filed:** 2026-07-05 by exp_dev (cell author)
**Cell:** `experiments/exp_schema_relation_hitsatk_mrr_reframe_v1.py`
**Anchor:** `schema_relation_hitsatk_mrr_reframe_v1`
**Queue (staged; NOT dispatched by exp_dev):** `overnight_queue` (GPU; JOINT arm is torch-autograd
  trainable, batched B=2; FROZEN is torch-bmm B=2; device auto->cuda on the box). Acceptable fallback
  `remote_cpu_queue` (numpy/torch-cpu path is correct, ~30s/eval x 54 evals ~= 27 min).
**Timeout:** 3600 s (GPU estimate ~10-15 min; kills a mis-routed slow-CPU run before it wastes hours).
**Progress logging:** `print_flush_true` (all progress lines flush=True; line-buffered stdout). Required
  because FULL timeout_s >= 1800.

## KB_REFERENT
- notes/research_reframe_rank_set_prediction_one_to_many_ceiling_2026-07-05.md (design source; filtered
  Hits@k/MRR reframe, Bordes et al. 2013)
- data/exp_schema_relation_richer_content_vscan_v1/metrics.json (the EXACT-MATCH HARD_FAIL this reframes):
  verdict=HARD_FAIL, best_joint_rms@V300+=0.1067, best_joint-frozen=0.0022 (<0.02)
  MEASURED@data/exp_schema_relation_richer_content_vscan_v1/metrics.json:{verdict,best_joint_rms_at_V300plus,best_joint_minus_frozen_at_V300plus}

## Prior-work check (substrate-KB concept-query before authoring)
`bash tools/substrate_query.sh "rank based hits at k MRR filtered protocol relation prediction one to
many entropy ceiling knowledge graph completion"` top hit cosine=0.3154
(research_drill_L4_GNN_SHARES_MATH... R-GCN basis decomposition, KG-adjacent but a DIFFERENT mechanism);
remaining hits 0.30-0.31 are NL-understanding / retrieval-density drills. No prior arc cell at
cosine>0.30 tests the filtered Hits@k/MRR RANK reframe of the exact-match one-to-many ceiling. **This
cell is genuinely novel** (a metric-correctness lever on the SAME content representation, not a re-run
of any prior mechanism; CLS-dual-store explicitly NOT re-opened per research task constraint).

## Scientific question (the metric-correctness reframe)
The richer-content vscan cell landed HARD_FAIL under an EXACT-MATCH (argmax single-label) metric. A
research drill recomputed the FROZEN scorer's FULL (T,V) score matrix off-disk and found the true
object very often lands in the top-k but not at rank-1: the exact-match metric grades the substrate OUT
of signal it is actually recovering. The mechanism is NOT raw fan-out (subject-identity oracle
E[1/fanout]=0.81/0.94 is an order of magnitude above observed exact-match ~0.06-0.09
CITED@notes/research_reframe_rank_set_prediction_one_to_many_ceiling_2026-07-05.md) -- it is NEAR-MISS
content-neighbor competition. Standard KG-completion practice (Bordes et al. 2013 filtered Hits@k/MRR)
is the field-standard remedy for exactly this one-to-many/many-to-many regime.

**Decisive question:** under the FILTERED Hits@k/MRR protocol, does the substrate's inductive
(novel-subject) relational ranking recover strong signal -- best-of-{FROZEN,JOINT} filtered Hits@10
real_minus_shuf >= 0.20 AND MRR real_minus_shuf >= 0.15 on >=2 relations x >=2 encoders at V>=300?

## THE ONE CHANGE vs the parent cell (richer_content_vscan_v1)
The EVAL METRIC ONLY. Same FROZEN/JOINT scorer (verbatim `fit_scorer_paired`/`fit_scorer_np` +
`joint` autograd), same split builder (`build_split_scaled`/`load_relation`), same features
(bge_small_schema_TEM_entities_v1.npz / gsbc_expand2x cache), same paired REAL/SHUFFLED arms, same
inductive/transductive modes, same corpus (conceptnet5_en_100k.jsonl). Instead of argmax->single-label
accuracy we keep the full (T,V) score matrix and compute FILTERED rank metrics.

## Filtered protocol (Bordes et al. 2013) -- the load-bearing new machinery
For a held-out test pair (s, o*): rank o* against the V codebook objects, but EXCLUDE the subject s's
OTHER in-codebook true objects (from `by_subj[s]`, the full corpus co-occurrence set) before counting.
`filtered_rank(o*) = 1 + #{ j : j != o*, j not in filter_set(s), score[j] > score[o*] }`. Both FILTERED
and RAW (no exclusion) reported; **FILTERED is the gating metric** (raw-vs-filtered is not a hidden
researcher DoF). Metrics: Hits@1/3/5/10/20 + MRR. Filter set is ground-truth-derived -> IDENTICAL
across REAL/SHUFFLED arms (only the trained scorer differs), so rms isolates subject->object
correspondence. Formula verified at import on hand-constructed exact ranks (see `_test_filtered_ranks`).

## Mechanism / arms (discriminator = REAL - SHUFFLED on INDUCTIVE filtered rank, PAIRED)
- **FROZEN** (HP-gating): frozen content feature -> fixed random proj (df=384) -> trained bilinear W
  (RESCAL/DistMult, 2000 steps). VERBATIM parent code path.
- **JOINT** (HP-gating): shared 2-layer MLP content encoder (d->256->128, tanh, dropout 0.1) trained
  end-to-end with bilinear R (Adam lr 2e-3, wd 1e-3, 500 steps). VERBATIM parent hyperparams.
- **KNN** (REFERENCE, NOT HP): same frozen features, ZERO trained params; similarity-weighted top-k
  (k=15) neighbor object vote -> (T,V) score. If a parameter-free neighbor vote lands in the same rms
  band as the trained scorers, the signal lives in the REPRESENTATION not scorer capacity (rules out a
  "trained scorer memorized a spurious ranking" artifact). REAL uses y_train, SHUFFLED uses y_shuf.
- **SHUFFLED control:** subtracts the label-marginal / popularity ranking.
- **POP reference:** C-independent train-frequency ranking (diagnostic floor).
- **DerivedFrom watchdog (NOT HP):** surface-morphological ~single-answer relation; when content
  genuinely resolves the answer its rank mass concentrates at top-1 (narrow spread). The contrast vs
  the semantic relations' wide rank-1-to-rank-10 spread is evidence the semantic ceiling is
  content-resolution-specific, not architecture-generic.

## Contract -- PRE-REGISTERED BANDS (falsifiable; both directions)
- **HARD_PASS** = best-of-{FROZEN,JOINT} FILTERED inductive real_minus_shuf clears **Hits@10 >= 0.20
  AND MRR >= 0.15** on the SAME slot (no cross-metric cherry-pick), holding on >=2 semantic relations
  (AtLocation + CausesDesire) x >=2 encoders (bge + gsbc) at V>=300. Discriminator must fire.
  Interpretation: the substrate's relational transfer was being graded by the wrong (exact-match)
  yardstick; under the field-standard metric it is a genuine broad win.
- **HARD_FAIL** = max over semantic (rel x enc) at V>=300 of best-of-{FROZEN,JOINT} filtered Hits@10
  rms < 0.10 (while discriminators fire). Interpretation: even a generous top-10 rank reframe fails to
  recover half the original exact-match bar; thin generic-sentence content cannot resolve novel-entity
  relational identity at realistic vocab under ANY scoring convention -> only remaining lever is
  structurally richer per-entity content.
- **MIDDLE_BAND** = anything between (Hits@10 rms in [0.10,0.20) at V>=300, OR Hits@10 clears 0.20 but
  MRR does not clear 0.15 same-slot, OR clears both but not across >=2 rel x >=2 enc). Interpretation:
  the reframe recovers REAL signal (converts the exact-match HARD_FAIL into a genuine partial win) but
  content-resolution (not scoring convention) is still the limiting factor -> pair with a
  structured-content iteration next. Per the research note's preliminary read + this cell's multi-seed
  preview (below), MIDDLE_BAND is the MOST LIKELY outcome.

Bands are ordered and well-separated (HF 0.10 < MIDDLE < HP 0.20 = 2x the HF ceiling); not a
floor-hugging single-threshold -> META_RULE_L satisfied by construction.

## Compute architecture
Class **(a) batched-GPU**. FROZEN trains both PAIRED arms in one torch-bmm B=2 pass; JOINT trains both
PAIRED arms in one batched autograd model (B=2); kNN is a vectorized cosine + scatter-add. Storage
strategy: **no_storage** (no composition; single-hop relational ranking). numpy/torch-cpu fallback for
FROZEN/kNN if torch absent; JOINT records failure_class if torch absent (never dispatched to torchless
queue). No generative-LLM calls (deterministic caches only; n_generative_llm_calls=0).

## SCHEMA-VET pre-dispatch checklist
- `cardinality_ok`: EXPECTED_N_UNITS = sum over grid of (rels x encs) x 3 slots x 2 arms x 2 evals.
  FULL = 3 V x 3 rels x 2 encs = 18 combos x 12 x 3 seeds = **648 units**. Verdict HARD_FAILs on breach
  unless explained by gsbc-cache-missing.
- `arms_differ_verified`: FROZEN/JOINT REAL vs SHUFFLED score-matrix sha256 differ (META_RULE_AF).
  MEASURED@smoke: True.
- `final_metrics_atomicity`: `tmp_replace` (metrics.json.tmp + os.replace).
- `except SystemExit: raise` before `except Exception` (no BaseException; grep-clean: no bare except,
  no BaseException). start-marker + crash-diagnostic + heartbeat present.
- `crlb_n/a`: rank transfer has no closed-form noise floor. Reachability: at V=1000 k=10 filtered,
  random Hits@10 ~ 10/1000 = 0.01; rms bands (0.10/0.20) far above chance and far below saturation.
  `discriminator_reachability`: True (asserted at import: HF < HP < 0.95).
- `baseline_in_band` (META_RULE_AG): SHUFFLED filtered Hits@10 not saturated (< 0.95); REAL FROZEN in
  measurable band (~0.15-0.30 rms, not at ceiling). MEASURED@smoke: in band.
- `discriminator_fires` (META_RULE_K): synth_rank_signal (clean linear content map) must give FROZEN
  filtered Hits@10 rms >= 0.30 AND MRR rms >= 0.20; synth_rank_null (no signal) must give |rms| < 0.10.
  MEASURED@smoke: signal +0.48/+0.27 (FIRES), null +0.03/-0.005 (CLEAN). This is the smoke-provable
  discriminator; the V>=300 real-data recovery is the MAP question itself (partial-recovery IS a
  finding), justified NOT smoke-provable per DISCRIMINATOR-MUST-SURVIVE-SCALE option (C) preview arm.
- `calibration_check`: `adaptive_with_discriminator_gate` (filtered protocol is field-standard, not
  tuned-for-pass; synth signal/null are the fires/no-false-signal proofs).
- `HP_SCOPE`: {best-of-{FROZEN,JOINT} REAL/inductive/FILTERED SEMANTIC at V>=300: [HARD_PASS, HARD_FAIL,
  MIDDLE_BAND]; KNN: reference NOT HP; DerivedFrom: watchdog NOT HP; SHUFFLED/POP/raw: controls NOT HP}.
- §15 gates: no primitive-composition (single-hop ranking, no chained retrieval) -> Gate A/C n/a
  (no sweep-misalignment, no primitive->primitive edge). Gate B: the reframe is a metric change on an
  established scorer, not a difficulty sweep; discriminating band is guarded by the synth signal/null
  controls. Gate D positive control: filtered-rank arithmetic reproduced at import on hand-constructed
  exact ranks (`_test_filtered_ranks`); FROZEN scorer is the SAME code path as the parent (byte-identical
  fit_scorer functions). Gate E functional requirement: "recover top-k signal the exact-match metric
  discards" -> mapped to the filtered-rank primitive.

## Discriminator-survives-scale PREVIEW ARM (option C; FULL hyperparams, multi-seed)
Ran V300 x {AtLocation, CausesDesire} x bge x seeds {7,13,19} at FULL hyperparams (df=384, steps=2000,
JOINT 500) -- MEASURED@data/exp_schema_relation_hitsatk_mrr_reframe_v1_smoke/_multiseed_v300_full_hyperparam_preview.log:
- AtLocation/bge 3-seed MEAN best Hits@10 rms=+0.213 (sd 0.041), MRR rms=+0.108 (sd 0.011)
  -> Hits@10 clears 0.20, MRR does NOT clear 0.15.
- CausesDesire/bge 3-seed MEAN best Hits@10 rms=+0.449 (sd 0.252, JOINT high-variance), MRR rms=+0.166
  (sd 0.071) -> clears both at aggregate, but seed=7 alone (+0.160 Hits@10) would NOT -> multi-seed
  aggregation is load-bearing; single-seed would mislead.
- FROZEN filtered Hits@10 rms +0.147..+0.260 at FULL scale (well above HF ceiling 0.10, not saturated);
  kNN reference +0.167..+0.280 (SAME band -> representation-level signal, not scorer capacity).
Verdict: discriminator survives scale (does NOT saturate at full-N); MIDDLE_BAND is the likely FULL
outcome (expansion criterion needs >=2 rel x >=2 enc; only CausesDesire/bge clears both at aggregate;
gsbc untested in preview).

## Smoke result (LOCAL, exp_dev pre-flight; MEASURED@data/exp_schema_relation_hitsatk_mrr_reframe_v1_smoke/metrics.json)
- run_mode=smoke, device=cpu, torch_ok=True, good_units=48/48, size=117KB, elapsed 6.3s.
- arms_differ_verified=True; discriminator_fires=True (signal +0.48/+0.27, null +0.03/-0.005).
- V100 AtLocation/bge FROZEN filt Hits@10 rms +0.217, KNN +0.200; V300 FROZEN +0.100 JOINT +0.117 KNN +0.267.
- verdict=MIDDLE_BAND (best_filt_Hits@10_rms@V300+=0.15, best_filt_MRR_rms@V300+=0.114).
- Smoke exercises V100 + V300 (load-bearing V>=300 verdict branch), semantic relations, bge only.

## Expected FULL outcome (HYPOTHESIZED)
MIDDLE_BAND HYPOTHESIZED@this prereg (research preliminary + multi-seed preview both land here): the
filtered rank reframe converts the exact-match HARD_FAIL into a genuine partial recovery (Hits@10 rms
~0.2-0.45 at V>=300) but MRR and cross-encoder breadth likely fall short of a clean same-slot
>=2rel x >=2enc HARD_PASS. Either terminal is a clean, falsifiable, honest result.
