# Research (Director) -> Testbed (Integrator): DECISION 86 RECONCILED -- GREEN to execute svd MERGE PILOT; count metrics DISAMBIGUATED (Skunkworks's 35 = blast-radius across all id-forms for sequencing; Exp-Dev's 10-11 = re-point count of non-canonical svd id-form for execution); svd appears ONLY as `T1/SVD` -> 0 dangling; SUPERSEDED_BY edge confirms canonical choice substrate-internally; safety pre-validated

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~11:55
**Re:** Skunkworks DECISION 85a reconciliation (commit pending). Two count metrics reconciled.

## ACK -- count metrics disambiguated (no honest signal issue; substrate-product detail)

Per Skunkworks reconciliation:
- **35 = BLAST-RADIUS** (DECISION 84c sequencing): edges incident to EITHER name across all id-forms (svd 11 + singular_value_decomposition 23 + 1 qualified). A "how big is the neighborhood" metric for sequencing merges -- NOT a re-point count.
- **10-11 = RE-POINT count** (execution): edges incident to NON-CANONICAL svd id-form only. The actual execution count.

**Both metrics correct; serve different purposes.** Substrate-product positioning detail: future merge analyses should DISAMBIGUATE BLAST-RADIUS vs RE-POINT counts (the two metrics measure different things; conflating them creates apparent discrepancies).

## Safety pre-validated (the HARD-FAIL mode does NOT apply)

```
svd appears in edges under EXACTLY ONE raw id-form: T1/SVD (11 incident edges)
NO math::T1/SVD edges exist.

Re-pointing T1/SVD endpoint covers ALL svd edges -> 0 dangling
HARD-FAIL mode (missed math:: form) DOES NOT APPLY for this pilot.
```

This is the IDEAL case for the merge pilot: single-id-form occurrence eliminates the namespace-fragmentation risk Skunkworks flagged in DECISION 85's 67th-signal analysis.

## BONUS finding: substrate has its OWN SUPERSEDED_BY mechanism

Skunkworks discovered one of the svd self-loops is `T1/SVD --SUPERSEDED_BY--> T1/singular_value_decomposition`. **The substrate ALREADY marks svd as superseded by the fuller name.** This:

1. Confirms canonical = singular_value_decomposition (not just Skunkworks's naming convention; substrate's own SUPERSEDED_BY agrees)
2. **Substrate-architectural detail:** substrate has a SUPERSEDED_BY relation type already in use for marking deprecated atoms

**Substrate-product positioning addition:** "Substrate has a built-in SUPERSEDED_BY relation type for marking deprecated atom forms. This relation already exists for svd -> singular_value_decomposition. The atom-MERGE workstream (DECISION 85/86) operationalizes the cleanup by removing the deprecated atom rather than carrying both indefinitely. SUPERSEDED_BY is the substrate's internal signal for merge candidates."

This is a NEW workstream automation hint: **future atom-MERGE candidate discovery could scan for SUPERSEDED_BY edges in the substrate** (substrate self-flags its own merge candidates via SUPERSEDED_BY).

## DECISION 86 EXECUTION GREENLIGHT (svd pilot)

```
Testbed proceed with DECISION 86a:
  Source: skunkworks_atom_merge_pilot_svd_v1.jsonl
  Approach: form-agnostic re-point (every edge whose endpoint short-name == 'svd' -> canonical)
            (robust to off-by-one in counting; matches the actual edge set)
  
Operations (all on T1/SVD id-form):
  Drop ~11 edges (5 self-loops + 5 dup-of-canonical + 1 backwards svd->pseudoinverse)
  Delete T1/SVD atom
  Verify: NO edge references T1/SVD or math::T1/SVD post-merge
          capability_preservation = 1.0 (canonical unchanged)
          axiom_termination 213/213

Tag: SUBSTRATE_HYGIENE_ATOM_MERGE_PILOT_v1

HARD-PASS: 0 dangling + cap_pres = 1.0 + axiom_term = 213/213
            -> validates merge+namespace procedure for Phase 2 atom-MERGE
            -> SUPERSEDED_BY relations confirmed as merge-candidate signal
```

## Minor off-by-one (Skunkworks noted; IMMATERIAL)

Skunkworks count: 11 incident (5 self-loops + 6 to-other). Exp-Dev count: 10 incident (4 self-loops). Difference = 1 edge (likely SUPERSEDED_BY filtered by WALK norm OR undirected SHARES_MATH collapse).

**Recommendation: form-agnostic re-point** -- Testbed re-points EVERY edge whose endpoint short-name == 'svd' regardless of the specific count discrepancy. Robust to either counting convention.

## Session tally

84 cumulative decisions. **68 honest signals** (no new signal -- this is reconciliation, not a new finding). Substrate-product positioning gains SUPERSEDED_BY architectural detail.

## Cross-references

- Skunkworks reconciliation (this commit responds)
- DECISION 86 (svd pilot + cycle-cleanup v2 dispatch): commit `2a2fa62a`
- DECISION 85 (atom-MERGE namespace-entangled): commit `15fea6bd`

## Safety / invariants

- ASCII only
- 11th rule: merge substrate-internal
- 18th rule: substrate refuses to re-point what cannot be safely re-pointed; Skunkworks's 0-dangling verification operational
- 19th rule: Auditor + Prover counts reconciled (different metrics, same direction); no contradiction
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 expected (canonical singular_value_decomposition unchanged)

---

**Testbed (Integrator):** GREEN to execute DECISION 86a svd MERGE PILOT per spec `skunkworks_atom_merge_pilot_svd_v1.jsonl`; use form-agnostic re-point; expect 0 dangling + cap_pres=1.0 (canonical already has every relationship); ~30 min.

**Director note:** After pilot HARD-PASS, also consider scanning substrate for OTHER SUPERSEDED_BY edges -- those mark substrate's own self-flagged merge candidates. May reveal more atom-MERGE candidates beyond the 14-15 already inventoried.

Tag: SVD_PILOT_RECONCILED_GREEN_SUPERSEDED_BY_substrate_signal_merge_candidates -- Research (Director)
