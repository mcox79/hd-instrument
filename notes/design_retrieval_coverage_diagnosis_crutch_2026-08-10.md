# Design: RETRIEVAL COVERAGE diagnosis (crutch-fade dominant bottleneck)

Director design note (2026-08-10). Diagnose-before-build. Task SHAPE + pointers for exp_dev; exp_dev designs params.

## Why (doubly-confirmed)
Two independent builds converge: the crutch-fade CONSOLIDATION architecture works (fade 3x binary at the strict gate; combined-evidence promotion fires + high-fidelity at maturity; controls clean) BUT comprehension stays FLAT (+0.010) because it is capped by CRUTCH RETRIEVAL COVERAGE:
- 3-tier build (593fe79b0): coverage_audit.coverage_rate = 0.247 (whole-dev denominator).
- fix-run (e9ee736ec): retrieval_hit_rate 0.446-0.538 (conditional-on-fire denominator); use_quality_given_hit fine 0.68-0.80.
So the crutch (CSKG) reaches the gold answer for only ~1/4 of dev questions (~1/2 of fired gaps). Storage/promotion/use are NOT the wall (all validated); COVERAGE is. This is the next lever.

## The decisive question (mechanism-miss vs genuine gap)
SIQa was built by sampling ATOMIC and our crutch is ATOMIC-dominant -> the needed knowledge SHOULD largely be present -> hypothesis = the misses are a RETRIEVAL-CUE / grounding problem (we fail to FIND an edge that exists), not a genuine knowledge gap. VET this, do NOT assume.

## What to measure (diagnosis, cheap + decisive)
1. RECONCILE coverage precisely: report both denominators (whole-dev; conditional-on-fire) + the exact definition of a "hit" (does retrieval return an edge whose object/neighborhood contains/scores the gold answer?).
2. For the crutch's MISSES (fired gap, literal-lookup fails to reach the gold answer): partition into
   (a) MECHANISM-MISS = a reachable CSKG path to the gold answer EXISTS within <=k hops (k=1..3) but literal one-shot lookup did not surface it; vs
   (b) GENUINE GAP = no <=k-hop path to the gold answer in our CSKG slice.
   Report the split (this decides the fix: better-retrieval vs supply-knowledge).
3. Prototype BRAIN-FAITHFUL retrieval and measure coverage RECOVERY: spreading-activation / multi-hop pull-in over the CSKG neighborhood (owned: hdlab/cleanup_family.iterative_attractor = CA3 attractor completion; the community-routing store) + hub-penalty (already +0.03-0.04) INSTEAD of literal exact-match. Measure new coverage_rate + hit_rate + the comprehension delta ON THE NEWLY-COVERED subset (does recovered coverage convert to comprehension?).
4. Also measure GROUNDING loss: what fraction of misses are because the SIQa words did not link to the right CSKG node at all (grounding failure) vs the edge-traversal failing (retrieval failure)? (word->node grounding was ~94% in prior arcs -- confirm it holds here.)

## HARD-PASS shape (exp_dev sets exact bands)
- If MECHANISM-MISS dominates (>~50% of misses have a reachable path): spreading-activation/multi-hop recovers coverage materially (e.g. 0.247 -> substantially higher) AND the recovered coverage converts to comprehension on the covered subset (real lift, scramble-clean). -> route = build the spreading-activation retrieval.
- If GENUINE GAP dominates: coverage is a knowledge-supply problem (need broader/other KB) -> different route (SUPPLY), report that honestly.
Controls: scramble must stay clean (recovered coverage must be REAL knowledge, not spurious high-degree-hub pollution -- the hub-penalty guards this); no fabricated paths.

## Owned-organ pointers (reuse, do NOT rebuild)
- hdlab/cleanup_family.py :: iterative_attractor -- CA3 attractor completion (the spreading-activation readout).
- the community-routing / sharded store (Stage-2E, source/subject-tier routing) -- neighborhood-bounded retrieval.
- data/cskg_foundation -- the crutch (1.24M ATOMIC-dominant typed edges).
- data/corpora/social_iqa -- the benchmark.
- experiments/exp_crutch_fade_social_iqa_v1.py -- the harness (its coverage_audit + retrieval path is where the literal lookup lives; extend the audit, do not disturb the validated consolidation arms).

## Guardrails
Branch dataprep/mcguffey-graded-corpus (NOT main/origin). ONE variable (retrieval mechanism). Real held-out dev. self-test PASS. Resumable per-unit. Targeted commits only (churner active). VET on disk; scramble is the load-bearing control. This is a DIAGNOSIS -> it may recommend a build, not ship a capability.
