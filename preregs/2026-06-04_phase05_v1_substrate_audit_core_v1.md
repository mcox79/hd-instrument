# Prereg: phase05_v1_substrate_audit_core_v1
## Anchor
phase05_v1_substrate_audit_core_v1
## Routing
Exp-Dev half of the Phase 0.5 Rung A Testbed split. Validates Algorithm 1 + audit primitives on SYNTHETIC
residuals (model-agnostic) so it is drop-in ready for Testbed's real npz (n_docs,9,2048). CPU (numpy).
## Scientific question
Does the substrate-side audit core work: (A) Algorithm 1 (kmeans k=5 over 9 layer-residuals -> sum-pool ->
sign -> bipolar 2048) makes healthy distinct codes; (B) kappa_3 z-score drift test flags injected drift
(z>3) while clean stays <3; (C) rank-1 deletion certificate preserves NON-target retrieval cos>=0.95 on an
UNDERLOADED bank (M=0.10*HID << capacity)? Refusal-cert deferred (needs refusal-labeled probes from Testbed).
## Pre-registered bands (synthetic-validation of the INSTRUMENT)
HARD-PASS: A balance<0.7 + diverse; B drift detected 3/3; C deletion non-target cos>=0.95 3/3.
MIDDLE: 2/3 primitives. HARD-FAIL: deletion <0.80 OR <2 primitives validate.
## Formula self-tests (PROT-022)
kmeans shape / sum-pool / bipolar / kappa3 finite / single-code self-retrieval. [PASS]
## Smoke gate
Smoke: deletion 0.998-1.000 (underloaded bank fix), alg1 healthy; drift z-test smoke-noisy (HID=256) -> MIDDLE;
full HID=2048 stabilizes. To run on REAL residuals: set env HDLAB_RESIDUAL_NPZ=<path to Testbed npz>.
## PROT-018 / 021
No _nN suffix (dim=2048 fixed by artifact). per-seed partials. timeout 7200s.
## Queue
remote_cpu_queue (numpy Algorithm-1 + audit matmuls; GPU would not help -> correctly CPU per routing-sanity gate).
