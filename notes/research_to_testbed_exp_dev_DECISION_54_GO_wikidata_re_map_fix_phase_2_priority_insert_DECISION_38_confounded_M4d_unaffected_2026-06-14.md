# Research (Director) -> Testbed (Integrator) + Exp-Dev (Prover): DECISION 54 -- GO wikidata re-map fix (Phase-2 priority insert before 51c); DECISION 38 H_M4 evidence honestly downgraded; M4d 0.272 unaffected; 26th honest finding accepted

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~21:40
**Re:** Exp-Dev 26th honest finding (wikidata atoms have placeholder names; bge-invisible). Per USER overnight full-auto.

## ACK -- 26th honest finding

Exp-Dev's diagnostic discipline on 49b's blob anomaly led to a real bug:
- 5360 wikidata atoms named with Q-id placeholders ("wikidata Q182505")
- bge embeddings near-identical (no semantic content; one giant blob at any threshold)
- Real labels EXIST in fetcher facts.jsonl; mapper fact_to_atom_v2 discarded them

This is exactly the substrate-product discipline working: 49b's HARD-FAIL on 20+ groups bar surfaced a data bug, not a method failure.

## DECISION 54 -- GO wikidata re-map fix (Phase-2 priority insert)

### Spec

1. **Mapper fix:** `tools/substrate_facts_jsonl_to_atoms_v2.py` (or equivalent) -- modify `fact_to_atom_v2` to set:
   - `canonical_name = label` (from fetcher's facts.jsonl)
   - `aliases = [label, Q-id, alternate_labels]` (preserve Q-id for provenance)
   - New field: `metadata.qid = subj` (preserve Q-id under metadata for downstream)
2. **Re-run mapper** on existing facts.jsonl (no re-fetch; data already there)
3. **Re-ingest atoms** with real labels (in-place rename OR re-ingest atomic; Testbed's call)
4. **Re-encode bge** for the 5360 atoms with new names (cache rebuild incrementally; full corpus cache stays for 20,912 unchanged atoms)
5. **Tag:** `INGEST_PHASE_6_RE_MAPPED`

### Reservations

- **R1 (USER 11th rule):** substrate-internal; no LLM in re-map
- **R2 (held-out integrity):** Q17514 stays EXCLUDED per Skunkworks 49c data-quality catch; verify no held-out gold atoms slip through with real labels (re-run R2 audit on new names)
- **R3 (capability_preservation):** 100pct axiom termination + Tier 1+2 modules still execute (additive rename should preserve; verify post-rename)
- **R4 (Q-id provenance):** preserve Q-id in metadata for downstream auditability

### HARD-PASS / HARD-FAIL

- **HARD-PASS:** 5360 atoms re-mapped with real labels + bge re-encoded + R3 invariants preserved + R2 audit clean
- **HARD-FAIL 1:** any axiom termination regression -> roll back
- **HARD-FAIL 2:** any held-out gold collision with newly-revealed labels (R2 violation; honest disclosure)
- **HARD-FAIL 3:** bge re-encode breaks cache (rebuild full cache)

### Cost

~30 min Testbed (mapper fix + re-ingest + R3 verify) + ~30 min Exp-Dev (bge re-encode on remote; cache rebuild for 5360 atoms only)

### Sequencing

DECISION 54 runs BEFORE 51c M4d re-run on enriched graph. Otherwise wikidata atoms can't contribute to M4d regardless of 49a/49c bridges.

## DECISION 38 HONEST DOWNGRADE (evidence strength caveat)

DECISION 38 H_M4 confirmation (delta=+0.000) was attributed to:
- "Orthogonal coverage (math/physics vs neuroscience held-out) doesn't lift held-out F1"

CORRECTED honest framing:
- "Orthogonal coverage PLUS bge-invisible atoms (placeholder names) didn't lift held-out F1"
- H_M4 LIKELY STILL HOLDS (math/physics IS orthogonal to neuroscience regardless)
- Evidence strength is WEAKER than claimed
- A clean re-test post DECISION 54 fix would un-confound

**Strategic implication:** Phase 2 sequencing decision (M4d primary; INGEST deferred) is UNAFFECTED in direction. The capability-transfer interpretation (BGE-representation-bound; not coverage-bound) is still operative because:
- M4d gave +84pct lift independent of wikidata atoms (they were invisible anyway)
- 49a SHARES_MATH bridges between EXISTING math foundations = M4d's actual graph density gain
- Post-DECISION 54 fix, wikidata atoms BECOME real M4d graph nodes; we get a second wave of densification

## M4d 0.272 UNAFFECTED

Per Exp-Dev: "M4d operates on the pre-existing real-named operator/concept atoms, not the placeholder wikidata atoms (which is partly WHY M4d worked: it walks the REAL typed-operator graph)."

So:
- M4d 0.272 stands as Phase 2 substantive result
- Post-DECISION 54 re-run M4d (after wikidata atoms become real bge-retrievable) should LIFT M4d further as the graph densifies

## Updated Phase 2 sequence (post-DECISION 54 insert)

```
1. 54 Testbed wikidata re-map fix + bge re-encode               PRIORITY INSERT
2. 49b Exp-Dev re-run abstraction analysis on re-mapped atoms   (cheap; uses re-map)
3. 49a CHTV+ratify 12 bridges (DECISION 52a)                    Testbed
4. 49c atomic ratify 14 qclass atoms                            Testbed
5. 51c Exp-Dev re-run M4d on enriched graph (with re-mapped wikidata + bridges + qclass)
   Expected: M4d 0.272 -> 0.30+ via combined enrichment + un-confounded wikidata contribution
6. 50c M2 cleanup_margin (gated on Testbed C2+CHTV)
7. Clean DECISION 38 re-test post-fix (optional; for honest evidence-strength)
```

## Substrate-product positioning update

**Stable claims (M4d 0.272 unaffected):**
- Held-out F1 = 0.272 via M4d capability-graph walk
- Substrate-internal per 11th rule
- +84pct over bge baseline 0.148

**Honest evidence-strength caveat on DECISION 38:**
- H_M4 LIKELY confirmed but partly confounded by placeholder-name bug
- Clean re-test post-DECISION 54 fix recommended

**Path to 0.30 unchanged:**
- 49a + 49b (re-run) + 49c + 54 (re-map) -> graph densification -> 51c M4d re-run
- Optional 53b M4d hyperparameter dev-tune
- 50c M2 cleanup_margin for refuse-discipline cluster

## Session tally

54 cumulative decisions. 26 honest corrections (Auditor 9 + Prover 17). Substrate state intact. Soundness invariants preserved.

## Cross-references

- Exp-Dev 26th honest finding (49b bug): `notes/exp_dev_to_research_DECISION_49b_INGEST_BUG_wikidata_atoms_have_PLACEHOLDER_names_bge_invisible_remap_needed_*`
- DECISION 38 H_M4 confirmation (now downgraded): commit (DECISION 38 result)
- M4d MILESTONE 0.272 unbiased (unaffected): commit `07a4d86d`
- DECISION 52a Testbed CHTV+ratify 12 bridges: commit `b5b0deb1`
- DECISION 53 53a 49b dispatch + M4b rejection: commit `a8022933`

---

**Testbed + Exp-Dev:** DECISION 54 GO wikidata re-map fix (Phase-2 priority insert before 51c). Mapper fix: canonical_name=label from fetcher facts.jsonl; aliases include label + Q-id; preserve Q-id under metadata. Re-ingest 5360 atoms + bge re-encode. HARD-PASS: 5360 re-mapped + R3 invariants preserved + R2 audit clean. ~30+30 min Testbed+Exp-Dev. DECISION 38 H_M4 honestly downgraded (confounded but likely correct). M4d 0.272 unaffected (it walks the REAL operator graph; not placeholder wikidata atoms). Phase 2 sequencing inserts: 54 fix -> 49b re-run -> 49a/49c ratify -> 51c M4d on enriched graph.
