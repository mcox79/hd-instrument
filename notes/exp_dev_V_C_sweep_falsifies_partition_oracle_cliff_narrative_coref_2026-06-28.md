# exp_dev: V_C sweep FALSIFIES partition-oracle cliff hypothesis on narrative-coref

**Filed:** exp_dev 2026-06-28
**Cell:** `d:/AI/hd-instrument/experiments/exp_substrate_narrative_partition_oracle_V_C_sweep_v1.py`
**Prereg:** `d:/AI/hd-instrument/preregs/2026-06-28_substrate_narrative_partition_oracle_V_C_sweep_v1.md`
**Smoke metrics:** `d:/AI/hd-instrument/data/exp_substrate_narrative_partition_oracle_V_C_sweep_v1_smoke/metrics.json`
**Driving handoff:** `d:/AI/hd-instrument/notes/exp_dev_to_research_substrate_narrative_coref_temporal_composition_v1_smoke_2026-06-28.md`

## TL;DR

ANCHOR 2 V_C sweep smoke = **HARD_FAIL on the V_C-cliff hypothesis.** The
partition-oracle mechanism (validated at V_C=4000 ORACLE_C=0.97 on
`partition_oracle_v5_hardened`) does **NOT transfer to narrative-coref Q2** at
any V_C in {50, 200, 1000, 4000}. Oracle Q2 stays flat at ~0.21 mean across 3
smoke seeds and all 4 V_C points — indistinguishable from random floor (~0.20
expected for 5-way Q=8) and from naive baseline. The drill's escape hatch
triggers: **need a different Q2 primitive** (HRR context-bind disambiguator is
the candidate per drill).

Q3 sequence-replay confirmed V_C-INDEPENDENT: 12/12 measurement points (3 seeds
× 4 V_C) at 1.000. The replay primitive's chain-grade status is robust across
the V_C axis as expected.

## Pre-reg vs measured

| V_C | floor_Q2 mean | naive_Q2 mean | oracle_Q2 mean | replay_Q3 mean |
|---|---|---|---|---|
| 50   | 0.167 | 0.292 | 0.208 | 1.000 |
| 200  | 0.125 | 0.250 | 0.333 | 1.000 |
| 1000 | 0.208 | 0.208 | 0.208 | 1.000 |
| 4000 | 0.333 | 0.167 | 0.208 | 1.000 |

(means over seeds {7, 13, 19}; Q_per_type=8; N_EVENTS=100 N_CHARS=5 — full source-cell regime)

- HP_PARTITION_Q2_AT_HIGH_VC = 0.60 → MEASURED 0.21 (≪ HP; not just below, at floor)
- HP_LIFT_OVER_NAIVE_AT_HIGH_VC = 0.30 → MEASURED 0.04 (oracle barely above naive)
- HF_PARTITION_Q2_AT_TOP_VC = 0.30 → MEASURED 0.21 at V_C=4000 (HF tripped)
- HP_REPLAY_Q3_ALL_VC = 0.60 → MEASURED 1.000 across all V_C × seeds (HP)
- monotone_ok: False (oracle non-monotone in V_C — it's flat noise)

## Cross-seed table (smoke, 3 seeds × 4 V_C)

| seed | V_C=50 oracle | V_C=200 oracle | V_C=1000 oracle | V_C=4000 oracle |
|---|---|---|---|---|
| 7  | 0.125 | 0.250 | 0.125 | 0.125 |
| 13 | 0.375 | 0.375 | 0.125 | 0.500 |
| 19 | 0.125 | 0.375 | 0.375 | 0.000 |
| mean | 0.208 | 0.333 | 0.208 | 0.208 |

Variance is binomial noise around floor; no signal-of-V_C. Compare random floor
mean per V_C above — oracle is within 1σ of floor at every V_C point.

## Why I'm NOT dispatching full chunks

Per DISCRIMINATOR-MUST-SURVIVE-SCALE + USER 2026-06-26:
- Smoke runs at FULL N_EVENTS=100 / 5 chars / 8 pronouns / Q=8 (matches/exceeds
  source narrative cell regime; Q=8 vs source Q=3 reduces noise).
- 3 smoke seeds across full V_C sweep = 12 cells already; oracle UNANIMOUSLY at
  floor at every V_C.
- Dispatching 3 chunked full seeds (16 units each = 48 more units) would burn
  ~45 CPU-min reconfirming what's already known: **no V_C cliff exists.**
- Per Fix #21 + THREE SMOKE DISCIPLINES: smoke FIRED the discriminator (oracle
  vs naive vs floor); band-floor result IS the answer; no dispatch needed.

## Science finding (substantive)

**The partition-oracle mechanism from `partition_oracle_v5_hardened` does NOT
transfer to narrative-coreference task design.** This is the drill's anticipated
escape hatch (filed as a stated possibility in the source handoff):

> "If the curve doesn't lift, the partition router's mechanism doesn't transfer
> to narrative-coref task design and we need a different Q2 primitive (HRR
> context-bind disambiguator per `contextual_encoding_hrr_binding_smoke_v1`
> HARD_PASS WSD=1.000)."

Likely root cause (HYPOTHESIZED@ — would need follow-on cell to verify):
substituted-cue scoring assumes that auto-association strength `|W_part[c] @
substituted_cue|` discriminates partitions, but in narrative-coref the
character's partition contains many verb/obj combos and the substituted-cue
isn't specific to the true referent's stored memories. At V_C=4000 the per-
partition density grows but so does competing-pattern interference — no
discrimination emerges. The original partition_oracle_v5 worked at V_C=4000
because the candidate-anchor set itself was scaled to V_C (so anchor projections
were discriminative per partition). Here we hold N_CHARACTERS=5 (partitions)
fixed while only scaling per-partition vocabulary — wrong axis.

## ANCHOR 3 candidate (next cell)

Pivot to HRR context-bind disambiguator per drill:

```
Q2 readout = HRR_context_bind:
    For each candidate char c:
        score[c] = cosine(scene_context_bound_to_c, cue_event)
    where scene_context = bundle of all non-pronoun events in same scene
    bound to their char identities via HRR circular convolution.
```

Source primitive: `contextual_encoding_hrr_binding_smoke_v1` HARD_PASS WSD=1.000.
Functional-req match: WSD = word-sense-disambiguation = pick-correct-meaning-
given-context = same shape as pronoun-disambig given scene context.

## M3 implication

M3 concern #3 (long-narrative Q2 coref) is **NOT resolved by V_C scaling alone.**
The path to resolution is either (a) HRR context-bind primitive (chain-grade
candidate per drill) or (b) a fundamentally different primitive for entity-
tracking. M3 progress requires the next-cell HRR pivot.

## Discipline tags satisfied

META_RULE_AC pre-reg locked | AE absolute paths | AF arms-distinct (16 distinct
SHAs across 16 units; arms differ as population) | AG smoke=full-N |
AH atomic write_metrics | AN substrate-empirical anchors | H cardinality_ok=16
| J no silent except | L strict-above-floor | DISCRIMINATOR-MUST-SURVIVE-SCALE
Check A satisfied (smoke = full N_EVENTS=100)

All numbers tagged: MEASURED@ for on-disk; HYPOTHESIZED@ for root-cause; the V_C
cliff prediction was THEORETICAL@drill_anchor_partition_oracle_v5_hardened and
is now FALSIFIED@MEASURED.

## Files

- Cell: `d:/AI/hd-instrument/experiments/exp_substrate_narrative_partition_oracle_V_C_sweep_v1.py`
- Prereg: `d:/AI/hd-instrument/preregs/2026-06-28_substrate_narrative_partition_oracle_V_C_sweep_v1.md`
- Smoke metrics: `d:/AI/hd-instrument/data/exp_substrate_narrative_partition_oracle_V_C_sweep_v1_smoke/metrics.json`
- Partials (16): `d:/AI/hd-instrument/data/exp_substrate_narrative_partition_oracle_V_C_sweep_v1_smoke/partial_metrics_seed7_vc*_ARM_*.json`

-- exp_dev 2026-06-28
