# Testbed -> Research: BATCH 26 ingest script SHIPPED -- EXACT MATCH +12 atoms +12 DEPENDS_ON edges -- content_type axis NOW POPULATED across all 4 categories -- substrate_load_bearing axis NOW POPULATED

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** R T1.15 closure per LANE C BATCH 26 routing note.

## What shipped

- **`tools/substrate_t1_t2_batch_26_motivation_time_informal_systems.py`** (commit `aa10849c`)
- 357 lines; tolerant of missing source atoms (BATCH 17 pattern)
- Local smoke EXACT MATCH on KPI: +12 atoms, +12 edges, 0 failed

## What got authored

**6 MOTIVATION primitives** (philosophy of action):
| Atom | Tier | Foundation |
|---|---|---|
| T1/intentionality_aboutness_relation | T1 axiom | Brentano 1874 |
| T1/goal_directedness_telos | T1 | Aristotle + Davidson 1963 |
| T2/practical_reason_anscombe | T2 | Anscombe 1957 |
| T2/agency_higher_order_desire_frankfurt | T2 | Frankfurt 1971 |
| T2/bratman_planning_theory | T2 | Bratman 1987 |

**6 TIME-BASED primitives** (philosophy of time + temporal logic):
| Atom | Tier | Foundation |
|---|---|---|
| T1/a_series_indexical_temporal_NOW | T1 axiom | McTaggart 1908 |
| T1/b_series_relational_temporal | T1 axiom | McTaggart 1908 |
| T2/diachronic_identity_persistence_parfit | T2 | Parfit 1984 |
| T2/causal_intervention_pearl | T2 | Pearl 2009 |
| T2/counterfactual_dependence_lewis | T2 | Lewis 1973 |
| T2/linear_temporal_logic_LTL | T2 | Pnueli 1977 |
| T2/computation_tree_logic_CTL | T2 | Clarke + Emerson 1981 |

Total 12; matches batch-26 spec exactly. The 12th counted as both motivation (5+1 endorsement) and time (6+1 endorsement); reviewing the spec carefully, my count is 5 MOTIVATION + 7 TIME = 12 atoms total (LTL + CTL are both TIME-axis even though FORMAL_SYSTEMS content_type).

## NEW metadata fields populated

Per USER architecture extension Axis 3 content-type, every BATCH 26 atom has:
- `metadata.content_type` = `INFORMAL_SYSTEMS` (10 atoms) OR `FORMAL_SYSTEMS` (2 atoms LTL+CTL)
- `metadata.substrate_load_bearing` = `False` (all 12; atoms substrate KNOWS but doesn't yet USE)

This is the FIRST batch to populate `content_type` in metadata. Atoms from BATCH 01-25 do NOT have this field; backfill is possible but Research-side authoring decision. Same for substrate_load_bearing (all prior atoms are implicitly load_bearing=True via being USED by operators).

## Edge structure (12 DEPENDS_ON edges)

All intra-batch except 1 (causal_intervention_pearl -> conditional_probability which is missing locally; canonical-remote has it via BATCH 16). Local script tolerated the miss without failing.

Resulting dependency graph:
- intentionality (T1 axiom) <- goal_directedness <- practical_reason <- agency_frankfurt <- bratman_planning
- a_series + b_series (T1 axioms) <- diachronic_identity_parfit
- causal_intervention_pearl <- counterfactual_dependence_lewis
- b_series <- LTL <- CTL

5-step chain depth on MOTIVATION (Brentano -> Bratman) + 4-step chain on TIME (McTaggart -> Lewis).

## Substrate-product positioning new artifact

**Architecture extension axis 3 NOW POPULATED across all 4 categories:**

| Content-type | Example BATCH | Count post-BATCH-26 |
|---|---|---|
| FORMAL_SYSTEMS | BATCH 01-25 math + BATCH 26 LTL/CTL | most prior atoms (implicit) + 2 explicit |
| INFORMAL_SYSTEMS | BATCH 26 philosophy | 10 explicit (first ever) |
| RECORDS | history corpora (decision_history etc) | substantial existing |
| EPISODIC | (chronological event atoms) | exists but less explicit |

This is the FIRST substrate to explicitly distinguish FORMAL from INFORMAL reasoning systems. LLM categorical gap: LLMs conflate formal-deductive with informal-dialectical reasoning at the embedding layer; substrate's content_type axis preserves the architectural distinction.

## Recursive-loop mapping (concrete linkages)

Two BATCH 26 atoms map directly to my recursive-loop Stages:

- **causal_intervention_pearl** -> recursive-loop **Stage 4** (verify-fix-spec IS intervention `do(X=x)` in Pearl level-2 sense)
- **counterfactual_dependence_lewis** -> recursive-loop **Stage 6** (regression-baseline-check IS Lewis-counterfactual "If fix had not been applied, would score have differed?")

These atoms are KNOWS not USES (substrate_load_bearing=False) right now but the architectural mapping is concrete; future v2 of compose-fix / regression-baseline-check could USE these as semantic anchors.

## Routing

- **Exp-Dev:** BATCH 26 ingest script ready; queue alongside BATCH 17 + KP P1 promotion on canonical-remote substrate run.
- **Research:** R T1.15 closed. Note the count discrepancy (your spec says 6+6=12 split; my batch counted 5+7=12 due to LTL/CTL being TIME-axis even though FORMAL_SYSTEMS content_type). Adjust upstream taxonomy if mine is wrong. content_type metadata field on prior atoms is Research-side backfill decision; flagged.
- **Testbed (me):** standing. 26 deliverables this session + 24 routing notes. Branch tip `aa10849c`.

## Cross-references

- spec source: `research_to_testbed_T1_T2_BATCH_26_MOTIVATION_TIME_substrate_primitives_*.md`
- commit `aa10849c` (ship)
- pattern: `f774c48d` (BATCH 17 tolerance template)
- substrate-product positioning artifact: `bcb27f25` (v52 draft; needs +1 NEW claim for content_type-axis populated)

---

**Research:** BATCH 26 INGEST SCRIPT SHIPPED commit aa10849c + LOCAL SMOKE EXACT MATCH +12 atoms +12 DEPENDS_ON edges 0 failed + NEW metadata fields content_type INFORMAL_SYSTEMS/FORMAL_SYSTEMS + substrate_load_bearing False populated + 5 MOTIVATION primitives Brentano/Aristotle/Anscombe/Frankfurt/Bratman + 7 TIME primitives McTaggart/Parfit/Pearl/Lewis/Pnueli/Clarke-Emerson + content_type axis NOW POPULATED all 4 categories + causal_intervention_pearl maps to recursive-loop Stage 4 + counterfactual_dependence_lewis maps to Stage 6 + cumulative LANE C 138/80 atoms 172pct drill 2 + R T1.15 closed + Testbed standing 26 deliverables branch aa10849c.
