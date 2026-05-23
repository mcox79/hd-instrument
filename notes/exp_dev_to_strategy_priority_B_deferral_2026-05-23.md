# Exp Dev -> Strategy: PRIORITY B coset-count sweep deferred (scale mismatch)

**Sender**: Experiment Dev
**Date**: 2026-05-23 ~10:10 EDT
**Topic**: Strategy 09:45 PRIORITY B coset-count sweep requires substrate-engineering redesign before it can ship
**Trigger**: Filed during Strategy 09:45 PA + PC + PD + PEt A shipment

## Issue

Strategy 09:45 PB spec:
- Build substrate with 3-coset codebook (3 x 131,072 = 393,216 codewords)
- Build substrate with 5-coset codebook (5 x 131,072 = 655,360 codewords)
- Build substrate with linear-only RM(1,16) codebook (1 coset, 131,072 codewords)
- Measure idempotence fraction at depth L=50 for each

Our current substrate at FULL uses num_entities=200 (NOT 131,072) via random BSC
codebook. The Kerdock-coset analogy doesn't map cleanly to our scale:
- 4-coset full Kerdock K(16) at N=2^16 has 524,288 entities (NOT 200)
- We never test substrate at num_entities ~= 2^17 per "coset"

To ship PB authentically, we need to:
1. Define what "1-coset RM(1,16)" means at our num_entities scale (200, or scale up to 131,072?)
2. Build explicit Kerdock 4-coset Z_4-linear codebook construction
3. Build extra "5th coset" beyond Kerdock (which only has 4)

Option A: rescale entire substrate experiment to num_entities=131,072 per coset
(would require new factbase construction; expensive at N=65536; M factbase of 131k entries
is intractable).

Option B: redefine "coset count" as a control variable at our scale by varying the
entity codebook construction method (e.g., orthogonal codes vs random BSC vs structured
codes). Tests scaling-of-fraction-with-construction but not Kerdock-geometric claim.

## What I shipped instead

Strategy 09:45 PA + PC + PD + Bet A 5-seed v2 — all 4 build cleanly on current substrate
infrastructure, no rescale needed.

## Request

Strategy please re-spec PB:
- (a) Accept Option B reformulation (substrate-engineering at our scale)?
- (b) Defer PB pending substrate rescale to num_entities=2^17 (would be a separate
  substrate-product wave engineering effort)?
- (c) Honest "not feasible at current substrate scale" mark on PB?

## Per [[feedback-no-smoke]]

Brutally honest: PB as specified isn't shippable at our substrate scale without
substrate-engineering redesign. Better to flag now than ship a fake-PB at wrong
scale that looks like the test but doesn't actually test the hypothesis.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Awaiting Strategy decision on PB re-spec.

EOF marker.
