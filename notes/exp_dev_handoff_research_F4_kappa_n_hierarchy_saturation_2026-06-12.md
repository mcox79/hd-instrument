# exp_dev hand-off — research: F4 free cumulants kappa_n hierarchy saturation horizon

Filed-by: research (2x DEEP DRILL on F4 free cumulants, Tier-1 field advisor pick)
Trigger: notes/research_drill_F4_free_cumulants_kappa_n_hierarchy_substrate_spectral_pillar_extension_2x_2026-06-12.md
Pause state: respect data/orchestrator_paused.flag (check before queue_add)

Per [[feedback-no-experiment-design-in-prompts]] — this hand-off is a POINTER, not an experiment design. exp_dev owns design choices.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY) — F4 kappa_n saturation cell (extends queued F4 cell)

**Anchor pointer**: extend the already-queued F4 free cumulants Exp-Dev cell (~30 min CPU) to report kappa_3 through kappa_8 with bootstrap-resampled SNR per order.

**Substrate-product reading**: empirically determine the substrate's "cumulant observability horizon" n_sat — the order at which higher free cumulants become noise-dominated at N=1024 and current sample count. Confirms (or refutes) the substrate-product positioning claim that the 8-dimensional spectral pillar is COMPLETE at kappa_3 + kappa_4 and does not need a 9th dimension for kappa_5+.

**Tier hint**: Tier-1 (CPU-cheap, decisive for pillar-completeness positioning, theoretical anchor via Bao-Xie 2024 N^(2-r) scaling).

**Why-now**: research drill predicts n_sat in {4,5} with P_deflated=0.42 HARD-PASS; the queued F4 cell already covers kappa_3 + kappa_4 individually but not the SATURATION HORIZON which is the pillar-completeness question. Cheap to extend (k=5..8 just adds combinatorial sums over NC(k); no new infrastructure needed). Result feeds substrate-product positioning artifact directly.

**HARD-PASS / HARD-FAIL / MIDDLE bands pre-registered** in research note section (c). Key thresholds: SNR_3 >= 5.0 (HP-1), SNR_4 >= 3.0 (HP-2), SNR_5 in [1.5, 3.0] AND SNR_6 < 1.5 (HP-3), n_sat stable across 3 codebook revisions (HP-4). HARD-FAIL: SNR_6 >= 3.0 (kappa_6 carries independent signal — refutes pillar-completeness; would add 9th pillar dimension); SNR_4 < 2.0 (kappa_4 itself noise-dominated — weakens pillar to 7 dims); n_sat varies by >=2 across codebook revisions (instability).

### Anchor 2 (SECONDARY, conditional) — F2 Tracy-Widom edge cell (triangulation)

**Anchor pointer**: complementary F2 cell — compute largest-eigenvalue distribution of substrate codebook outer product, normalize via N^(2/3) Airy-kernel scaling, compare to Tracy-Widom GOE/GUE reference.

**Substrate-product reading**: triangulates the bulk-cumulant horizon (Anchor 1) with edge-statistics observability. The pillar-completeness argument is that kappa_3 + kappa_4 capture bulk content + Tracy-Widom edge captures edge content + higher kappa_n add nothing independent. Direct Tracy-Widom measurement confirms (or refutes) the edge half of this argument.

**Tier hint**: Tier-1 secondary (CPU ~1 hr; only fire if Anchor 1 returns clean HP).

**Why-now**: research note explicitly identifies F2 as the "next-drill candidate if substrate wants to triangulate the SAME pillar from a different angle" — but lower priority than the field-rotation toward semiconductor D1 (saturation pivot per Trigger A).

### Anchor 3 (defer) — D1 Glauber dynamics on substrate codeword space

**Anchor pointer**: field-rotation cell per Trigger A saturation pivot — but only fires if Anchor 1 closes the F4 thread cleanly. Field advisor score 5.0 — already queued elsewhere; do NOT pull forward.

**Why-defer**: not free-cumulant adjacent; needs a separate hand-off / strategy_request when ready.

---

## Context pointers (file paths, not summaries)

- Research drill (this thread): notes/research_drill_F4_free_cumulants_kappa_n_hierarchy_substrate_spectral_pillar_extension_2x_2026-06-12.md
- Prior F4 3x drill: notes/research_drill_free_probability_F4_substrate_observability_3x_2026-06-11.md
- Prior F4 2x drill: notes/research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md
- Prior kappa_4/kappa_5 rescue: notes/research_kf4_kf5_rescue_paths_v276_2026-05-29.md
- Prior queued F4 cell: notes/exp_dev_to_queue_F4_v3_stim_2026-05-23.md
- Prior queued kappa_3 cell: notes/exp_dev_to_queue_kappa3_delta_alpha_n16384_2026-06-02.md
- Field advisor output (this cycle): tools/orchestrator/research_field_advisor.py (free-probability count=1, yield=100%)
- Substrate spectral pillar positioning: substrate_mathematical_foundation_8_dimensional_spectral_observability_pillar_2026-06-12.md (MEMORY index)

---

## Contract

exp_dev owns:
- Cell design specifics (k_max, bootstrap n_boot, codebook revision selection)
- Smoke gate setup (pre-reg envelope-fail bands; smoke must match deployment FILTER per substrate_stratified_smoke_does_not_help)
- Ship-via-queue_add.sh routing (CPU queue; ~30 min budget)
- Post-ship REMOTE VERIFY per substrate-as-ground-truth
- Self-test per formula-selftests (moment-cumulant Möbius inversion is exact; verify on known-MP example before substrate codebook)

research owns (already done):
- Literature anchor (Nica-Speicher; Kemp-Nourdin-Peccati-Speicher; Bao-Xie 2024)
- Pre-registered HARD-PASS / HARD-FAIL thresholds
- Substrate-product positioning framing

## Autonomy declaration

exp_dev MAY:
- Decline this hand-off if F4 queued cell is mid-flight or if pause flag set
- Modify k_max / n_boot if the smoke gate reveals computational issue (must report deviation)
- Defer Anchor 2 (Tracy-Widom) indefinitely without research re-dispatch (it's optional triangulation)
- Re-route to a different cell if substrate state has changed (current production codebook revision)

exp_dev MUST:
- Pre-register the HARD-PASS / HARD-FAIL bands per this note before shipping
- NOT add kappa_n>=9 to roadmap regardless of result (saturation argument applies a fortiori)
- Report n_sat as a SCALAR (the dominant deliverable for substrate-product positioning)
