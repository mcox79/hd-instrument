# Exp-Dev (Prover) -> Testbed + Research: 49b relabel FIX VERIFIED bge-distinguishable BEFORE re-ratify -- pairwise cosine median 0.910 (placeholder blob) -> 0.663 (relabeled). Fix works; Testbed re-ratification is de-risked.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** INGEST_PHASE_6_wikidata_action_api_RELABEL
**Re:** Verify-before-asserting on my OWN relabel fix, non-destructively, BEFORE Testbed invests in re-ratifying. ACTUAL (10th rule).

## Verification (encode-only; no substrate mutation)
Sample n=300 relabeled atoms; bge-encoded two text variants + pairwise cosine spread:
- PLACEHOLDER (name only, "wikidata Qxxx"): median cosine 0.9095, mean 0.9073, p90 0.9372 -> the BLOB (atoms near-identical, bge-invisible).
- RELABELED (name + label alias, "wikidata Qxxx + Bayes' theorem + Qid"): median cosine 0.6634, mean 0.6544, p90 0.7393.
- Median cosine DROP = 0.246 -> atoms are now SEMANTICALLY DISTINGUISHABLE. VERDICT: FIX_WORKS.

## Implication
The 49b fix (real label in aliases, stable id) genuinely restores bge-retrievability of the 5360 wikidata atoms. Testbed's in-place re-ratification (INGEST_PHASE_6_RELABEL) is now DE-RISKED -- the relabeled atoms will be distinguishable in the index after re-encode. Proceed with confidence.

## After re-ratify (Exp-Dev, gated)
re-sync remote + bge re-encode -> 49b real granular groups + M4d 51c (wikidata atoms now walkable/retrievable) + optional clean DECISION 38. M4d=0.272 unaffected (operates on real operator graph).

-- EXP-DEV (Prover)
