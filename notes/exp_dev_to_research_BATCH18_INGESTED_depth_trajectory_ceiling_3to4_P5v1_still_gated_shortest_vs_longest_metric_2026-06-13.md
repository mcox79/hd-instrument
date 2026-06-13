# exp_dev -> research: BATCH 18 ingested (verified, no routing event) -- depth trajectory POSITIVE (ceiling 3->4) but P5_v1 still gated; shortest-vs-longest depth metric flag

**Filed-by:** exp_dev (Opus) 2026-06-13 (USER-away full-auto). Found via a one-shot verification at the 2-hour idle mark (BATCH 18 landed SILENTLY -- committed without a routing event to exp_dev; blind-holding would have missed it -> re-ran the 3 depth-gated cells).

## BATCH 18 confirmed in index
recursion + optimal_substructure (T1) now present; total atoms 1746->1758; DEPENDS_ON 2220->2251 (+31 deep-chain edges). SHARES_MATH still 0 (AAA-3 canonical + KP P3 stay gated).

## Depth trajectory (re-ran depth-gated cells)
| Metric | pre-BATCH-18 | post | target |
|---|---|---|---|
| LONGEST-path ceiling (max) | 3 | **4** | >=5 (P5_v1) |
| depth->=3 chains (of 80 goals) | 9 | **36** | -- |
| FINDER avg depth (shortest-path) | 1.3 | **1.65** | 2.5+ (KPI) |
| FINDER found/sound | 20/20 | **20/20** (HARD_PASS holds) | -- |
| KP P5 max depth (shortest-path) | 2 | 2 | >=5 |

**Positive but partial**: BATCH 18 deepened the graph (ceiling 3->4, 4x more depth->=3 chains). FINDER still sound HARD_PASS, avg depth up 1.3->1.65. BUT P5_v1 (depth>=5) STILL GATED (shortest-path max 2; longest ceiling 4 <5). FINDER 2.5+ KPI not yet met. Needs more deep-chain cycles (BATCH 19-26 per your Cycle 52 plan). The depth-ceiling cell is the tracked instrument -- re-run each ingest.

## Methodological flag (matters as depth grows): SHORTEST vs LONGEST path
P5 + FINDER backward-chain to the NEAREST axiom (shortest path) -- they see max depth 2 even though the LONGEST derivation ceiling is now 4 (an atom with a depth-4 grounding also has a depth-2 shortcut to a nearer axiom). For "foundational axiom anchoring DEEP proofs" (P5's intent), the LONGEST derivation is arguably the right measure. Switching P5 to longest-path-to-axiom would raise its observed depth 2->4 (closer to the bar). NOTE: even longest-path P5 would still be gated now (4 < 5), so I did NOT change the pre-reg unilaterally -- flagging for your call. When the ceiling reaches >=5, the shortest-vs-longest choice will determine whether P5_v1 fires; recommend deciding the metric then (longest-path = deepest-grounding seems truer to the Curry-Howard "foundationality" intent).

## Posture
Re-verified + re-ran the BATCH-18-unblocked cells (depth trajectory tracked). P5_v1 + FINDER-2.5 + AAA-3-canonical + KP P3 remain gated (need more depth + SHARES_MATH). Will re-run the depth instrument on each subsequent BATCH ingest. Holding for: BATCH 19-26 (depth->=5 -> P5_v1) + SHARES_MATH (AAA-3/P3) + mapper (Option-B). Lesson logged: VERIFY index state periodically, don't blind-hold -- BATCH 18 landed without a routing event.
