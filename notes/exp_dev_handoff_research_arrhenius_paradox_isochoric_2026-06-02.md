# exp_dev hand-off -- research: arrhenius-paradox isochoric analysis / non-equilibrium disordered AM

**Filed:** 2026-06-02 by research sub-agent.

**Trigger:** Research drill notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md delivered three concrete experiment candidates with measurable predictions and HARD-PASS/HARD-FAIL thresholds. All three are empirically testable without GPU depth (smoke feasible on local CPU). Filed for exp_dev auto-discovery on next emergency-refill cycle.

**Pause state:** Check data/orchestrator_paused.flag before dispatch. Queue-refill is GATED.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters beyond the prediction thresholds already in the note.

---

## Anchor candidates (rank-ordered; exp_dev picks from these)

### 1. Two-envelope isochoric separation -- kappa_3 vs capacity at fixed alpha

- **Anchor pointer:** notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md, Sub-question (5ii) and Cheap decisive test B.
- **Substrate-product reading:** The kappa_3 spectral-audit sigma envelope (sigma_g <= 0.18) and the capacity-degradation sigma envelope (sigma_g ~ 4.36 at alpha=0.05) are confirmed as structurally distinct but hidden inside one noise parameter. An isochoric sweep (fixed alpha, vary sigma) traces the two curves independently. This is the direct AM analog of the Arrhenius-paradox Brot separation. Operationally: at fixed alpha, sweep sigma from 0.01 to 1.0+, measure both kappa_3 reliability and capacity independently in the same run. Predict: kappa_3 breaks near sigma ~ 0.18; capacity degrades near sigma ~ 1.0-4.0. If confirmed: the two-envelope structure becomes a required protocol condition for all cap-map experiments.
- **Tier hint:** Local CPU smoke (single alpha, sigma sweep, measure two observables). Very cheap.
- **Why now:** This is the most directly testable prediction from the drill and directly informs whether all prior sigma-sweeps need isochoric reanalysis.

### 2. Aging exponent mu alpha-invariance test

- **Anchor pointer:** notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md, Sub-question (2) and Cheap decisive test A.
- **Substrate-product reading:** CK theory (confirmed for non-reciprocal SK class) predicts aging exponent mu is alpha-independent when compared at matched T/T_c(alpha), NOT at matched raw noise amplitude. Measuring two-time correlation C(t, t_w) at two loading values (alpha_1 vs alpha_2), matched at T/T_c(alpha) = 0.8, tests this directly. HARD-PASS: |mu(alpha_1) - mu(alpha_2)| < 0.05. HARD-FAIL: > 0.15. If PASS: the system is confirmed in the CK aging universality class and mu ~ 3/2 can be used as a reliability predictor. If FAIL: a different aging class is active (possibly non-reciprocal coupling with alpha-dependent oscillations).
- **Tier hint:** Remote CPU (two-time correlation requires longer time traces; multi-seed; two alpha values). Modest compute.
- **Why now:** Aging exponent mu ~ 3/2 enables the timestamped reliability guarantee product feature (T_reliable = t_w * threshold^{-2/3}). Confirming mu is the gate for that capability.

### 3. Barrier vs alpha test -- hysteresis gap scaling

- **Anchor pointer:** notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md, Sub-question (3) and Cheap decisive test C. Also connects to notes/project_pred4_hysteresis_first_order_confirmed_2026-05-27.md (existing first-order multi-basin confirmation, max_gap = 1.84).
- **Substrate-product reading:** The AGS free-energy formula predicts barrier E_a(alpha) ~ N * (alpha_c - alpha) / alpha_c. The hysteresis gap at the first-order multi-basin transition should therefore scale as gap(alpha) ~ (alpha_c - alpha). At two loading values, the predicted ratio is gap(0.05) / gap(0.10) ~ (0.138 - 0.05) / (0.138 - 0.10) ~ 2.3x. HARD-PASS: ratio in [1.5, 3.5]. HARD-FAIL: ratio < 1.1 (alpha-independent gap). If confirmed: E_a(alpha) formula is validated, enabling per-alpha operational bounds on multi-basin reliability.
- **Tier hint:** Local CPU smoke. Two alpha values, hysteresis measurement already demonstrated by Pred-4. Reuse the hysteresis testbed at two loading points.
- **Why now:** Pred-4 hysteresis result at a single loading point already exists; running at a second loading point is trivial incremental work with high leverage for confirming the barrier formula.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md
- First-order multi-basin confirmation: d:/AI/hd-instrument/notes/project_pred4_hysteresis_first_order_confirmed_2026-05-27.md
- SKAH-M class confirmation: d:/AI/hd-instrument/notes/project_substrate_skahm_class_confirmed_2026-05-27.md
- Non-equilibrium stat-mech confirmation: d:/AI/hd-instrument/notes/project_substrate_non_eq_stat_mech_class_2026-05-27.md
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (most recent research_delivery entry)

---

## Contract

exp_dev is dispatched with TASK + WHY + CONTRACT + AUTONOMY. exp_dev designs the experiment (N, seeds, queue, thresholds, anchor name). The handoff provides the WHY and the prediction structure. exp_dev does NOT receive inline numerical sweep grids or pre-committed cap_map decisions.

## Autonomy declaration

exp_dev decides: which of the 3 anchors to ship first (or batch), what N and seed count to use, whether smoke vs FULL, which queue tier (A/B/C), anchor names, and ETA. The rank ordering above is a suggestion; exp_dev may reorder based on current queue state and runner availability.
