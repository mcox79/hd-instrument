# exp_dev hand-off — research: PP-50 capacity phase boundary transition zone width

**Filed:** 2026-06-03 by research sub-agent.

**Trigger:** Research drill on PP-50 MIDDLE result (5/10 below-boundary violations). Research note at `notes/research_drill_pp50_transition_zone_width_2026-06-03.md`.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching. If present, hold.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N sweep values, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical grid or queue.

---

## Anchor candidates (rank-ordered)

### 1. N-sweep mechanism discriminator (PRIORITY — cheap decisive test)

**Anchor pointer:** `notes/research_drill_pp50_transition_zone_width_2026-06-03.md` Section "Cheap decisive test."

**Substrate-product reading:** The research identified two competing mechanisms for the wider-than-predicted transition zone: (A) Tracy-Widom soft-edge scaling as N^{-2/3} and (B) Hadamard off-diagonal O(1)-in-N structural term. The test is: fix (load fraction, sigma_g = sigma_g_crit) and sweep N. If violations are roughly constant across N, Hadamard dominates (N-independent safe envelope is correct). If violations decay as N^{-2/3}, TW dominates (envelope must be N-parameterized). This directly validates or refutes the product API claim.

**Tier hint:** CPU sweep (forward-pass retrieval overlap only, no gradient, no training). 4-cell x N sweep.

**Why now:** PP-50 MIDDLE blocked the capacity_phase_boundary row promotion. This test resolves which mechanism is responsible AND whether sigma_g < 0.5 * sigma_g_crit is N-independent or not. Gate for product API claim.

---

### 2. Safe envelope boundary probe at sigma_g = 0.5 * sigma_g_crit

**Anchor pointer:** `notes/research_drill_pp50_transition_zone_width_2026-06-03.md` Section Q3 + HARD-PASS HP1.

**Substrate-product reading:** Research predicts zero retrieval failures at sigma_g = 0.5 * sigma_g_crit for N >= 1024 across any load fraction <= 0.9. This is the product API claim to be validated. A clean sweep across (N, load fraction) at sigma_g = 0.5 * sigma_g_crit with >= 20 seeds per cell either confirms the API claim (HP1 HARD-PASS) or triggers envelope tightening to 0.4 (HF1 HARD-FAIL).

**Tier hint:** GPU if multi-seed x multi-(N, load) grid; CPU if smoke at single (N, load) point first.

**Why now:** Directly productizes the PP-50 finding. API doc cannot claim the envelope without empirical validation at the claimed sigma_g level.

---

### 3. Capacity prefactor measurement at sigma_g = 0.5 * sigma_g_crit

**Anchor pointer:** `notes/research_drill_pp50_transition_zone_width_2026-06-03.md` Section Q3 + HARD-PASS HP3.

**Substrate-product reading:** Research predicts capacity prefactor in [0.70, 0.80] at sigma_g = 0.5 * sigma_g_crit (from Bhattacharjee & Martin 2025 multiplicative noise formula: (1 - 0.25) = 0.75). This quantifies the capacity loss budget for the product API envelope claim. If prefactor is outside [0.70, 0.80], the formula is wrong and the capacity budget stated in the API needs revision.

**Tier hint:** CPU smoke (measure alpha_c under noise vs noiseless; single N, single sigma_g).

**Why now:** Completes the capacity_phase_boundary API claim: not just "safe" but "safe with < 25% capacity penalty."

---

## Context pointers

- Research note: `notes/research_drill_pp50_transition_zone_width_2026-06-03.md`
- PP-50 verdict context: `data/orchestrator_status_log.jsonl` (last capacity_phase_boundary entry)
- Cap map: `notes/substrate_capability_map.md` (capacity_phase_boundary row)
- Bhattacharjee & Martin 2025: arXiv:2503.00241 (multiplicative synaptic noise capacity formula)
- Castellana & Zarinelli 2011: arXiv:1104.4726 (N^{-2/3} TW scaling in disordered systems)

---

## Contract

This hand-off DOES NOT specify: anchor names, N sweep values, sigma_g grid points, seed counts, threshold bands, queue assignment, ETA, or pre-committed cap_map decisions. exp_dev determines all of these.

The research finding is: TWO mechanisms (TW + Hadamard); sigma_g < 0.5 * sigma_g_crit defensible for N >= 1024; cheap decisive test is N-sweep at sigma_g = sigma_g_crit.

## Autonomy declaration

exp_dev owns: experiment design, queue routing, anchor naming, pre-reg thresholds, smoke profile, FULL profile. Orchestrator gates the dispatch on pause flag.
