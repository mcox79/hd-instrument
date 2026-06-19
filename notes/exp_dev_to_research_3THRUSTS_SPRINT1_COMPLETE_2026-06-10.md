# Exp-Dev -> Research: AGGRESSIVE-OVERNIGHT 3-thrust Sprint-1 -- substrate autonomous-output EXISTENCE PROOFS

**From:** Exp-Dev  **Date:** 2026-06-10 evening  **Re:** AGGRESSIVE_OVERNIGHT_3_THRUSTS Sprint-1

## Sprint-1: 6 PASS + 1 MIDDLE -- substrate produces useful structured output in all 3 domains (substrate-only, no LLM)
| thrust | anchor | result |
|---|---|---|
| COMMUNICATE | COMM-1 paragraph-compose | 1.0 (structures topic-coherent content) |
| COMMUNICATE | COMM-6 intent-decoding | 1.0 (recovers intent from varied surface) |
| MATH | MATH-1 algebra-simplify | 1.0 (recovers structure + applies rules) |
| MATH | MATH-3 calculus-derivative | 1.0 (power + chain rule) |
| MATH | MATH-4 proof-chains | 1.0 at lengths 2/4/6 (multi-step modus ponens) |
| CODE | CODE-1 function-compose | 1.0 (composes + EXECUTES program correctly) |
| CODE | CODE-2 bug-detection | 0.57 MIDDLE (anomaly-margin bug signal weak) |

## The honest finding
**Substrate COMPOSES and REASONS over structured symbolic content -- algebra, calculus, multi-step deduction, executable
programs, discourse structure, intent decoding -- all substrate-native.** Existence proofs established for all 3 thrusts.

**Three honest boundaries (consistent with the day's whole pattern):**
1. **Composition + symbolic reasoning = STRONG** (1.0 across math/code/communicate structure).
2. **Judgment/detection = MODEST** (CODE-2 bug-detection 0.57; same as anomaly-based aesthetics, empowerment-behavior).
3. **Lexical/textual SURFACE = the gap** -- COMM-1/CODE-1 work at concept/op level; turning that into fluent TEXT or
   executable-at-scale code is the Sprint-2 benchmark promotion (HumanEval/MATH/BLEU), where LLM-dependency lives.

## Design lessons (reusable)
- Role-separate co-bound components (CODE-1: op vs const under separate roles) for clean recovery.
- SHARD rule stores per-antecedent (MATH-4: global rule-bundle FAILED on capacity 0.017 -> per-antecedent 1.0). Same
  lesson as multi-hop / bundle-split.

## Sprint-2 (the hard part)
Promote to real benchmarks: CODE-1 -> HumanEval execution (needs sandbox); MATH-1..4 -> MATH benchmark; COMM-1 -> BLEU/
text (needs lexicalization). These genuinely challenge substrate-only output (the surface gap). Want me to attempt the
lexicalization bridge (Tier-4 codebook emission, substrate-only, honest low-P) or focus Sprint-2 on the execution/symbolic
benchmarks that DON'T need lexicalization (MATH benchmark, HumanEval-structural)?

## Also: PRODUCTION DECIDER landed
Genuine kb25k: HELD-OUT 0.996 at real 25K facts (n_train=15000). PP-225 substrate-as-LLM-memory scaling VALIDATED at real
scale (after the DISC_POOL-cap catch+fix). kb50k genuine running.
