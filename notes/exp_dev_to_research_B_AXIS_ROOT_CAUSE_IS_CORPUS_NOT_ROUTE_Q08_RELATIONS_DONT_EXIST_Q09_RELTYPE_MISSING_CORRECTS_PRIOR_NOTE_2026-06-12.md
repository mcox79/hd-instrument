# Exp-Dev -> Research: B-axis root-cause CORRECTION -- it is CORPUS-bound, not route-bound (Q08 relations don't exist; Q09 rel-type USED_FOR_LIFT not in corpus). Corrects my prior "B-axis route mechanism I can own ~+0.05" recommendation.

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM. Verify-before-asserting correction.

## What I did
Per "continue" + decide-and-act, I dug into the two B-axis zeros (Q08-B, Q09-B) from the failure map to improve route_B. Before
changing the route, I verified the underlying relations exist in the corpus (2682 relations). They do NOT.

## Root cause (both zeros are CORPUS gaps, not route bugs)
- **Q08-B** ("atoms with INSTANCE_OF to SCHOOL/discriminative_learning_family", gold = structured_perceptron_collins /
  discriminative_perceptron_pipeline / CAP_discriminative_perceptron): there are **ZERO INSTANCE_OF edges to
  discriminative_learning_family** in the corpus. The relation was never authored. No route fix can score this -- the edges
  don't exist. (Corpus/authoring gap.)
- **Q09-B** ("math atoms USED_FOR_LIFT by PP-364_pos_tagger", gold = structured_perceptron_collins): the relation type
  **USED_FOR_LIFT does not exist** in the corpus (rel_types are USES/RELATES/DEPENDS_ON/INSTANCE_OF/SPECIALIZES/... no
  USED_FOR_LIFT). The gold IS reachable, but only via pp-364 --RELATES--> structured_perceptron_collins (different rel-type, and
  the OTHER direction than route_B returns). So Q09 is a benchmark<->corpus rel-type/direction MISMATCH, not a parse bug.

## Correction to my prior note
My failure-map note said "B-axis route mechanism I can own (~+0.05)." **That was wrong** -- the B-axis 0.325 is substantially
CORPUS-bound: the gold relations are missing (Q08) or named with rel-types the corpus doesn't have (Q09), and gold-attrition=19
across the benchmark. Improving route_B (bidirectional matching, last-segment target match, explicit-rel-type parse) has
marginal-to-risky upside (might recover Q09-class via RELATES-bidirectional, but risks precision loss on other B questions; and
canNOT recover Q08-class where the edges don't exist).

## The real B-axis lever (path-to-0.70)
- **CORPUS AUTHORING (Research/Testbed):** author the missing relations the benchmark expects (INSTANCE_OF to learning-family
  schools; the USED_FOR_LIFT / lift-provenance edges). This is the dominant B-axis lever -- per methodology-rule-8 (substrate
  content authored by us/substrate), it is yours/Testbed's, not route R&D.
- **Benchmark<->corpus rel-type RECONCILIATION:** the benchmark uses rel-type names (USED_FOR_LIFT) the corpus doesn't have.
  Either author those edges or reconcile the benchmark to the corpus's actual rel-types (USES/RELATES/DEPENDS_ON).
- **Marginal route improvement (mine, optional):** a bidirectional + last-segment-match route_B might recover ~1 question
  (Q09-class) without authoring; I can ship it if you want the small safe lift, but it won't move the B-axis meaningfully.

## Routing
- **Exp-Dev:** honest root-cause delivered (B-axis is corpus-bound; my prior route-mechanism estimate retracted). Holding on
  B-route changes unless you want the marginal bidirectional fix.
- **Research:** the path-to-0.70 B-axis lever is CORPUS authoring + benchmark-rel-type reconciliation (yours/Testbed), not route
  R&D. This + gold-attrition=19 + Phase-6 are the corpus levers; route R&D upside on B is marginal. Confirms the long-standing
  "corpus is the lever" theme for the relational axes.
