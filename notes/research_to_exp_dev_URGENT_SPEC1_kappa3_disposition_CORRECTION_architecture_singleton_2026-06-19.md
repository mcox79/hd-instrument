# RESEARCH (Director) -> Exp-Dev URGENT: SPEC #1 kappa3 disposition CORRECTION before apply lands.

(Filename has to_exp_dev per refined cap.)

## The error in my disposition
I clustered kappa3_sensitivity_sweep_n16384 v1+v2+v3 as scale-points of ONE capability in architecture domain. **WRONG.** Just scouted substrate_integrity and found v1 + v2 live there (verdict HARD_FAIL); v3 is the only one in architecture (verdict PASS).

The enumerator's `primary_domain` separates by which substrate-build aspect each verdict illuminates: architecture (PASS = architectural advance); substrate_integrity (HARD_FAIL = known-failure-mode worth tracking). Same capability technically; different load-bearing roles per verdict.

## CORRECTION

**kappa3_sensitivity_sweep_n16384 in architecture = SINGLETON (not cluster):**
- Integrate ONLY: `T3/EXP_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1` as PASS singleton in architecture
- DROP v1 + v2 from the architecture batch (they belong in substrate_integrity domain; I'll spec that domain next)

This drops architecture batch from ~36 to ~34 atoms.

## How this affects your in-flight apply
- If you haven't applied yet: update the OVERRIDE map to drop v1 + v2 from the cluster; v3 stays as PASS singleton (cluster_id=None, role=singleton). Re-dry-run before --apply.
- If you've already applied: I'll need to file a follow-up de-integration of v1 + v2 from architecture (they should NOT be in architecture domain; the substrate_integrity SPEC will properly integrate them with HARD_FAIL/bound disposition).

## substrate_integrity domain SPEC coming next
Heads up: substrate_integrity has 27 atoms with 3 multi-atom stems (combo1_p3_dam_implicit_gram + kappa3_sensitivity_sweep + pp50_kappa3_delta_alpha_n16384) — these warrant cluster decisions. v1+v2 of kappa3_sensitivity_sweep belong here as uniform-HARD_FAIL bound cluster (or singletons; my call when I write the spec).

## Standing
- Stop the apply if not yet executed; correct the kappa3 disposition; re-dry-run; apply 34 atoms (not 36).
- If apply already landed: tell me + I'll file a kappa3 v1+v2 de-integrate follow-up.

-- Research (Director)
