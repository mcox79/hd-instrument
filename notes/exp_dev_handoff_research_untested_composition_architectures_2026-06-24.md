# exp_dev hand-off — research: untested composition architectures (2x drill)

**Filed-by:** research (Opus 4.7-1M)
**Date:** 2026-06-24
**Trigger:** research drill at `notes/research_untested_composition_architectures_2x_drill_2026-06-24.md` proposes 3 substrate-native composition architectures with brain-existence-proof + cheapest-decisive-test. USER directive: "I refuse to accept this. Do more research" — REJECTS premature cf-RPE cap framing.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. This hand-off is INFORMATIONAL; queue-add discretion remains with exp_dev + Director gate.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N_DIM verification, seed count, exact threshold bands within the pre-reg ranges, queue choice (local_cpu vs remote_cpu vs overnight), anchor name format, ETA, smoke profile, FULL profile.

**Per [[feedback-results-to-application-cadence-same-cycle-atomize-and-hdlab-update]]:** any HARD_PASS from these cells should immediately atomize to Store + hdlab/ primitive update.

---

## Trigger context (what changed)

- USER refusal of "substrate-as-LM cap at cf-RPE alone" framing
- Research drill identifies 3 UNTESTED composition architectures NOT covered by the companion brain-mechanisms-NOT-yet-tested drill (which covered word-level / 2-level PC / WM)
- Each has brain-existence-proof + substrate-native path + cheapest decisive test
- Calibration penalty 0.20-0.30 applied; P_deflated in [0.45, 0.55] range

---

## Anchor candidates (rank-ordered for dispatch)

### Anchor 1 — PRIMARY: heterogeneous composition routing (3-arm + baseline)

- **Anchor pointer:** `notes/research_untested_composition_architectures_2x_drill_2026-06-24.md` Section L3 + cheap-decisive-test spec
- **Substrate-product reading:** 3 architectures (theta-phase two-W, freq-routed K=2, orthog-subspace) in ONE cell with discriminating-regime gate. The cheapest possible decisive test: zero new primitives; reuses A1 cell W matrices + cf-RPE update + readout step.
- **Tier hint:** local_cpu (~45min CPU on laptop) OR remote_cpu if laptop saturated. NOT a GPU candidate (no matmul-bound workload).
- **Why now:** primary refutation/confirmation of cap claim; refutes premature "cf-RPE is cap" framing if ANY arm HARD_PASSes
- **Pre-reg pointer:** Section L3.1/L3.2/L3.3 + cheap-decisive-test pre-reg bands (BPC <= 6.95 HARD_PASS; BPC >= 7.30 HARD_FAIL; specific bands per arm)
- **Discriminating-regime gate (mandatory per C5):** which of the 3 architectures (if any) HARD_PASSes; differential frequency-stratified top-1 confirms routing has measurable effect

### Anchor 2 — SECONDARY: multi-scale hierarchical composition

- **Anchor pointer:** drill Section L1 Stream C (V1-V4 multi-scale PC) + L5 recommendation 2
- **Substrate-product reading:** K=3 levels with coarse/medium/fine context windows in HRR bundle stack at N_DIM=8192. Brain-canonical (V1->V2->V4->IT). Complements heterogeneous routing on a different axis.
- **Tier hint:** local_cpu (~1hr CPU on laptop)
- **Why now:** dispatch AFTER Anchor 1 lands; if Anchor 1 HARD_PASSes, multi-scale may STACK additively
- **Pre-reg pointer:** TBD by exp_dev within the drill's L5 framework; HARD_PASS at BPC <= 7.00 for full 3-level stack
- **Discriminating-regime gate:** flat-vs-hierarchical contrast must be non-null (>=0.05 BPC differential between 1-level baseline and 3-level arm)

### Anchor 3 — TERTIARY: attention-as-compose primitive

- **Anchor pointer:** drill Section L1 Stream B + L5 recommendation 3
- **Substrate-product reading:** bind(Q,K)->softmax->bundle(V) as substrate-native composition operator. Substrate uses cf-RPE for plasticity but never used attention as a COMPOSITION operator.
- **Tier hint:** local_cpu (~30min CPU on laptop)
- **Why now:** dispatch IF Anchor 1 HARD_FAILs on all 3 arms (signals architectural pivot needed). Otherwise defer.
- **Pre-reg pointer:** HARD_PASS at BPC <= 7.05 for attention-compose arm vs current cf-RPE baseline 7.09; HARD_FAIL at BPC >= 7.20

### Anchor 4 — STACK companion: Path C encoder Phase-1

- **Anchor pointer:** `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` S2 atom encoder cell `enc_atom_graph_neighborhood_v1`
- **Substrate-product reading:** substrate-OWNED encoder per USER's standing emphasis (`project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23` memory). Orthogonal axis to composition; results STACK with Anchor 1.
- **Tier hint:** local_cpu (~3-4 days build + ~2-4hr full cell)
- **Why now:** PARALLEL with Anchor 1 (orthogonal axes); does not block dispatch of Anchor 1
- **Pre-reg pointer:** prior drill's pre-reg HARD bands (modularity-Z >= 2.5, LRG-stability >= 0.50, ARI metrics >= 0.30)

---

## Context pointers (file paths, not summaries)

**Companion drills:**
- `notes/research_composition_collapse_critical_drill_2026-06-24.md` — primary mechanism diagnosis (MH-cleanup logit-shape distortion); addresses PRIMARY collapse, this drill addresses SECONDARY
- `notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md` — brain mechanisms inventory (word-level, 2-level PC, WM); orthogonal axis to this drill's composition architectures
- `notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md` — substrate aliveness map confirming K=2 multi-bank already composes super-additively (MIDDLE_BAND); foundation for heterogeneous routing
- `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` — Path C encoder spec; stacks with composition architectures

**A1 cell + composition-collapse:**
- prior A1 5-primitive joint compose cell (HARD_FAIL @ BPC 7.89; refer to composition-collapse drill for cell ID)
- fair_harness baseline at BPC 7.3065
- cf-RPE-only baseline at BPC 7.0888
- A1 W matrices + cf-RPE update + readout step are REUSED in Anchor 1

**USER directives (load-bearing):**
- `feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23` — brain achieves +60-80% top1; substrate must too
- `feedback_empowered_to_experiment_where_lit_says_dismissed_USER_2026-06-22` — empowered to test brain-canonical with substrate-native variants
- `project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23` — Path C IS the substrate-product answer
- `feedback_route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20` — this drill IS the negative revival per USER directive

---

## Contract

- exp_dev designs ALL numerical parameters (per [[feedback-no-experiment-design-in-prompts]])
- exp_dev applies envelope-fail-bands (per [[feedback-envelope-expansion-fail-bands]])
- exp_dev pre-flight: smoke gate + schema-vet + cell-author smoke per Fix #17 + commit-first per remote-dispatch-cell-readiness-checklist + run_mode='full' verification
- exp_dev applies pre-dispatch verify-the-referent (Fix #26): run `tools/predispatch_check.py <anchor>` to catch duplicates + recent HARD_FAIL re-dispatches
- exp_dev respects spawn budget (Fix #14): max 3 in flight; if at ceiling, queue Anchor 2/3/4 for next cycle
- exp_dev verifies per-arm metrics not summary verdict_msg (Fix #28 recurring)

## Autonomy declaration

exp_dev decides:
- Exact N_DIM (verify 8192 is feasible per local_cpu_queue constraints; downscale if needed)
- Seed count (recommend 3 per drill standard)
- Threshold bands within drill's pre-reg ranges (BPC <= 6.95 HARD_PASS / >= 7.30 HARD_FAIL for Anchor 1)
- Queue choice (local_cpu vs remote_cpu vs overnight)
- Anchor name format (suggested: `exp_substrate_compose_heterogeneous_routing_v1`)
- Cell-author smoke profile (recommend: 1 seed, 1000 train tokens, T-grid subset)
- FULL profile (recommend: 3 seeds, 100000 train tokens, full T-grid extended)
- Dispatch order (Anchor 1 first; Anchor 2/3/4 sequenced per HARD_PASS/FAIL outcome of Anchor 1)

Research does NOT specify these — only that the cell exists and the discriminating-regime gate is honored.

---

**End of hand-off.**
