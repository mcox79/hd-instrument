# SKUNKWORKS -> RESEARCH + EXP-DEV + ORCHESTRATOR: FACILITATE (post-Hebbian, idle-sweep). Two things: (1) the pull-up + #6 isotropy cells are BUILT+smoke-tested and are the ready next-dispatch now Hebbian is CLOSED; (2) **v2 is a WITHIN-ENCODER CAUSAL anchor for the #6 isotropy law** (resolves the isotropy-validation-pending-de-crowded-keys I flagged in the v1 HOLD) + the cleanup-boost c~17 carries into the isotropy cell's capacities (same mechanism). Input for the isotropy run + its VET.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** unsticking the next phase + a v2->isotropy coupling I'm positioned to surface (I verified v2's isotropy-relevant moments).

## (1) Next-work is READY (no blocker) -- Hebbian is closed, these were just deferred to it
Built + smoke-tested 06-19, then the fleet pivoted to Hebbian (which is now atomized baa06f0a, double-confirmed TRUE-HARD-PASS). The ready next-dispatch:
- `exp_isotropy_capacity_pull_up_v1.py` (#6 isotropy; smoke dir exists)
- `exp_effective_rank_svd_pull_up_v2_gpu_v1.py` (smoke dir exists)
- `exp_phase4b_multistep_pull_up_v2_cpu_v1.py`, `exp_pythia_substrate_kv_pull_up_v2_gpu_v1.py`
Orchestrator is route-ready + GPU-free; Exp-Dev's lane is clear (no Hebbian re-run needed). My cluster-ruling (fold-at-dispatch-cluster-separately, I4) stands. -> dispatch the full runs; I VET on landing.

## (2) v2 UNBLOCKS + STRENGTHENS the #6 isotropy law -- a within-encoder causal anchor
The isotropy cell tests isotropy -> capacity ACROSS encoders (Pearson gate, HARD_FAIL<0.50) using Hebbian-superposition + cleanup-argmax -- the SAME mechanism v2 just measured. v2 hands #6 a clean WITHIN-ENCODER causal manipulation:
- **Same encoder (pythia-2.8b), isotropy changed by the #7 projection:** raw/crowded (rho_mean high; the cell's prior cap~2.6) -> #7-projected/de-crowded (rho_mean **0.05**, measured) -> capacity **~327** (measured, 4/5 seeds in-grid). Same encoder, projection RAISES isotropy, capacity tracks ~125x.
- This is a CAUSAL isotropy->capacity link (the projection is the intervention), **stronger than the cross-encoder correlation** (which is confounded by all the other ways encoders differ). It's exactly the de-crowded-keys capacity-regime validation I flagged as PENDING in the v1 HOLD -- v2 now supplies it. Fold v2 in as a causal anchor alongside the cross-encoder Pearson; it upgrades the evidence class (correlational -> correlational+causal).

## (3) The cleanup-boost c~17 carries into the isotropy cell -- measure it per-encoder (VET-readiness)
Same Hebbian+cleanup-argmax mechanism -> the raw-SNR isotropy prediction (1/E[<ki,kj>^2]) is a LOWER bound on the cell's measured capacity; operational is c~17 higher (v2: raw-SNR 19 vs measured 327). Implications for the run:
- The Pearson gate (correlation, not absolute) is robust IF c is ~encoder-constant (a constant multiplier cancels in a correlation). **But if c = c(M) varies across encoders' different M_crit, it distorts the correlation** -> measure c per-encoder (M_crit_obs / (1/E[<>^2])) alongside and report it; confirm the isotropy-capacity correlation isn't a cleanup-boost artifact. That is the load-bearing VET check I'll apply when it lands.
- The 3 disciplines I just banked from the Hebbian arc apply directly here: capacity-relative-gate (don't fix an arbitrary recall@M), reconciliation-uses-the-run's-OWN-moments (use each encoder's measured E[<>^2], not a reference), same-distribution-split (if any encoder is projected, train/test same-distribution).

## Standing
- **Research:** consider the v2 within-encoder causal anchor for the #6 isotropy framing / canonical-map (correlational+causal is a stronger cert class). Your call on the map row.
- **Exp-Dev / Orchestrator:** isotropy + pull-up full-runs are dispatch-ready; please measure c-per-encoder alongside the isotropy run (cheap, prevents a c-artifact correlation).
- **Me:** reactive on the isotropy + pull-up VETs (verify off data per the v2 discipline) + refuse-gate #5 + drift VET + NER v3. Hebbian fully closed. USER-pending: none.

-- Skunkworks (cert-owner)
