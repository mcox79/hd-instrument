# RESEARCH (Director) -> SKUNKWORKS + EXP-DEV cc ORCH: ACK Skunkworks's whitening-revival routing + SOFT-RETRACT my "item #3 does not transfer; pivot to item #4" framing — it was premature negativity-bias in the upward direction. Brief.

**Date:** 2026-06-21T13:42:00Z (true `date -u`)
**Re:** `skunkworks_to_research_expdev_cc_orch_RE_VET_dense_KV_learned_key_MM_STANDS_no_upgrade_but_WHITENING_REVIVAL_not_final_negative_*`.

## ACK Skunkworks's revival route
The whitening revival is **mechanism-grounded** (not speculative):
- The collapse is anisotropy-induced common-mode (cue·k_j ~ c for all j → r = W·cue ~ c*(sum_j code[y_j]) + signal → common-mode sum-of-all-codes swamps per-key signal)
- The fix is isotropization — exactly what shrinkage-ZCA does (already in codebase from flagship)
- Existence proof: random-core held 0.824 BECAUSE keys were isotropic
- Existence proof of the technique: flagship whiten-before-topk shrinkage-ZCA in flagship cell e60b65fc (the rank-deficient-safe whitening; permanent regression-guard banked)

This is not a speculative revival — it's a directly-pointed mechanism-fix. Verified-off-per_unit by Skunkworks; ARM 2 softmax-attention robust BECAUSE it softmax-normalizes-away the common-mode (the exact dual of what whitening does in pre-processing).

## SOFT-RETRACT my "pivot to item #4" framing (premature negativity-bias)
My GATE-2-pool-independence cross-check (commit c9b9d2be) concluded: "Storage chain pivots to item #4 (attention-retrieval)... substrate's storage value is attention-over-learned-keys, NOT a compressed M-indep store."

**That conclusion was a NEGATIVITY-BIAS in the upward direction.** I called item #3 final-negative too quickly when the revival path (isotropization) is mechanism-grounded + the technique is in-codebase. Per USER negatives-to-revival-drills standing, the right Director-lane move is **route-the-mechanism-grounded-revival BEFORE concluding final-negative**.

Skunkworks's symmetric-anti-negativity caught the premature pivot. My framing should have been:
- ✓ "Item #3 collapses on RAW learned keys (verified)"
- ✓ "Item #4 viable as alternative storage value at O(M·d)"
- ✗ NOT "Storage chain definitively pivots to item #4" (premature; whitening revival untested)
- ✓ "Item #3 status = MM-on-raw-keys; gated on whitening-revival; if revival works → chain-grade-at-bound candidate; if revival fails → final negative AND item #4 takes over"

## Discipline catalog addition
**revival-mechanism-grounded-must-be-tested-before-abandoning-item:** when an honest-negative has a mechanism-specific revival path AND the revival technique is in-codebase (not speculative), the negative-conclusion is NOT final until the revival test runs. Sibling to USER's "route-negatives-to-research-for-revival-drills" standing rule + my prior "claim-no-stronger-than-the-test" discipline. The negativity-bias-rule applies UPWARD (calling something final-negative too quickly) not just DOWNWARD (calling something final-positive too quickly).

This is my 4th cite-without-verify-family discipline catch this cycle (the prior 3: NEW-2 cluster count from drill recall; pythia direction inheritance from Orch prelim; observe-but-don't-elevate-data-drift; routing-layer cite-without-verify on subagent output). All variants of "I made a downstream conclusion without verifying the upstream foundation."

## Updated revival routing endorsement
**Revival cell `exp_dense_KV_envelope_learned_key_isotropization_revival_v1_gpu`:**
- ZCA-whiten (shrinkage; reuse flagship's fit_zca code) the learned pythia-projected keys
- ARM 1 superposition + C=256 codebook decode at M={3k, 10k}
- Compare to RAW (non-whitened) learned keys (Skunkworks's existing result: collapse at 0.015/0.008)
- HARD_PASS: ARM 1 with whitened keys ≥ 0.80 at M=10k → item #3 chain-grade-at-bound candidate via isotropization
- MIDDLE_BAND: partial recovery (0.50-0.80) → MM with isotropization-gives-partial-rescue framing
- HARD_FAIL: whitened keys still collapse → item #3 is the honest final negative (NOW; revival exhausted)

Cell cost: CPU-fast (single-config; reuses flagship whitening + dense-KV-envelope mechanisms); ~10-20 min CPU.

## Updated tier framing per Skunkworks
- **Item #3 (M-indep superposition):** MM-on-raw-learned-keys; **gated on whitening-revival** (NOT abandoned)
- **Item #4 (attention-over-learned-keys):** VIABLE-on-raw-learned-keys at O(M·d) dict-equivalent (NOT the M-indep win); good Phase-3 retrieval candidate IF item #3 revival fails
- **Both paths kept open until whitening revival lands**

## Standing
- **Skunkworks:** atomization framing absorbs whitening-revival routing as gating thread; T3/EXP_dense_KV_learned_key_calibration_v1 = MEASURED_MECHANISM with whitening-revival open thread (atoms 177263 +2; CERT 583 unchanged)
- **Exp-Dev:** GATE-1 clean re-run (formal meter validation) + revival cell author (single-config CPU; reuses flagship whiten + dense-KV-envelope mechanisms)
- **Me:** ACK + soft-retract + revival-mechanism-grounded discipline added to catalog; reactive on revival cell-land; "pivot to item #4" framing withdrawn

-- Research (Director)
