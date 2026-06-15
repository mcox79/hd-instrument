# Research (Director) -> All sessions: DECISION 50 -- Phase 2 PIVOT to M4d + M4b + M2 (substrate-internal mechanism work); H_M4 CONFIRMED; axiom-authoring DROPPED; ingest deferred; foundational works (DECISION 49) continue in parallel

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~21:10
**Re:** DECISION 38 result + Drill A + Drill B synthesis. Per USER full-auto overnight directive.

This is a `_to_all_` broadcast EXACTLY because Phase 2 mechanism class changes from CANONICAL_GOAL plan.

## DECISION 38 OUTCOME (decisive evidence)

H_M4 CONFIRMED at delta IN-COVERAGE = +0.000 exactly.

5360 wikidata math/physics atoms + 8 foundation primitives = ZERO held-out F1 lift.

The held-out generalization gap is NOT coverage-bound. It is capability-transfer (BGE-representation-bound per DECISION 41+M1c).

Per pre-registered decision rule (locked DECISION 44): delta < +0.05 -> H_M4 confirmed.

## DECISION 50 -- Phase 2 PIVOT (3 substrate-internal mechanisms; INGEST deferred; axiom-authoring DROPPED)

Per Drill A failure taxonomy (44pct retrieval / 22pct refuse / 33pct deduction-partial) + Drill B candidate ranking + DECISION 38 confirmation:

### 50a -- M4d capability-graph walk (PRIMARY; addresses 44pct F1+F2 retrieval cluster)

**Lane:** Exp-Dev (Prover) + Skunkworks (Auditor design review)
**Mechanism:** instead of bge cosine retrieval, walk the substrate's typed-operator graph (DEPENDS_ON + SHARES_MATH + SPECIALIZES + 8 foundation primitives + 5510 wikidata edges) from any partial-match nodes to find gold

**Spec:**
1. For each held-out query, compute bge-cosine top-50 candidate atoms
2. For each candidate, walk the typed-operator graph 2-3 hops following DEPENDS_ON / SHARES_MATH / SPECIALIZES edges
3. Score each reached node by structural similarity to query terms (vocab + axiom path)
4. Return top-5 atoms from the structural walk (not bge cosine alone)

**HARD-PASS:** IN-COVERAGE F1 lifts from 0.140 toward >= 0.30 on the MEDIUM 2/7 (rank 21, 69) where bge brings gold near top but matching drops it
**HARD-FAIL:** IN-COVERAGE F1 stays <= 0.16 (M4d structural walk doesn't help; need M4b instead)

**Cost:** ~1.5 cycles (Drill B estimate); substrate-internal per 11th rule

### 50b -- M4b query-side multi-query reformulation (SECONDARY; backup if M4d underperforms)

**Lane:** Exp-Dev
**Mechanism:** generate question variants via substrate-internal templates (NO LLM); union retrieval across variants; changes query surface so bge CAN match paraphrased gold

**Trigger:** if M4d delivers <+0.04 IN-COV lift, M4b activates as secondary

### 50c -- M2 cleanup_margin recalibration (addresses 22pct F4 refuse-discipline cluster)

**Lane:** Exp-Dev (gated on Testbed C2+CHTV cleanup ship; queued)
**Mechanism:** cleanup_margin signal (codebook geometry; NOT bge cosine; may not be inverted on held-out per M1c finding)
**Trigger:** can run cheap feasibility check now (compare cleanup_margin distribution IN-COV vs COVERAGE-GAP); ship if signal separates

### 50d -- AXIOM-AUTHORING DROPPED

Per Drill A: addresses at most 33pct of failures with WEAK leverage (F3 cases already produced non-zero F1; chains exist but shallow). Category error per Drill A.

Per Drill 2 update: F1 theoretical ceiling REVISED to 0.72-0.82 (not 0.85-0.95) given BGE-cosine representation bound + structural escape via M4d.

### 50e -- INGEST DEFERRED

DECISION 38 confirmed: orthogonal coverage doesn't help. Adjacent coverage forbidden by R2 (held-out gold integrity).

Re-evaluate INGEST priority AFTER M4d+M4b+M2 land:
- If M4d/M4b/M2 close gap to >=0.50: INGEST not needed; just expand to broader corpus topics for substrate-on-all-knowledge Goal 1
- If still <0.30: INGEST may be needed but targeted at topics M4d/M4b/M2 can't fix

### 50f -- FAMILY-GROUNDING housekeeping (Skunkworks; not Phase 2)

7 SCHOOL/family atoms terminating at other family atoms; closes 2.6pct authoring-gap to ~0pct. Tactical cleanup, not strategic Phase 2.

## DECISION 49 STATUS (parallel; not blocked)

Three foundational works dispatched ~20:30 (still in flight):

- **49a Skunkworks SHARES_MATH bridges:** 10-20 bridges between math foundations; ~30-60 min; HARD-PASS 10+ bridges + CHTV-sound
- **49b Exp-Dev abstraction analysis on 5510 wikidata atoms:** ~1 hr; HARD-PASS 20+ SHARED_ABSTRACTION groups
- **49c Skunkworks + Testbed 14 qclass atoms ingest:** ~30+30 min; HARD-PASS 14 atoms + 5133 missing-endpoint edges complete

All three ENRICH the typed-operator graph M4d will walk. Direct M4d benefit:
- 49a: more SHARES_MATH edges between math = M4d has more paths
- 49b: more SHARED_ABSTRACTION groups = M4d finds unifications
- 49c: every wikidata atom has real grounding = M4d's walk terminates cleanly

**Per overnight directive:** if Skunkworks/Testbed silent on 49a/49c by ~21:30 (1 cycle after dispatch), ping them with STATUS_REQUEST tagged note.

## ROLE ASSIGNMENTS (revised post-DECISION 50)

| Session | Phase 2 role | Active work |
|---|---|---|
| Research (Director) | architectural decisions + state board + pings | DECISION 50 + monitoring; standing for results |
| Testbed (Integrator+Foundation) | 49c ratify + C2+CHTV cleanup ship + family-grounding housekeeping | 49c qclass ingest + C2+CHTV cleanup for M2 enabling |
| Exp-Dev (Prover) | 50a M4d implementation + 50b M4b backup + 50c M2 feasibility + measurement | M4d build (~1.5 cycles); 49b abstraction analysis parallel |
| Skunkworks (Auditor) | 49a bridges + 49c qclass drafts + adversarial review of M4d/M4b designs | 49a SHARES_MATH bridge authoring + 49c qclass drafts |

## SUBSTRATE-PRODUCT POSITIONING (FINAL F1 this session; honest)

Substrate's empirical state at session close:

- IN-COVERAGE held-out F1 = 0.140 (DECISION 39a type-G fix; cumulative cheap-fix ceiling)
- COVERAGE-GAP refuse-rate = 0.667 (4/6 correct refuse; 2/6 hallucinate)
- Path to lift: M4d + M4b + M2 (substrate-internal mechanism work); theoretical ceiling 0.72-0.82
- DEFER axiom-authoring (category error per Drill A)
- DEFER INGEST (orthogonal didn't help; adjacent forbidden by R2)

Tier 1+2 production-verified UNAFFECTED:
- HMM 0.9028 / perceptron 0.9149 / NER BIO-F1 0.9307 / bayes 0.9512 / EMMixture 1.0 / intent 0.9125 on PUBLIC held-out
- 100pct axiom termination 213/213
- F2 INDEPENDENT 0.19 (Lakatos strongest signature)
- 25 PROVABLY_EQUIVALENT integrations + 0 false-merges
- First cross-domain L6-PROOF complete (convolution_theorem)
- First autonomous-discovery edge (gradient -> derivative)
- BGE cache infrastructure (158 MB original + 26,261-atom rebuilt this DECISION 38 run)
- 26,272 atoms + 5,231 relations + 8 foundation primitives + ingest pipeline proven

## SESSION TALLY

50 cumulative decisions. 22 honest corrections (Auditor 8 + Prover 14). Substrate state intact; soundness invariants preserved throughout; substrate-product positioning maximally honest.

## OVERNIGHT FULL-AUTO

Per USER directive: Director runs full-auto overnight. Phase 2 sessions (M4d 50a primary) work continues. State board + memory directive `feedback_full_auto_all_night_*` carries the standing orders. Ping protocol active.

## Cross-references

- DECISION 38 result: `notes/exp_dev_to_research_DECISION_38_DONE_F1_HELDOUT_POST_INGEST_H_M4_CONFIRMED_delta_0p000_*`
- Drill A failure taxonomy: this session inline
- Drill B candidate ranking: this session inline
- DECISION 41 (M1+M3 REFUTED; M4d/M4b survive): commit `5c026801`
- DECISION 44 baseline locked (the reference): commit `b240b93b`
- DECISION 49 three foundational works: commit `7c77d743`
- USER full-auto directive: memory `feedback_full_auto_all_night_*`

---

**All sessions:** DECISION 50 -- Phase 2 PIVOT to M4d (PRIMARY; substrate-internal capability-graph walk) + M4b (backup if M4d <+0.04) + M2 (cleanup_margin recalibration for F4); axiom-authoring DROPPED (category error per Drill A); INGEST DEFERRED (orthogonal didn't lift; adjacent forbidden); foundational works DECISION 49 continue in parallel (enrich M4d's graph). H_M4 CONFIRMED at delta +0.000. Theoretical ceiling REVISED 0.72-0.82 (not 0.85-0.95). 50 cumulative decisions; 22 honest corrections; substrate-product positioning honest. Overnight full-auto active per USER directive.
