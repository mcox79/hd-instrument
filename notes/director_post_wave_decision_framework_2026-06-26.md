# Director post-wave decision framework (2026-06-26)

Fast lookup: when each in-flight cell lands, this maps verdict → atomization route → next dispatch.

## CELL B v2 (compose fly-LSH + multi-bank + partition; multi-hop revival)

PRIMARY arm: ARM_COMPOSE_PARTITION_5HOP (HP bar 0.70; v1 seed-7 partial 0.95; smoke 0.98).
GATE arm: ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP must land in [0.08, 0.25] for META_M7 OK.

| Verdict | What it means | Same-turn action |
|---|---|---|
| HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL | PARTITION>=0.70 AND REPRODUCE in band | Spawn Skunkworks tier-rule batch IMMEDIATELY (Gap 1 lifted; cap_map bump candidate); dispatch follow-up REAL-ROUTER cell (resolves BIAS-P oracle scope flag) |
| HARD_PASS_REVIVAL_WITH_META_M7_NOTE | PRIMARY clears but REPRODUCE diverges | Skunkworks tier-rule (likely chain-grade-with-scope-flag); spawn investigation cell on regime-diff source (what beyond W-binding count differs) |
| MIDDLE_BAND | PRIMARY in [0.30, 0.70) | Don't tier; design wider sweep + harder construction |
| HARD_FAIL | PRIMARY < 0.30 | seed-7 v1 partial was noise; close partition-per-hop angle; pivot to Cell C v2 or Cell X beam |

## CELL C v2 (bidirectional meet-in-middle; multi-hop revival)

PRIMARY arm: ARM_BIDIRECTIONAL_5HOP_MEET_MID (HP bar 0.50; v1 partial 0.67; smoke 0.94).
GATE arm: ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP in [0.08, 0.25].

| Verdict | Same-turn action |
|---|---|
| HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL | Skunkworks tier-rule batch; cap_map bump; atomize meet-in-middle as substrate primitive into hdlab/; dispatch deeper depth (7-hop, 10-hop) follow-up |
| HARD_PASS_WITH_META_M7_NOTE | Skunkworks tier-rule (chain-grade-with-scope); investigate regime-diff |
| MIDDLE_BAND | Don't tier; consider deeper MID + tighter cosine band |
| HARD_FAIL | Close bidirectional angle |

## CELL X (beam search with WM candidates; 6th multi-hop attempt)

PRIMARY arm: ARM_BEAM_W10_TOPK5_5HOP (HP bar 0.50).

| Verdict | Same-turn action |
|---|---|
| HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM | 6th attempt SUCCEEDS via brain-correct PFC; cap_map bump; atomize beam as substrate primitive |
| HARD_PASS_PARTIAL | W10>=0.30 lift over rail; weaker than chain-grade but informative |
| HARD_FAIL_BEAM_DOESNT_HELP | beam-of-W=10 not the lever; multi-hop more fundamental than candidate-preservation |

## ANISOTROPY v4 CPU PATH (cerebellar expansion at brain-scale)

KEY arms: ARM_FLY_LSH_4096x vs ARM_AB_CONTROL_4096x.

| Verdict | What it tells us | Same-turn action |
|---|---|---|
| HARD_PASS_BRAIN_SCALE_EXPANSION_RESCUES | FLY_4096x>=0.85 AND beats AB_CONTROL by >=0.10 AND monotonic | Cerebellar mechanism real; atomize fly-LSH expansion as substrate primitive; cap_map bump |
| HARD_PASS_CONTROL_ALSO_HELPS | BOTH FLY and AB_CONTROL >=0.85 | Expansion IS the mechanism (not LSH-specific); atomize as "any high-dim sparse expansion" |
| HARD_FAIL_CONTROL_DOMINATES | AB_CONTROL > FLY by >=0.05 | fly-LSH NOT the mechanism; 3rd cell-confirmation; close anisotropy as bypass-only |
| HARD_FAIL_EXPANSION_DOESNT_HELP | FLY_4096x <= FLY_8x + 0.02 | cerebellar mechanism doesn't transport to substrate scale |
| MIDDLE_BAND_PARTIAL_LIFT | monotonic but FLY_4096x < 0.85 | mechanism real but insufficient at this corpus regime |

If HARD_FAIL_CONTROL_DOMINATES OR HARD_FAIL_EXPANSION_DOESNT_HELP → escalate priority to polarimetric.

## POLARIMETRIC MULTI-PROBE (USER materials-science insight)

PRIMARY arms: ARM_POLARIMETRIC_K10_LEARNED + ARM_POLARIMETRIC_K10_PCA_AXES.

| Verdict | Same-turn action |
|---|---|
| HP_LEARNED | pol_learned>=0.85 AND beats AVG/AB/FLY by >=0.10 | Anisotropy "solved" via probe-response (hardware-friendly!); cap_map bump; atomize; superior to expansion mechanism |
| HP_PCA | structure-aware works without learning | Atomize PCA-axes variant; brain-aligned |
| HP_PARTIAL_RANDOM_K | AB_CONTROL_K >=0.85 | informative: "any K probes help"; mechanism is multi-view averaging not structure |
| HF_DOESNT_HELP | pol_learned<=0.30 | cross-domain reframe falsified; close polarimetric path |
| HF_AVERAGED_DOMINATES | avg_K10 >= pol_learned | mechanism collapses to averaging; not structure attribution |

## BRAIN CONSOLIDATION (3 cells; Gap 3 + Gap 4)

### Cell A NREM replay
- HARD_PASS: drift_red >=0.30 AND best.forget<=0.05 → Gap 4 (continual) closes; cap_map bump
- MIDDLE: drift_red in (0.05, 0.30) → real but bounded; consider longer cycle horizon
- HARD_FAIL: replay doesn't help → close NREM analog
- Smoke was MIDDLE at 0.067 (borderline FAIL/MIDDLE); full at N=4096/2500cyc has bigger baseline drift = room to help

### Cell B REM homeostasis
- HARD_PASS: best.forget<=0.05 AND min_integrity>=0.95 → Gap 4 closes
- HARD_FAIL_DESTROYS_OLDER: any arm worse than baseline by 0.05 → over-aggressive
- Smoke was DESTROYS_OLDER at small regime; full at larger baseline drift may rescue

### Cell C cortex schema
- HARD_PASS: COMBINED>=0.50 AND lift>=0.15 → Gap 3 (compositional gen) closes
- HARD_FAIL_DOESNT_HELP: max_lift<=0.02 → HRR-aggregation insufficient; need different mechanism
- Honest preview: full N=8192 precedent gives NN=0.40, feat=0.42, comb=0.38 → still borderline HARD_FAIL likely. If HARD_FAIL → spawn alternative schema cell (learned attractor, exact lookup, attention)

## NESS alpha-high (envelope data)

Not load-bearing. Quick verdict, slot into envelope-extension atom group with refuse-gate V_REL=256.

## SKUNKWORKS TIER-RULE BATCH READINESS

Currently READY to tier (already landed; not yet routed):
1. META v4 self-discovered (chain-grade-confirmed)
2. Refuse-gate V_REL=256 extension (chain-grade up to 256)
3. KV learned projection M=100k (MIDDLE_BAND)
4. Anisotropy fly-LSH expansion v1 GPU OOM (partial; need formal tier on what landed)

Trigger Skunkworks batch when first of (B v2, C v2, anisotropy v4) lands AND adds a 5th candidate (so batch is 5-artifact like prior tier-rule waves).

## CAP_MAP BUMP CANDIDATES (post-tier-rule)

If Skunkworks confirms chain-grade:
- META reasoning v4 → bump META row (self-evaluation primitive operational)
- Refuse-gate V_REL=256 → bump audit-device row (32x envelope extension)
- KV learned projection M=100k → bump KV row (envelope extended)
- IF Cell B v2 or C v2 chain-grade → bump multi-hop row (Barrier 1 closes)
- IF anisotropy v4 OR polarimetric chain-grade → bump anisotropy row (mechanism found)
- IF brain consolidation chain-grade → add NREM / REM / cortex rows

## 2ND SUBSTRATE LAYER DECISION TREE

Contingent on Cell Z (expansion sweep — landed OOM) + Cell C cortex schema outcomes:

| Cell Z verdict | Cell C verdict | 2nd layer dispatch? |
|---|---|---|
| Expansion HARD_PASS | schema HARD_PASS | OPTIONAL (both gaps closed without 2nd layer); maybe still add for Tier 4 LM |
| Expansion HARD_PASS | schema HARD_FAIL | CRITICAL PATH (2nd layer provides decorrelated inputs for cortex retry) |
| Expansion HARD_FAIL | schema HARD_PASS | CRITICAL PATH (2nd layer becomes anisotropy fix) |
| Expansion HARD_FAIL | schema HARD_FAIL | URGENT (both gaps need rescue; 2nd layer is the candidate mechanism) |

Cell Z already HARD_FAIL_PARTIAL_OOM at v1; anisotropy v4 CPU path is the actual test.

## NEXT-WAVE FOLLOW-UP CELL CANDIDATES (queue-when-ready)

1. Real-router multi-bank routing cell (resolves Cell B v2 BIAS-P oracle scope flag)
2. Multi-hop deeper-depth cell (7-hop, 10-hop) if Cell B or C v2 chain-grade
3. Alternative schema mechanism cell (learned attractor / exact lookup / attention) if Cell C HARD_FAIL
4. 2nd substrate layer cell (W1 → W2 hierarchical decorrelation) per decision tree above
5. Continual extension cell (5000+ cycles) if NREM + REM both chain-grade
6. Stage 4 substrate-as-LM fair-harness rerun (with cleaned methodology per session 2026-06-23 audit)

## OPERATIONAL DISCIPLINE FOR THE WAVE

- **Fix #28:** read per-arm metrics.json BEFORE making any verdict claim; default UNDER-claim; let Skunkworks tier UP
- **META_M7:** check REPRODUCE arm landed in [0.08, 0.25] before claiming Cell B/C revival
- **BIAS-Q:** flag any arm >= 0.995 cv=0; honest scope note
- **BIAS-P:** Cell B v2 PARTITION + MULTI_BANK use oracle routing; do NOT claim chain-grade without real-router follow-up
- **Spawn budget Fix #14:** dispatch follow-ups one at a time; don't fan out
- **Atomize same-cycle** per USER results-to-application cadence: chain-grade HARD_PASS → Store atom + hdlab/ code primitive update SAME CYCLE
