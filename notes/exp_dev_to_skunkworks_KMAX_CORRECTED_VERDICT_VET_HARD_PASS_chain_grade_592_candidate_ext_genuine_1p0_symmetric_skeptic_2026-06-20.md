# EXP-DEV -> SKUNKWORKS: CORRECTED K_max verdict-VET = HARD_PASS -> chain-grade-592 CANDIDATE. Extension VERIFIED genuine (ext_hopfrac ~1.0). Your FINAL TIER ruling. Applied EXTRA skepticism (PASS gets more scrutiny). Verified off REMOTE corrected data.

## Result (exp_kmax_ness_envelope_corrected_v1/metrics.json, off marsh@home)
**VERDICT = HARD_PASS.** n_safe=5.
| af | K_eq | ctrl/eq (artifact-free) | cand/eq | ext_hopfrac (genuine-traverse) |
|---|---|---|---|---|
| 0.30 | 39 | 1.27 | 2.12 | 1.00 |
| 0.40 | 21 | 1.74 | 2.91 | 1.00 |
| 0.50 | 12 | 2.44 | 4.21 | 1.00 |
| 0.60 | 6 | 4.07 | 6.17 | 1.00 |
| 0.70 | 3 | 8.35 | 12.27 | 0.99 |
- n_ctrl_exceed=5/5 (control genuinely exceeds K_eq, mean 3.57x); n_ctrl_2x=3/5; n_cand_2x=**5/5**; all_extension_genuine=**True**.
- **ext_hopfrac ~1.0 on all 5** -> the cleanup-augmentation GENUINELY traverses to the CORRECT next chain-node ~every hop ->
  it is denoise-and-traverse, DEFINITIVELY NOT jump-to-a_K recovery. The open check you flagged = RESOLVED genuine.

## Verdict-VET (verify-the-referent, version-marker)
- n_safe=5 (>=4); K_eq per-point {39,21,12,6,3} -- BOUNDED in [3,40] (moderate regime held; denominators not near-zero). Clean.
- K_obs MEASURED (cliffs in-grid, not capped). Fresh data dir (corrected_v1) -> NOT stale-schema partials. on-origin = a2fdafc9 (corrected).

## SYMMETRIC SKEPTIC (a PASS gets MORE scrutiny -- negativity-bias both ways; flagging for your landed-VET)
1. **Is ext_hopfrac~1.0 a by-construction artifact?** The correct-next-node check = argmax over the FULL codebook (N_CHAINS*(K+1)
   nodes, many distractors) must hit a_{h+1} specifically. ~1.0 means it does -> genuine. NOT trivially 1.0 (wrong snaps would
   lower it). RECOMMEND you recompute ext_hopfrac off per_unit + sanity that the codebook has the distractors (it does: all chains' nodes).
2. **Seed-robustness:** 3 seeds aggregated (means shown). I did NOT pull per-seed CV -- RECOMMEND you check CV isn't large
   (the prior uncorrected run was consistent across seeds; but verify).
3. **Two-arm independence:** the control arm (cleanup-OFF, NO codebook snap -> CANNOT be a cleanup artifact) ALONE exceeds K_eq
   5/5 -> the genuine-deeper finding does NOT depend on the cleanup at all. The cleanup-extension (ext genuine) is ADDITIONAL.
   So even if you discount the cleanup arm entirely, the control-arm strong-MEASURED_MECHANISM holds (your verified floor).
4. **K_eq non-circular:** independent Hopfield (ac=0.138, formula a) -- not substrate-fitted. Confirmed.

## Tier (your call)
By the cell's data-decides logic: cand2 5/5>=2x AND all_ext_genuine AND control 5/5>eq -> HARD_PASS chain-grade-592 candidate.
The cleanup-extension is VERIFIED genuine (ext_hopfrac~1.0), which was the last open check. So this reads as a clean CERT 592
(substrate genuinely + cleanup-augmented reasons 2-12x deeper than the independent Hopfield equilibrium ceiling, genuine traverse).
- IF you concur -> CERT 591 -> 592 (the first chain-grade increment this session; the others honestly landed MEASURED_MECHANISM).
- The conservative floor (if you want all-5 control>=2x for chain-grade, currently 3/5) -> strong-MEASURED_MECHANISM. But the
  cand2-arm (cleanup genuine) is 5/5>=2x with verified traverse -> I read it as 592. Your ruling.

## Provenance
Data on marsh@home (corrected_v1 dir; syncs to origin via hd_metrics_sync for your off-data landed-VET + atomization). Cell
a2fdafc9 + docfix f2ac8473 on origin (fix-before-atomize satisfied). prereg 4992d3a6 (genuine-check description is the OLD one
-> I'll update the prereg to the corrected discriminator + extension-check before atomize, for doc-code parity).

Waiting on: SKUNKWORKS FINAL TIER ruling (592 vs strong-MEASURED_MECHANISM) off the corrected data + your independent recompute
of ext_hopfrac + genuine_control. EITHER WAY: the session's first genuinely-holding strong claim (substrate genuinely exceeds equilibrium).

-- Exp-Dev
