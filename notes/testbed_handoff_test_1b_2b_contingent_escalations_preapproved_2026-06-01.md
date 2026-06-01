# Testbed + Research handoff: Test 1B + Test 2B contingent escalations PRE-APPROVED

**From**: orchestrator
**To**: testbed + research (both will read on inbox poll)
**Date**: 2026-06-01
**Source**: `notes/routed_completed/strategy_request_to_strategy_negative_results_followon_experiments_2026-06-01.md` (Test 1A + 2A; this routing adds contingent-escalation pre-authorizations)
**Authorization**: USER EXPLICIT 2026-06-01 (~11:55 ET)

## TL;DR

Pre-approve BOTH contingent escalations from research's negative-results 2x deep so a HARD_FAIL on Test 1A or Test 2A doesn't create strategic vacuum:

- **Test 1B (FSS power-law sweep, GPU ~100 GPU-min)** — IF Test 1A HARD_FAIL. Cost ~$2-5 cloud Lambda OR ~2h local GPU. **PRE-APPROVED for orchestrator-dispatch via exp_dev when Test 1A FAIL verdict lands.**
- **Test 2B (DSBC sparse block codes, ~2-3 eng-weeks engineering)** — IF Test 2A HARD_FAIL. **PRE-APPROVED for testbed-dispatch when Test 2A FAIL verdict lands.**

No additional user gates between Test 1A/2A FAIL verdicts and the contingent escalations dispatching. Don't make me come back.

## Test 1B pre-authorization (FSS power-law sweep; orchestrator-dispatched via exp_dev)

**Trigger**: Test 1A `path_d_percolation_depth_sweep_v1_n4096` lands HARD_FAIL (depth=1 already shows >20% divergence between N=4096 and N=16384 — per-hop K=1 physics IS N-dependent, percolation framework loses K=1 single-hop prediction).

**Spec sketch (exp_dev refines)**:
- K=1, depth=5, alpha=16 (M=16N)
- N in {4096, 8192, 16384, 32768}
- 5 seeds per cell
- Pre-reg HARD-PASS: clean log-log power-law R^2 > 0.99, exponent gamma in [0.5, 3.0]
- Pre-reg HARD-FAIL: no power-law shape detectable
- Pre-reg MIDDLE: power-law but exponent out of range OR R^2 in [0.95, 0.99]

**Strategic value**: empirically locates the N-scaling exponent for K=1 substrate-physics signal. Either gives finite-size-scaling framework as percolation's replacement (HARD-PASS) OR rules out FSS as the next framework candidate (HARD-FAIL, escalate research to find a third candidate).

**Cost estimate**: ~100 GPU-min = ~2h local GPU (if 8GB 4060 Ti sufficient) OR ~$2-5 cloud Lambda H100. Within standing cloud budget; no new user-go needed for cloud variant.

**Dispatch path**: orchestrator dispatches via /exp_dev with PROT-022 BSC guard (N=8192 log2-odd) — fall back to BSC explicitly OR skip N=8192 if Kerdock-required (exp_dev decides per design).

## Test 2B pre-authorization (DSBC sparse block codes; testbed-dispatched)

**Trigger**: Test 2A `pp11_kronecker_cleanup_test_2a_2026-06-01` lands HARD_FAIL (gap >= 4pp on majority seeds OR audit accuracy < 95% on any seed — Kronecker cleanup doesn't close the 5pp gap, confirming intrinsic Hebbian cross-talk hypothesis).

**Spec (per research's Test 2B description)**:
- Encoding: dense bipolar substrate REPLACED with DSBC sparse block codes / BCF (Distributed Sparse Block Codes; Block Cipher Factorization)
- Audit primitive: re-engineered for sparse block structure (audit moat risk MODERATE-LOW per research — sparse block codes preserve exact factorization for M < some-N-dependent capacity)
- Test rig: depth=3 chains, structured keys, 5 seeds, N=4096
- Compare against random-key baseline at same capacity load

**Pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND** (per research): same shape as Test 2A's bands (HP gap <2pp + audit >= 95% on exact factorization; HF gap >= 4pp OR audit < 95%).

**Engineering scope**: ~2-3 eng-weeks (substantially more than 2A's ~1 week because DSBC requires reworking codeword construction + audit primitive; published BCF achieves 99% factorization in clean settings).

**Audit-moat veto pre-assessment**: MODERATE-LOW — sparse block structure has formal properties that should preserve audit accuracy, but moat accuracy under real workload only verifiable empirically.

## Test 2C contingent acceptance (~0-2 eng-weeks docs only)

**Trigger**: Test 2B ALSO lands HARD_FAIL (or MIDDLE_BAND that doesn't meaningfully change PP-11 row positioning).

**Action**: promote PP-9 depth-conditional caveat to first-class product boundary. Re-position the substrate's product story as:
- "Audit-grade fast retrieval over pre-stored chains with depth-conditional quality bounds (0.95^d random-key baseline; ~0.95^d - 5pp structured-key worst-case)"
- "GDPR-grade deletion-cert compliance gate (cert FP <= 0.01% TPR >= 99.9%)" — pending cert_threshold v2 verdict
- "Production deployment at K=2 op-point: 50x latency reduction vs K=100" — already validated v309
- DROP the "substrate as reasoning store at production-equivalent quality" framing

**No experiment**. Documentation-only pivot. P(remaining technical fix works) < 0.25 by that point.

**This is pre-approved as the floor outcome**: even if 2B fails, the product has clear positioning that's empirically grounded; this just makes the depth-ceiling explicit in customer-facing materials.

## Strategic context

The negative-results-2x-research pattern (per memory) is operating cleanly:
- R4 percolation refutation → research files 2x drill → orchestrator dispatches diagnostic Test 1A → if FAIL, FSS framework probe Test 1B → if FAIL, no framework candidate at this layer
- PP-11 4WC v4 closure → research files 2x drill → orchestrator dispatches Test 2A → if FAIL, sparse-block-codes Test 2B → if FAIL, acceptance + re-positioning Test 2C

The contingent escalation ladder has finite depth and known floor; pre-authorizing eliminates round-trip latency.

## What testbed/research/orchestrator do at each branch

| Verdict | Who dispatches | Authorization |
|---|---|---|
| Test 1A HARD_PASS | (no escalation) | — |
| Test 1A HARD_FAIL → Test 1B | orchestrator via /exp_dev | PRE-APPROVED (this routing) |
| Test 1A MIDDLE_BAND | testbed re-runs with 5 seeds | (no new auth needed) |
| Test 1B HARD_PASS | (no escalation) | — |
| Test 1B HARD_FAIL or MIDDLE | research drills next framework candidate | (research-discipline) |
| Test 2A HARD_PASS | (no escalation) | — |
| Test 2A HARD_FAIL → Test 2B | testbed engineering | PRE-APPROVED (this routing) |
| Test 2A MIDDLE_BAND | testbed re-runs at higher N OR proceeds to 2B | (no new auth needed) |
| Test 2B HARD_PASS | (no escalation) | — |
| Test 2B HARD_FAIL → Test 2C | testbed docs pivot | PRE-APPROVED (this routing) |

## Files referenced

- `notes/routed_completed/strategy_request_to_strategy_negative_results_followon_experiments_2026-06-01.md` (Test 1A + 2A source)
- `notes/research_negative_results_2x_deep_2026-06-01.md` (research full drill synthesis)
- `notes/testbed_handoff_pp11_kronecker_cleanup_test_2a_2026-06-01.md` (Test 2A engineering handoff)
- Cap_map v312 (post-R4-refutation; PP-11 at 0.40-0.55; Path D row at 0.92-0.98 unchanged)

## Closing this routing

Move to `routed_completed/` when EITHER Test 1A or Test 2A's first verdict-handler verdict lands. Or when both land. Either way; one transition to closed state.
