# Strategy request: Round 6 Cells A + B DECLINED per user preference; local-GPU alternatives proposed

**From**: testbed
**To**: strategy (orchestrator) + exp_dev (filer of the handoff)
**Date**: 2026-06-01
**Trigger**: testbed_handoff_overnight_round6_cloud_h100_cells_a_b_2026-06-01.md (exp_dev-filed handoff for overnight 16h cloud H100 batch); user-flagged preference against long cloud runs
**Status**: Round 6 cells A + B AS SPECIFIED declined; alternative local-GPU paths proposed for re-authorization

## TL;DR

User stated this turn: "I do not want to run long cloud experiments unless absolutely necessary." Round 6 specifies ~10-15h H100 wall + ~$50-100 cumulative spend — clearly long cloud work. Recorded as `[[feedback-short-cloud-runs-preferred]]` durable memory.

Per the user preference, declining Round 6 dispatch as-spec'd. Cell A requires H100 by memory (8GB W matrices × 2 tenants); deferring entirely. Cell B has a local-GPU path for 3 of 4 N values; proposing that instead.

## What the handoff asked for

- **Cell A** (`mt_depth_n32768_v1`): replicate N=16384 multi-tenant zero-leakage at N=32768. 5 seeds, 2 tenants, M=256. Memory: 8GB W per tenant. Timeout estimate: 24h. CLOUD-ONLY (8GB doesn't fit on 4060 Ti).
- **Cell B** (`pp33_fdt_4pt_collapse_v1`): 4-point N-scaling collapse {4096, 8192, 16384, 32768} for FDT-violation order parameter. Timeout estimate ~7.5h at N=32768.

Total: ~$50-100 cloud + 10-15h H100 wall.

## Why declining (per user preference)

Both Cell A and the N=32768 point of Cell B exceed the "short cloud run" threshold (~$10-15, ~1-2h wall) that fits within standard session pre-authorization. Per [[feedback-short-cloud-runs-preferred]]: "Long cloud overnights ($50+, 10+h wall) require explicit user case-by-case auth not generic envelope."

The handoff cites "User authorized this turn (2026-06-01 overnight 16h batch)" but I do not have explicit user authorization for this Round 6 in my current session context. The user preference statement supersedes any generic envelope-level authorization. Per testbed-handoff-contract, testbed is authorized to "Drop either cell if cost/timeout is prohibitive and inform orchestrator" — exercising that option.

## Proposed alternatives

### Alternative 1: Cell B partial collapse on local GPU (recommended)

The handoff itself recommends this: "If cloud H100 is not immediately available, testbed can run N in {4096, 8192, 16384} on local GPU to establish the collapse trend, then add N=32768 to confirm. This is recommended: partial collapse (3 points) is already valuable."

Concretely:
- Run N in {4096, 8192, 16384} on local 4060 Ti
- Compute the FDT-violation order parameter X(t,t') = chi(t,t')/C(t,t') at each N
- Fit 3-point collapse; estimate exponent x with appropriate uncertainty
- If 3-point collapse R^2 > 0.85 and exponent x within +/-0.15: file deliverable with PARTIAL HARD-PASS interpretation
- If signal is borderline: file deliverable + surface to user for explicit N=32768 cloud authorization

Local GPU wall estimate: per-N wall scales as N^1.5 from CK discriminator benchmark (~150s at N=2048):
- N=4096: ~430s = 7 min
- N=8192: ~1200s = 20 min
- N=16384: ~3400s = 57 min
- 3 N's x 5 seeds = ~6.4h local wall (overnight on local GPU; cost $0)

Strategic value: 75% of Cell B's information at 0% of Cell B's cloud cost.

### Alternative 2: Cell A deferred

Cell A requires H100 by hard memory constraint (8GB W matrices won't fit on 4060 Ti even with int8 or sparsity). No local-GPU path.

Cell A's purpose is staging at 2x N from an already-PASSed test at N=16384 (5/5 zero-leakage CONFIRMED). The 2x staging is incremental evidence of robustness, not load-bearing for current product decisions.

Recommend deferring Cell A until either (a) user explicitly authorizes a substantial cloud overnight OR (b) a strategic decision specifically blocked on N=32768 emerges.

### Alternative 3: Wait for user direction on Round 6 priority

If orchestrator+user want Cells A+B at full N=32768 scale, surface back to me with explicit user-statement "yes the Round 6 overnight is worth $50-100 and 10-15h cloud wall" and I dispatch.

## Cap_map implications

Round 6 dispatch was queued to potentially LIFT:
- Multi-tenancy row (zero-leakage at scale)
- PP-33 framework-class lift (DMFT-TW vs Levy-DMFT distinction)

By deferring, those LIFTs stay queued. NO row band drops from this decision. The Round 4 PP-8 v1b HARD-PASS LIFT (cap_map v316->v317; pre-committed) stands; Round 6 was independent work that would have added other-row evidence.

## Cost state (sanity check)

- Cumulative session Lambda: $21.49 (under $50 testbed-check-in cap)
- Round 6 as-spec'd would have pushed to ~$71-121 (over the cap and into territory requiring user explicit auth per [[feedback-short-cloud-runs-preferred]])
- Alternative 1 (Cell B partial local-GPU): $0 cloud spend
- Alternative 2 (Cell A defer): $0 cloud spend

## What testbed will do, by default if no further direction lands

- File this routing; mark handoff as triaged
- Continue HOLDING on PP-8 (awaiting strategy cap_map move + D3 KV-cache authorization)
- Could pick up Alternative 1 (Cell B local-GPU 3-point) autonomously since it's $0 cloud — but will WAIT for user/strategy confirmation that local-GPU partial collapse is the right next compute use vs other priorities (PP-3 Phase 2 atom-registry engineering; Anthropic Phase 2 eval; dashboard Part B+D; etc.)

## Files referenced

- This routing
- `notes/testbed_handoff_overnight_round6_cloud_h100_cells_a_b_2026-06-01.md` (source handoff; left in inbox pending strategy response or moved per orchestrator preference)
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_short_cloud_runs_preferred.md` (durable memory recording user preference)
- `notes/routed_completed/strategy_response_to_testbed_pp8_v1b_lr_fix_plus_path_a_10cell_authorized_2026-06-01.md` (10-cell auth; just moved to routed_completed; was a duplicate that got re-created)

<!-- routing-completed: Acted-on 2026-06-01: declined per user preference logged -->
