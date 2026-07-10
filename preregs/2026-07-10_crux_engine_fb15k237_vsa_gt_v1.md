# Pre-reg: crux_engine_fb15k237_vsa_gt_v1

Substrate-native generate-and-test inference engine on FB15k-237. Step-2 of the CRUX arc: the prior
VET'd cell `gt_induction_fb15k237_dense_v1` proved DENSITY + VERIFIER load-bearing but was pure symbolic
AMIE and LOST to the per-relation-frequency prior. This cell makes the engine (a) substrate-native
(FHRR bind/unbind compose PROPOSE + resonance VERIFY) and (b) able to beat frequency via three scoring
levers (Director course-correction 2026-07-10).

Cell: `experiments/exp_crux_engine_fb15k237_vsa_gt_v1.py`
Dataset: FB15k-237 standard split (train 272115 / valid 17535 / test 20466; 14541 ent, 237 rel).

## Scoring levers (the reason to expect a beat over Step-1)
Step-1 lost because relation-GLOBAL path support/confidence IS the frequency statistic -> collapses to
POP_RELFREQ. Beating frequency requires:
- L1 HEAD-CONDITIONAL (make-or-break): score candidate c by THIS head h's grounded-path evidence via
  per-(h,c,path-type) grounding multiplicity `mult_gain(m)=1+log(m)` weighting a head-specific bundle
  read against the rule profile (NBFNet-flavored). `mult_gain != const` makes score head-specific.
- L2 HOP-NORMALIZED: positive rule weight = conf * hop_gain(len), hop_gain(L)=L, so 2-3-hop chains are
  length-fair vs high-support 1-hop.
- L3 NEGATIVE EVIDENCE: high-body/low-conf path-types (conf<=NEG_CONF_MAX=0.02, body>=min_support) form
  a NEGATIVE profile; score -= NEG_LAMBDA(0.5) * neg-resonance (the "rules-out" signal).
The graded VSA bind/unbind bundle is the soft head-conditional aggregator hard symbolic rules cannot
express; ablating bind->add floods crosstalk (superposition catastrophe) so bind stays load-bearing.

## Arms
SUBSTRATE_GT (FHRR bind head-conditional propose-verify) | POP_RELFREQ (THE bar) | POP_DEGREE |
SYMBOLIC_GT (relation-global conf dict, same enumeration) | BIND_UNBIND_ABLATED (bind->add) |
BROKEN_VERIFIER (reach, random score) | RANDOM | GT_SPARSE (SUBSTRATE on downsampled graph).

## Bands (pre-registered; RELATIVE to this run's own POP_RELFREQ arm; eps=0.02 = META_RULE_L margin)
HARD_PASS (real substrate inference engine that beats frequency):
  SUBSTRATE_GT.h@1 >= POP_RELFREQ.h@1 + eps  AND  SUBSTRATE_GT.mrr >= POP_RELFREQ.mrr + eps
  AND BIND_UNBIND_ABLATED.mrr <= 0.7*SUBSTRATE_GT.mrr        (bind/unbind LOAD-BEARING)
  AND SUBSTRATE_GT.h@10 >= 1.5*GT_SPARSE.h@10                (density-contrast holds)
  AND BROKEN_VERIFIER.mrr <= 0.5*SUBSTRATE_GT.mrr AND BROKEN.h@1 <= 0.5*SUBSTRATE_GT.h@1 (verifier LB)
  AND no tail-collapse (beat-frequency holds on LOW+MID gold-degree strata).
HARD_FAIL (valuable: even substrate-native richer generate-and-test does not beat frequency):
  SUBSTRATE_GT.mrr <= POP_RELFREQ.mrr OR SUBSTRATE_GT.h@1 <= POP_RELFREQ.h@1   (ties/loses freq)
  OR BIND_UNBIND_ABLATED.mrr >= 0.9*SUBSTRATE_GT.mrr   OR BROKEN.mrr > 0.7*SUBSTRATE_GT.mrr
  OR HARD_FAIL_TAIL_COLLAPSE (aggregate beats freq but LOW/MID rare-tail stratum does not).
else MIDDLE_BAND.

## Diagnostic waterfall (localizes weak link, PASS or FAIL)
1 candidate_recall ceiling | 2 compose_fidelity vsa-vs-sym recall@C | 3 verifier_lift (post - pre) +
precision@1 cond | 4 rank_quality conditioned on gold-proposed | 5 info-ceiling per freq-tertile.
Plus degree/freq-STRATIFIED (LOW/MID/HIGH gold-tail degree) SUBSTRATE_GT vs BOTH POP_RELFREQ + POP_DEGREE.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (3 FULL); verdict counts len(per_seed).
- arms_differ_verified: hash-test at smoke (True).
- final_metrics_atomicity: tmp_replace (write_metrics + crash writer os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except) -- grep-gate CLEAN.
- crlb_n/a: rank-based KG-completion, no closed-form noise floor. discriminator_reachability: ceiling
  (candidate_recall ~0.44 smoke) > POP_RELFREQ.h@1 (~0.25) => h@1 beat physically reachable.
- baseline_in_band: POP_RELFREQ neither 0 nor 1 (smoke h@1=0.247 mrr=0.316).
- calibration_check: adaptive_with_discriminator_gate -- levers add hop_gain/mult_gain/NEG_LAMBDA/
  NEG_CONF_MAX (principled defaults, NOT tuned on smoke); self-test D1/D2 verify bind-vs-add compose
  discriminator still fires.
- discriminator survives scale: self-test (planted, scale-independent) fires bind-load-bearing (D1
  bind=1.0, D2 add=0.0 via superposition catastrophe at neg_lambda=0). At smoke bind_loadbearing gate
  ALSO fires on real data (ABLATED ratio=0.19). FULL is the canonical beat-frequency judge.
- sweep_alignment_verdict: n/a (no parameter sweep axis).
- positive_control_arms: SYMBOLIC_GT reproduces the relation-global symbolic scorer (Step-1 family) as
  the foil; delta SUBSTRATE_GT - SYMBOLIC_GT isolates the head-conditional VSA lift.
- functional_requirements: propose (path enumeration = candidate recall) -> verify (head-conditional
  resonance ranking) -> beat frequency (head-specificity). Each mapped to a mechanism in the cell.
- cell_chunked: false (3 seeds in one cell; per-seed heartbeat + crash diagnostic + start marker).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: print_flush_true (per-seed line + build-mining every 50 rels + eval every 1000 q,
  all flush=True; runner also uses python -u). timeout_s >= 1800 so this field is mandatory.

## Compute architecture
Class: mixed (sequential-CPU combinatorial path enumeration + memoized small-N FHRR bind/dot readout,
computed once per path-type). No large matmul; GPU not required but routed to overnight_queue (GPU box,
idle, dash-visible) per Director. Storage: sharded-equivalent (per path-type distinct FHRR vectors;
profiles are confidence-weighted bundles = the rule store, read by resonance).

## Smoke (tiny, local, non-gating) -- MEASURED@data/exp_crux_engine_fb15k237_vsa_gt_v1_smoke/metrics.json
seed 7, N_DIM=1024, N_EVAL=300, 40 rels, MIN_SUPPORT=3, ~7-32s:
SUBSTRATE_GT h@1=0.073 mrr=0.092 | POP_RELFREQ h@1=0.247 mrr=0.316 | ABLATED mrr=0.017 (ratio=0.19,
bind_loadbearing FIRES) | BROKEN mrr=0.013 (broken_fails) | density_contrast True | ceiling=0.440.
beats_freq=False at tiny N -- head-conditional does NOT beat frequency in the NOISY smoke regime
(MIN_SUPPORT=3 admits noisy negative rules; N_DIM=1024 low SNR; hop-norm boosts unreliable multi-hop).
Honest read: smoke gives NO positive beat-frequency signal yet; FULL (MIN_SUPPORT=10, N_DIM=2048, all
237 rels, cleaner rules) is the real judge. A clean HARD_FAIL at FULL is itself valuable (says even
head-conditional substrate generate-and-test does not beat frequency on FB15k-237).

## FULL dispatch
overnight_queue (GPU), 3 seeds [7,17,23], N_DIM=2048, N_EVAL=3000, all 237 rels, timeout 7200s.
