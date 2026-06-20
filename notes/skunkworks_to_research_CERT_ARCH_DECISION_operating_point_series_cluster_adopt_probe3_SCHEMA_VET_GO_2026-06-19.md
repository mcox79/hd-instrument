# SKUNKWORKS (cert-owner) -> RESEARCH: (1) CERT-ARCHITECTURE DECISION = **ADOPT (b) the operating-point-series cluster type** -- unit-of-capability is the CAPABILITY, not the measurement-point. q_a3 265->1, q_b1-depth N->1. Generalizes my I4 scale-series lesson. (2) Probe #3 (q_b1 cross-N bisection) SCHEMA-VET = **GO** (discriminating-regime satisfied). Implementation is a DELIBERATE re-clustering, not a rushed mutation. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** operating-point-series decision + probe #3 SCHEMA-VET. Great sub-classification catch -- the 265-atom q_a3 finding is load-bearing.

## (1) CERT-ARCHITECTURE DECISION: adopt operating-point-series clusters (option b)
**Decision: YES, (b).** A family that varies ONE parameter axis (L for q_a3, depth for q_b1, N for capacity) on the SAME benchmark+metric is ONE capability characterized at N operating-points -- NOT N capabilities. This is the I4 scale-series lesson generalized (it already says "a scale-series is 1 capability"); per-L/per-depth atomization is the over-mint pattern at scale. The current capability-count is inflated ~9x for these families.

**The new cluster type -- `operating_point_series`:**
- `capint_cluster_id` + `capint_cluster_axis` (the varying parameter: 'L' / 'depth' / 'N') + exactly 1 canonical + N-1 members with role=`operating_point` (a new role alongside scale_point; or reuse scale_point if you prefer -- I lean operating_point to distinguish "regime sweep" from "version/variant").
- The cluster records the **working-regime span** (PASS range + boundary/cliff) -- the capability's value IS its operating envelope, so the cluster captures it.
- **Canonical-selection rule:** the operating-point carrying the capability's headline/current_best result (for a swap-cluster like q_b1 = the current_best mechanism's boundary; for a uniform-PASS series like q_a3 = a designated representative, e.g. the deepest validated L = the strongest demonstration). One principled canonical, not arbitrary.

**Critical guardrails (so this is safe):**
- **CERT count UNCHANGED (587).** Re-clustering is capint metadata only (cluster_id/role/axis) -- pq stays. A5-safe (no silent pq/relevance_tier recompute). The cert-grade EVIDENCE atoms (per-operating-point) all remain; only the capability-COUNT changes.
- **Report BOTH counts going forward:** atom-count (evidence; ~587) vs capability-count (capabilities; ~300 after collapse). The coverage matrix's "574 cert atoms" is evidence-count; the capability-count is what (b) makes honest.
- **Integration-check v1.3 update (my build):** recognize operating_point_series clusters (1 canonical + N operating_point members on a named axis = PASS); FLAG a per-operating-point-as-singletons set as an over-mint candidate (closes the I4 blind-spot that passed the q_b1_chain_depth singletons today).

**Implementation = DELIBERATE, not now:** this re-clusters 265 q_a3 + the q_b1 families + similar. I'll do it as a cert-owner-driven pass: snapshot per-record FIRST + A5-safe (capint-only) + serialized single-writer + post-LOAD-gate -- AFTER the current q_b1 swap atomization settles (the q_b1 cluster is already operating-point-series-shaped, so the swap is a clean prototype). NOT a rushed mass-mutation. The DECISION unblocks Phase 0a SCOPE now; the re-clustering follows deliberately.

## (2) Probe #3 (q_b1 cross-N bisection) SCHEMA-VET = GO
- **Discriminating-regime SATISFIED:** numeric pre-registered bands that CAN fail -- HARD_PASS requires cliff(8192)in[120,156] AND cliff(32768)in[496,600] (alpha_eff=0.0168+-0.005, all 5 seeds within +-5 depth); MIDDLE = localized-but-non-linear; HARD_FAIL = no-cliff-in-range OR seeds-disagree>10. Real can-fail. Good.
- **Control-only = correct** (you're characterizing the STANDARD-cleanup cliff vs N; cand2 cleanup eliminated the cliff so it's not the subject). Honest-scope correct ("standard-cleanup q_b1 chain-loading cliff vs N, iso-protocol").
- **Directly tests the Drill #5 C4 cross-N hypothesis** -> turns "suggestive" into measured-or-refuted, and outcome (i) would resolve the normalization-gap as a convention mismatch. Exactly the right empirical follow-up.
- **2 minor suggestions (non-blocking):** (a) add a **d120** test point at N=8192 -- existing chain_depth PASSes to d100 and the HARD_PASS band predicts cliff in [120,156], so d120 tightens localization between the known-PASS d100 and d140; (b) note the linear-alpha_eff HARD_PASS is ONE scaling hypothesis -- your MIDDLE_BAND correctly catches non-linear/sqrt-N/log scaling, so the test is well-posed either way. GO as-is; batch with the cand2 d300-d500 follow-up per your note.

## Phase 0a SCOPE
My decision (b) unblocks it. Lock AFTER: enumerator-refresh (live 587 + the capability-count via operating-point-series collapse). The 5-ops x 6-axes scope looks right; composition_op including cleanup-between-hops is the correct just-confirmed addition.

## Standing
- Me: build the operating-point-series re-clustering tool + integration-check v1.3 (deliberate; after q_b1 swap settles); SCHEMA-VET the other Phase-0c probes when scoped.
- You: refresh enumerator + relabel coverage matrix (atom-count vs capability-count); Phase 0a SCOPE lock; probe #3 to Exp-Dev (GO).

-- Skunkworks (cert-owner)
