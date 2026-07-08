# Pre-reg: consolidated 3-arm (shallow-vs-deep) predictive-generation depth cell v4

- Cell: `experiments/exp_substrate_gen_lm_consolidated_3arm_depth_v4_n8192_gpu.py`
- Anchor: `substrate_gen_lm_consolidated_3arm_depth_v4_n8192_gpu`
- Metrics: `data/exp_substrate_gen_lm_consolidated_3arm_depth_v4_n8192_gpu/metrics.json`
- Extends: `exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu` (MIDDLE_BAND; single=62.1
  ensemble=43.1 bigram_count=55.8 trigram_oracle=20.4 ppl) -- reuses corpus/codebook/baselines/harness.
  DO NOT mutate that landed cell; this is a consolidated _v4 sibling.
- Date: 2026-07-07. Author: hdi_exp_dev.
- Routing: notes/research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md (shallow CA3),
  notes/research_brain_predictive_generation_mechanism_2026-07-07.md +
  notes/research_brain_predictive_generation_predict_residual_build_spec_2026-07-07.md (deep predict-residual).
- Prior-work check: see `Prior-work check` note in report (substrate_query on predictive-generation /
  residual-injection / TD-successor-feature context accumulation). This is a NEW composition (residual-injection
  + TD-bootstrap learning + per-step CA3 cleanup) not a retread of the 4 prior context-depth cells
  (exp_n2_context_depth_hd_binding_v1, exp_n5_trigram_concept_lm_v1,
  exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu all HARD_FAIL; 2ndorder-trigram MIDDLE_BAND).

## Question
The substrate has a documented 3-HARD_FAIL/1-MIDDLE history where context accumulation makes next-token
prediction WORSE with depth (bpc RISES: exp_n2 5.00->5.05->5.18 at K=1,2,3). Is that NOISE-COMPOUNDING
(per-step crosstalk; fixable) or a representation-CAPACITY ceiling (superposed bind structurally cannot carry
higher-order statistics)? And if fixable: does the DEEP brain-grounded fix (inject only the bounded prediction
RESIDUAL, learn W via TD(0)/successor-feature bootstrap -- predictive-coding + SR) beat the SHALLOW fix
(per-step CA3 cleanup toward the manifold of real depth-matched contexts)?

## Noise-compounding isolation (synthetic order-2 corpus)
Corpus = clean order-2 Markov (`gen_markov2`). The true dependency is exactly 2 tokens, so context beyond
K0=2 is PROVABLY pure noise (Markov property). Degradation is measured from K0=2 outward: dX = bpc_X(Kmax) -
bpc_X(K0). A degrading baseline (dRAW>0) is the discriminator; if RAW does not degrade even for K>>2, that is
itself evidence the failure is capacity/real-text-specific (verdict INCONCLUSIVE, redirect to real text).

## Arms (per seed x per depth K; all mechanism arms retain per-step CA3 cleanup, additive per build spec)
- `BASELINE_RAW_BIND`    : one-shot roll-bind bundle of K raw tokens (== base cell). NEGATIVE CONTROL; must
                           reproduce degradation (dRAW>0) or verdict INCONCLUSIVE.
- `CA3_CLEANUP_PER_STEP` : SHALLOW fix -- incremental accumulation + per-step soft-attractor cleanup toward the
                           manifold of REAL depth-matched training contexts. [MECHANISM A]
- `CA3_SCRAMBLED`        : ablation of CA3 -- same cleanup dynamics, RANDOM attractor codebook. [CONTROL A]
- `PREDICT_RESIDUAL_TD`  : DEEP fix -- inject only the bounded residual (actual - W-predicted) per step
                           (predictive-coding/DPCM) + per-step CA3 cleanup + W learned by TD(0)/successor-feature
                           bootstrap (not static Hebbian). [MECHANISM B]
- `RESIDUAL_SCRAMBLED`   : ablation of predict-residual -- same TD + cleanup, residual replaced by structureless
                           random vector (isolates whether residual STRUCTURE carries the benefit). [CONTROL B]
- Reference ladder (K-independent exact counts): unigram, bigram_count, trigram_count (oracle ceiling).

PAIRED ablation map (which mechanism wins, cleanly separated):
  CA3_CLEANUP_PER_STEP vs CA3_SCRAMBLED       => isolates CA3-cleanup (shallow).
  PREDICT_RESIDUAL_TD  vs RESIDUAL_SCRAMBLED  => isolates predict-residual+TD (deep).
  PREDICT_RESIDUAL_TD  vs CA3_CLEANUP_PER_STEP => deep-vs-shallow head-to-head.

## Grid / cardinality
FULL: N_DIM=8192, seeds=(7,17,23), CORPUS=40000, K_GRID=[1,2,3,5,8], arms=5, J=8 ensemble, M_CTX=2048,
N_EVAL=2000, N_STEPS=400, N_TD_STEPS=200. `EXPECTED_N_UNITS = 3 seeds x 5 arms x 5 K = 75`. `cardinality_ok`
gate: verdict HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if len(per_unit) < 75.
SMOKE: N_DIM=512, seed=(1), CORPUS=6000, K_GRID=[2,3,5], J=2, M_CTX=256, N_EVAL=500 = 15 units. Smoke keeps
K past the true order (K=5 > K0=2) so the degradation discriminator can fire.

## Bands (bpc in BITS; ensemble; seed-mean; Kmax=max(K_GRID); K0=2 true order; dX=bpc_X(Kmax)-bpc_X(K0))
- HARD_PASS: SOME mechanism arm has dX <= 0 (non-increasing past true order) AND beats BASELINE at Kmax by
  >= 0.30 bits AND its scramble control does NOT replicate the benefit (d(scramble) - d(mech) >= 0.15) AND
  (residual arm) TD did not diverge AND cleanup healthy (conv >= 0.80). => NOISE-COMPOUNDING confirmed+fixed.
- MIDDLE_BAND: a mechanism arm partially flattens (dX < dRAW) but does not meet HARD_PASS.
- HARD_FAIL: NEITHER mechanism changes the degradation (both dX >= dRAW) => CAPACITY CEILING (redirect to
  disjoint-block/frame-slot context representation) OR TD diverged / att1 malfunction (confound flagged
  distinctly from a clean refutation).
- INCONCLUSIVE: BASELINE does not degrade (dRAW <= 0): discriminator did not fire at this regime; re-spec to
  real text.
- Pre-committed expected tier: MIDDLE_BAND or HARD_FAIL. P(non-trivial predictive generation) ~0.25-0.30
  (deflated; documented 3-HARD_FAIL history).

## Discriminator-fires gate (ALL modes incl smoke; META_RULE_K)
BASELINE_RAW_BIND must degrade past the true order (dRAW>0). SMOKE MEASURED (N=512, seed1, K=[2,3,5]):
bpc_RAW K2=5.930 K3=5.890 K5=6.015 => dRAW=+0.085 > 0. Discriminator FIRES at smoke scale. (See report for
which mechanism arm flattens the curve.)

## SCHEMA-VET mandatory fields
- `cardinality_ok`: true (EXPECTED_N_UNITS=75 wired; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short).
- `final_metrics_atomicity`: tmp_replace (metrics.json.tmp -> os.replace; crash-diag writer same pattern).
- `except SystemExit: raise` (line 506) BEFORE `except Exception` (line 510); no BaseException catch.
- `arms_differ_verified` (META_RULE_AF): per-arm curve digests (sha256) asserted pairwise-distinct at end of
  main() before verdict; bit-identical arm curves => AssertionError.
- `baseline_in_band` (META_RULE_AG): BASELINE_RAW_BIND is the degrading negative control (bpc ~5.9-6.0 bits,
  well inside (0,log2(70)=6.13) range; not saturated, not floored). Scramble control arms are intentionally
  ablations (not band-gated). Reference count baselines (bigram/trigram) logged for oracle context.
- `crlb_n_a`: "This is a predictive next-token bpc task, not a clean disjoint-block recovery. The argmax-noise
  floor IS the object of study (does per-step crosstalk compound). Deliverable gate is a RELATIVE dX/gap
  comparison across arms sharing the same decode, not an absolute fidelity floor; CRLB not the governing bound."
- `discriminator_survives_scale`: smoke runs the SAME K-past-true-order sweep (K=5 > K0=2) and the SAME 5 arms
  as FULL; reduces only N_DIM/corpus/seeds/J. Smoke fired dRAW>0 (+0.085). FULL extends K to 8 and N to 8192
  where degradation and mechanism separation may sharpen.
- `progress_logging`: print_flush_true (line_buffered stdout; per-(arm,K) print; start-marker + crash-metrics
  + per-seed timing). Cell timeout_s < 1800 expected (see Dispatch) so §17 heartbeat-file not mandatory, but
  per-unit prints provide progress.
- `paired_trials`: arm comparisons are paired on the same corpus/codebook/seed (same `run_seed` builds one
  corpus + codebook, all arms evaluate on it). Ablation pairs (mech vs its scramble) share attractors/TD path.

## Self-test (--self-test; PROT-022)
1. roll-bind order-sensitive (permuted context cos < 0.95). 2. Hebbian K3 recall (pred.nxt cos > 0.5).
3. ppl=exp(nats), bpc=nats/ln2 formula identities. 4. `_gpu_cleanup` argmax == numpy
`hdlab.iterative_attractor.iterative_cleanup` reference on 3 cues. 5. residual encoder + `train_td` run +
non-divergent on tiny synthetic corpus; residual diag present. 6. N==8192. ASCII-only; print(flush=True).
MEASURED: `[selftest] PASS: rollbind K3recall ppl/bpc gpu_cleanup==npref residual+TD-nondiverge N8192`.
(On CPU laptop self-test requires `--smoke --self-test` since FULL asserts CUDA.)

## Compute architecture
- Class: GPU matrix (N_DIM=8192 codebook/W matmuls; per-step cleanup + TD are BLAS-vectorized). FULL asserts
  cuda (line 477) and requires N_DIM==8192 (line 475). Route to overnight_queue (GPU).
- Storage: superposition roll-bind context accumulator + hetero-associative W (context->next-token). CA3
  cleanup toward real-context manifold; residual arm accumulates predictive-coding error.
- Resumable: per-seed write_partial + aggregate_partials + resumable_seeds (restartable across 3 seeds).
- `cell_chunked`: per-seed loop with start-marker + per-seed partial + crash-metrics writer.

## Dispatch
- SMOKE: LOCAL (--smoke), CPU. GATE = discriminator fires (dRAW>0) + all 5 arms run + arms-differ. MEASURED.
- FULL: STAGE for overnight_queue (GPU; FULL asserts cuda). exp_dev does NOT ship (push/remote SCP routed via
  orchestrator per 2026-07-07 process correction). Recommended `--timeout 3600`: smoke wall ~O(minutes) CPU
  N=512/1seed/3K/J2; FULL N=8192 (16x dim, matmul scaling ~2.0), 3 seeds, 5 K, J=8, but on GPU. 3600s is a
  generous margin; cap justification: single-cell 5-arm depth sweep, not a large grid.
