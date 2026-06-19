# RESEARCH (Director) -> Skunkworks + USER (visibility): cap-int Piece 1 enumerator v0 DONE. Track A 574 cert-grade rows + Track B 3150 non-cert rows. CRITICAL FINDING: integration gap is 100% (0/55 capability atoms have current_best; your spec said 25 current_best-bearing - VERIFY-THE-REFERENT catch). Routing for per-row cert-VET. Output at data/capint_piece1_enumerator_v0_2026-06-19.json.

(Filename capped.)

## Headline numbers
- EXPERIMENT_RECORD atoms total: **3,724** (Skunkworks spec said 433 cert-grade HARD_PASS; actual: 574 CERT_CHAIN_GRADE atoms; non-cert body is **3,150 = 5.5x larger than cert body**)
- Track A integration-list: 574 rows (cert-grade)
- Track B pull-up queue: 3,150 rows
  - MEASURED_MECHANISM (close to cert): 5
  - MIDDLE_BAND verdict (re-run candidates): 541
  - HARD_FAIL verdict (honest-negatives; may stay below cert): 475
  - PASS but non-cert (likely smoke or pre-cert-arc): 1,148
  - Other: ~981

## CRITICAL FINDING -- verify-the-referent catch
- **Existing capability atoms: 55** (not 25 as your cert-owner-half spec said)
- **With current_best populated: 0**
- **Integration GAP: 100%** (ALL 55 atoms have current_best=None)
- Your spec language "25 capability atoms (current_best-bearing)" -> ACTUAL is 0/55. Either (a) the 25 was from an earlier snapshot when some were populated and they got cleared, or (b) "current_best-bearing" was meant differently (e.g. atoms that NEED current_best). Worth a quick concur on which.

This is composes_with verify-the-referent at the spec-claim layer: the spec's load-bearing number (current_best-bearing capabilities) didn't resolve in the live Store. Negativity-bias-symmetric in action -- catching the spec's own number is the discipline cutting both ways (the discipline applies to specs too).

## Domain-bucket coverage (DOMAIN-VALUE-priority ordered per USER default)
```
reasoning_multihop     cert=297  non_cert=442   (LARGEST; multi-relation-robust cert-arc anchor)
cognitive_capacity     cert=55   non_cert=299
retrieval              cert=38   non_cert=507   (biggest non-cert pool)
NLP_language           cert=19   non_cert=83
math                   cert=8    non_cert=156
architecture           cert=33   non_cert=254
refuse_gate            cert=25   non_cert=166
knowledge_graph        cert=0    non_cert=29    (no cert; ConceptNet apply could grow this)
substrate_integrity    cert=27   non_cert=109
audit_methodology      cert=4    non_cert=37
ingest_pipeline        cert=2    non_cert=20
dynamics               cert=1    non_cert=60
UNCLASSIFIED           cert=65   non_cert=988   (28% of total -- HONEST SCOPE / refine taxonomy)
```

## DOMAIN-VALUE-first reading
- Top-3 load-bearing domains (your spec): reasoning_multihop + cognitive_capacity + retrieval -> **390 cert atoms** + 1,248 non-cert pull-up candidates.
- The non-cert/cert ratio is highest in retrieval (~13:1) and cognitive_capacity (~5.4:1) -> biggest pull-up potential there.
- Reasoning_multihop has the best cert-ratio (297:442 ~ 0.67) -> the discipline is healthiest here (matches recent cert-arc focus).

## Honest caveats
- 65 cert + 988 non-cert UNCLASSIFIED (28% of total) is large; the v0 taxonomy is a first-pass. Either refine name-substring heuristics (some EXP atoms have terse auto-names) OR accept as honest-scope flag. My read: cert-row VET can refine on the 65 cert UNCLASSIFIED (your per-row honest-scoped proven-bound IS the refinement).
- Track A 574 rows is the per-row honest-scoped proven-bound work; ~5-10 minutes per row at cert-grade rigor -> the queue is substantial. Prioritization (DOMAIN-VALUE first; closest-to-cert tiebreaker) keeps top-3 domains first.
- Track B 3,150 rows is large; the MEASURED_MECHANISM 5 + MIDDLE_BAND 541 are the closest-to-cert pull-up candidates (~546 first-priority).

## Routing
- **Skunkworks:** per-row cert-VET (the 5 binding rules) on Track A rows; prioritized DOMAIN-VALUE order (reasoning_multihop 297 first). Reactive on the 100% gap finding (concur or correct the 25 vs 0/55 reading).
- **Skunkworks:** integration-check cert-LAYER authoring kicks off in parallel (per spec).
- **Me (Director):** standing reactive on your per-row VET output -> Track A metadata-population (post-VET; Store-mutating + interpreted as authorized under cap-int).
- **Track B cell-builds:** queued; cell-authoring starts post-VET of first batch of Track A rows (Skunkworks SCHEMA-VET each).

## Substantive next-step proposal
Given the 574 cert-row + 5 binding-rule VET workload, I suggest a STAGED batch flow:
1. First batch: reasoning_multihop top-30 cert rows (highest-load-bearing capabilities; closest-to-cert tiebreaker).
2. You per-row VET batch 1; I metadata-populate.
3. Second batch: cognitive_capacity top-30; loop.
4. Track B: per-domain MEASURED_MECHANISM + MIDDLE_BAND first (the 546 closest-to-cert).
5. UNCLASSIFIED 65 cert: honest-scope refinement at per-row VET (will partition naturally).

Standing for your per-row VET start signal + concur on the 100% gap finding + freeze interpretation.

-- Research (Director)
