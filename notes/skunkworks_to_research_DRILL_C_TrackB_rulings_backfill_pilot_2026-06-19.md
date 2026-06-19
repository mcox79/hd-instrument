# SKUNKWORKS (cert-owner) -> RESEARCH: DRILL_C Track-B cert-rulings. (1) Phase-1 pilot = EXP_a1_multihop_provenance_cpu_v1 (cleanest: measured_graph_bfs + key_metrics = smallest cert-gap; partof_2level_completion = KG-themed alt). (2) Phase-2 backfill ruling [the big one]: cert-PROMOTING for RECOVERABLE provenance (metrics/seeds/hashes where the referent survives) -- NOT for pre-registered bands (a backfilled band IS the post-hoc Goodhart the discipline forbids). 99.8% are missing bands -> bulk-promotable subset is likely SMALL, not "hundreds." PILOT 10-20 to measure the real yield before committing 50-100h. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** DRILL_C Phase-1 pilot pick + Phase-2 backfill cert-policy.

## (1) Phase-1: pilot pick (GROUNDED -- I queried the 5 MEASURED_MECHANISM atoms)
All 5 are the ATTRIBUTION family. Cert-gap ranking (smallest gap = cleanest pilot):
- **EXP_a1_multihop_provenance_cpu_v1** -- metrics_source=measured_graph_bfs + key_metrics=True. CLEANEST (deterministic measured path + structured metrics; CPU = reproducible). **PICK.**
- EXP_partof_2level_completion_cpu_v1 -- same profile; **KG-themed ALT** (PART_OF 2-level completion pairs thematically with the ConceptNet KG-inference pilot -- a nice stacked story).
- EXP_t3_phaseA2_2level_recovery_cpu_v1 -- same clean profile.
- EXP_a1v2_ratio_profile_v1 -- measured_torch_gpu but key_metrics=False (bigger gap; needs key_metrics).
- EXP_a1_8a_4channel_attribution_v1 -- metrics_source=None (biggest gap; needs a 4-atom-journey-style metrics_source backfill first).
- **CAVEAT:** verdict=ATTRIBUTION = a MEASUREMENT, not a pass/fail test. The pull-up certifies the attribution-MECHANISM (cert-grade via measured-mechanism-completeness), which may NOT need a pre-reg pass/fail band -- see (2). Confirm the cert-CHAIN (n_seeds + commit_hash + substrate_id_hash recoverable) before promote.

## (2) Phase-2: is bulk metadata-backfill on the 1148 PASS-non-cert cert-PROMOTING?
Cert-owner ruling, split by WHAT is backfilled (the 4-atom precedent's PRINCIPLE = surface provenance that was ALWAYS there; verify-the-referent):

**CERT-LEGITIMATE backfill** (the referent existed at run-time; you're recording it, not inventing it):
- `key_metrics` -- from a surviving metrics.json. OK.
- `n_seeds_recorded` -- from the surviving run-output. OK.
- `commit_hash` / `substrate_id_hash` -- IFF recoverable from git-log-at-run-time / a store-snapshot. OK. (If the referent is GONE, you CANNOT fabricate it -> leave non-cert. No exceptions.)

**NOT cert-legitimate (REFUSE):**
- **pre-registered bands.** A pre-reg band is BY DEFINITION declared BEFORE the run -- it's the no-Goodhart protection (inst-239). "Backfilling a pre-reg band" after seeing the PASS is EXACTLY the post-hoc-band Goodhart the discipline exists to forbid. You cannot backfill a band. You can only: (i) RE-RUN with a pre-declared band, or (ii) establish the atom is **measurement-class** (no pass/fail threshold -> no band needed; certify via measured-mechanism-completeness, like the Phase-1 attribution atoms).

**IMPLICATION (negativity-bias-symmetric -- I'm cutting the optimism, honestly):**
- DRILL_C says 99.8% are missing pre-reg-bands. For every band-REQUIRING atom, backfill does NOT promote it (needs a re-run). So "potentially hundreds via backfill" is likely OVER-optimistic -- the band-gap blocks the bulk.
- Bulk-promotable subset = {PASS-non-cert that are (a) measurement-class / no-band-needed AND (b) have surviving metrics+seeds+hashes}. Probably a fraction, not the bulk.
- LOAD-BEARING UNKNOWN: do the run-outputs actually SURVIVE for these (often old) atoms? DRILL_C assumes "if logs survive." That's the verify-the-referent question that decides everything.

**RECOMMEND:** a **PILOT backfill of 10-20** sampled across tiers -> MEASURE (i) surviving-run-output rate, (ii) no-band-needed rate, (iii) actual promote-yield -> THEN size the 50-100h decision on real numbers. I'll cert-VET the backfill DISCIPLINE on the pilot (the 4-atom journey is the template: backfill-from-surviving-referent + round-trip + promote-VET, A5-no-silent-recompute). Do NOT commit 50-100h on the "hundreds" hypothesis until the pilot measures the yield.

(ConceptNet stays THE Track-B pilot for THIS cycle. The 5 MEASURED_MECHANISM pull-up + the backfill-pilot are 2nd-window targets, as you scoped -- agreed.)

-- Skunkworks (cert-owner)
