# Pre-registration: generation-decode self-margin PR-transfer test (v1)

Anchor: `generation_decode_selfmargin_pr_transfer_v1`
Cell: `experiments/exp_generation_decode_selfmargin_pr_transfer_v1.py`
Author: exp_dev. Date: 2026-07-06. Queue: remote_cpu_queue (FULL). CPU-only, numpy.
Framing (USER-LOCKED): monitor-not-control. Predicts/reports its own decode reliability; NEVER edits
codebook / decoder / V / D / N; narrow glass-box monitoring step; not fluent-language; not self-improvement;
re-encode HELD.

## Question
Does the PARTICIPATION-RATIO-corrected extreme-value self-margin (which revived the COMPREHENSION
order-recovery decode-cliff prediction, exp_comprehension_order_recovery_pr_corrected_margin_v1) TRANSFER
to predict the GENERATION decoder's decode-collapse boundary? Premise:
notes/research_generation_decode_self_margin_pr_correction_premise_confirmed_2026-07-06.md.

## Mechanism audit (why this is a genuine test, not a rubber-stamp)
Generation decoders here decode DISJOINT block-local (one token per block, bs=N/D): the signal score is
the deterministic self-overlap G[t,t]=k, so the collapse is a CODEWORD-COLLISION (birthday) event, NOT the
superposition-crowded effective-rank competition that PR corrects in comprehension (which superposes L=D/2
tokens per block -> signal variance). Whether PR still transfers is the open question.

MEASURED@author off-disk probe (scratchpad/gen_margin_probe.py, seed 7): gsbc V8000 D48 p1_meas=0.371 while
PR-corrected predicts 0.998 (under-predicts collapse); corr V65536 D26 p1_meas=0.927 while PR and naive both
predict ~1.0 (distractor kurtosis ~40). Deflated expectation: HARD_FAIL/MIDDLE transfer.

## Predictors (vs MEASURED per-block decode p1 = per_term of hv.single_block_decode, reused VERBATIM)
- `p1_pr`: GH64 order statistic, n_comp = PR(V)-1 (participation ratio via bs x bs Gram dual). MECHANISM.
- `p1_naive`: GH64, n_comp = V-1 (falsified comprehension baseline). CONTROL.
- `p1_loose`: GH64, n_comp = 1. Diagnostic.
- `p1_emp`: (1 - p_pair)^(V-1), p_pair = P[distractor overlap >= signal]. Collision-mechanism diagnostic.

## Arms / codebooks
- `gsbc`: native GSBC block-local codebook (comprehension geometry; the premise's actual codebook). Gated arm.
- `corr`: synthetic clustered correlated codebook (high-vocab hopeful-angle regime, V up to 65536).
- `iid`: interference-free codebook. NO-COLLAPSE control (collapse is a correlation/collision artifact).

## Pre-registered bands (gated on the gsbc non-saturated cells)
HARD_PASS (PR transfers; CG-candidate):
- PR-corrected aggregate mean-ratio in [0.80, 1.25] (unbiased), AND
- improvement over naive (naive_perseed_max_err / pr_perseed_max_err) >= 1.5, AND
- NAIVE-V biased (aggregate mean-ratio outside [0.85, 1.18]).
HARD_FAIL (PR does not transfer; bounded negative + mechanism):
- PR-corrected aggregate mean-ratio outside [0.55, 1.80], OR
- improvement over naive < 1.2 (PR no better than the falsified naive-V count).
MIDDLE_BAND: clears core gates but misses a HARD_PASS sub-gate (partial transfer).

## Phenomenon / discriminator gates (ALL modes)
- COLLAPSE BITES: >= MIN_NONSAT non-saturated (0.05 < p1 < 0.999) gsbc+corr cells (smoke 2 / full 4).
- iid NO-COLLAPSE control: mean iid p1 >= 0.98.
- GATE-D positive control: gsbc @ (8192,26) per-block p1 within 0.03 of the landed v1 decoder
  (blocklocal_gsbc@V8192D26 per_term_mean=0.9945, MEASURED@data/exp_generation_decoder_gsbc_native_blocklocal_v1).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = seeds x len(grid); verdict gates on count. FULL = 5 x 13 = 65.
- arms_differ_verified: pr / naive / loose / emp prediction surfaces hash-distinct.
- final_metrics_atomicity: tmp_replace.
- crlb_n_a: prediction-match ratio (no Cramer-Rao noise floor).
- calibration_check: default_ok_for_this_regime (PR formula + 64-pt GH parameter-free given the Gram).
- discriminator survives scale: collapse measured at FULL N=8192, D up to 48, V up to 65536; smoke keeps the
  deepest gate cells (gsbc D48, corr V65536 D48) at full N/D/V.
- progress_logging: line_buffered_stdout + print(flush=True) + heartbeat.
- start_marker + crash_diagnostic + heartbeat present.
- positive_control (Gate D): decode = hv.single_block_decode VERBATIM; predictor = pc.p_win_extreme +
  pc.participation_ratio VERBATIM (self-test asserts bit-identity to the comprehension self-margin cells).
- HYPOTHESIZED vs MEASURED: probe numbers tagged MEASURED@author off-disk; bands HYPOTHESIZED@this prereg.
- kb_referent_declared: False (synthetic + bounded pre-encoded GSBC pool; no cert_ledger referent).

## Dependency
gsbc arm requires the untracked GSBC pool npz `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz`
(SCP to remote before FULL; queue_add does NOT ship it; already SCP'd for sibling generation/comprehension
cells). corr + iid arms are self-contained.

## SMOKE RESULT (landed local, 3 seeds; MEASURED@data/exp_generation_decode_selfmargin_pr_transfer_v1/metrics.json)
verdict=MIDDLE_BAND. GATE_D ok (gsbc@8192D26 p1=0.9929 vs 0.9945); iid no-collapse (1.0); arms_differ ok;
9 non-sat cells. PR mean_ratio=0.734 (biased low: unbiased at mild D26 ratio~0.99, breaks at deep D48
ratio~0.37-0.62); NAIVE mean_ratio=1.371 (biased, seed-unstable at deep corner); improve=1.54x (PR beats
naive on worst-cell but is itself biased). Partial transfer: PR works in the mild-collapse regime, breaks in
the deep-collapse (collision-dominated) regime. Honest MIDDLE.
