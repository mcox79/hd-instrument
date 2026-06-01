# Strategy request: N=32768 envelope sweep sizing dry-run (exp_dev)

**From**: research
**To**: strategy → exp_dev
**Date**: 2026-06-01
**Note**: NOT a research drill — this is a sizing/feasibility ask for an already-justified envelope step. Filed parallel with `notes/strategy_request_to_strategy_capabilities_expansion_followon_experiments_2026-06-01.md`.

## What

The N=32768 envelope sweep has been flagged multiple times (compaction-prep notes, today's stock-taking) but fell through cracks. Modern Hopfield activation regime + a_query_sim defense + C3V4 cross-N all HARD_PASS at N=16384. N=32768 is the next envelope step.

**Problem**: I previously stated "$40-60 / 22-30h on A100 80GB" as a rough estimate. **I have NOT verified this cost.** N=32768 is 4× memory of N=16384; OOM risk on A100 80GB is real at high M; cost could be 2-4× higher depending on test envelope (single-N capacity sweep vs full M/depth grid).

**Don't pre-commit a dollar number without a sizing dry-run.**

## Ask

exp_dev: do a sizing dry-run to bracket the actual cost of an N=32768 envelope sweep. Specifically:

1. **Memory footprint estimate**: W matrix at N=32768, M=16N (typical production envelope) = 32K × 32K = 1B float32 entries = 4GB just for W. Plus codebook + workload state + cert chain. Fits on A100 80GB? H100 80GB?
2. **Wall-time estimate**: single-cell timing at N=32768 vs N=16384 baseline; scaling exponent. Lambda Exp A (a_query_sim @ N=16384, 15 cells) ran somewhere within today's Lambda spend; use that as anchor.
3. **OOM risk**: at what M/N envelope does OOM hit on A100 80GB? On H100 80GB?
4. **Recommended test scope**: single-N capacity sweep only (M ∈ {4N, 8N, 16N, 32N, 64N}, 5 seeds)? Or full multi-cell envelope (Path D depth + adversarial + compression)?
5. **Bottom-line dollar estimate** ± 30% confidence interval

## What we're NOT asking for (yet)

No experimental design beyond sizing. No pre-reg bands. No anchor name. exp_dev's autonomy on the sizing methodology + cost-estimate format.

## Why now

This has fallen through cracks twice. Filing as standalone routing to ensure it gets the sizing pass it needs before any commit. If sizing confirms <$60 and <30h wall, the experiment is dispatchable; if it surfaces 2-4× higher cost or OOM risk, strategy decides whether the strategic value justifies the higher spend.

## Cap_map relevance

If sizing comes back tractable AND the eventual experiment HARD-PASSes: Modern Hopfield activation regime row tightens past N=32768 → 🟢→🟢 (just envelope-extension; no row class change). If it HARD-FAILs: meaningful — substrate has a ceiling around N=16384-32768 that the validated wedge had not yet bracketed.

## Closing

Move to `routed_completed/` when exp_dev returns the sizing-dry-run cost estimate. Decision-to-ship-or-defer then made by strategy/user based on the bracketed cost.


---
**ROUTED-COMPLETED**: Acted-on 2026-06-01: sizing dry-run added to exp_dev Tier 1 dispatch batch (strategy_request_to_exp_dev_research_round1_tier1_dispatch_2026-06-01.md item 13)
