# PRE-REG: SCALE meaning-learning v3 relobj -- joint MLM + foundation-relational self-teacher (R1/R3)

- anchor: `scale_meaning_learn_arc_heldout_v3_relobj`
- cell: `experiments/exp_scale_meaning_learn_arc_heldout_v3_relobj.py`
- date: 2026-07-27
- author: exp_dev (hdi_exp_dev), per Director task "build the ENCODER RELATIONAL SELF-TEACHER experiment"
- base: `exp_scale_meaning_learn_arc_heldout_v2.py` -- REUSES its exact leak-proof pipeline (concept-level
  scrub, corpus prep, BPE build, controls, zero-overlap witness, semantic+relational eval code, verbatim).
  ONE variable = the training OBJECTIVE (add L_rel jointly to L_mlm). Architecture/data/steps unchanged.
- plan: `notes/THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md` (R1/R3 self-teacher),
  `notes/research_encoder_breadth_vs_relational_objective_scoping_2026-07-27.md` (this cell's build spec),
  `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (the prior-art guardrail this cell obeys)
- target queue: `overnight_queue` (GPU) -- SMOKE landed locally (this doc); FULL is a HAND-OFF, orchestrator
  ships + verifies after USER go-ahead (exp_dev cannot push). Sequence AFTER the currently-running
  `prop_extraction_selfteach_v6` job so they don't contend on the single remote GPU.
- compute class: (a) batched-GPU (transformer MLM + L_rel relational step + concept encode all batched; AMP on cuda)
- storage strategy: no_composition (learned-encoder cell; no HD store / no bundled composition)

## Prior-work check (substrate-KB concept-query, mandatory before authoring)
`bash tools/substrate_query.sh "relational self-teacher joint objective MLM foundation edges encoder
training"` -> top hit cosine=0.3672, `notes/research_teacher_free_relational_encoder_objective_2026-07-08.md`
(+ its landed pilot `data/exp_teacher_free_relational_encoder_cn_subgraph_v1_selftest/metrics.json`,
SELFTEST_PASS). READ. That drill is REAL prior art on the *general* teacher-free relational-objective
question (VICReg-style repulsion + relational-neighbor contrastive), but it is a small (222-node,
432-edge) shallow-linear-projection-head CPU pilot over CACHED surface features on the ConceptNet
subgraph -- NOT a joint end-to-end MLM+L_rel training loop over the from-scratch text Transformer, and not
run at anywhere near this cell's scale. It is complementary evidence for "relational InfoNCE + a fixed/
degree-agnostic anti-collapse mechanism is buildable," not a duplicate of this experiment. VERDICT: this
cell is genuinely novel at this scale/architecture, not a rediscovery. (Second-ranked hit, cosine=0.3447,
is THE_PLAN's own R1/R3 section, already cited above as the plan this cell executes.)

## CRITICAL PRIOR-ART GUARDRAIL (disk-verified BEFORE building, per task instruction)
`notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (2026-07-04 RKD attempt, HARD_FAIL):
"DENSE_SIGN (NO sparsifier) collapsed 0.825(smoke 3k) -> 0.368(full 178k)... RKD target is in-batch
`x@x.T`... In-batch pairwise coverage batch/V: smoke 6.4% -> full 0.32% (20x drop)... graded near-neighbor
pairs... NEVER supervised at scale." Root cause = (a) EXTERNAL teacher (BGE, violates no-borrowed-vector
lock) + (b) random in-batch co-occurrence collapses at scale. THIS CELL DIFFERS on both axes: teacher =
`cskg_foundation_v1`'s OWN typed edges (self-supervised, zero external model); negatives = a FIXED
landmark pool (top-TRAIN-degree concepts, selected ONCE per seed's shared data bundle), not a fresh random
V-slice per step. THEORETICAL coverage argument (crlb-style, for the discriminator-survives-scale gate):
at FULL_CFG, landmark/negative-pool coverage per relational step = n_land_batch/n_landmarks = 96/2048 =
4.7% (vs the failed run's 0.32%, ~15x higher), and because the pool is FIXED (not resliced), each landmark
accumulates ~= n_rel_steps * n_land_batch / n_landmarks = 7500*96/2048 ~= 351 gradient visits over the run
-- graded geometry IS supervised repeatedly against a stable frame, the concrete R1 anti-collapse fix.

A prior SMALL-SCALE attempt at the SAME objective class is also on disk:
`experiments/exp_deep_text_encoder_self_teacher_heldout_new_v1.py`
(`data/exp_deep_text_encoder_self_teacher_heldout_new_v1/metrics.json`, MIDDLE_BAND, ts=2026-07-26,
MEASURED `full_fusion_same_lex_auc - raw_grounding_same_lex_auc = -0.0180`). CONFOUNDED WITH SCALE
(`cap_nodes=5000`, `total_tokens_used=265273`, `d_model=128`, `n_layers=2`) AND load-bearing
ARCHITECTURE DIFFERENCE: its "joint" loss trains a separate shallow `FusionEncoder` head on TOP OF FROZEN
MLM-pretrained features (two-stage: `mlm_pretrain_deeptext` then `train_fusion` on precomputed, non-
gradient-flowing text features) -- not a truly joint `L = L_mlm + lambda*L_rel` over the SAME encoder used
for both losses, backpropagated together every step. This cell IS that truly-joint version, at
`exp_scale_meaning_learn_arc_heldout_v2`'s much larger FULL_CFG scale (d_model=512, 6 layers, 130M
tokens) -- genuinely different, not a rerun.

## What v3 adds (v2 unchanged otherwise)
- `L_rel`: every `rel_every` MLM steps, an InfoNCE relational step runs on the SAME `TinyTransformer`'s
  SAME `model.pooled()` contextual rep the MLM head and `encode_concept_text_reps` both use. Anchor batch
  = TRAIN concepts with >=1 TRAIN-TRAIN foundation neighbor; positive = one true neighbor (sampled);
  negatives = a subsample of the FIXED landmark pool (minus true neighbors). Cross-entropy / `infonce_tau`.
  `L = L_mlm + lambda_rel * L_rel` at relational steps, `L = L_mlm` otherwise. `L_mlm`/`L_rel` LOGGED
  SEPARATELY every log step (objective-conflict diagnosis, not just the summed loss).
- SECOND LEAK GATE: `cskg_foundation_v1/heldout_edges.jsonl` (24,774 edges, the foundation's OWN held-out
  edge split) excluded from `L_rel`'s TRAIN-TRAIN candidate pool -- independent of and additional to the
  existing concept-level text/split leak-scrub. Zero-witness: the exclusion set is built and applied
  BEFORE the pool is ever sampled from (`build_train_rel_index`), so by construction 0 excluded pairs can
  leak into training; the count of pairs actually caught (`n_excluded_heldout_pair`) is logged as evidence
  the gate was live, not that leakage occurred. MEASURED@smoke: 38 pairs caught at smoke scale (49,486
  heldout pairs loaded), confirming the gate is real and active, not a no-op.
- CHECKPOINT-ALWAYS: `_save_inprogress_ckpt` (atomic tmp+os.replace) every `ckpt_every_steps` DURING
  training (v2 only checkpointed once, at the very end). MEASURED@smoke: `n_ckpt_saves=4` at
  `ckpt_every_steps=80` over 250 steps.
- BASELINE REUSE (store discipline: no retrain): if `data/exp_scale_meaning_learn_arc_heldout_v2/
  ckpt_seed_<seed>.pt` exists, its persisted tokenizer+weights are RELOADED (never retrained) and
  evaluated on THIS run's own postings/split/adjacency (deterministically identical given unchanged cfg)
  to get a same-architecture, zero-retrain MLM-only baseline. VERIFIED on disk this session: v2's
  `ckpt_seed_7.pt` (109MB, `run_mode=full`, `model_cfg={vocab:16000,max_len:128,d_model:512,n_layers:6,
  n_heads:8,ffn_mult:4}`) exists and its `model_cfg` EXACTLY matches this cell's `FULL_CFG` -> baseline
  reuse WILL activate for seed 7 at FULL scale. `ckpt_seed_13.pt` does NOT exist on disk (v2's FULL run
  state is uncertain: no `metrics.json`/partials anywhere for v2, only the one checkpoint) -> seed 13 falls
  back to the CITED historical reference (~0.56 relational-AUC, task-prompt/THE_PLAN). `baseline_source`
  is logged per seed so the two evidence classes (`reused_checkpoint` vs `cited_reference`) are never
  silently conflated in the verdict.

## Arms (per-query AUC; base 0.5) -- same family as v2, computed on the v3 (relobj) encoder
RAW_GROUNDING [validity floor] | RAW_TEXT/TEXT_ARM [OBJ arm -- the test] | FUSED_EQ/ZAVG/WTUNED/SELECTED
[reported, not gated] | RANDOM_INIT [isolate learning] | COLLAPSE_SHUFFLE [can-fail/leak witness ~0.5] |
POPULARITY [validity ~0.5] | BASELINE_MLM_ONLY [reused v2 checkpoint or CITED reference; not trained here].

## Pre-registered bands (RELATIONAL held-out-NEW AUC is THE one number; semantic is a guard, not primary)
- HARD_PASS_RELOBJ_CLEAN_WIN: OBJ(TEXT_ARM relational-AUC) - BASELINE_MLM_ONLY relational-AUC >= +0.03 on
  BOTH seeds (per-seed strictly > 0), AND OBJ semantic-AUC does not regress > 0.02 vs baseline
  (objective-conflict guard), AND `L_rel` training loss visibly decreased, AND validity holds.
- HARD_FAIL_ARCHITECTURE_BOUND: margin stays within +/-0.02 of baseline DESPITE `L_rel` loss visibly
  decreasing => ceiling is readout/pooling-bound (e.g. `encode_concept_text_reps`'s mean-pool concept-
  aggregation order-blindness, the same defect class already found+fixed once in the reader loop this
  session), not objective-absence. Redirect to the readout mechanism next.
- HARD_FAIL_REL_OBJECTIVE_NOT_LEARNING: `L_rel` never fired or never decreased -> training-dynamics bug,
  margin numbers not trustworthy, fix before re-interpreting.
- MIDDLE_BAND_RELOBJ_PARTIAL: margin positive but < +0.03, or semantic regresses beyond the guard.
- HARD_FAIL_INVALID: validity gate fails (collapse/popularity/raw-grounding/power controls).
- VALIDITY (required): COLLAPSE_SHUFFLE in [0.44,0.56], POPULARITY in [0.44,0.56], RAW_GROUNDING >= 0.55,
  min held-out query power >= 120.

## Discriminator-must-survive-scale (option B analytical + C smoke preview, hybrid)
(B) THEORETICAL landmark-coverage argument above (4.7% per-step coverage vs the failed run's 0.32%, ~351
cumulative gradient-visits per landmark at FULL scale) -- FULL's n_landmarks=2048 is not itself
smoke-previewed 1:1 (wall-time), the coverage argument covers that gap.
(C) SMOKE preview at n_landmarks=256 MEASURED the discriminator firing for real: `n_rel_fired=50`,
`rel_loss_first=4.5147 -> rel_loss_last=4.4858` (`rel_loss_decreased=True`), `n_ckpt_saves=4`,
`n_excluded_heldout_pair=38` (second leak gate live), `SMOKE_PASS`. This is a genuine, if underpowered,
preview of the mechanism actually differentiating (loss moving), not a vacuous smoke.
MEASURED@data/exp_scale_meaning_learn_arc_heldout_v3_relobj_smoke/metrics.json: raw=0.6118 text(OBJ)=0.5400
rel_raw=0.5485 rel_text(OBJ)=0.5400 baseline_source=cited_reference(0.56) rel_margin=-0.0200 (smoke is NOT
expected to clear the FULL-scale HARD-PASS bar -- undertrained model on a 3.15M-token slice; the gate here
is "does the mechanism run + differentiate," not "does smoke already win").
Self-test (tiny scale) MEASURED: SELF-TEST PASS, `n_rel_fired=5`, `n_ckpt_saves` > 0, `n_excluded_
heldout_pair=8`, baseline correctly fell back to `cited_reference` (cfg mismatch at selftest scale, by
design -- confirms the fallback path is live, not just the happy path).

## Leak-proofness
- Concept-level held-out split (sha256, PYTHONHASHSEED-free) + zero-overlap witness (unchanged from v2).
- FIRST leak gate (v2, unchanged): tokenizer/MLM/postings never see held-out text.
- SECOND leak gate (NEW, this cell): `L_rel`'s TRAIN-TRAIN edge pool excludes any pair also present in
  `cskg_foundation_v1/heldout_edges.jsonl`, checked BEFORE the pool is built (not a post-hoc filter).
- Landmarks/anchors/positives are ALL TRAIN-split concepts only; a HELD concept is never an L_rel anchor,
  positive, or landmark (enforced in `build_train_rel_index`: `if is_held[i]: continue`).
- Baseline-reuse evaluates the RELOADED v2 encoder on THIS run's own held-out split (same salt, same cfg)
  -- no additional leak surface (the v2 encoder itself was trained leak-proof per v2's own pre-reg).

## SCHEMA-VET declarations
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (2 for FULL); verdict checks len(per_seed)==n_seeds.
- final_metrics_atomicity: tmp_replace (write_metrics + per-seed partials) PLUS periodic mid-training
  checkpoint (`ckpt_seed_<seed>_inprogress.pt`, tmp+os.replace, every `ckpt_every_steps`).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / no bare
  except). VERIFIED by grep gate (0 matches).
- crlb_n/a: AUC discriminator base = 0.5 exactly; collapse+popularity+random-init witness the floor.
- baseline_in_band: smoke collapse=0.4944 pop=0.5008 raw=0.6118 (0.05 < baseline < 0.95). PASS.
- HP_SCOPE: HARD_PASS gates apply to TEXT_ARM (OBJ) relational-AUC vs BASELINE_MLM_ONLY primary; semantic
  non-regression is a secondary guard; FUSED/ZAVG/WTUNED/SELECTED arms reported, not gated.
- arms_differ_verified: True (sha256 hash-test over RAW/TEXT/RANDOM base rep matrices; halts if identical).
- calibration_check: default_ok_for_this_regime (AUC base 0.5 analytic; controls witness it).
- defensive_error_checking: passed_all_4_patterns (start_marker + CELL_CRASHED crash-diag w/ traceback +
  _heartbeat.jsonl incl. rel_loss + specific-exception classes, incl. non-finite JOINT loss guard that
  reports both mlm and rel loss values). cell_chunked: false (per-seed partials + shared bundle).
- real_code_path: --self-test constructs the REAL objects (load_concept_universe, count/collect/tokenize
  passes, build_bpe, `mlm_train_relobj` incl. the L_rel relational step, `relobj_prep`/heldout-edge
  exclusion, encode, select_fusion_on_train, semantic+relational eval, baseline-reuse-or-CITED-fallback,
  checkpoint save+reload) at tiny scale. SELF-TEST PASS; `real_code_path_exercised` covers `TinyTransformer`,
  `mlm_train_relobj`, `relobj_prep`, `load_heldout_edge_pairs`, `_load_v2_baseline_encoder`.
- progress_logging: print_flush_true (MLM + L_rel step logs) + _heartbeat.jsonl incl. rel_loss
  (timeout_s >> 1800). REQUIRED and present.
- test-design gates: no sweep axis (single `lambda_rel=0.2` point, per compute-proportionality -- a sweep
  was considered and rejected given v2's own wall-time uncertainty, see Runtime section); positive control
  = RAW_GROUNDING reproduced at the test regime; discriminator can-fail confirmed at smoke (L_rel loss
  moves); FUSED_EQ still present as the dilution control (inherited from v2, unchanged).

## HARD INVARIANTS
TEACHER-FREE. NO borrowed vectors anywhere (learned token embeddings + from-scratch Transformer; BPE
vocab built FROM ARC; the L_rel "teacher" is `cskg_foundation_v1`'s own typed-edge graph, itself built
with no borrowed embeddings). INDUCTIVE. LEAK-PROOF (two independent gates, above). ASCII-only.
Deterministic seeds (sha256 split + fixed ints + `sorted()`; no `hash()`/`list(set())` -- landmark
selection is `sorted(picked)` after a deterministic degree-then-index rank). AI2 ARC Corpus = INTERNAL
research use only.

## Remote dependencies (orchestrator: verify before launch -- same as v2, already staged, PLUS the v2 ckpt)
- torch with CUDA on the GPU box; python package `tokenizers`; ARC corpus staged; `cskg_foundation_v1/`
  staged (incl. `heldout_edges.jsonl`, verified present, 24,774 lines); NLTK WordNet cache.
- NEW: `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt` should be present on the REMOTE box
  under the same relative path for baseline-reuse to activate there (verified present on LOCAL disk this
  session; if the remote copy differs/is absent, the cell degrades gracefully to the CITED reference for
  BOTH seeds -- not a blocking dependency, just a weaker baseline evidence class, logged honestly).

## Runtime + timeout
FULL config identical to v2 (max_lines=10M, train_token_budget=130M, vocab=16000, d512/6L/8H/seq128,
cap_mentions=128, heldout=800, mlm_steps=60000, 2 seeds) PLUS `n_landmarks=2048, n_land_batch=96,
n_anchor_batch=128, rel_every=8` (~7500 relational steps/seed, ~+30-40% wall-time over v2 by the
per-step-cost estimate: 128 anchor + 128 positive + 96 landmark sequences vs an MLM batch of 128, done
1/8th as often). v1's FULL wall was MEASURED@preregs/2026-07-27_scale_meaning_learn_arc_heldout_v2.md as
20363s (~5.65h) on the remote RTX 4060 Ti; v2 (eval-side changes only) was estimated ~6h; this cell's
own v2 FULL run state is UNCERTAIN on disk (checkpoint but no metrics -- see Baseline Reuse section), so
its actual elapsed_s could not be independently confirmed this session. Sizing off v1's confirmed 20363s
base + the ~30-40% relational overhead + negligible baseline-reuse-eval/mid-ckpt overhead gives an
estimate of ~26000-29000s (~7.5-8h). Per the research note's own guidance ("if wall-clock is unknown/
tight, ship ONE lambda point, both seeds, stop there") this cell ships `lambda_rel=0.2` as a SINGLE point,
NOT a sweep. Timeout set to 39600s (11h), generous per v2's own precedent (v2 used a 1.6x margin over its
own estimate; this cell's estimate carries more uncertainty than v2's did, so a wider margin is justified).
