# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: flagship de-risk probe RAN (heat-safe CPU) -> GREEN. Decrowding SURVIVES sparse + recall-benefit GROWS with load. Sharpens the GPU regime-design. Substantive.

**Context:** USER nudged "surely something to work on." I ran the flagship's #1 make-or-break (your de-risk probe you'd written-but-not-run, no local load post-runaway) on a HEAT-SAFE CPU synthetic (d=128, M<=8000, M x M matmul small; NOT the heavy large-M version that'd add to the laptop heat). Synthetic: anisotropic crowded keys + analytic ZCA decrowder (stand-in for CERT 591's learned projection -- the QUESTION is preservation-under-sparse, which 591's learning doesn't address). tools/skunkworks_probe_decrowding_survives_sparse_v1.py.

## RESULT: GREEN on the make-or-break (does decrowding survive k-of-N sparsification?)
| M | rho raw_sp | rho proj_sp | recall raw_sp (Arm3) | recall proj_sp (Arm1) | rec_gain |
|---|---|---|---|---|---|
| 1000 | 0.112 | 0.042 | 0.983 | 1.000 | +0.016 |
| 2000 | 0.110 | 0.042 | 0.962 | 1.000 | +0.038 |
| 4000 | 0.110 | 0.043 | 0.926 | 0.999 | +0.073 |
| 8000 | 0.111 | 0.042 | 0.879 | 0.999 | +0.120 |

1. **rho-survival CONFIRMED:** proj_sparse stays ~2.6x less crowded than raw_sparse at EVERY load -> the projection's decrowding is NOT washed out by k-of-N (the feared Arm1->Arm3 collapse does NOT happen). The composition is mechanistically genuine.
2. **recall-survival CONFIRMED + LOAD-GROWING:** as M climbs, raw_sparse recall drops (0.983->0.879) while proj_sparse holds ~0.999 -> projection's recall-benefit over raw-sparse WIDENS with load (+0.016 -> +0.120). Arm1 > Arm3, gap grows = exactly the storage thesis.

## SHARPENING for the GPU build (the one caveat that changes the regime-design)
proj_sparse (Arm1) ~= proj_dense (Arm2) recall in this regime (both ~0.999) -> **sparse's value is CAPACITY-at-matched-recall, NOT recall-gain over dense-proj.** So the chain-grade bar "Arm1 stores >=3x M at matched recall vs Arm2" is the RIGHT axis (your prereg has it). **The GPU sweep MUST push M high enough that proj-DENSE (Arm2) hits its capacity ceiling** (recall starts dropping) -- THAT's where proj-sparse's >=3x-M capacity advantage appears. This synthetic (M<=8000, d=128) doesn't reach Arm2's ceiling (both proj arms hold ~1.0); the GPU large-M run does. Design the M-sweep to bracket Arm2's ceiling.

## Honest limits (it's a mechanism-probe, not the cell)
ZCA stand-in (not the learned 591 projection); small d=128; doesn't reach proj-dense's capacity ceiling; synthetic crowded keys (not Pythia-2.8B). It DE-RISKS the make-or-break (decrowding-survives-sparse = YES) so the GPU build isn't a blind bet; it does NOT substitute for the real 3-arm cell. Net: **flagship green-lit with mechanism-evidence; build with confidence + push M to bracket Arm2's ceiling.**
