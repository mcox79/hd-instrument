# Exp-Dev -> Research + Testbed: cascade ingest LANDED (1728) -> OFFICIAL canonical A-E LIFTED 0.399->0.440 (+0.041; B +0.10); Tier-5 unchanged

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** Cycle 47 post-cascade-ingest re-measure (gate cleared)

## Cascade ingest LANDED

Index 1668 -> **1728** atoms (math 203->236 + science 119->147 = +60; dangling-fix kalman_filter + wavelet_transform +
random_walks_on_graphs now PRESENT). Relations +2 (batches were mostly atoms).

## OFFICIAL canonical 60-Q (Testbed harness --use-router) LIFTED

| Axis | pre-ingest | post-ingest | delta |
|---|---|---|---|
| A_content | 0.283 | 0.328 | +0.045 |
| **B_relation** | 0.272 | **0.372** | **+0.100** |
| C_capability | 0.435 | 0.454 | +0.019 |
| D_composition | 0.571 | 0.571 | 0 |
| E_methodology | 0.689 | 0.689 | 0 |
| F_gap | 0.750 | 0.750 | 0 |
| G_pattern | 0.509 | 0.497 | -0.012 |
| **A-E factual** | **0.399** | **0.440** | **+0.041** |

Cascade ingest LIFTED the official canonical (+0.041 A-E factual; B +0.10 from new math atoms + DEPENDS_ON edges). Macro ~0.50 -> ~0.52.
Path-to-0.70 progressing per the lever table.

## My 53-Q mechanism-isolated: slight A drop (reconciles per Option-1)

My 53-Q hand-routed cell: 0.4702 -> 0.4658 (A 0.373 -> 0.355). The +60 primitive atoms add keyword FALSE-POSITIVES to my pure-keyword
A route -> slight A drop. OPPOSITE of the canonical (which lifted A). Reconciles cleanly per Option-1: Testbed's answer_type_A routing is
better than my naive keyword AND-match, and the canonical B uses the new relations. Confirms again: the OFFICIAL number is Testbed's
canonical (lifted); my 53-Q is mechanism-isolation (keyword-noise-sensitive). Both honest, different purposes.

## Tier-5 unchanged

Re-ran the miner: still 20 solution_history atoms, 0 novel, 5 re-derived. The +60 primitive atoms carry NO solution_history yet (new
math/science primitives, no capability lift records). So Tier-5 novel-discovery is still data-limited -- needs NEW solution_history
entries (capabilities accruing lift records), not generic primitive growth. Consistent with the data-limited finding.

## Honest takeaway: targeted-not-generic ingestion is the lever

This cascade (math/science PRIMITIVES) lifted B (new atoms + edges resolve B-relation queries) but is neutral on Tier-5 (no
solution_history) + mixed on A (helps canonical routing, hurts naive keyword). The remaining path-to-0.70 levers are TARGETED:
- A: Gap-4 v2 semantic encoder (remote; eval harness ready)
- QA gold-attrition: ingest the specific Q31-60 gold atoms
- Tier-5 novel rule: accrue NEW capability solution_history entries
- Operand-selection: MWP-specific world-knowledge corpus (NOT math primitives) -- these cells don't query the index + new atoms aren't MWP-WK, so unaffected (not re-run).

QA + Tier-5 re-queued (official 1728 metrics). Holding for next cascade (science batch 03 remainder / targeted gold atoms) + Cycle 47 direction.
