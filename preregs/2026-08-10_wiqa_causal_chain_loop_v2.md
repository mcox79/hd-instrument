# Pre-reg: exp_wiqa_causal_chain_loop_v2

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents, no queue dispatch -- CPU-only
glass-box text processing on the real WIQA dev split; per Director's task Contract, run
FOREGROUND TO COMPLETION locally, CHEAP, no queue_add). This pre-reg is filed alongside the
already-executed --self-test / --smoke / --full runs (all completed this session before this
doc was written) because the decisive gate threshold and the two extraction changes were fixed
in `experiments/exp_wiqa_causal_chain_loop_v2.py` BEFORE the full-dev run was executed -- no
post-hoc tuning of `DECISIVE_COLLAPSE_FRACTION` or the stemmer/same-step changes against the
observed subset-scramble numbers.

## Prior-work check (mandatory, 2026-07-01 USER-locked)

`bash tools/substrate_query.sh "causal chain propagation WIQA multihop extraction abstain
reduce"` -> top-5 hits all generic lexical/wordnet entries (`extraction` cosine=0.3525,
`chain_reaction` cosine=0.3398, `chain reaction` cosine=0.3398, `propagation` cosine=0.3389,
`CN_abstraction` cosine=0.335) -- none is a substantive prior WIQA-v2 subset-scramble or
abstain-reduction drill; all are single-entity wordnet/concept-atom lexical entries, same
signature as v1's own prior-work check. **Prior-work check verdict: NOVEL** (extends v1
directly, does not rediscover it).

## Question

Director's task (WIQA flagship, DECISIVE follow-up to v1's MIDDLE_BAND): (1) does the knowledge-
SCRAMBLE control collapse CAUSAL-CHAIN-LOOP's edge over POLARITY-ECHO specifically on the subsets
where the mechanism actually fires (active / active_multihop / negation_crossing), separating
"genuine causal-edge reasoning diluted by abstain" from "structural artifact"; (2) does reducing
the 72.09% abstain (v1) via label-blind extraction/anchoring improvements change the aggregate
picture?

## Design: two label-blind extraction/anchoring changes over v1

Both changes are structural generalizations of v1's existing mechanism, not new information and
not label-informed (neither reads `answer_label`):

1. **Light suffix-stripping stemming** (`light_stem()`) applied to BOW content tokens before
   hashing to a word-vector. MEASURED@calibration this session (scratch script
   `wiqa_stem_test.py`, same anchor/gate pipeline as v1, GATE_THRESH unchanged at 0.05): reduces
   gate-fail-driven abstain from 41.09% to 36.67% of all 6894 dev items (recovers morphological
   near-misses like "grows"/"growing"/"grow" that v1's raw-token BOW missed -- diagnostic
   (`wiqa_examples.py`) confirmed several of v1's near-miss items (p_score in [0.037, 0.046],
   just under GATE_THRESH=0.05) were genuine morphological mismatches, e.g. pert clause "more
   time needed happens" vs step "Turn the bicycle upside down" scoring near-threshold on
   unrelated words while true-match steps elsewhere in the same paragraph were morphologically
   obscured).
2. **Same-step zero-hop propagation allowed**: v1 structurally forced an abstain whenever
   `p_idx == o_idx` (perturbation and outcome clauses both anchor to the same paragraph step).
   `propagate_sign(reg, lo, hi)` already handles `lo == hi` correctly as a genuine zero-hop walk
   (`sign=+1`, empty trace) -- no special-casing was added to that function; v2 simply removes the
   `p_idx != o_idx` gate in the abstain condition. Self-test `_hand_case_zero_hop` asserts this
   directly.

**Diagnosed but NOT fixed this session (honest disclosure):** the single largest remaining
abstain driver is EXOGENOUS_EFFECT perturbation clauses with literally zero content-word overlap
with any paragraph step (e.g. "more nails hit happens" vs a bike-repair paragraph with no
"nail"/"puncture" vocabulary at all -- MEASURED@calibration this session, `wiqa_examples.py`
near-miss dump: p_score in [0.037, 0.046], i.e. near-zero real overlap, not a stemming-fixable
near-miss). This requires world/commonsense association (nails -> punctures -> tire steps), not
lexical normalization -- disclosed as a genuine content ceiling, not engineered around. A second
diagnosed-not-fixed driver: ~19-26% of items have `pp==0` (perturbation clause has no
INCREASE_WORDS/DECREASE_WORDS lexicon hit, e.g. "soil was replenished with fertilizer happens")
-- fixing this would require a dictionary-sense-based lexicon expansion (replenish/deplete/
overuse/etc.), scoped out of this cell to keep the extraction change auditable and small.

### Compute architecture

Unchanged from v1: sequential-CPU justified (per-item cost is dict lookups + <=1024-dim vector
sums/dots over <=10 steps; FULL landed in 17.6s wall this session, MEASURED, see Results).

## Decisive subset-scramble gate (the load-bearing addition over v1)

Four subsets, all reported (contract-mandated):
- **all**: every dev item (n=6894).
- **active**: CAUSAL-CHAIN-LOOP did not abstain (n MEASURED=2554).
- **active_multihop**: active AND `metadata_path_len >= 2` (n MEASURED=2029) -- the PRIMARY
  decisive subset.
- **negation_crossing**: active AND the TRUE register's hop trace crossed >=1 polarity=-1 edge
  (n MEASURED=95, matches Director's task estimate exactly) -- SUPPORTING evidence only (too
  small for a primary gate), but the sharpest single subset for isolating whether the SIGNED
  edge-flip specifically matters (this is the ONE case the scramble ablation actually perturbs;
  the direct-interpretation edge, v1's larger source of lift, is topology-only and untouched by
  scrambling which step's text is checked for negation).

**Gate formula** (`DECISIVE_COLLAPSE_FRACTION = 0.5`, fixed in code before the full run):
for a subset with `loop_minus_polecho = loop_acc - polecho_acc > 0`, define
`collapse_frac = (loop_acc - scramble_median_acc) / loop_minus_polecho` (scramble_median = median
of 3 independent scramble draws, seeds [7,17,29], matching v1's convention). Decisive-per-subset:
`True` (causal-validated) if `collapse_frac >= 0.5`; `False` (not-causal) if `collapse_frac < 0.5`;
`None` (inconclusive on this subset) if `loop_minus_polecho <= 0` (no edge to attribute).

**Tiers:**
- **HARD_PASS (CAUSAL_VALIDATED):** decisive=True on BOTH `active` and `active_multihop`.
- **HARD_FAIL (NOT_CAUSAL_STRUCTURAL):** decisive=False on `active_multihop` (the primary
  subset), OR decisive=None there (loop doesn't even beat polecho on the primary subset).
- **MIDDLE_BAND:** decisive differs between `active` and `active_multihop` (mixed/inconsistent).

Director's framing (explicitly not deviated from): both outcomes are decision-useful; report
what is TRUE, do not engineer toward a collapse.

## Report contract

Per-subset table (n, loop, polecho, scramble-median-of-3, loop-minus-polecho, loop-minus-scramble,
collapse_frac) for all 4 subsets; new aggregate abstain rate + loop-vs-polecho; majority/polecho/
BoW baselines retained; ABLATION-2 (no-validate) retained for continuity with v1's validate-
matters check (not part of the primary v2 gate). Deterministic seeding (hashlib-based, no
`hash()`/`list(set())`), self-test, `arms_differ_verified`.

## SCHEMA-VET fields

Same shape as v1's checklist (arms_differ_verified, final_metrics_atomicity=tmp_replace, no bare
except / BaseException -- grep-verified clean, crlb_n/a declared, cardinality_ok, per-unit
failure-class instrumentation, calibration_check=default_ok_for_this_regime, deterministic_seeding,
progress_logging=print_flush_true, real_code_path + substrate_signature preflight in self-test).
New self-test additions over v1: `_hand_case_zero_hop` (asserts lo==hi propagation),
`_hand_case_stemming` (asserts morphological collision), and a `scramble_fires_same_as_loop`
invariant check (ABLATION-1 fires on exactly the same item set as CAUSAL-CHAIN-LOOP, since both
share anchors/admission/topology and differ only in edge-polarity assignment).

## Results (MEASURED, full dev, 6894 items, elapsed_s=17.555)

| subset | n | loop | polecho | scramble (median/3) | loop-polecho | loop-scramble | collapse_frac |
|---|---|---|---|---|---|---|---|
| all | 6894 | 0.3489 | 0.3420 | 0.3506 | +0.0068 | -0.0017 | -0.255 |
| active | 2554 | 0.4389 | 0.4205 | 0.4436 | +0.0184 | -0.0047 | -0.255 |
| active_multihop | 2029 | 0.5525 | 0.4963 | 0.5584 | +0.0562 | -0.0059 | -0.105 |
| negation_crossing | 95 | 0.3579 | 0.3053 | 0.3895 | +0.0526 | -0.0316 | -0.600 |

**On every subset, scramble accuracy is HIGHER than loop's own accuracy** (negative
`loop_minus_scramble`) -- scrambling which step's text is checked for a negating word does not
just fail to collapse the gain, it does not cost anything at all. `active_multihop_decisive =
False`, `active_decisive = False`. **Verdict: HARD_FAIL / NOT_CAUSAL_STRUCTURAL.** The loop's real
and reproducible lift over POLARITY-ECHO on the subsets where it fires (+1.8 to +5.6pp) is NOT
coming from the SIGNED causal-edge information (negation-flip propagation) -- it is coming from
the topology-only "direct interpretation when the outcome clause has no stated polarity word"
structural mechanism (v1's own disclosed larger source of edge), which the scramble ablation does
not perturb at all for the vast majority of paths (only 95/2554 active items cross a negative
edge in the first place). Even on the `negation_crossing` subset built specifically to isolate
the edge-sign-sensitive case, scramble still does not collapse the gain (collapse_frac=-0.600) --
if anything the reverse. Honest reading: this cell's general-CSKG-retrieval-style causal register
does not yet extract or exploit paragraph-internal negation structure in a way a real signed-edge
mechanism would require; WIQA's genuine multi-hop signal (where present) needs a different/
stronger paragraph-internal causal-structure extraction than literal negating-word-on-adjacent-
step detection.

Abstain: 72.09% (v1) -> 62.95% (v2, MEASURED), a genuine -9.14pp reduction from the two label-
blind extraction changes. New aggregate: loop=0.3489 vs polecho=0.3420 (+0.68pp, same order of
magnitude as v1's +0.57pp aggregate lift -- the abstain reduction did not meaningfully change the
aggregate picture, consistent with the NOT_CAUSAL_STRUCTURAL reading: more coverage did not bring
more genuine signal, it mostly extended the same structural mechanism to more items).
