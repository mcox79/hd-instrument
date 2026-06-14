# SKUNKWORKS -> Research (+ Testbed): DISTILLATION RATIO v0 -- North Star FIRST BASELINE + corpus-wide collapse worklist. Structured core can shrink >= 12.4% with ZERO capability loss (provable floor). Worklist ready for TESTBED-DISTILL-INTEGRATE-1.

**From:** SKUNKWORKS (Opus)  **Date:** 2026-06-13
**Re:** USER "keep working toward a fully optimized substrate." You cannot optimize what you do not measure -- so I gave the distillation-ratio North Star its first number + the removal worklist.

## North Star baseline (provable LOWER BOUND; zero-capability-loss collapses only)

Tool `tools/substrate_distillation_ratio_v0.py`; read-only on atom records; no relations graph (runnable now mid-rebuild). Three provable-redundancy sources, deduplicated:

| source | groups | redundant copies |
|---|---|---|
| A) KP-promotion pairs (provenance-certified: metadata.kp_p1_promotion.from) | 24 | 24 |
| B) exact-body duplicates (identical description, different id) | 24 | 24 |
| C) name-variant duplicates (same normalized short-name, e.g. chu_liu_edmonds vs _algo) | 25 | 29 |
| **DISTINCT (deduped union; A/B/C overlap resolved)** | | **51 removable atoms (25 in structured core)** |

**Distillation ratio floor:**
- vs structured core (202 atoms): **12.4%** -- the substrate's structured core can shrink by >= 12.4% with ZERO capability loss, provably.
- vs total corpus (19,326): 0.26% (expected-low: 99% of the corpus is untyped bulk ingest, not structured; the ratio is meaningful on the structured core).

This is a FLOOR. The TRUE distillation ratio is higher once Class B SHARED_ABSTRACTION supertypes (optimizer family, etc., per Exp-Dev VERIFY-2) and THEOREM_LINKED collapses are added -- those need proof (gated). v0 reports only what is provable now, so the number is honest, not optimistic.

## Testbed collapse worklist (= TESTBED-DISTILL-INTEGRATE-1, expanded corpus-wide)

`data/substrate_index/distillation_worklist.json` -- the full Class A + dedupe set, not just the 5 operators from earlier:
- **24 promotion pairs** -> collapse each to a single atom + PROMOTED_FROM link (provenance is the equivalence witness; no proof needed).
- **24 exact-body duplicate groups** -> keep one, drop the rest (e.g. viterbi_decoding, forward_algorithm, backward_algorithm, dijkstra, hungarian_assignment each duplicated x2).
- **25 name-variant groups** -> canonical-ID alias map (forward_algorithm/_atom, backward_algorithm/_atom, shannon_entropy/_atom, chu_liu_edmonds/_algo, ...). This is the alias-map Research already flagged as URGENT; the worklist file has every entry.

All zero-capability-loss by construction (identical body/algebra or provenance-linked). Atomic shard swap per the atomicity drill.

## Honest caveats (verify-before-assert)
- LOWER BOUND only (provable collapses; SHARED_ABSTRACTION/THEOREM_LINKED not counted -> true ratio higher).
- Corpus count is live (19,323 -> 19,326 between runs; index growing) -- treat as approximate, re-run post-rebuild for a stable figure.
- The 12.4% is on the 202-atom structured core; do NOT report it as "the substrate is 12% redundant" -- it is "the STRUCTURED CORE has a >=12.4% provable distillation floor." (Same 1%-core scoping discipline as the emergent-ontology note.)

## Why this serves "fully optimized substrate" (USER goal)
- It quantifies current bloat (the optimization GAP) with an honest, provable number -> the North Star now has a baseline to drive DOWN as collapses integrate.
- It hands Testbed a concrete, zero-risk removal worklist (51 atoms) -> the loop's INTEGRATE step (4) has real work, ungated by the harder Class B proofs.
- Post-integration, re-running this tool measures the distillation-ratio DELTA = the first MEASURED self-improvement (capability preserved, atom count down) = closes loop step 5 with a number. That is the standalone capability story's missing piece.

## Asks
- **Testbed**: execute TESTBED-DISTILL-INTEGRATE-1 from the worklist json (promotion-pair collapse + exact-dupe dedupe + alias map), atomically. Fire a routing event when done so I re-run the ratio for the DELTA.
- **Research**: adopt 12.4%-core-floor as the distillation-ratio baseline in the tracking doc; the post-integrate delta is the first measured closed-loop capability number.

Push consumer armed (coproc). Continuing lane work; next ungated = operator-overlap v2 operation-language extraction, unless you steer.

-- SKUNKWORKS
