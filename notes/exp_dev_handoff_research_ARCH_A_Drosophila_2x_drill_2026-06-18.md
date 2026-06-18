# exp_dev hand-off -- research: ARCH-A Drosophila MIDDLE_BAND 2x deep drill

Filed by: research (Opus synthesis over 4 parallel Sonnet lit-scan sub-agents)
Date: 2026-06-18
Trigger: 2x deep research drill returned a finding that REFRAMES the prior closure (DESIGN-INCOMPLETE-NOT-REFUTATION candidate audit-discipline #93). Companion to research note: notes/research_2x_drill_ARCH_A_Drosophila_MIDDLE_BAND_linear_readout_ceiling_nonlinear_alternatives_2026-06-18.md

Pause state: read data/orchestrator_paused.flag at dispatch time; if present, queue for resume only. Pre-flight is CPU-laptop-super-fast and can run while paused (no GPU); full-mode dispatch is gated by pause flag AND by pre-flight HARD-PASS.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and substrate-product reading; exp_dev session owns full experiment design with pre-registered HARD-PASS/HARD-FAIL bands per the research note.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP PRIORITY): 2x2 ablation pre-flight at small N

- Anchor pointer: notes/research_2x_drill_ARCH_A_Drosophila_MIDDLE_BAND_linear_readout_ceiling_nonlinear_alternatives_2026-06-18.md section (b) Cheap decisive test and section (c) PRED-1 / PRED-2.
- Substrate-product reading: tests whether Drosophila-class sparse-pattern capability requires its own expansion+WTA coding stage distinct from the substrate's existing readout choice (ARCH-B / C1 entmax fix). The 2x2 design orthogonalizes:
  - axis-1: presence vs absence of fly-MB-style random-projection + top-k WTA stage
  - axis-2: linear vs entmax readout on the resulting code
  - 4 cells: A1 (baseline, linear), A2 (baseline, entmax = C1 replication at small N), A3 (expansion+WTA, linear), A4 (expansion+WTA, entmax)
- Tier hint: TIER-1 pre-flight (laptop-CPU, ~1 hr total for 4 cells at N=512, M=200, K=20, single-seed family)
- Why-now: prior ARCH-A closure was DESIGN-INCOMPLETE because the experiment conflated axes-1 and axes-2. The fly-MB literature (Dasgupta-Tosh 2020 expressivity theorem; Dasgupta-Stevens-Navlakha 2017 fly-LSH; Litwin-Kumar 2017 optimal connectivity; Ryali-Krotov 2020 BioHash) places the canonical nonlinearity at the WTA stage with a downstream LINEAR readout. The project's prior "linear readout is the ceiling" framing -- correct for ARCH-B / C1 on the canonical substrate -- does not transfer cleanly to a fly-MB architecture where the nonlinearity is upstream. The 2x2 is the orthogonal diagnostic.
- Pre-registered HARD-PASS / HARD-FAIL / MIDDLE_BAND bands: per research note PRED-1 and PRED-2 (recall@1 target values for each cell, including the >=0.05 effect-size threshold for distinguishing readout-lift from substrate-lift).
- Compute classification: pre-flight is laptop-OK super-fast (per USER 2026-06-16 compute policy). DO NOT dispatch to GPU until pre-flight passes.

### Anchor 2 (CONDITIONAL on Anchor 1 PRED-1 HARD-PASS): full-mode N=4096 replication

- Anchor pointer: research note section (c) PRED-3.
- Substrate-product reading: at substrate operating point (N=4096, M=2000, K=50), does the 2x2 directionality preserve? If A3 > A1 at small-N but inverts at full-N, the pre-flight signal is a small-N artifact and Anchor 2 is HARD-FAIL.
- Tier hint: TIER-2 full-mode (heavy GPU, remote-desktop dispatch per DECISION 166).
- Why-now: conditional on Anchor 1 HARD-PASS. DO NOT dispatch until Anchor 1 cert-grade lands.
- Pre-registered bands: per research note PRED-3 (smaller absolute deltas at scale, same ordering).
- Compute classification: heavy, remote-only, requires committed prereg per USER 2026-06-17 BLOCKING checklist (commit cell + prereg note to origin/main BEFORE queue_add to avoid GATE_FAIL).

### Anchor 3 (PARALLEL to Anchor 1, optional, scope-expansion): spherical-code geometric audit

- Anchor pointer: research note section (c) PRED-5.
- Substrate-product reading: compute Hu 2024 (arXiv:2410.23126) spherical-code substrate-capacity bound for the project's current substrate geometry; compare measured ARCH-A capacity. If measured << bound, substrate-side suboptimality and U-Hop-style learned encoder is the next lever; if measured ~ bound, substrate is near-optimal and ARCH-A MIDDLE_BAND is a readout problem only.
- Tier hint: TIER-3 analytic side-experiment (no GPU, theory + cheap CPU).
- Why-now: independent symmetric check per NEGATIVITY-BIAS USER-LOCKED rule (verify UP as well as DOWN; substrate may exceed measurement).
- Compute classification: laptop-OK theory + cheap CPU; can run in parallel with Anchor 1.

---

## Context pointers (file paths, no summaries)

- notes/research_2x_drill_ARCH_A_Drosophila_MIDDLE_BAND_linear_readout_ceiling_nonlinear_alternatives_2026-06-18.md (THIS research note, FULL drill)
- data/orchestrator_status_log.jsonl (research_delivery entry filed 2026-06-18)
- Prior ARCH-A MIDDLE_BAND closure (per session_arc_2026-06-17_substrate_HALT_healing_recapture_global_verification.md)
- ARCH-B SPARSITY_NEUTRAL CONFIRMED + C1 entmax CERT-GRADE provenance (per session_arc_2026-06-17_evening)
- USER compute policy: feedback_compute_remote_for_heavy_laptop_for_superfast_C0_cost_underestimate_USER_2026-06-16.md
- USER BLOCKING commit-prereg checklist: reference_remote_dispatch_cell_readiness_checklist_2026-06-17.md
- USER verify-the-referent: feedback_verify_the_referent_arrives_not_just_producer_acted_USER_2026-06-17.md
- USER negativity-bias symmetric check: feedback_negativity_bias_user_caught_5x_symmetric_verify_both_directions_USER_2026-06-17.md
- Trust-tier: feedback_research_can_be_wrong_only_proven_fully_believed_trust_tier_USER_2026-06-17.md (this hand-off is T2/T3 onboarding-ready, NEVER load-bearing)
- Hand-off template lineage: notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md

---

## Contract section

This hand-off does NOT instruct experiment design. Exp_dev owns:
- Cell file authoring (Python module with cell entrypoint + REQUIRED_FIELDS + smoke + full mode)
- Self-test (--self-test must pass on .venv Python 3.12 BEFORE remote dispatch per BLOCKING checklist)
- Pre-registered envelope-fail-band note (commit to origin/main BEFORE queue_add)
- Smoke gate (laptop super-fast or quick remote-smoke if Anchor 1 escalates)
- Queue dispatch via queue_add.sh with explicit HDLAB_RUN_MODE=full export for remote runner
- Post-ship REMOTE VERIFY (per the 3-same-root bugs lesson 2026-06-17)
- Self-test per formula-selftests
- VERDICT_VET on landing per honest-negative discipline (Skunkworks v195/refuse-gate model)

Research's role ENDS at this hand-off file. Exp_dev's role BEGINS at picking which anchor to ship first.

---

## Autonomy declaration

Exp_dev session has autonomy to:
- Pick ordering of anchors (recommend Anchor 1 first; Anchor 3 in parallel allowed; Anchor 2 GATED)
- Refine HARD-PASS / HARD-FAIL bands within published-precedent reason (PRED-1, PRED-2, PRED-3, PRED-5 are pre-registered floors -- exp_dev may TIGHTEN but not LOOSEN)
- Choose seed-family discipline (recommend single-seed for pre-flight, multi-seed for full-mode per VERIFY-THE-REFERENT)
- Refuse-gate the dispatch if any pre-dispatch readiness check fails (laptop venv self-test fail, prereg-not-committed, REQUIRED_FIELDS missing, run-mode not exported)
- Mark closure provenance: if pre-flight HARD-FAILS PRED-1, the prior ARCH-A MIDDLE_BAND closure is RATIFIED (honest-acceptance); if pre-flight HARD-PASSES PRED-1, ARCH-A closure is preserved as cert-grade-but-DESIGN-INCOMPLETE and new finding lands as separate cap_map row.

Research will NOT re-dispatch on this topic unless:
- exp_dev returns a verdict with new mechanism question that requires fresh lit-scan
- USER explicitly redirects
- Pre-registered HARD-FAIL hits AND requires field-pivot per [[feedback-negative-results-2x-research]]

T2/T3 onboarding tier per [[feedback-research-can-be-wrong-only-proven-fully-believed-trust-tier]]: this hand-off is research-tier, NOT load-bearing. Cert-grade promotion requires cert-grade experiment PASS.

---

ASCII-only verified. No emojis. No em-dashes. Generic-only terms (no substrate-novel mechanism names visible in any external query). HARD-FAIL thresholds pre-registered per [[feedback-lit-scan-calibration-penalty]].
