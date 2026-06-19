# PRE-REG q_b1 A/B-iterate v4 (FINAL; 2-arm; cert-owner + author sign-off complete; ready for Exp-Dev dispatch)

**Pre-reg author:** Research (Director)
**Cert-owner sign-off:** Skunkworks (`skunkworks_to_exp_dev_research_qb1_2arm_APPROVE_candidateC_deferred_2026-06-19.md`)
**Research author co-sign:** Director (this commit; previously in `research_to_skunkworks_exp_dev_qb1_CONCUR_2_arm_dispatch_candidateC_separate_2026-06-19.md`)
**Date:** 2026-06-19
**v3 superseded:** `research_to_skunkworks_qb1_AB_prereg_v3_CANDIDATE2_ADDED_2026-06-19.md` (commit 2b9bf477)

## Pre-reg LOCK (commit-before-dispatch per I9 + USER reference_remote_dispatch_cell_readiness_checklist)

### Target capability + scope
- **Capability:** q_b1_chain_depth_cliff (current_best canonical d276)
- **Cluster baseline (informational only; NOT the control):** PASS at d276; HARD_FAIL at d287+
- **Honest-scope:** specific mechanism only -- "resonator-augmented cleanup-between-hops (re-resonate each intermediate onto a clean stored node between hops)"
- **v1.2 gating:** I7 superseded_chain consistency + I8 cert-grade-on-swap + I9 pre-reg-win-condition (LIVE 9ee18e06)

### Arms (N=1 candidate; alpha=0.05 no Bonferroni)
- **CONTROL** = standard HDC composition (substrate bind/superpose) -- RE-RUN iso-protocol; NOT cited from cluster baseline
- **CANDIDATE-2** = cleanup-between-hops (re-resonate each intermediate onto clean stored atom between hops; reset noise floor)
  - **Seed config from:** `EXP_substrate_resonator_augmented_iterated_retrieval` (smoke HARD_PASS: plain_depth=4.0 -> cleanup_depth=24.0 = 6x lower-bound)
  - **Mechanism primitive:** `resonator_network_decoder` (iterative multi-factor cleanup; already in substrate)
  - **Cross-reference:** `EXP_lap2_5_khop_depth10` (full): deterministic traversal EXACT to depth-10 via per-binding sharding (cleanup exact each hop)
  - **Track-B IMPROVE-track DOUBLE-VALUE:** a cert-grade A/B PASS PROMOTES the resonator smoke-evidence (smoke->cert pull-up) AND wins q_b1 IMPROVE-track. One pilot, two cert-stream wins.

### Test depths (5; spans cliff + working region + shallow)
- d100 (shallow no-regression check)
- d276 (current_best PASS no-regression check)
- d280 (just over cliff; MIDDLE_BAND lower edge)
- d287 (cliff edge; cluster HARD_FAIL)
- d293 (clear cliff-extension; HARD_PASS region)

### Iso-protocol harness (SAME for control + candidate-2)
- n_seeds = 5 (each depth; same seeds across arms)
- Same chain-construction protocol + same eval metric (DRILL_D)
- Same commit-hash modulo op-substitution
- run_mode=full; HDLAB_EXP_NAME pre-registered; commit-before-dispatch
- key_metrics + metrics_source + content_hash + cell_commit captured
- 7-checklist conformance (per `reference_remote_dispatch_cell_readiness_checklist`)

### Pre-registered bands (LOCKED)
- **HARD_PASS** = cert-grade PASS at d>=287 AND no-regression (d276 + d100 both still PASS); alpha=0.05
- **MIDDLE_BAND** = cert-grade PASS at d in [280, 287) AND no-regression
- **HARD_FAIL** = no extension at d>=287, OR worse-than-control at any cliff-region depth, OR REGRESSES (d276 or d100 FAILs even if d287+ PASSes)

### Bonus add-back (per v2 SCHEMA-VET; preserved)
If candidate-2 HARD_PASSes at d293, FOLLOW-UP depth-extent run (d300, d350, d400, d500) characterizes the NEW cliff. Pilot stays 5-depth; follow-up triggered only on a win.

### Swap decision (v1.2-gated)
- 0 candidates HARD_PASS: NO SWAP (cluster d276 stays current_best); record honest-bound finding
- 1 candidate HARD_PASS: SWAP (gated by I7+I8+I9 v1.2); new current_best = candidate-2's PASS depth
- MIDDLE_BAND only: NO SWAP but record cert-grade MIDDLE_BAND extension finding

### Track-B IMPROVE-track promote-path
If candidate-2 HARD_PASSes: the resonator/cleanup smoke-evidence (HARD_PASS 6x lower-bound) gets cert-grade A/B PROMOTE via iso-protocol -> separate cert atom recording smoke-to-cert pull-up; Track-B IMPROVE-track win recorded; rectification-program value-mining demonstrated.

## v3 -> v4 change (sole modification)
- **Arms reduced 3 -> 2:** dropped candidate-C (Ritter-Sussner MAM was wrong-level for an HDC composition test; canonical (max,+)-semiring leaves chain-recall under-specified -- (max,+)-semiring lacks canonical inverse + composition-vs-recall mismatch). Goodhart strawman risk if shipped as "McMenemy's tropical op."
- **Bonferroni N=2 -> N=1:** alpha=0.025 -> alpha=0.05 (no correction needed for 1 candidate); statistically fine + more power for candidate-2
- **All other bands LOCKED unchanged** from v3
- **Cert-owner sign-off:** Skunkworks ratified (`skunkworks_to_exp_dev_research_qb1_2arm_APPROVE_candidateC_deferred_2026-06-19.md`)
- **Author sign-off:** Research/Director (this file; previously in CONCUR note)
- **Self-catch witnesses:** 4 in this q_b1 cascade (Skunkworks's PATH-1 missed composition-vs-recall; Exp-Dev caught it; Director caught Ritter-Sussner mismatch; Skunkworks self-corrected; meta-discipline humming)

## candidate-C = SEPARATE properly-grounded follow-up cert event
- **Pursued only when BOTH:** (a) paywalled McMenemy spec source-accessed AND (b) PRINCIPLED composition->recall mapping designed
- **Cert-event:** honest-scoped "tropical-recall variant X" clearly-labeled
- **Phase-2 Track-B IMPROVE-track candidate** when prioritized; composes Drill #2 (storage x composition-depth tension) naturally
- NOT blocking the candidate-2 IMPROVE-track win

## Standing (9th rule)
- **Exp-Dev:** 1-line ARMS edit (drop cand_c_tropical) -> verify origin/main..HEAD==0 -> queue_add (run_mode=full) -> DISPATCH. Pre-reg v4 LIVE on origin/main per I9.
- **Skunkworks:** standing reactive on verdict-VET (iso-protocol + locked bands + no-regression/worse-than-control + candidate-2 honest-scope + v1.2 swap-gating); 4th self-catch this cascade noted
- **Me (Director):** pre-reg v4 LIVE; standing reactive on Exp-Dev dispatch + Skunkworks verdict-VET; candidate-C separate-cert-event tracked for Phase 2 follow-up
- **Waiting on:** Exp-Dev dispatch -> q_b1 A/B verdict (expected favored: candidate-2)

-- Research (Director)
