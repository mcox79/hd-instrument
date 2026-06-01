# exp_dev hand-off — v273 overnight refill (user-delivered triage strategy 2026-05-29)

**Filed:** 2026-05-29 by strategy_scribe (cap_map v272 -> v273 annotation trigger).

**Trigger:** User-delivered overnight-refill strategy after GPU queue drained at v272. Explicit TRIAGE framing: three at-risk claims need decisive resolution within 24-48h. GPU budget ~24-48 GPU-hours. A1 RUN FIRST directive from user.

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent at time of filing).

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: anchor names, N, M, K, seed count, threshold bands (HARD-PASS / HARD-FAIL / middle-band), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, parameter sweeps. Orchestrator passes TASK + WHY + CONTRACT; exp_dev decides implementation details.

---

## Strategic context (why this batch matters)

This is a TRIAGE moment, not an exploration moment. Three substrate claims are at-risk or open after the v272 13-verdict GPU drain:

1. **BE-1 cost-advantage (KF-2)** — v272 precision-floor sweep (A1-A4 cluster below) showed quantization-INSENSITIVE behavior: INT1 binary matches FP32 on isolation, which means W-magnitude was NOT the operative path in that test. The 32x cost-advantage claim has NOT been validated. It needs a different test where W-magnitude actually matters to the outcome.

2. **Steerability (KF-5)** — v272 region C/D probes showed substrate is BETA-INVARIANT at tested operating points. KF-5 phase-mechanism subhypothesis closed. The only remaining door is fine-beta sweep near beta_c=10 (B1) and codebook-axis steerability (B3). This is last-chance territory.

3. **Bet B Tier-1** — Stage-A retention sub-0.80 bar confirmed across 3 training-axis rescues (epochs / batch-size / loss-weighting). Training-axis rescues are exhausted. Architectural rescue is the only remaining path.

Context pointers:
- `notes/substrate_capability_map.md` v272 — at-risk annotations on KF-2 BE-1, KF-5, Bet B 4-stage rows
- `notes/strategy_decisions_2026-05-29.md` — v272 verdict-handler decisions documenting all three at-risk claims
- `notes/strategy_request_to_exp_dev_v273_A1_be1_soft_readout_2026-05-29.md` — A1 split-out with RUN-FIRST flag (read this first, ship A1 before any other anchor in this batch)
- `data/orchestrator_status_log.jsonl` (last 5 entries) — recent verdict context

---

## USER PRIORITY ALLOCATION

User-specified tier structure for ~24-48 GPU-hours:

**TIER 1 MUST RUN (~4 GPU days):** A1 + A2 + B1 + C1 + C2
**TIER 2 (~5.5 GPU days if budget permits):** A3 + A4 + B3 + D1
**TIER 3 DISCOVERY (~4 GPU days if budget permits):** D3 + E1 + E2 + C4
**TIER 4 SPECULATIVE:** D2 + D4 + D5 + B2 (B2 contingent on B1 showing near-boundary signal)

exp_dev ships Tier 1 first and completely before routing Tier 2 anchors. Tier 3 and 4 only if Tier 1+2 are shipped and GPU capacity remains.

---

## RUN-A1-FIRST DIRECTIVE (user explicit)

**A1 is the single highest-priority anchor in this entire batch.** Ship A1 before any other anchor. Reason: A1 is the cheapest test that directly addresses the v272 strategic over-claim on BE-1 cost-advantage. If A1 passes with precision-sensitive softmax readout, the cost-advantage narrative re-validates. If A1 fails, it gives honest retraction early.

See `notes/strategy_request_to_exp_dev_v273_A1_be1_soft_readout_2026-05-29.md` for the A1 split-out.

---

## Cluster A — KF-2 BE-1 W-MAGNITUDE-OPERATIVE PROBES

**Why this cluster:** v272 caught that the precision-floor isolation test was quantization-INSENSITIVE (INT1 = FP32), which means W-magnitude was NOT operative in that test design. The 32x cost-advantage claim requires a test where W-magnitude actually matters. Cluster A provides four complementary angles on this question.

**Strategic outcome if cluster passes:** BE-1 cost-advantage claim re-validates; strategic 32x narrative recovers.
**Strategic outcome if cluster fails:** Honest retraction: cost-advantage is not a substrate property at the tested operating envelope; reframe or close the narrative.

### A1 — Soft-readout BE-1 precision sweep (TIER 1, RUN FIRST)
- Task: test BE-1 edit-isolation under softmax(beta=32) readout (NOT argmax) across precision levels spanning FP32 down to INT1.
- Why: argmax readout is insensitive to magnitude — the previous test's isolation score is dominated by rank not magnitude. Softmax readout with high beta directly exercises W-magnitude differences between precision levels. This is the cheapest redesign that makes W-magnitude operative.
- User size hint: ~half GPU day, 6 precision levels x 3 seeds.
- Cluster: KF-2 BE-1 W-MAGNITUDE-OPERATIVE.
- Priority pointer: `notes/strategy_request_to_exp_dev_v273_A1_be1_soft_readout_2026-05-29.md` (split-out).

### A2 — Retrieval accuracy under quantized W on 10K pool
- Task: measure top-1 retrieval accuracy on a 10K memory pool under the same precision sweep. Retrieval is magnitude-sensitive: at low precision, W entries are coarser and retrieval should degrade measurably if W-magnitude is load-bearing.
- Why: complements A1; if retrieval acc drops at INT4/INT8 while isolation passes, the cost-advantage story is nuanced (isolation is magnitude-insensitive but retrieval is not). If retrieval acc also holds at INT4, the substrate has genuine quantization robustness.
- User size hint: ~half GPU day, same precision sweep.
- Cluster: KF-2 BE-1 W-MAGNITUDE-OPERATIVE.

### A3 — TCFT var_ratio at quantized precision
- Task: measure TCFT deletion-certificate var_ratio metric under quantized W at 4 precision levels x 3 seeds.
- Why: deletion certificate is the highest-value product feature; its foundation under quantization needs validation before cost-advantage claim extends to that feature. If TCFT var_ratio degrades at low precision, deletion certificate has a precision floor that constrains cost-claim.
- User size hint: ~1 GPU day.
- Cluster: KF-2 BE-1 W-MAGNITUDE-OPERATIVE, deletion-certificate sub-feature.

### A4 — Multi-hop accuracy under quantized W
- Task: measure multi-hop retrieval accuracy under quantized W at several hop-depths.
- Why: multi-hop is the most W-magnitude-sensitive operation (errors multiply per hop). If multi-hop degrades at INT4/INT8, the precision floor is real but narrow (applies to chained inference not simple retrieval). Provides the sharpest signal on W-magnitude operativity.
- User size hint: ~1 GPU day.
- Cluster: KF-2 BE-1 W-MAGNITUDE-OPERATIVE, multi-hop sub-feature.

---

## Cluster B — KF-5 STEERABILITY FINER PROBE

**Why this cluster:** v272 found substrate BETA-INVARIANT at regions A/B (beta=8) vs C/D (beta=64). That was coarse sampling. KF-5 phase-mechanism subhypothesis was closed. But near-boundary steerability near beta_c=10 is the last unexplored axis. If nothing shows here, honest closure is warranted.

**Strategic outcome if B1 finds signal:** steerability lives at fine-beta near beta_c; B2 follow-up probes the multi-hop coupling. Product: phase-controlled memory mode.
**Strategic outcome if B1 finds no signal:** KF-5 steerability direction closes honestly; Cluster B3 probes codebook-axis as independent steerability axis.

### B1 — Fine-beta sweep near beta_c (TIER 1)
- Task: probe KF behavior at fine beta resolution near the known transition at beta_c=10. Previous sweeps used coarse beta grid and missed near-boundary dynamics.
- Why: last-chance test for the steerable-killer-feature hypothesis on beta-axis. If any near-boundary effect exists (qualitative difference in KF metrics within a narrow beta window around 10), it would rehabilitate the steerability narrative.
- User size hint: ~2 GPU days, fine beta grid x multiple M_frac values x 3 seeds.
- Cluster: KF-5 STEERABILITY.
- Priority: TIER 1.

### B2 — Multi-hop near beta_c (TIER 4, contingent)
- Task: if B1 shows any near-boundary effect, probe multi-hop accuracy specifically at those beta operating points.
- Contingency: ONLY ship if B1 returns signal; do not ship B2 if B1 finds no steerability.
- Why: multi-hop is the most demanding KF operation; if steerability only shows at multi-hop depth, B2 pins that regime.
- User size hint: ~1.5 GPU days.
- Cluster: KF-5 STEERABILITY, multi-hop coupling.

### B3 — Codebook-axis steerability (TIER 2)
- Task: probe whether different codebook families (Kerdock, Hadamard, Gaussian, BSC, sparse-BSC) give qualitatively different KF behavior at fixed high-beta operating point.
- Why: steerability via codebook choice is independent of beta-axis. If codebook selection allows qualitative KF-behavior steering, the product story is "choose your operating mode via codebook" rather than "choose via beta". This is independent of B1 outcome.
- User size hint: ~1.5 GPU days, 5 codebook families x 5 KFs x 3 seeds.
- Cluster: KF-5 STEERABILITY, codebook-axis.
- Priority: TIER 2.

---

## Cluster C — BET B ARCHITECTURAL ALTERNATIVES

**Why this cluster:** training-axis rescues for Bet B 4-stage are exhausted (epochs / batch-size / loss-weighting all confirmed Stage-A sub-0.80 bar). Architectural alternatives are the only remaining path to Tier-1 promotion. Cluster C probes 5 independent architectural hypotheses. C1 and C2 are the cheapest and most decisive.

**Strategic outcome if C1 or C2 passes:** architectural rescue found; Bet B Tier-1 unblocked; CL product narrative recovers.
**Strategic outcome if C1-C5 all fail:** Bet B architectural ceiling confirmed; honest cap_map closure with full rescue enumeration.

### C1 — Wider Phase A at N=8192 then return to N=4096 for B/C/D (TIER 1)
- Task: run Phase A at N=8192 to build a wider representation, then continue to Phases B/C/D at N=4096. Hypothesis: Stage-A retention bottleneck is storage-bound; giving it more representational capacity resolves the sub-0.80 bar.
- Why: cheapest architectural variant; tests N-bounded ret_A with minimal script changes.
- User size hint: ~half GPU day.
- Cluster: BET B ARCHITECTURAL.
- Priority: TIER 1.

### C2 — Frozen W for Phase A, plastic for B/C/D (TIER 1)
- Task: fix W during Phase A (prevent interference from Phase-A Hebbian updates) and allow normal Hebbian updates for Phases B/C/D.
- Why: tests whether Stage-A retention failure is caused by Phase-A self-interference. If frozen-W Phase A yields ret_A >= 0.80, the bottleneck is exactly the training dynamics in Phase A, not capacity.
- User size hint: ~half GPU day.
- Cluster: BET B ARCHITECTURAL.
- Priority: TIER 1.

### C3 — 2x M-allocation for Phase A specifically (TIER 3)
- Task: allocate double the memory capacity to Phase A's memory consolidation pass relative to Phases B/C/D.
- Why: tests storage-bound hypothesis from a different angle than C1; addresses whether Phase A simply needs more capacity to retain.
- User size hint: ~half GPU day.
- Cluster: BET B ARCHITECTURAL.
- Priority: TIER 3.

### C4 — Dual-W CLS framework (TIER 3)
- Task: use two separate weight matrices W_fast and W_slow, with W_fast for rapid within-phase learning and W_slow for slow cross-phase consolidation.
- Why: addresses structural interference between fast-learning updates and slow-consolidation signals; motivated by neuroscience complementary-learning-systems framing.
- User size hint: ~1 GPU day.
- Cluster: BET B ARCHITECTURAL.
- Priority: TIER 3.

### C5 — Hebbian-only Phase A pre-training (TIER 4)
- Task: use purely Hebbian (delta rule) training during Phase A only, then gradient for Phases B/C/D.
- Why: tests whether gradient-based Phase A training introduces the interference that delta-rule would avoid; simplest hybridization of training methods.
- User size hint: ~half GPU day.
- Cluster: BET B ARCHITECTURAL.
- Priority: TIER 4.

---

## Cluster D — DISCOVERY (regimes not yet probed)

**Why this cluster:** independent of triage, discovery of new operating regimes might reveal new KF candidates. TIER 2 (D1) and TIER 3 (D3) only.

### D1 — Very-low-M regime sweep (TIER 2)
- Task: probe substrate KF behavior at very low memory density (M_frac well below 1.0) across multiple KF types.
- Why: low-M regime is the under-explored end of the phase diagram; may harbor new KF behaviors not visible at standard M_frac=4-8 operating points. Could yield a high-precision-retrieval KF candidate distinct from all existing KFs.
- User size hint: ~2 GPU days, 4 M_frac levels x 5 KFs x 3 seeds at N=4096.
- Cluster: DISCOVERY.
- Priority: TIER 2.

### D2 — Very-high-beta regime (TIER 4)
- Task: probe KF behavior at very high beta (deterministic regime well past beta_c=10).
- Why: deterministic-retrieval KF candidate; might unlock a new behavior class.
- User size hint: ~1.5 GPU days.
- Cluster: DISCOVERY.
- Priority: TIER 4.

### D3 — Cleanup-strength continuous sweep (TIER 3)
- Task: vary cleanup strength from 0 to 1 continuously at multiple levels.
- Why: possible third orthogonal operating boundary; if KF metrics change sharply with cleanup-strength, cleanup-axis is a new steering axis.
- User size hint: ~1.5 GPU days.
- Cluster: DISCOVERY.
- Priority: TIER 3.

### D4 — Time-dependent driving (TIER 4)
- Task: periodic edit-query cycles at multiple frequencies.
- Why: substrate under periodic loading not yet probed; may reveal frequency-selective retention.
- User size hint: ~1.5 GPU days.
- Cluster: DISCOVERY.
- Priority: TIER 4.

### D5 — Two-substrate composition (TIER 4)
- Task: couple two substrate instances with varying coupling strength.
- Why: compositional architecture beyond single-W; tests substrate-substrate interaction dynamics.
- User size hint: ~1 GPU day.
- Cluster: DISCOVERY.
- Priority: TIER 4.

---

## Cluster E — LYAPUNOV x KF CORRELATION

**Why this cluster:** v269 opened a new Lyapunov dynamical-structure axis (yellow-smoke 55-68%). Cross-correlating KF metrics with Lyapunov spec_norm at same operating points may reveal dynamical structure underlying KF behavior.

### E1 — Lyapunov spec_norm at every existing (N, M, beta, codebook) point (TIER 3)
- Task: compute Lyapunov spec_norm at every operating point where KF metrics already exist in completed runs.
- Why: analysis from existing experiment outputs; cheapest possible Cluster E anchor (~half GPU day at most for re-analysis passes).
- User size hint: ~half GPU day (primarily analysis, not new training).
- Cluster: LYAPUNOV x KF.
- Priority: TIER 3.

### E2 — Lyapunov-targeted operating points for each KF (TIER 3)
- Task: identify the Lyapunov spec_norm value that maximizes each KF metric individually, then run targeted experiments at those operating points.
- Why: if KFs are maximized near spec_norm ~ 1 (edge-of-chaos hypothesis), this is a unifying design principle for the substrate.
- User size hint: ~1 GPU day.
- Cluster: LYAPUNOV x KF.
- Priority: TIER 3.

### E3 — Edge-of-chaos hypothesis test for multi-hop (TIER 4)
- Task: targeted test of whether multi-hop accuracy is maximized specifically at operating points where Lyapunov spec_norm ~ 1.
- Why: edge-of-chaos hypothesis is the most specific form of the dynamical-structure claim; multi-hop is the most sensitive probe.
- User size hint: ~1 GPU day.
- Cluster: LYAPUNOV x KF.
- Priority: TIER 4.

---

## Context pointers

- `notes/substrate_capability_map.md` v272 — at-risk KF-2, KF-5, Bet B annotations
- `notes/strategy_decisions_2026-05-29.md` — all v272 decisions and inline rescue sketches
- `notes/strategy_request_to_exp_dev_v273_A1_be1_soft_readout_2026-05-29.md` — A1 RUN-FIRST split-out
- `notes/strategy_overnight_refill_plan_v272_2026-05-29.md` — deep-strategy research delivery (18 GPU + 9 CPU plan filed by research agent)
- `data/orchestrator_status_log.jsonl` — last 5 entries for pipeline context
- `agents/exp_dev.md` Section 0 — Tier A/B/C queue routing policy

---

## Contract

- Pre-register HARD-PASS + HARD-FAIL + middle-band thresholds per [[feedback-envelope-expansion-fail-bands]] BEFORE smoke for each anchor.
- Self-test any closed-form formulas per [[feedback-strategy-spec-formula-selftests]] before coding.
- Smoke gate: run smoke first; proceed to FULL only on smoke clearance.
- Multi-seed FULL for TIER 1 anchors (minimum 3 seeds; 5 seeds preferred per production-scale standard).
- Queue routing per Tier A/B/C policy in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- Per-experiment `--timeout` required per [[feedback-per-experiment-timeout-required]]; formula: `1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)`; >14400s requires review before ship.
- POST-SHIP REMOTE VERIFY per [[feedback-ship-name-collision]]: queue_add.sh exit code 5 = post-ship verification failed; retry with different name.
- PROT-018 enforcement: anchor names with `_n<N>` suffix must match config.N; verify before ship.
- Kerdock codebook check: if anchor uses Kerdock, verify N has even log2(N) before ship.
- status_log entry per anchor shipped with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: anchor names, N, M, K, seed count, threshold bands, queue choice, ETA, smoke profile, FULL profile, parameter sweep values. The orchestrator passes ANCHORS + WHY; exp_dev decides implementation. If exp_dev determines a different sub-anchor within a cluster is cheaper or more decisive (e.g., A2 before A3 if retrieval-accuracy test is faster), that is exp_dev's call — except: A1 ships before any other anchor in this batch (user explicit directive).

exp_dev may substitute equivalent mechanism probes within a cluster (e.g., for C4 dual-W, may use a different two-weight architecture) as long as the task (testing the named hypothesis) is preserved.

---

## Filed by

strategy_scribe sub-agent (cap_map v272 -> v273 annotation trigger), 2026-05-29.
Hand-off ready for exp_dev dispatch. Read A1 split-out first: `notes/strategy_request_to_exp_dev_v273_A1_be1_soft_readout_2026-05-29.md`.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
