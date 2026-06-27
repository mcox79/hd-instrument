# Research drill 2x: Hopfield consolidation revival after v2 HARD_FAIL (regime-fix-failed)

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** `exp_gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix` HARD_FAIL methodology_drift_ceiling. ALL 4 arms hit `heldout_acc=1.0000` across 3 seeds at the alpha=0.0488 / SNR_pred=4.53 regime that THIS MORNING'S 3x drill said would be discriminating.
**Calibration:** P_deflated 0.15-0.25; novel-synthesis cap 0.50.
**Builds-on (do NOT re-derive):**
- `notes/research_drill_hopfield_consolidation_by_construction_3x_2026-06-27.md` (regime/alpha; v2 cell-spec — now also refuted)
- `notes/research_drill_5x_consolidation_saturation_barrier_2026-06-27.md` (Battery 2 TOP-3 = BTSP / STC / engram-dropout)
- `data/exp_gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix/metrics.json` (the v2 HARD_FAIL)
- `data/exp_gap4_stc_capture_selective_downscale_v1/metrics.json` (sister cell ALSO HARD_FAILed selectivity 2026-06-26)
- `preregs/2026-06-27_{btsp_binary_synapse_one_shot_v1, stc_tag_and_capture_v1, engram_dropout_inhibitory_plasticity_v1, cyclic_sws_rem_eta_schedule_v1, memristive_soft_bound_update_v1, hierarchical_3_tier_W_v1}.md` (Battery 2 already-filed mechanisms)

---

## v2 POSTMORTEM — what the failure metrics actually say

Per-arm read of `metrics.json` (Fix #28 discipline; not framing from verdict_msg):

| arm | heldout_acc | w_schema_cone | cor_score | replay_cycles |
|---|---|---|---|---|
| ARM_BASELINE_HEBBIAN | 1.000 (3/3 seeds) | 1.000 | 0.000 | 0 |
| ARM_HEBBIAN_SLOW | 1.000 (3/3 seeds) | 0.246 | 0.000 | 0 |
| ARM_HOPFIELD_REPLAY_SLOW | 1.000 (3/3 seeds) | 0.245 | 0.000 | (n=50 applied) |
| ARM_HOPFIELD_GENERATIVE_REPLAY | 1.000 (3/3 seeds) | 0.245 | 0.000 | (n=50 applied) |

The 3x drill's alpha-pre-dispatch gate fired GREEN (alpha=0.049 in [0.03, 0.20]; SNR_pred=4.53 in [2.5, 6.0]) and STILL the regime saturated. **The alpha-only diagnosis was incomplete.** Diagnoses missed by 3x drill:

1. **N_TRAIN=100 is itself a denoiser.** ARM_BASELINE_HEBBIAN computes `prototype = mean(N_TRAIN noisy instances)`. At N_TRAIN=100 and noise=0.60, the per-component noise std collapses by sqrt(100)=10x; the prototype recovers the clean mean to within ~0.06 RMS. Heldout queries (also noise=0.60) are then matched against a near-perfect prototype across only 100 categories in 2048-dim space — Z-score ≈ (1 - cos(60deg))/0.06 ≈ 8. **Ceiling.** The lit-scan SNR_Hebbian = sqrt(N/P) formula assumes random orthogonal patterns; it does NOT model the within-category averaging that BASELINE arm does FOR FREE.

2. **BASELINE arm and the "Hopfield-augmented" arms read from different surfaces.** BASELINE uses prototype-cosine (w_schema_cone=1.0 trivially because the prototype IS the row); SLOW arms use W-cosine (w_schema_cone=0.246). The cell never tested whether the mechanisms would beat a prototype-cosine baseline; it tested whether they'd beat themselves. Even an oracle would tie 1.000 at this regime.

3. **n_replay_cycles_applied = 0 for BASELINE and HEBBIAN_SLOW (expected); but the two consolidation arms only applied 50 replay cycles, not the 5000 declared.** Possible silent decimation or `replay_every=100` arithmetic at this scale.

**Bottom-line:** v2 didn't fail because regime was wrong; it failed because (a) BASELINE prototype-averaging dominates at any N_TRAIN >> 10 in the presence of i.i.d. noise, AND (b) the discriminator was structurally untestable because BASELINE reads a different surface than the mechanism arms.

This validates Skunkworks' v3 recipe direction (drop N_TRAIN 100→10, raise proto_noise 0.60→0.85): kill the within-category denoiser AND push the noise past the prototype-cosine cliff. **But the deeper question — is even THIS enough — is what this drill answers.**

---

## ANGLE A — REGIME REVIVAL (ship Hopfield-v3 with Skunkworks recipe + extra spine)

### A.1 The Skunkworks recipe analyzed

Recipe: `N_TRAIN=10, proto_noise=0.85, alpha=0.0488` (so N_DIM=2048 and N_CAT=100 unchanged), target BASELINE in [0.40, 0.65].

Analytical prediction at this regime:
- Prototype noise per component: sqrt(N_TRAIN) noise reduction = 0.85/sqrt(10) ≈ 0.27 std on the prototype.
- Heldout query noise: 0.85 std.
- Effective per-component SNR at retrieval: signal/sqrt(0.27^2 + 0.85^2) ≈ 1 / 0.89 ≈ 1.12.
- Z-score across 100 competing categories: requires margin >> noise floor. At cosine-similarity readout against the prototype: `cos(query, true_proto) ≈ 0.4-0.6`; `cos(query, false_proto) ≈ 0.02 +/- 0.04`. Z-score ≈ 12.

**This says BASELINE will likely land in [0.55, 0.75] — close to ceiling edge but not pinned at 1.000.** Discriminating but only marginally. The recipe is barely in band.

### A.2 v3 proposal 1: Skunkworks recipe + within-category structured correlation (CRITICAL ADD)

Beyond just lowering N_TRAIN: the v1 + v2 drills both missed that **at any N_TRAIN > 1 with i.i.d. noise, the optimal classifier IS the prototype-mean.** Information-theoretically, NO mechanism can beat the prototype baseline on i.i.d.-noisy data — replay over the SAME stored instances literally cannot add information. The 3x drill called this out at section 1.6 ("Hopfield-replay collapses to Hebbian-prototype at well-separated codebook") but didn't operationalize the fix.

**Fix:** instances within a category are NOT i.i.d. noisy copies of a prototype; they share a CORRELATED SUBSPACE (k=8 dimensions of shared per-category structure) on top of i.i.d. noise. Now the prototype-mean retains only the mean of the correlated subspace (loses the i.i.d. variance contribution); replay over the instance trajectories CAN recover the correlated-subspace shape if the replay mechanism includes any form of covariance estimation.

Recipe v3-A:
- N_DIM=2048, N_CAT=100, **N_TRAIN=10**, N_HELDOUT=30, N_REPLAY=5000
- **proto_noise=0.85** (Skunkworks)
- **NEW: WITHIN_CAT_CORR_SUBSPACE=8** (each category has k=8 shared latent dimensions; instances = proto + corr_subspace_sample + iid_noise)
- HARD_PASS bands: BASELINE_HEBBIAN in [0.40, 0.65]; ARM_HOPFIELD_REPLAY_SLOW lift >= 0.10 over BASELINE; cor_score >= 0.30
- HARD_FAIL: any arm > 0.85 baseline (ceiling); any arm < 0.20 baseline (floor); all arms within 0.05 (mechanism null)
- **Pre-dispatch smoke check: 1 seed at full-N reports baseline in [0.40, 0.70] OR cell is rejected.** (META_RULE_K)

P_deflated: 0.35 (deflated from 0.55 unbiased; deflation = +0.10 for "still might tie at 1.000" risk + the v2 HARD_FAIL precedent).

### A.3 v3 proposal 2: Cleanup-net spine + Skunkworks recipe (revive WITH Plate-2003 cleanup)

Cleanup-net (Plate 2003) was identified in the 5x drill (Mechanism 4.1) as a substrate-native primitive that DOESN'T add capacity but DOES tighten basins. Add it to Hopfield-v3 as an architectural augment:

- Storage W from outer-product Hebbian (unchanged)
- **Retrieval pipeline:** `q -> W @ q -> cleanup_attractor(.) -> argmax`
- cleanup_attractor uses iterative softmax-Hopfield over a fixed reference codebook (not the storage W)
- Baseline arm uses raw `W @ q -> argmax`; mechanism arm adds cleanup
- Without the cleanup spine, raw `W @ q` at alpha=0.049 already converges to prototype-mean — that's why v2 saturated. With the cleanup spine, the mechanism arm has a non-trivial extra step that COULD lift OR could be neutral.

Risk: cleanup arm AND baseline still hit 1.000 because regime IS too easy (per A.1 prediction). Resolution: use A.3 IN COMBINATION with A.2 (structured within-cat correlation) to land in the discriminating regime first. Cleanup-spine is a complementary architectural lever.

P_deflated: 0.30 (deflated from 0.50 unbiased; high risk that cleanup adds nothing measurable above prototype-mean baseline).

### A.4 v3 proposal 3: Honest-bound atomization, no v3 cell at all

Per Fix #28 + META_RULE_L: the rigorous interpretation of v1+v2 BOTH at 1.000 across 4 arms x 3 seeds is **HONEST_NEG with by-construction-saturation** in the test setup. The Hopfield-family replay primitive (atom 588 `replay_cycle`) over stored episodes COLLAPSES to Hebbian-prototype-mean in ANY regime where instances are i.i.d.-noisy around per-category prototypes. The mechanism IS structurally redundant for this task class. No amount of regime-tweaking restores discriminability without first changing the task (add structured within-cat correlation OR change the readout class entirely).

**This is what the existing 5x drill ALREADY concluded** ("All substrate consolidation cells touch W globally; none of them implement SELECTIVE-SUBSET consolidation. The brain's engram + STC + BTSP all share the property that only a SUBSET of synapses is consolidated per event."). The 5x drill's TOP-3 picks (BTSP / STC / engram-dropout) are SELECTIVE-SUBSET mechanisms by design — they don't reduce to Hebbian-prototype-mean.

If A.4 is correct, then: **Battery 2 cells already in flight ARE the answer; Hopfield-v3 with Skunkworks recipe ships diminishing-returns evidence at best.**

---

## ANGLE B — DIAGNOSTIC: is Hopfield itself the issue or the test?

### B.1 Modern Hopfield (Ramsauer 2020) — would it differ?

Modern Hopfield uses `xi = X @ softmax(beta * X.T @ q)` — explicit softmax over stored patterns. At the substrate's regime (alpha=0.049; well-separated quasi-orthogonal codebook), Ramsauer Theorem 3 guarantees one-step convergence and the readout degenerates to argmax (per 3x drill section 1.2). **No mathematical difference vs classical Hopfield in this regime.** At critical-load (alpha > 0.10) modern Hopfield DOES win, but the substrate's task is well below that.

Verdict: dispatching modern Hopfield as a v3 arm is not a separate angle; it's a NULL arm that will tie. Skip.

### B.2 Is BASELINE_HEBBIAN a valid baseline at all?

This is the cell-architecture critique. BASELINE_HEBBIAN reads from `prototype = mean(instances)` directly. ARM_HOPFIELD_REPLAY_SLOW reads from `W @ q` where W was built by Hebbian writes. **They read different surfaces.** The cell PRE-FAILS as an A/B test because the two arms aren't measured against a common readout.

Two valid fixes:
- **Fix B.2a:** Force ALL arms to read from W (matching surface). Then BASELINE is W-built-by-Hebbian-without-replay; mechanism is W-built-by-Hebbian-PLUS-replay. The 3x drill's mechanism math then directly applies: replay over stored episodes adds zero new information at well-separated codebooks. **Predicted result: all arms tie, but not at 1.000 — at whatever W-cosine-readout supports (~0.5-0.7 at this regime per HEBBIAN_SLOW's actual w_schema_cone=0.245 and predicted readout acc ~0.5).** This MIGHT discriminate replay-lifts-W-readout, but theoretical headroom is small.
- **Fix B.2b:** Force ALL arms to read from prototype (matching surface). Then mechanism = "replay updates the prototype somehow" — but `replay_cycle` doesn't update prototypes, it updates W. So this fix REQUIRES extending the consolidation primitive. Not a v3 fix; a mechanism redesign.

Verdict: Fix B.2a is the right surgical fix to the test. **This is the highest-value revival angle: it makes the existing v2 cell actually testable without changing the mechanism.**

### B.3 Sister cell evidence — STC ALSO failed selectivity 2026-06-26

`exp_gap4_stc_capture_selective_downscale_v1` HARD_FAILed: "Selectivity NOT working: STC reproduces Cell B failure mode. ARM_STC_TAG_DECAY_K100_PRP_BUDGET_100 forget=1.0000 vs baseline 0.8700." STC arm at K=100 PRP_BUDGET=100 reproduced the global-downscale forget-everything failure. Only ARM_STC_TAG_DECAY_K100_PRP_BUDGET_INFINITY (no protein-budget constraint) matched baseline forget=0.8700 — meaning the tag mechanism, when budget-limited, doesn't preferentially preserve TAGGED synapses; it just downscales differently from no-downscale, in a way indistinguishable from global.

**Implication:** the substrate's existing W-write primitive doesn't expose a per-synapse selectivity surface that STC can hook into. STC tags work in spiking nets because synapses are physically discrete; in dense W they need an explicit mask primitive. **Battery 2's STC and engram-dropout cells inherit this risk** — they need a per-synapse mask not just a per-pattern mask.

### B.4 Plate-2003 cleanup-net for Hopfield: would it prevent saturation?

Cleanup-net adds basin-tightening (per 5x drill Mechanism 4.1). At well-separated codebook (alpha=0.049, current substrate regime), basins are ALREADY tight — cleanup adds nothing. At critical-load (alpha > 0.10) cleanup helps because basins are merging. **Cleanup-net is a critical-load tool, not a sub-critical tool.** Cannot rescue v2 at the current regime.

### B.5 Synthesis of Angle B

- B.1: Modern Hopfield won't differ → skip.
- B.2: BASELINE-vs-mechanism surface mismatch is a REAL test bug; fix B.2a is a clean revival path.
- B.3: Sister STC's HARD_FAIL is a warning that Battery 2 mechanisms aren't safe either.
- B.4: Cleanup-net doesn't help at this regime.

**Strongest single revival from Angle B: fix surface-mismatch (B.2a) AND lift to critical load via Skunkworks recipe (A.1) AND add within-cat correlation (A.2).** Combined, these MIGHT discriminate.

---

## CROSS-CHECK against Battery 2 (mandatory per drill instructions)

Battery 2 cells filed today (`preregs/2026-06-27_*.md`):

| Battery 2 cell | Subsumes what here? |
|---|---|
| `btsp_binary_synapse_one_shot_v1` | TOP-1 from 5x drill; SELECTIVE-SUBSET; orthogonal to Hopfield-revival angle |
| `stc_tag_and_capture_v1` | Selective; partially DUPLICATED by sister cell `gap4_stc_capture_selective_downscale_v1` HARD_FAIL — risk |
| `engram_dropout_inhibitory_plasticity_v1` | SELECTIVE-SUBSET via mask; complementary not overlapping with Hopfield |
| `cyclic_sws_rem_eta_schedule_v1` | DOES overlap with Angle A.2/A.3 (schedule-level cycling); both regime-level, both add no new information vs prototype-mean if BASELINE arm reads prototype directly |
| `memristive_soft_bound_update_v1` | Soft-bound on `W += dW` rule; complementary to Hopfield-revival; doesn't change readout surface |
| `hierarchical_3_tier_W_v1` | Multi-W slabs; different mechanism class entirely |

**Duplication ruling:**
- v3-A (Skunkworks recipe + within-cat correlation): NOT subsumed; closest is `cyclic_sws_rem_eta_schedule_v1` but that's schedule not regime/within-cat-structure. SAFE TO SHIP if value justifies.
- v3-B (cleanup-net spine): NOT subsumed; Plate-2003 cleanup is unique. SAFE TO SHIP but Angle B.4 says it won't help at this regime → DO-NOT-SHIP on independent grounds.
- v3-C (fix B.2a surface-mismatch fix as a single-arm-edit on v2 cell): NOT subsumed; this is an architectural fix to the v2 test rig, not a new mechanism. SAFE TO SHIP and CHEAP (1 cell-author edit).

---

## TOP-2 revival cells across Angles A + B

### REVIVAL CELL 1 (RECOMMENDED): `gap3_cls_two_tier_HOPFIELD_consolidation_v3_skunkworks_corr_subspace`

Combines Skunkworks recipe (A.1) + within-cat correlated subspace (A.2) + surface-mismatch fix (B.2a). Single cell.

- N_DIM=2048, N_CAT=100, **N_TRAIN=10**, N_HELDOUT=30, N_REPLAY=5000
- proto_noise=0.85, **WITHIN_CAT_CORR_SUBSPACE=8** (categories share k=8 latent dims; instances = proto + corr_sample + iid_noise)
- alpha_load=0.049 (in band per META_RULE_W)
- **CRITICAL FIX: all 4 arms read from same surface (W-cosine).** BASELINE is W-built-by-Hebbian-from-instances; mechanism arms are W-with-replay variants.
- Pre-dispatch smoke gate: 1 seed at full-N reports baseline in [0.40, 0.70]; reject if outside.
- HARD_PASS: ARM_HOPFIELD_REPLAY_SLOW heldout_acc >= 0.55 AND >= baseline + 0.10 AND baseline in [0.40, 0.70]
- HARD_FAIL: any arm > 0.85 (ceiling); all arms within 0.05 of each other (mechanism null per META_RULE_L)
- 3 seeds; remote_cpu_queue; ~30min full wall
- P_deflated: 0.35 (low end of "ship it" band; significant residual risk that replay over i.i.d.-noisy instances still adds zero information vs prototype-mean even with corr subspace)

### REVIVAL CELL 2 (DIAGNOSTIC ONLY, cheap): `gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic`

A 1-seed diagnostic that re-runs v2 cell with surface-mismatch fix B.2a only. NO other changes from v2. Purpose: definitively prove whether the v2 1.000 ceiling was driven by BASELINE prototype-read OR by underlying regime. If with surface fix BASELINE drops below 0.95, the surface-mismatch was THE bug. If BASELINE still pins at 1.000, the regime IS the issue.

- Same config as v2 (N_DIM=2048, N_CAT=100, N_TRAIN=100, proto_noise=0.60)
- All arms read W-cosine (no prototype-direct read)
- 1 seed; ~10min wall on remote_cpu_queue
- This is a CALIBRATION cell, not a mechanism cell. HARD_PASS = baseline lands [0.50, 0.80]; HARD_FAIL = baseline ties 1.000 at W-cosine readout (proves regime is structurally saturated even after surface fix).
- P_deflated: 0.55 (diagnostic; well-bounded outcome; provides definitive evidence either way)

---

## HONEST ASSESSMENT — should Hopfield-v3 ship at all?

**Recommendation: ship REVIVAL CELL 2 (diagnostic) NOW; gate REVIVAL CELL 1 on its outcome.**

Rationale:
1. The v2 HARD_FAIL had TWO confounded causes (regime + surface-mismatch). Until we untangle, ANY v3 is uncertain.
2. REVIVAL CELL 2 is cheap (~10min wall, 1 seed) and definitive about the surface-mismatch question.
3. If REVIVAL CELL 2 shows baseline drops below 0.95 with surface fix alone, REVIVAL CELL 1 becomes high-P_deflated (≈0.45) — ship next.
4. If REVIVAL CELL 2 shows baseline still 1.000 with surface fix, **the Hopfield-replay-over-stored-episodes mechanism is structurally redundant for this task class** and Battery 2 (BTSP / engram-dropout / 3-tier-W) carries consolidation. Atomize Hopfield-family as HONEST_NEG and pivot.
5. Battery 2 (5+ cells) is already in flight ON BTSP / STC / engram-dropout / cyclic / memristive / 3-tier axes. These are SELECTIVE-SUBSET (5x drill consensus) and don't share Hopfield's reduces-to-prototype-mean failure mode. **They are the strategic answer regardless of v3 Hopfield outcome.**

**Sister-cell warning:** `gap4_stc_capture_selective_downscale_v1` HARD_FAILed selectivity 2026-06-26. Substrate's W primitive doesn't yet expose the per-synapse mask that STC and engram-dropout require. Battery 2's `stc_tag_and_capture_v1` and `engram_dropout_inhibitory_plasticity_v1` BOTH inherit this risk and should be vetted for whether they ship the missing mask primitive or share the sister-cell failure mode. **File a Skunkworks vet request on Battery 2 selectivity-primitive coverage BEFORE dispatching.**

---

## OPERATIONAL RECOMMENDATIONS

1. **DISPATCH REVIVAL CELL 2 (diagnostic, 1 seed, ~10min) immediately** via Orchestrator to remote_cpu_queue. This is the cheapest evidence on whether v2's failure was surface-mismatch vs regime.

2. **GATE REVIVAL CELL 1 on REVIVAL CELL 2 outcome.** If diagnostic shows surface-mismatch was THE bug → ship REVIVAL CELL 1 (P_deflated 0.45 with diagnostic-confirmed regime). If diagnostic shows regime still saturates → DO-NOT-SHIP Hopfield-v3; atomize family as HONEST_NEG.

3. **DO-NOT-SHIP REVIVAL CELL alternatives:**
   - Modern Hopfield arm (B.1) — null at this regime
   - Cleanup-net spine only (A.3) — needs critical-load, current regime is sub-critical
   - Pure regime-revival without surface fix (A.1 alone) — repeats v2's confounded test

4. **File Skunkworks vet request: does Battery 2's `stc_tag_and_capture_v1` + `engram_dropout_inhibitory_plasticity_v1` ship the per-synapse mask primitive that sister cell `gap4_stc_capture_selective_downscale_v1` was missing?** If not, those two Battery 2 cells inherit the sister's failure mode and should be amended before dispatch.

5. **Per Fix #21:** poll filesystem for REVIVAL CELL 2 landing; do not wait for spawn-side notification.

---

## CITATIONS (new only; full lit-base in 3x + 5x companion drills)

- Plate T. (2003). "Holographic Reduced Representation: Distributed Representation for Cognitive Structures." CSLI Publications. [Cleanup-net architecture as separate-from-storage]
- Mu J., Viswanath P. (2018). "All-but-the-Top: Simple and Effective Postprocessing for Word Representations." ICLR 2018. arXiv 1702.01417. [Anisotropy hurts retrieval — relevant to surface-mismatch fix B.2a]
- Wu Y., Maass W. (2025 Jan). "A simple model for BTSP provides content addressable memory with binary synapses and one-shot learning." Nature Communications PMC11695864. [Battery 2 top-pick brain grounding]
- Companion: `notes/research_drill_hopfield_consolidation_by_construction_3x_2026-06-27.md`
- Companion: `notes/research_drill_5x_consolidation_saturation_barrier_2026-06-27.md`
- v2 metrics: `data/exp_gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix/metrics.json`
- Sister cell HARD_FAIL: `data/exp_gap4_stc_capture_selective_downscale_v1/metrics.json`
- Battery 2 preregs: `preregs/2026-06-27_{btsp_binary_synapse_one_shot,stc_tag_and_capture,engram_dropout_inhibitory_plasticity,cyclic_sws_rem_eta_schedule,memristive_soft_bound_update,hierarchical_3_tier_W}_v1.md`

---

## LIT-SCAN CALIBRATION

- All P estimates deflated 0.15-0.25; novel-synthesis cap 0.50 applied (none binding here).
- 2 angles drilled per instructions: REGIME REVIVAL (A) + DIAGNOSTIC (B).
- HONEST symmetric correction: the 3x drill's alpha-pre-dispatch gate was NECESSARY but NOT SUFFICIENT. Today's drill identifies a SECOND gate (surface-mismatch + within-category-i.i.d.-noise denoising) that must also fire for any Hopfield-family cell to be testable. **Adding this as META_RULE proposal:** any associative-memory consolidation cell with BASELINE arm must verify (a) baseline reads same surface as mechanism, (b) within-category instances have non-trivial covariance structure OR N_TRAIN <= 10, (c) smoke baseline lands in [0.40, 0.70] at full-N — else reject pre-dispatch.

-- Research (Opus 4.7 1M; 2-angle revival drill on Hopfield consolidation v2 HARD_FAIL; TOP-2 = diagnostic surface-fix cell + gated regime/corr-subspace v3 cell; sister cell + Battery 2 cross-checked; META_RULE proposal for surface-mismatch gate filed in synthesis).
