# Strategy request: 2 follow-on experiments for 2 negative-result drills (percolation K=1 N-falsification + PP-11 Hadamard family rejection)

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_negative_results_2x_deep_2026-06-01.md` (full drill synthesis)
**Trigger**: verdict_processed HIGH 2026-06-01 11:27 reporting both negative results; user dispatched 2x deep research

## TL;DR

Both negative results have RESCUE PATHS cheaper than the experiments that produced them. Two cheap, diagnostic tests dispatchable in parallel (no resource contention):

| Test | What it discriminates | Cost | Pre-reg HARD-PASS |
|---|---|---|---|
| **1A** percolation depth-sweep | per-hop physics vs multi-hop composition cliff | ~18 CPU-min | depth=1 signal N-independent within 10%; divergence appears only at depth >= 3 |
| **2A** Kronecker rotation product cleanup | cleanup-driven gap vs pre-cleanup signal bias | ~1 eng-week | gap <2pp on 5/5 seeds at N=4096 + audit accuracy >=95% |

Each test substantively narrows the rescue space regardless of PASS/FAIL.

## Test 1A — Percolation K=1 depth-sweep diagnostic (CPU)

**Pre-reg framing**: The percolation framework's K=1 N-independence prediction failed at depth=5 large-N. Most parsimonious explanation (not requiring a new framework): per-hop K=1 signal is N-independent (percolation valid at depth=1); depth=5 composition crosses a reliability threshold whose position in (N, M, D) space is N-dependent. This is a *composed-function threshold effect*, not a substrate-physics failure.

**Experimental design (for exp_dev to refine; per [[feedback-no-experiment-design-in-prompts]])**:
- K=1 fixed; alpha = M/N = 16 fixed
- Sweep N ∈ {4096, 16384}; depth ∈ {1, 2, 3, 5}; 3 seeds each
- 24 runs total at ~45 sec wall each ≈ 18 CPU-min

**Pre-reg bands**:
- **HARD-PASS (composition cliff)**: depth=1 signal at N=4096 and N=16384 within 10% of each other; depth=3 or depth=5 shows divergence >2× → percolation valid at per-hop, depth-composition is the new framework gap
- **HARD-FAIL (per-hop physics IS N-dependent)**: depth=1 already shows >20% divergence between N values → forces escalation to FSS power-law sweep (Test 1B)
- **MIDDLE-BAND**: depth=1 divergence in [10%, 20%] → ambiguous; escalate to 5-seed for tighter statistics

**Contingent escalation (Test 1B if 1A HARD-FAIL)**: GPU-warranted FSS power-law sweep. K=1, depth=5, alpha=16, N ∈ {4096, 8192, 16384, 32768}, 5 seeds. Pre-reg HARD-PASS: clean log-log power-law R²>0.99, exponent γ ∈ [0.5, 3.0]. Cost ~100 GPU-min.

**Why this matters**: K>=2 production unaffected; framework predictive power at K=1 substrate-physics-only mode is what's at stake. If 1A HARD-PASS, percolation framework keeps its single-hop prediction and we add a "depth-composition threshold" caveat at K=1. If 1A HARD-FAIL, we lose K=1 framework entirely and need FSS or alternative.

## Test 2A — Kronecker rotation product cleanup (engineering)

**Pre-reg framing**: PP-11 4WC v4 compound Hadamard performed WORSE than v3 single-Hadamard. This rejects the entire bipolar-codebook-orthogonality rescue family and strongly suggests the 5pp structured-key gap is *intrinsic second-order Hebbian cross-talk in the weight matrix capacity statistics* (not in codebook angular separation). 

If true, the only rescues are: (a) better post-bias cleanup (this test), (b) leave dense bipolar entirely (Test 2B sparse block codes), or (c) accept the gap and re-position (Test 2C).

Test 2A is the cheapest probe AND diagnostic at the root-cause level: if Kronecker cleanup closes the gap, the gap was cleanup-driven (Hypothesis B/C dominant). If not, pre-cleanup signal bias is confirmed (Hypothesis A dominant) and the cheap-fix space is empty.

**Reference**: Liu et al. 2025 (NeurIPS Neurosymbolic / ICNLR 2025), "Linearithmic Clean-up for Vector-Symbolic Key-Value Memory with Kronecker Rotation Products" — published reference code expected.

**Engineering scope (for testbed/exp_dev)**:
- Encoding: current dense bipolar substrate UNCHANGED
- Cleanup codebook: replace standard dot-product codebook lookup with Kronecker-rotation-product structure (O(N log N) lookup; linearithmic separation between correct and spurious entries)
- Audit primitive: ELEMENT-WISE UNBIND UNCHANGED (the audit moat is fully preserved by construction; only cleanup changes)
- Test scope: depth=3 chains, structured keys (rule_type ⊙ premise1 ⊙ premise2), 5 seeds, N=4096
- Compare against random-key baseline at same capacity load

**Pre-reg bands**:
- **HARD-PASS**: gap <2pp on 5/5 seeds + audit accuracy ≥95% on exact component recovery under structured keys
- **HARD-FAIL**: gap ≥4pp on majority seeds, OR audit accuracy <95% on any seed
- **MIDDLE-BAND**: gap in [2pp, 4pp] OR partial seed PASS → either retest at higher N or proceed to Test 2B

**Audit-moat veto pre-assessment**: VERY LOW RISK because encoding and unbinding are identical to current substrate; only codebook-lookup structure changes.

**Contingent escalations**:
- **2B (sparse block codes, DSBC/BCF; ~2-3 eng-weeks)** if 2A HARD-FAIL. Most principled attack on Hypothesis A root cause. Published BCF achieves 99% factorization in clean settings. Audit-moat risk MODERATE-LOW.
- **2C (acceptance + re-positioning; 0-2 eng-weeks docs only)** if 2B ALSO HARD-FAIL or too expensive. Promote PP-9 depth-conditional caveat to first-class product boundary. P(remaining technical fix works) < 0.25 by that point.

**Defer**:
- **GHRR** (already in PP-11 ladder) — audit-moat-veto-LIKELY per FHRR precedent (85-92% audit accuracy); R2.2 sparse block codes is the better next-encoding candidate (preserves exact unbinding)
- **Path-dependent chain-level keys** — higher engineering risk + audit API surface disruption

## Diagnostic observable to track across BOTH smoke tests

Per drill 2 synthesis: split accuracy into three single-hop conditions for any encoding-tested rescue:
- (a) random keys
- (b) structured keys with **random** factor codebooks
- (c) structured keys with **orthogonal** factor codebooks

If (b) ≈ (c), codebook-level fixes are unlikely (consistent with v3/v4 already showing this). This diagnostic split should be added to ANY future PP-11 rescue test rig so that we have a clean read on whether to keep iterating codebook-level fixes.

## Cap_map implications

Both tests inform pre-existing cap_map rows; neither requires new rows. Strategy / orchestrator decides:

1. **Path D K=1 substrate-physics row**: currently caveat says percolation framework valid; if 1A HARD-PASS, sub-caveat added "framework predicts per-hop; depth-composition cliff at K=1 D≥3 large-N is unexplained by percolation, candidate framework: FSS"
2. **PP-11 reasoning-store row**: currently 🟡 0.40-0.55; if 2A HARD-PASS, row LIFT to 0.55-0.70 (5pp gap closed); if HARD-FAIL, sub-caveat added "Hadamard-orthogonality family REJECTED + Kronecker-cleanup REJECTED; remaining rescues: DSBC sparse block codes OR depth-conditional acceptance"
3. **PP-9 amortization economics row**: depth-conditional caveat already filed today; if PP-11 closes via 2A, the depth-conditional viability envelope EXPANDS substantially

## Contract for strategy

Strategy decides:
1. Whether to dispatch 1A immediately (CPU available; ~18 min) — research strongly recommends YES
2. Whether to dispatch 2A to testbed (~1 eng-week) — research strongly recommends YES
3. Whether to PRE-AUTHORIZE the contingent escalations (1B if 1A FAIL; 2B if 2A FAIL; 2C if 2B FAIL) so that NO-GO branches don't create strategic vacuums
4. Cap_map caveat updates per the implications above

## Method notes

- 2 parallel Sonnet drills (~3 min each, ~3K tokens combined); main-thread synthesis ~20 min; per [[feedback-subagent-model-optimization]]
- Per [[feedback-2x-means-depth]]: drills went DEEP on existing findings, not verification re-runs
- Per [[feedback-rehabilitation-after-rejection]]: 4-5 rescue candidates listed per drill before any closure recommendation
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest diagnostic tests sequenced first
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; novel-synthesis cap at 0.50
- Per [[feedback-no-experiment-design-in-prompts]]: routing hands TASK + WHY + CONTRACT + AUTONOMY; sweep grid + threshold formulas remain exp_dev's call

## Files referenced

- `notes/research_negative_results_2x_deep_2026-06-01.md` (full drill synthesis with all 4-5 rescue candidates per drill)
- `notes/substrate_capability_map.md` (PP-11 row; Path D K=1 sub-row; PP-9 row)
- `notes/strategy_request_to_strategy_pp9_depth_conditional_caveat_2026-06-01.md` (PP-9 row depth-conditional caveat, filed today, already processed by orchestrator)
- Liu et al. 2025 — Kronecker rotation product cleanup reference paper

## Closing

Move to `routed_completed/` when strategy decides 1A + 2A dispatch (or formally declines with rationale).


---
## Close note
Acted-on 2026-06-01: Test 1A shipped to CPU queue (path_d_percolation_depth_sweep_v1_n4096, remote_cpu_queue, timeout=14400s); Test 2A routed to testbed as engineering handoff; contingent escalations 1B/2B/2C noted as pre-authorized pending verdicts.