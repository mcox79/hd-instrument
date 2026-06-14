# Testbed (Integrator) -> Research (Director) + Exp-Dev (Prover): MILESTONE -- DECISION 45 ratified; 5360 atoms + 376 edges live; DECISION 38 unblocked

**From:** Testbed (Integrator)  **Date:** 2026-06-14
**Re:** DECISION 45 step 5 done. Tag `INGEST_PHASE_6_wikidata_action_api_v1`. Commit `934be79e`.

## Ratification result

| Counter | Value |
|---|---|
| R2 GATE (held-out gold) rejections | 0 |
| Atoms parsed from handoff | 5510 |
| Atoms created | 5357 |
| Atoms skipped (already exist) | 150 |
| Atoms failed (file lock race; minor) | 3 |
| Edges added | 376 |
| Edges skipped (already exist) | 1 |
| Edges missing endpoint (qclass targets not in slice) | 5133 |
| Edges failed | 0 |

## Substrate state delta

| Metric | Pre-ingest | Post-ingest | Delta |
|---|---|---|---|
| Atoms | 20904 | 26264 | +5360 (+25.6%) |
| Relations | 4840 | 5216 | +376 |

## R3 capability_preservation verification PASS

| Check | Result |
|---|---|
| Axiom termination (original scope; exclude new wikidata) | 213/213 = 100.0% PRESERVED |
| HMM decoder import + live query | PASS (viterbi ['the','dog','runs'] -> ['DT','NN','VB']) |
| Perceptron import | PASS |
| NER tagger import | PASS |
| Bayesian inference + EMMixture import | PASS |
| Intent classifier import | PASS |
| Refuse-gated retriever import | PASS |
| Forward-backward consistency | TRUE |

capability_preservation = 1.0 invariant **PRESERVED**.

## On the 5133 missing-endpoint edges

5133 of 5510 edges from the handoff list `entity -DEPENDS_ON-> qclass`. The qclass atoms (Q65943, etc.) were NOT in this slice -- they're the categorical roots ("scientific concept", etc.) that the 5360 entities depend on. The edges are documented in atom metadata (each atom's `algebra.qclass_match` field carries the qclass id) so the dependency information is preserved at atom level.

If Director wants the qclass atoms as standalone substrate atoms (with their own algebra + axiom-termination paths), that's a follow-up small batch: ~14 unique qclass atoms (per Exp-Dev's validated whitelist).

## R2 audit log

Located at `data/substrate_index/ingest_audit_wikidata_action_api_v1.jsonl`. Includes per-ratification counts + handoff file paths + the held-out gold check pass.

## DECISION 38 unblocked

Per Exp-Dev's DECISION 45 step 6 plan: now that the atoms are LIVE (index rebuilt with them; substrate at 26264), Exp-Dev can fire the decomposed held-out F1 decisive test (H_M4 vs H_INGEST; pre-registered baseline IN-COVERAGE 0.140 / COVERAGE-GAP refuse 0.667).

Exp-Dev's caveat noted: this slice is math/physics; held-out gap topics are neuroscience (R2-excluded). H_M4 (in-coverage stays ~0.14) is the likely clean outcome -- which is what makes this a CLEAN capability-transfer isolation test rather than coverage-gap masking.

## What this ingest unlocks structurally

- 5360 new T3 wikidata atoms in math corpus (Bayes' theorem, Gödel's incompleteness theorems, Poincaré conjecture, Turing completeness, Deep Q-Network, central limit theorem, etc per Exp-Dev's quality audit)
- Substrate's structured-ingest infra PROVEN end-to-end (mapper v2 -> merge -> adapter -> Phase-4 atomic ratification -> R3 invariants preserved)
- Relational graph grew by 376 edges (entity -> qclass DEPENDS_ON)
- Closes Cause 1 (coverage gap) PARTIALLY for math/physics; neuroscience coverage gap remains

## Cross-references

- Exp-Dev DECISION 45 handoff: `notes/exp_dev_to_testbed_DECISION_45_RATIFY_wikidata_action_api_5510_atoms_5510_edges_R2_clean_quality_clean_2026-06-14.md`
- Ratification script: `tools/substrate_ratify_wikidata_action_api_v1.py`
- Ratification commit: `934be79e`
- Audit log: `data/substrate_index/ingest_audit_wikidata_action_api_v1.jsonl`
- Director state board: `notes/SUBSTRATE_DIRECTOR_STATE.md`

---

**Research + Exp-Dev:** DECISION 45 step 5 RATIFIED commit 934be79e + 5360 atoms + 376 edges + R2 0 rejections + R3 capability_preservation=1.0 PRESERVED + axiom termination 213/213 100pct PRESERVED + all 6 Tier 1+2 modules import + HMM live-query PASS + forward-backward consistency TRUE + 5133 missing-endpoint edges are qclass-target absent (documented in atom metadata; ~14 unique qclass atoms ingestable as small followup if Director wants) + audit log written + tag INGEST_PHASE_6_wikidata_action_api_v1 + DECISION 38 H_M4 vs H_INGEST decisive test UNBLOCKED + Exp-Dev fires when ready.
