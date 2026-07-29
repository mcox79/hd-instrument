# PRE-REG: SCALE meaning-learning v5 -- FORWARD PREDICTIVE-CODING (causal-LM) encoder objective
# retrain, ledger row 1 (brain-fidelity gap: encoder objective)

- anchor: `scale_meaning_learn_arc_heldout_v5_forwardpc`
- cell: `experiments/exp_scale_meaning_learn_arc_heldout_v5_forwardpc.py`
- date: 2026-07-29
- author: exp_dev (hdi_exp_dev), per Director task "BUILD the hard thing: a BRAIN-FAITHFUL FORWARD
  PREDICTIVE-CODING encoder objective retrain -- ledger row 1, #1 fidelity gap"
- base: derived from `experiments/exp_scale_meaning_learn_arc_heldout_v2.py` (import, not copy --
  `import experiments.exp_scale_meaning_learn_arc_heldout_v2 as V2`; reuses V2's leak-proof corpus
  pipeline, concept universe/split, BPE build, `TinyTransformer`/`encode_concept_text_reps`,
  `select_fusion_on_train`/`semantic_eval`/`relational_eval`/`eval_from_reps`, ARM constants + bands
  verbatim, UNCHANGED). ALSO imports `experiments.diag_order_critical_comprehension_calib_v1` (
  `gen_cross_boundary`, `score_readout_arm`, `fit_binary_probe`, `MARGIN_THRESH=0.15`,
  `COHERENT_FLOOR=0.65` -- the CROSS_BOUNDARY comprehension-VET construction, already validated against
  a real HF reader at BGE_SMALL MEAN_POOL margin=+0.2600, CITED not re-run) and
  `experiments.exp_unified_self_learning_loop_v2` for `_scramble_words` (word-order scrambling control,
  same convention as `exp_cross_boundary_meanpool_replicate_v1.py`).
- plan: Director task contract (2026-07-29, this spawn); `notes/v4_negative_brain_fidelity_audit_
  readout_is_order_blind_next_lever_2026-07-27.md` (locates the readout defect + the CROSS_BOUNDARY
  instrument + why order-sensitivity matters); `data/exp_cross_boundary_meanpool_replicate_v1_selftest`
  (the seed-replication VET this cell must now re-run for a DIFFERENT encoder objective:
  RELOBJ_v3's own MEAN_POOL margin FAILED_TO_REPLICATE seed_7->seed_13 per that cell's docstring
  MEASURED@RELOBJ_v3_seed_7=+0.2083 CITED, seed_13 collapse pattern per Skunkworks seed-luck finding).
- ONE VARIABLE = the training OBJECTIVE (causal-LM / forward-temporal next-token prediction, replacing
  MLM's bidirectional masked-cloze). Architecture (d_model=512/6L/8H/ffn_mult=4), vocab=16000, max_len=
  128, token budget=121,082,196 (V2's own MEASURED realized value, not the 130M nominal -- same fix
  v4_breadth already applied for the identical reason: v2's ARC-only pool exhausts `max_lines` before
  reaching the nominal budget), mlm_steps=60000, mlm_batch=128, corpus=ARC-only (same as v2, NOT
  v4_breadth's multi-source breadth pool -- keeping the axis isolated) are ALL UNCHANGED from v2.
- target queue: `overnight_queue` (GPU). Per the canonical LOCKED process, exp_dev authors + self-tests
  + runs the HEADROOM PRECHECK locally (CPU, foreground, this doc's Evidence section) and RETURNS the
  exact `queue_add.sh` command for the FULL dispatch; the Orchestrator ships (SCP/SSH, cannot be done by
  this role) + owns post-ship REMOTE VERIFY. FULL dispatch is CONDITIONAL on the headroom precheck
  passing (see Headroom gate below) -- if it does not pass, this pre-reg's FULL section is NOT invoked
  and no queue_add command is issued.
- compute class: (a) batched-GPU (causal-LM forward/backward identical FLOP profile to V2's MLM
  forward/backward -- same transformer, same batch, same AMP; only the loss-mask/target shift differs,
  a cheap elementwise op). Corpus-scanning passes are sequential-CPU, justified identically to V2/v4 (the
  scrub-before-append leak-proofing primitive).
- storage strategy: no_composition (learned-encoder cell).

## Why forward-temporal, not another relational-contrastive retrain (faithfulness is the whole point)
Two prior retrains (`v3_relobj` = MLM+foundation-relational-InfoNCE, `v3_grounding`'s R3/R4 self-teacher
= landmark+VICReg+relational-InfoNCE+EMA) both HARD_FAILED and were BOTH relational-CONTRASTIVE
(graph-alignment) objectives, not forward-temporal prediction. The brain's cortical learning signal
(Rao & Ballard 1999; Friston 2005 free-energy/predictive-coding) is CAUSAL: predict the next input from
past-only context, prediction-error drives synaptic update. This cell implements a genuinely causal
next-token objective (GPT-style: causal self-attention mask + next-token cross-entropy over ALL
positions, not a 15%-masked bidirectional cloze) -- the untested faithful axis, not a third variant of
the already-refuted contrastive family.

## Design decision: REPLACE MLM with causal-LM (not stack both)
Stacking an auxiliary causal term ONTO the existing bidirectional MLM would (a) blur the ONE-VARIABLE
isolation (two objectives active, unclear which one is responsible for any lift), and (b) leave the
encoder's attention pattern BIDIRECTIONAL at the "primary" MLM loss the model still optimizes hardest
for, undermining the faithfulness claim (the brain's forward layers are not bidirectional). REPLACING
MLM with pure causal-LM is a clean single-variable swap: identical architecture parameter count,
identical embedding/encoder/head modules, the ONLY change is (i) the attention mask direction
(`torch.nn.Transformer.generate_square_subsequent_mask`, causal lower-triangular) and (ii) the loss
target (next-token shift-by-one over ALL non-pad positions, vs 15%-random-masked reconstruction). No new
parameters, no new forward pass, no confound from a second loss term's relative weighting.

## Model / training implementation (in-cell, does not modify V2.py)
- `CausalTinyTransformer`: a self-contained copy of `V2.TinyTransformer` (same submodule names --
  `tok_emb`/`pos_emb`/`enc`/`norm` -- so state_dict schema is architecturally compatible) with a
  `causal: bool` constructor flag; when True, `_contextual` builds
  `torch.nn.Transformer.generate_square_subsequent_mask(L, device=...)` and passes it as `mask=` to the
  `TransformerEncoder` call (in addition to the existing `src_key_padding_mask`). `pooled()` (mean over
  non-pad token hiddens, L2-normalized) is UNCHANGED -- deliberately: this lets the comprehension-VET
  test whether the SAME mean-pool readout becomes more order-sensitive purely because each token's
  causally-contextualized hidden state now encodes a directional running summary (a scrambled sentence
  changes every token's causal context, unlike bidirectional attention where a token's context is the
  whole window regardless of internal order) -- this is a stated, falsifiable MECHANISM HYPOTHESIS, not
  an assumed win; the comprehension-VET measures it directly rather than assuming it.
- `causal_lm_train(...)`: mirrors `V2.mlm_train` exactly (same optimizer/AMP/heartbeat/NaN-guard
  pattern) except: builds `CausalTinyTransformer(..., causal=True)`; loss =
  `F.cross_entropy(logits[:, :-1].reshape(-1,V), ids[:, 1:].reshape(-1), ignore_index=pad_id)` (shifted
  next-token CE over the causally-masked forward pass; no explicit masking of inputs needed since the
  causal attention mask already prevents future leakage). Same `FloatingPointError` non-finite-loss
  guard as V2.
- Checkpoint (`_save_checkpoint_causal`, in-cell): identical schema to V2's `_save_checkpoint` PLUS
  `causal=True` and `objective="causal_lm"` tagged into `model_cfg`/top-level fields. NOTE for future
  reuse (documented here, not silently left as a footgun): any tool that reloads THIS ckpt must
  reconstruct via `CausalTinyTransformer(..., causal=mc.get("causal", False))`, NOT
  `V2.TinyTransformer(...)` bare -- `V2`'s own `diag_readout_limit_probe_v1.load_frozen_encoder` does
  NOT know about the causal flag and would silently reconstruct a bidirectional model on this cell's
  weights (architecturally loadable, semantically WRONG at inference). This cell's own comprehension-VET
  and eval code always uses the causal-aware loader; downstream integration (registry wiring) is a
  post-landing task, flagged not hidden.
- Real baseline = V2's OWN trained MLM encoder. At FULL scale: REUSE `data/exp_scale_meaning_learn_arc_
  heldout_v2/ckpt_seed_<seed>.pt` (no retrain -- store discipline, v4_breadth precedent). At
  self-test/smoke scale: v2's real ckpt architecture doesn't config-match the tiny smoke/self-test model
  sizes (same accepted limitation as v3_relobj/v4_breadth's own smoke sections), so a FRESH tiny MLM
  baseline is trained on the SAME data bundle via `V2.run_one_seed` unmodified, giving a true apples-to-
  apples smoke-scale A/B (both objectives see identical tokenizer/split/stream/postings).

## Comprehension brain-metric: CROSS_BOUNDARY MEAN_POOL margin, own-encoder, both seeds
Reuses `diag_order_critical_comprehension_calib_v1.gen_cross_boundary` (word-multiset-identical clause-
order-flip construction, calibration-validated against BGE_SMALL at margin=+0.2600, CITED not re-run
here) + `score_readout_arm`/`fit_binary_probe` (linear probe fit TRAIN-only, scored on COHERENT vs
WORD-SCRAMBLED eval sentences). For each of {causal-PC encoder, MLM baseline encoder, RANDOM_INIT
untrained CausalTinyTransformer (structure-alone confound guard, same architecture, seed+999 init)}:
encode via `model.pooled()` (own encoder's MEAN_POOL readout, no bolt-on reader), fit the probe on
TRAIN, score `margin = coherent_acc - scrambled_acc`. `comprehension_specific = margin >= MARGIN_THRESH
(0.15) AND coherent_acc >= COHERENT_FLOOR (0.65) AND train-probe beats chance`.
`replicates = comprehension_specific on BOTH seed_7 AND seed_13, AND RANDOM_INIT does NOT independently
clear MARGIN_THRESH (guards against the STRUCTURE_ALONE_CONFOUND pattern already caught once this
session on RELOBJ_v3/ENTITY_STATE)`.

## Headroom pre-check (MANDATORY gate before FULL GPU dispatch; discriminator-must-survive-scale option C)
Cost-responsibility gate per task contract: before committing the multi-hour GPU retrain, run BOTH
objectives at SMOKE scale (d_model=128/2L/vocab=4096/max_len=48/mlm_steps=250, ~1-2 min each on CPU,
foreground) on the IDENTICAL data bundle (same tokenizer/split/stream), then score both on (a) held-out-
NEW semantic TEXT-arm margin (`V2.eval_from_reps`, `semantic_margin_text_minus_raw`) and (b)
CROSS_BOUNDARY MEAN_POOL margin at a reduced construction scale (train_target=300, eval_target_per_
label=80 -- fast, single seed=7 only, PLUS the RANDOM_INIT control).
- **HEADROOM_YES** (proceed to FULL): causal-PC's CROSS_BOUNDARY margin is not catastrophically worse
  than the fresh MLM baseline's own CROSS_BOUNDARY margin at this tiny scale (`causal_margin -
  mlm_margin > -0.05`) AND at least one of {causal CROSS_BOUNDARY margin approaches the pass bar
  (`>= 0.5 * MARGIN_THRESH = 0.075`), causal semantic TEXT margin >= fresh-MLM-baseline semantic TEXT
  margin} shows a genuine positive or non-worse directional signal for the causal objective. This is a
  DIRECTIONAL smoke-scale preview per the discriminator-survives-scale option-C precedent, not a
  statistically powered claim -- smoke-scale absolute numbers are expected to be noisy (small model,
  250 steps); the gate is a "not obviously doomed" filter, honestly documented as such.
- **HEADROOM_NO** (ABORT, do not dispatch FULL, report clean negative): causal-PC is worse on BOTH axes
  simultaneously by a nontrivial margin (`causal_margin - mlm_margin <= -0.05` on CROSS_BOUNDARY AND
  causal semantic TEXT margin also below the fresh MLM baseline's) -- the objective shows no plausible
  headroom at even the friendliest (in-distribution, same architecture, same tiny scale) comparison; a
  multi-hour full-scale GPU run is very unlikely to reverse a smoke-scale double-negative on the SAME
  encoder family, and the "honest abort beats a doomed run" discipline applies.

## Pre-registered bands for FULL (BEFORE running; only invoked if headroom check passes)
Real baseline = V2's reused MLM ckpt (CITED numbers if unavailable on the FULL execution host, per
v4_breadth's `baseline_source` distinction; MEASURED semantic_margin_text_minus_raw=0.0387,
CROSS_BOUNDARY comprehension not yet MEASURED for the v2 MLM encoder specifically -- this cell measures
it fresh on BOTH instruments so the comparison is apples-to-apples, not assumed from RELOBJ_v3's
different-objective number).
- **HARD_PASS_FORWARDPC_WIN**: (mean over seed_7/seed_13) causal-PC `semantic_margin_text_minus_raw` -
  MLM-baseline `semantic_margin_text_minus_raw` `>= +0.03` (a genuine lift over MLM, not just clearing
  V2's pre-existing generic gate which MLM already clears), **OR** the CROSS_BOUNDARY comprehension-VET
  `replicates == True` on BOTH seeds for causal-PC while the MLM baseline's own CROSS_BOUNDARY
  comprehension-VET does NOT replicate on both (i.e., a genuinely NEW capability attributable to the
  objective change, not something MLM already had) -- AND in either branch, RANDOM_INIT structure-alone
  guard does not confound (RANDOM_INIT CROSS_BOUNDARY margin `< MARGIN_THRESH=0.15`), AND validity holds
  (collapse/popularity in `[0.44,0.56]`, raw_grounding `>=0.55`, `n_query_min>=120`, per V2's own gates).
- **HARD_FAIL_NO_LIFT_NO_REPLICATE**: semantic lift delta `< 0` on both seeds AND CROSS_BOUNDARY
  comprehension-VET does NOT replicate for causal-PC on either seed (margin `< 0.15`) -- reported
  PLAINLY: the forward-temporal objective change does not lift the encoder's comprehension signal at
  this scale; a clean negative ruling out the objective-only lever (distinct from architecture/readout/
  consolidation, which remain untested by this cell).
- **MIDDLE_BAND**: mixed evidence -- e.g. semantic lift positive but `< +0.03`, or CROSS_BOUNDARY
  replicates on one seed only, or RANDOM_INIT triggers the structure-alone confound guard (own-mechanism
  learned signal cannot be credited even if the raw margin number looks good).
- **HARD_FAIL_INVALID**: V2's own validity gate fails (collapse/popularity/raw-grounding/power controls)
  -- the instrument itself is broken at this scale/regime, independent of the objective question.

## Leak-proofness
Identical to V2 (concept-level held-out split, sha256/PYTHONHASHSEED-free, `_zero_overlap_witness`,
scrub-before-append inside `count_pass`/`collect_pass`/`tokenize_train_stream`) -- UNCHANGED, reused by
import not reimplemented. CROSS_BOUNDARY construction is a SEPARATE synthetic agent/patient-style corpus
(no relation to the ARC held-out concepts), so it introduces no new leak surface into the semantic/
relational held-out-NEW eval.

## SCHEMA-VET declarations
- cardinality_ok: `EXPECTED_N_UNITS = n_seeds` (2 for FULL, plus a fixed 3-unit comprehension-VET panel
  {causal-PC, MLM-baseline, RANDOM_INIT} per seed).
- final_metrics_atomicity: tmp_replace (`write_metrics`/`write_partial` via `_seed_checkpoint`, same as
  V2/v4_breadth).
- except-ordering: `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE
  `except Exception` (no bare `except`/`BaseException`) -- grep-gated before ship.
- crlb_n/a: AUC/probe-accuracy discriminator base = 0.5 exactly (linear probe on a binary construction);
  no CRLB applies.
- baseline_in_band: verified at smoke (see Evidence).
- HP_SCOPE: HARD_PASS gates apply to {semantic TEXT-arm lift margin, CROSS_BOUNDARY comprehension-VET
  replicate flag} jointly (either sufficient per the OR clause above); RANDOM_INIT is a guard-only arm
  (never itself a HARD_PASS candidate); MLM-baseline is the comparison reference, not itself gated.
- arms_differ_verified: True (sha256 hash-test over {causal-PC, MLM-baseline, RANDOM_INIT} held-out rep
  matrices AND over the three CROSS_BOUNDARY score vectors).
- calibration_check: default_ok_for_this_regime (CROSS_BOUNDARY's own instrument-validity was
  established against BGE_SMALL at margin=+0.26, CITED from `diag_order_critical_comprehension_calib_
  v1.py`'s own docstring evidence; not re-run here to avoid a `transformers`-library dependency on the
  remote GPU box, an explicit scope-reduction documented not hidden).
- defensive_error_checking: passed_all_4_patterns (start_marker, CELL_CRASHED crash-diag w/ traceback,
  `_heartbeat.jsonl`, specific-exception classes -- `FloatingPointError` for non-finite loss,
  `(OSError, RuntimeError, ValueError)` for checkpoint I/O). `cell_chunked: false` (2 seeds sequential in
  one process, matching v2/v4_breadth convention; per-seed partials preserve a seed-7 result if seed-13
  crashes).
- real_code_path: `--self-test` constructs the REAL objects at N~16-40 scale: `CausalTinyTransformer`,
  `causal_lm_train`, `V2.load_concept_universe`/`prepare_data`/`run_one_seed` (fresh MLM baseline arm),
  `gen_cross_boundary`, `score_readout_arm`, `fit_binary_probe` -- all exercised inside `main()`'s
  self-test branch, not a synthetic-only side path.
- progress_logging: print_flush_true (training step logs + eval logs, `flush=True` throughout;
  `_heartbeat.jsonl` every `log_every` steps). MANDATORY given `timeout_s` will be >>1800s for FULL.
- deterministic_seeding: fixed int seeds (`seed`, `seed+999` for RANDOM_INIT, `SEED=20260728` matching
  `diag_order_critical_comprehension_calib_v1.SEED` for the CROSS_BOUNDARY construction RNG, matching
  `exp_cross_boundary_meanpool_replicate_v1`'s own convention) throughout; no `hash()`/`list(set())`
  ordering; grep-gated before ship.

## Capability-integration note (gate applies on landing)
If HARD_PASS_FORWARDPC_WIN: register `causal_forward_pc_encoder` in `data/capability_registry.jsonl` as
a candidate replacement for `scale_win_tinytransformer_encoder`'s MLM objective; WIRE target = update the
"best-validated from-scratch concept encoder" pointer + flag the `load_frozen_encoder`/registry-consumer
tools that need a `causal`-aware reconstruction path before other cells can safely reuse this ckpt. If
HARD_FAIL_NO_LIFT_NO_REPLICATE: register the negative (forward-temporal objective axis tested and
refuted for THIS ceiling, alongside the two already-refuted relational-contrastive variants) so the
ledger's row 1 moves from "untested" to "tested, refuted" and future sessions redirect to the
architecture/readout/consolidation rows instead of re-spinning the objective axis a 4th time.

## Evidence (this session, local CPU; MEASURED per META_RULE_AC tagging)
- Self-test: `MEASURED@data/exp_scale_meaning_learn_arc_heldout_v5_forwardpc_selftest/metrics.json`,
  verdict SELF-TEST PASS, real code paths (CausalTinyTransformer, causal_lm_train, V2.prepare_data/
  run_one_seed fresh-MLM arm, gen_cross_boundary, score_readout_arm) all fired, ckpt saved, elapsed 102s.
- HEADROOM PRECHECK (smoke, seed 7, both objectives trained fresh on identical bundle, d=128/2L/vocab=
  4096/250 steps, CROSS_BOUNDARY n_eval=160):
  `MEASURED@data/exp_scale_meaning_learn_arc_heldout_v5_forwardpc_smoke/metrics.json`:
  - CROSS_BOUNDARY MEAN_POOL margin: causal-PC=0.0812 (coherent_acc=0.575, scrambled_acc=0.494),
    MLM-baseline=0.0312 (coherent_acc=0.500), RANDOM_INIT(causal arch, untrained)=0.0875.
    causal-vs-MLM delta=+0.0500 (mechanism-consistent direction).
  - Semantic held-out-NEW TEXT-lift (text-RAW): causal=-0.1029, MLM-baseline=-0.1085, delta=+0.0056
    (both negative at smoke = undertrained tiny model; delta is noise-level).
  - final causal_lm_loss=6.8955 (finite, decreasing 86.4->6.9 over 250 steps).
  - HEADROOM verdict = HEADROOM_YES (causal beats MLM on the discriminator, semantic non-worse).
  - **HONEST CAVEAT (surfaced by the RANDOM_INIT arm, reported loudly, not hidden):** at smoke scale
    random-init causal (0.0875) ~= trained causal (0.0812), so the +0.05 CROSS_BOUNDARY advantage over
    MLM is attributable to the causal ATTENTION MASK (order-sensitive pooling even untrained), not to
    LEARNING, at this scale. This is an UNDERTRAINING artifact (coherent_acc 0.575 ~ chance => neither
    model has left init at 250 steps), so it is uninformative about the FULL outcome; the causal-vs-MLM
    delta (both equally undertrained) is the decision-relevant "not obviously doomed" signal. The FULL
    run's own RANDOM_INIT + both-seeds confound guards (build_full_verdict:
    MIDDLE_BAND_STRUCTURE_ALONE_CONFOUND if random-init clears MARGIN_THRESH; HARD_PASS requires
    both-seed replication) are what render the honest learned-vs-mask verdict at proper scale.

## Timeout (queue_add.sh `timeout_s`) -- computed BEFORE FULL dispatch, only if headroom passes
V2's own FULL run: `elapsed_s=10206.5` per seed (2.83h) for MLM at IDENTICAL architecture/steps/batch.
Causal-LM's per-step FLOP cost is architecturally identical (same transformer forward/backward; the only
difference is the loss computed over ~100% of positions instead of ~15%, a cheap elementwise
cross-entropy over the SAME logits tensor already computed for MLM at every position -- negligible
marginal cost). Comprehension-VET overhead (CROSS_BOUNDARY construction + 3-arm probe fit/score) is
smoke-cheap (pure numpy/small-linear-probe fit, no GPU) -- a few minutes at FULL scale (1800 train items,
2 eval labels x 300).
CRITICAL: `timeout_s` is the WHOLE-CELL timeout and the cell runs BOTH seeds in ONE process. v2's own
2-seed FULL wall = 2 x 10206.5 = 20413s. Plus causal-negligible per-step overhead + comprehension-VET
(a few min/seed) + FULL MLM-baseline arm = REUSED ckpt (re-encode postings only, ~minutes/seed, no
retrain) -> ~21400s realistic 2-seed wall. `timeout_s = ceil(1.5 * 21400) = 32100s`. Exceeds the 14400s
soft cap -- justified: SAME order of magnitude as v2's own already-landed 2-seed FULL on identical
architecture/compute; each seed's partial written independently so a mid-run failure after seed_7
preserves that seed's result. (An earlier draft used 16029 = a PER-SEED value; that is WRONG for the
whole-cell timeout -- would timeout-kill after seed 7. Corrected to 32100.)

## Queue dispatch (exp_dev hand-off; orchestrator ships + REMOTE VERIFIES) -- HEADROOM_YES confirmed
```
bash tools/orchestrator/queue_add.sh overnight_queue scale_meaning_learn_arc_heldout_v5_forwardpc \
  experiments/exp_scale_meaning_learn_arc_heldout_v5_forwardpc.py \
  preregs/2026-07-29_scale_meaning_learn_arc_heldout_v5_forwardpc.md 32100
```
REMOTE PREREQUISITES the orchestrator must satisfy before/at ship (exp_dev cannot push/SCP):
1. Push commit to origin/main (hd_metrics_sync) OR add-only SCP the cell + its sibling imports
   (`exp_scale_meaning_learn_arc_heldout_v2.py`, `diag_order_critical_comprehension_calib_v1.py`,
   `exp_unified_self_learning_loop_v2.py`, `experiments/_seed_checkpoint.py`) -- remote checkout is
   stale-by-design. The cell's module-level imports do NOT pull `transformers` (calibration HF path not
   invoked) -- verified by clean local self-test + smoke.
2. Confirm on remote GPU box: ARC corpus at `data/corpora/arc/` (v2's FULL ran there -> present) AND
   v2 baseline ckpts `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_{7,13}.pt` (FULL MLM-baseline
   arm; CITED-fallback if a seed's ckpt absent, reused_checkpoint strongly preferred).
3. Post-ship REMOTE VERIFY: queue_add exit 0 (not exit-5 referent-absent); on landing, verify
   run_mode=full (a 668B self_test landing = dispatch bug, per RUN_MODE VERIFICATION discipline).
Sequencing: GPU idle/free confirmed (`inflight_monitor.py`: gpu util 0%, overnight_queue pending=0);
`data/orchestrator_paused.flag` confirmed absent (re-verify at hand-off).
