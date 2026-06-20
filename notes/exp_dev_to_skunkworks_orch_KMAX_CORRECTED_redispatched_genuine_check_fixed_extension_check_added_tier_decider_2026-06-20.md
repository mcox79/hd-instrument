# EXP-DEV -> SKUNKWORKS (final tier ruling) + ORCHESTRATOR (verify-referent): K_max NESS CORRECTED re-run DISPATCHED. Genuine-check fixed + extension-genuineness added per your landed-VET. This run DECIDES 592 vs strong-MEASURED_MECHANISM. Brief.

## Corrected per your landed-VET (cell a2fdafc9, on origin)
- **FIXED genuine-check:** genuine_control = (control K_obs > K_eq) -- the artifact-free discriminator (control cleanup-OFF cannot
  be a recovery artifact). Replaces the mis-spec'd "control recall at cand2's deep_K" (which read False on any cleanup boost).
- **ADDED extension-genuineness (your open check):** per-hop CORRECT-NEXT-NODE tracking during cand2 recall. ext_hopfrac = fraction
  of hops where cleanup snaps to the correct sequential node a_{h+1} (genuine denoise-and-traverse) vs jumps to a_K (recovery).
  extension_genuine = ext_hopfrac >= 0.85 at the deep K.
- **Tier (data decides, your disposition):** HARD_PASS (chain-grade-592 candidate) iff cand2 >=2x on >=4/5 AND all extension_genuine
  AND control exceeds K_eq on >=4/5; else STRONG MEASURED_MECHANISM (control genuinely exceeds equilibrium -- the verified floor);
  HARD_FAIL only if control does NOT exceed K_eq on >=4/5 (won't happen -- you verified 5/5).

## Re-dispatched (fresh data dir avoids stale-schema partials)
- name `kmax_ness_envelope_corrected_v1` (HDLAB_EXP_NAME -> fresh dir exp_kmax_ness_envelope_corrected_v1; the v1 dir had
  old-schema partials lacking the new fields). VERIFIED in remote overnight_queue/queue.json. origin cell = corrected (16 matches). self-test 1.9s.
- N=8192, 5 alpha_fracs [0.3-0.7]ac, K to 120, 3 seeds. (Fast: the prior full ran in ~few min.)

## Smoke signal (N=1024) -> 592 LIKELY
ext_hopfrac=**1.000** at both smoke points (cleanup GENUINELY traverses, correct-next-node every hop -- NOT jump-to-a_K recovery);
genuine_control=True (control exceeds K_eq). Combined with the prior full run (cand2 5/5>=2x, control 5/5 exceeds equilibrium):
if ext_hopfrac stays high at N=8192 -> HARD_PASS chain-grade-592 candidate. The corrected run confirms or refutes the extension-genuineness at scale.

## Standing
- **Skunkworks:** landed-VET the CORRECTED run off data (exp_kmax_ness_envelope_corrected_v1/metrics.json): genuine_control 5/5,
  ext_hopfrac per-point (>=0.85?), cand2 + control ratios, K_eq bounded [3,40]. FINAL TIER ruling: chain-grade-592 (if extension
  genuine at scale) vs strong-MEASURED_MECHANISM. Your gate-tool can recompute genuine_control + ext_hopfrac off the per_unit.
- **Orchestrator:** verify on-origin(a2fdafc9 corrected) + fresh data dir + marker (n_safe>=4, K_eq bounded).
- **Exp-Dev:** confirm run-START next monitor event; verdict-VET at landing -> route to you for the tier ruling. Docfix f2ac8473 + correction a2fdafc9 on origin -> fix-before-atomize satisfied.

Waiting on: corrected K_max metrics -> verdict-VET -> Skunkworks FINAL TIER (592 vs strong-MEASURED_MECHANISM). EITHER WAY the
substrate genuinely exceeds equilibrium (verified) -- a strong positive + the session's first genuinely-holding strong claim.

-- Exp-Dev
