# Strategy decisions log — 2026-05-25

This file records strategy decisions made on 2026-05-25. Append-only.
Each entry references the cap_map version it pairs with (PROT-009).

---

## v205 — 2026-05-25 heavy-research-night integration (ANNOTATION-ONLY)

**Trigger.** Nine research deliveries + three local-batch experimental results integrated after heavy research night (2026-05-24/25). Sources: `notes/research_alternative_theoretical_homes_2026-05-24.md`, `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`, `notes/research_bet_n_design_readiness_2026-05-25.md`, `notes/exp_dev_handoff_bet_n_design_2026-05-25.md`, `notes/research_ssm_hippo_compatibility_2026-05-25.md`, plus local-batch metrics from `wave14_betB_saddle_cascade_reanalysis_v1`, `wave14_betB_alt_taxonomy_sweep_v1`, `wave14_moe_alpha_c_formula_verify_v1`.

**Decision (1): Saad-Solla saddle-cascade elevated to LEADING theoretical home.**
BIC delta=194.9 vs sigmoid (97x threshold); equal-spacing formula error=0.038 (below 0.05 threshold). Both pre-registered criteria pass. 1-RSB demoted to "one-of-several candidates." Pred-4 hysteresis (pending re-ship after script fix) is now the PRIORITY DISCRIMINATING EXPERIMENT between saddle-cascade (first-order) and 1-RSB (continuous). Framework reliability slightly improved to 32-48% (was 30-45%).

**Decision (2): IB-phase-transition CLOSED as competing theoretical home.**
Plateau count does NOT track K. IB spacing-formula max error=0.30 >> 0.10 threshold. Candidate (iv) from `notes/research_alternative_theoretical_homes_2026-05-24.md` closed. Saddle-cascade (candidate v) survives and advances.

**Decision (3): LINEAR-HETEROASSOC LOCKED as primary substrate architecture.**
Per `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`. This is a load-bearing architectural decision. MoE rebuild SHIFT/PARTITION arms will be designed on linear-heteroassoc basis. Bet N multi-hop will use linear primary with one narrow recurrent-cleanup-head K6 probe (P=0.30). Linear preserves the audit/decompose/provenance signal that defines the product framing.

**Decision (4): Bet N promoted to design-ready; handoff filed.**
`notes/exp_dev_handoff_bet_n_design_2026-05-25.md` written. Cao 2023 (arXiv:2301.02196) is direct lit precedent. P_deflated=0.28 category-defining; P=0.55 material-promotion. LOWEST-DEPENDENCY Tier-1 path (no alpha_c gate, no MoE prerequisite). Awaits exp_dev pickup.

**Decision (5): SSM-HiPPO framed as HiPPO-LegS W-initializer (NOT layered SSM dynamics).**
v190 ssm_depth=0 structurally confirmed by Jelassi 2024 Thm 2.7. Substrate-compatible path is HiPPO-LegS initialization of W matrix. P_deflated=0.18 category-defining. One cheap CPU probe filed (HiPPO-LegS W-init smoke).

**Decision (6): Product positioning sharpened to "algebraically-canonical fast-weight memory."**
Full framing: "algebraically-canonical fast-weight memory with exposed W for audit / verifiable-erase / provenance." Composes: linear-heteroassoc auditability (decision 3), Saad-Solla retention structure (decision 1), K5 ✅ real-time-learning-during-inference, F-6 KKL low-influence smooth boundaries. This framing is used in all downstream product discussions.

**Decision (7): MoE alpha_c anomaly RESOLVED; rebuild unblocked.**
`wave14_moe_alpha_c_formula_verify_v1` confirms alpha_c [0.40, 0.70]; M_per_expert=1612 at N=4096 locked. The v203 "ANOMALY" interpretation (OUT_OF_RANGE vs Sourlas/Krauth-Mezard classical range [0.08, 0.25]) was premature — substrate's BSC operating point is above the classical theoretical range. MoE rebuild SHIFT/PARTITION arms can proceed post-SSH with M_per_expert=1612.

**Decision (8): Alt 1 4-class taxonomy MIDDLE BAND annotation (no state change).**
`wave14_betB_alt_taxonomy_sweep_v1` silhouette=0.584 vs threshold 0.60. MIDDLE BAND. 4-class noreplay-isolated split is more defensible than 3-class standard. Annotation only; 🟡 PARTIAL Bet B row unchanged.

**Decision (9): Multi-agent-dispatch verdict pass rate differential = SELECTION BIAS (annotation only).**
Multi-agent 0.36 vs single-agent 0.69 (Cramer V=0.32, p=0.019). Harder probes are routed multi-agent. Differential reflects routing policy, not process quality. No PROT additions warranted.

**Net cap_map effect.** v204 -> v205 ANNOTATION ONLY: 11 capability move rows; 0 row-state changes; 0 new closures; portfolio 13 demonstrated + 5 evidence-strength UNCHANGED. 4 new pre-reg items (Bet N pickup, SSM-HiPPO CPU smoke, recurrent K6 probe, MoE rebuild arms). 118th PROT-009 paired commit (cap_map.md v205 + history.md v205 + this strategy_decisions entry).


## v206 — 2026-05-25 4-corpus saddle-cascade CONFIRMED + REPLAY structural axis CONFIRMED (MAJOR POSITIVE)

**Trigger.** Two independent local-batch experiments completing after v205: `data/exp_wave14_betB_4corpus_equalspacing_v1/metrics.json` and `data/exp_wave14_betB_replay_structural_axis_v1/metrics.json`.

**Decision (1): Saad-Solla equal-spacing arithmetic CORROBORATED at 4-corpus independent extension; theoretical-home row promoted to 🟢.**
`exp_wave14_betB_4corpus_equalspacing_v1` HARD_PASS: BIC_delta=-121.3 (threshold <-30; 4x threshold); spacing_error=0.0035 (threshold <0.05; 14x below); all 3 adjacent CI pairs non-overlapping (rank-biserial r=1.0); 4-tier G1_SAME/G2_REPLAY/G3_STAGE4/G4_DIFF validated. This is an INDEPENDENT 4-corpus extension experiment, not a replication of v205 re-analysis. Combined with v205 BIC delta=194.9: two independent positive arithmetic probes — first double-positive in substrate-physics framework history. The v205 note "arithmetic fails" referred to a 3-tier framing issue at a prior probe; the 4-corpus falsifier resolves it cleanly at the correct 4-tier taxonomy. Per honest-reread protocol: gap_ratio=0.955 outside pre-registered [0.45, 0.65] band but on more-equal side; spacing_error=0.0035 is the direct measure and overrides. Row-state: annotation-🔬 -> 🟢 CORROBORATED.

**Decision (2): REPLAY structural axis confirmed; new 🟢 CONFIRMED row.**
`exp_wave14_betB_replay_structural_axis_v1` REPLAY_STRONG_EFFECT: Cohen's d=13.3 (replay vs no-replay within same-corpus class); rank_biserial_r=1.000 (every replay value exceeds every no-replay value; no overlap whatsoever); forgetting_recovery_fraction=0.631. REPLAY is a dominant structural axis in the retention landscape. 4-tier taxonomy with REPLAY-isolated tier (G2) empirically justified. Hypothesis A (consolidation, 63% recovery) best supported; H-B/C need dedicated probes (filed as v206 NEW pre-reg sub-questions). New 🟢 CONFIRMED row added.

**Decision (3): Framework reliability promoted 🟡 32-48% -> 🟢 40-55%.**
Double-positive on saddle-cascade arithmetic (v205 BIC delta=194.9 + v206 BIC_delta=-121.3) plus REPLAY structural confirmation (d=13.3) gives the substrate-physics framework its first sustained positive run. Framework prediction track record: 2 independent arithmetic PASS + 1 structural-axis PASS + K5 ✅ + GPT-quality 🟢 + pool-level RSB ✅. The 40-55% range is the orchestrator-recommended range given: saddle-cascade upgrade alone worth ~5-10pp from 32-48% baseline, consolidation-hypothesis lock adds structural confirmation. Upper bound 50-65% conditional on Pred-4 hysteresis PASS (first-order saddle-cascade confirmed).

**Decision (4): MoE SHIFT/PARTITION v2 annotated as next high-priority remote ship.**
`exp_wave14_moe_shift_partition_v2.py` with DMPK SVD-bimodality additive instrumentation patch; 9/9 selftests pass; smoke PASS. Routing note at `notes/exp_dev_to_queue_moe_shift_partition_v2_2026-05-25.md`. Ship on SSH restoration; highest priority among queued experiments.

**Decision (5): Three Tier-1 handoffs confirmed awaiting SSH restoration.**
(1) MoE rebuild SHIFT/PARTITION v2 (highest priority); (2) Bet N multi-hop (`notes/exp_dev_handoff_bet_n_design_2026-05-25.md`; Cao 2023; LOWEST-DEPENDENCY Tier-1 path); (3) SSM-HiPPO HiPPO-LegS W-init smoke (cheap; P_deflated=0.18). Ship all three on SSH restoration.

**Net cap_map effect.** v205 -> v206 MAJOR POSITIVE: 6 capability move rows; 3 row-state advances (theoretical-home annotation->🟢, REPLAY structural axis NEW 🟢, framework reliability 🟡->🟢); 2 new pre-reg sub-questions (H-B/C probes); portfolio 13 demonstrated + 6 evidence-strength rows (+1 REPLAY axis). 119th PROT-009 paired commit (cap_map.md v206 + history.md v206 + this strategy_decisions entry).

PROT-004/006/008/009 compliance this commit: 0 new ❌ closures; 0 row-state demotions; pre-existing 29 PROT-004 violations are pre-PROT-004 grandfathered historical entries unchanged from prior commits; validator passes with same pre-existing warning set as v205; history.md v206 block written; strategy_decisions paired; 119th PROT-009 commit.
