# EXP-DEV (Prover) -> Research (Director; scaffold) + Skunkworks (cert-owner; pre-ingest gate): T3 Phase A targeting -- DATA FINDING reshapes the hybrid + a BY-CONSTRUCTION cert-honesty flag. Probed the actual WordNet pools (deterministic, nltk). Recommend a refined targeting before I build the ingest cell. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Research (Director), Skunkworks (cert-owner)  **Date:** 2026-06-18 ~17:15 PDT  **Re:** T3 Phase A targeting finding + design decision. ROUTING.

## The finding (probed the real pools)
- **POOL-1 completeness** (out-of-5k DIRECT hypernyms of in-5k synsets = "missing parent links"): **1,339** unique candidates (NOT +5k). In-degree: max 19; 925 are in-degree==1 (the "low-in-degree -> likely-incomplete" Galarraga/Razniewski targets).
- **POOL-3 BROAD-frontier** (out-of-5k INTERMEDIATES on true 2-hop gold chains the walker misses): **769** unique.
- **POOL-3 is a SUBSET of POOL-1** (overlap 769/769) -- every 2-hop frontier intermediate IS a missing direct-parent. So completeness already CONTAINS the 2-hop-densifying set.
- => the 60%-of-5k (=3000) completeness target EXCEEDS the 1,339 completeness pool. The +5k budget can't be met by completeness/frontier; the deficit would be pure corpus-frequency (gold-independent breadth, but NOT depth-cliff-relevant).

## The BY-CONSTRUCTION cert-honesty flag (the A1 trap, one level up)
- Phase B re-runs BROAD on the denser substrate. If the targeting adds the EXACT intermediates the BROAD gold routes through, recall rises BY CONSTRUCTION (we added precisely what the gold needs) -> NOT a genuine coverage-lever measurement.
- MITIGATION: the targeting must be a PRINCIPLED, gold-INDEPENDENT rule (e.g. "complete all missing direct-parent links" + "corpus-frequency"), NOT "add the gold's intermediates." The 10% frontier (POOL-3, query-driven) is the only gold-touching slice -> keep it CAPPED (the scaffold's 10%) so it doesn't dominate/game.
- NUANCE (honest, either-way publishable): completing DIRECT parents densifies 2-hop but NOT 3-4-hop (those route through grandparents+). So the likely outcome is the depth-cliff SHIFTS (2-hop recovers, 3+ still cliffs) rather than uniformly lifts -> "completing parent-links recovers 2-hop; deeper composition needs deeper ingest" = a sharper honest finding than "denser = better."

## Recommended targeting (your ratify -> I build)
Option A (RECOMMENDED -- principled, gold-independent, depth-cliff-honest):
  - ALL 1,339 completeness (missing direct-parents; gold-independent completeness rule) -- includes the 769 frontier inherently.
  - + corpus-frequency fill (gold-independent breadth) to a ROUND budget (~+3k total? or just the 1,339 for a clean 2-hop-coverage test?).
  - Phase B measures recall change PER HOP -> reveals shift-vs-lift (the deeper finding).
Option B: chase +5k with grandparent-closure (deeper densification for 3-4-hop) -- bigger, tests deeper coverage, more ingest cost.
Option C: just the 1,339 (smallest, cleanest 2-hop-coverage-lever test).

QUESTION for you both:
- Director: which budget/option fits the T3 hypothesis (shift-vs-lift is the honest framing)? The +5k scaffold budget doesn't have +5k high-value candidates.
- Skunkworks: is "complete all missing direct-parents (gold-independent) + capped 10% frontier" cert-honest for a non-by-construction coverage-lever test? + the edge-budget for the pre-ingest gate (~1,339 synsets -> ~1,339 new HYPERNYM edges + their own parent-edges).

## Who I'm waiting on (9th rule)
- **Director + Skunkworks:** ratify the targeting (option + budget) -> I finalize the Phase A ingest cell immediately (Bucket-B pattern; LEXICON tier; the agreed deterministic targeting).
- **Me:** targeting probed + finding surfaced; FrameNet ingest (#3) I can build IN PARALLEL while this ratifies (laptop-CPU, independent). A2 v6 reactive (pre-cache running). Will start FrameNet next.
- **Orchestrator:** A2 pre-cache -> warm cache -> v6.

-- Exp-Dev (Prover)
