# Testbed handoff: PP-11 Test 2A Kronecker rotation product cleanup (~1 eng-week)

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Source**: `notes/strategy_request_to_strategy_negative_results_followon_experiments_2026-06-01.md` Test 2A
**Trigger**: PP-11 4WC v4 Hadamard-double-delta HARD_FAIL (worse than v3); Hadamard rescue family CLOSED at cap_map v312

## TL;DR

Research surfaced Liu et al. 2025 Kronecker rotation product cleanup as the cheapest probe AND root-cause-level diagnostic for the PP-11 5pp structured-key gap. If gap closes: cleanup-driven (rescue path). If not: confirms intrinsic Hebbian cross-talk in W capacity statistics (no cheap fix; escalate to Test 2B sparse block codes ~2-3 eng-weeks).

**Engineering cost**: ~1 eng-week. **Audit-moat risk**: VERY LOW (encoding + unbinding unchanged; only cleanup codebook structure changes).

## Why now

PP-11 row at cap_map v312 = 🟡 0.40-0.55. Hadamard family closed today. GHRR (in PP-11 ladder) has audit-moat-veto risk per FHRR precedent (85-92% audit accuracy). Kronecker rotation product cleanup is research's cheapest next-rescue with NO audit-moat veto risk.

Research's full rationale + reference (Liu et al. 2025 NeurIPS Neurosymbolic / ICNLR 2025 "Linearithmic Clean-up for Vector-Symbolic Key-Value Memory with Kronecker Rotation Products"): see source routing.

## Engineering scope

Per research routing Test 2A:

1. **Encoding**: current dense bipolar substrate UNCHANGED
2. **Cleanup codebook**: replace standard dot-product codebook lookup with Kronecker-rotation-product structure
   - O(N log N) lookup (linearithmic separation between correct and spurious entries)
   - Liu et al. 2025 published reference code expected — adapt to substrate's existing codebook layout
3. **Audit primitive**: ELEMENT-WISE UNBIND UNCHANGED (audit moat preserved by construction; only cleanup structure changes)
4. **Test rig**:
   - depth=3 chains
   - structured keys (rule_type ⊙ premise1 ⊙ premise2)
   - 5 seeds
   - N=4096
   - Compare against random-key baseline at same capacity load

## Pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND (research-locked)

- **HARD-PASS**: gap <2pp on 5/5 seeds + audit accuracy ≥95% on exact component recovery under structured keys
- **HARD-FAIL**: gap ≥4pp on majority seeds OR audit accuracy <95% on any seed
- **MIDDLE-BAND**: gap in [2pp, 4pp] OR partial seed PASS — either retest at higher N or proceed to Test 2B

## Diagnostic observable to embed (research's drill recommendation)

Split accuracy into 3 single-hop conditions:
- (a) random keys
- (b) structured keys with **random** factor codebooks
- (c) structured keys with **orthogonal** factor codebooks

If (b) ≈ (c) in v3/v4 data (likely; per Hadamard family closure), codebook-level fixes unlikely to bridge the gap. This diagnostic split should be embedded in the Test 2A rig AND in any future PP-11 rescue.

## Contingent escalations (pre-authorized)

If Test 2A HARD_FAIL:
- **Test 2B (DSBC sparse block codes, ~2-3 eng-weeks)** — most principled attack on Hypothesis A intrinsic-cross-talk root cause. Published BCF achieves 99% factorization in clean settings. Audit-moat risk MODERATE-LOW. Pre-authorized; testbed can dispatch without orchestrator re-confirmation if 2A fails.

If Test 2B ALSO HARD_FAIL:
- **Test 2C (acceptance + re-positioning, 0-2 eng-weeks docs only)** — promote PP-9 depth-conditional caveat to first-class product boundary. P(remaining technical fix works) < 0.25 by that point. Pre-authorized.

## Audit-moat veto pre-assessment

VERY LOW RISK for Test 2A specifically because encoding and unbinding are identical to current substrate; only codebook-lookup structure changes. Per research: "the audit moat is fully preserved by construction."

If during Phase 1 implementation testbed discovers that Kronecker structure DOES affect audit (e.g., element-wise unbind no longer recovers exact components), file IMMEDIATE routing to orchestrator — that's a much bigger finding than the cleanup verdict.

## Cap_map implications

Per research routing:
- **PP-11 reasoning-store row**: currently 🟡 0.40-0.55; if 2A HARD-PASS, row LIFT to 0.55-0.70 (5pp gap closed); if HARD-FAIL, sub-caveat added "Hadamard-orthogonality family REJECTED + Kronecker-cleanup REJECTED; remaining rescues: DSBC sparse block codes OR depth-conditional acceptance"
- **PP-9 amortization economics row**: depth-conditional caveat already filed today; if PP-11 closes via 2A, the depth-conditional viability envelope EXPANDS substantially (0.95^d → 0.98^d)

## Sequencing vs other testbed work

Defer behind:
- **PP-8 Week 2 feasibility smoke** (user-authorized today; ~$60-150 H100; load-bearing for 7-8 week build)
- **PP-3 Phase 2 compliance-first design** (in progress; ~6-9 days local)

Run in parallel with:
- **Anthropic Phase 2 production query eval** (pre-authorized $20-50; different resource pool)
- **Dashboard + watchdog events** (just-authorized; different resource pool)
- **Test 1A percolation depth-sweep** (CPU-only; orchestrator-shipped this turn via exp_dev)

So Test 2A can start when testbed bandwidth opens up — ideally after Phase 1 of PP-8 Week 2 dispatches (Phase 1 = Q-Former bridge wiring smoke).

## What testbed will do next

- Move this handoff to `routed_completed/` when Test 2A engineering work begins (not when complete)
- Status_log entry HIGH when each escalation step starts
- File deliverable + routing back to orchestrator at Test 2A verdict

## Files referenced

- This handoff
- `notes/strategy_request_to_strategy_negative_results_followon_experiments_2026-06-01.md` (source routing; Test 2A spec)
- `notes/research_negative_results_2x_deep_2026-06-01.md` (full drill synthesis)
- Cap_map v312 PP-11 row + PP-9 row
- Liu et al. 2025 reference (testbed has internet to fetch published code)

## Closing this routing

Testbed moves to `routed_completed/` when Test 2A dispatches.
