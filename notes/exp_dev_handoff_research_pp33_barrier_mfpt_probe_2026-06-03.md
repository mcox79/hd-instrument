# exp_dev hand-off -- research: PP-33 activation-barrier refutation deep dive

**Filed:** 2026-06-03 by research sub-agent.
**Trigger:** Research note `notes/research_drill_pp33_activation_barrier_refutation_deep_dive_2026-06-03.md`
**Pause state:** Check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N range, seed count, temperature schedule, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke vs FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Why now

PP-33 (activation-barrier sub-property) was closed after three consecutive HARD_FAILs (r3a, r3b, r3c) -- all hitting a structural ~0.5 boundary regardless of N or alpha. Research drill identified THREE viable explanations:

- Explanation A (P=0.35): the `nf_crit` proxy is a binary observable that saturates at chance level (0.5) by construction; the true barrier E_a(alpha, N) ~ N*(alpha_c - alpha)/alpha_c is intact and untested
- Explanation B (P=0.28): substrate is in the 1-RSB dynamical phase; barriers scale as N^{1/3} not N; the AGS 2.3x alpha ratio may survive at the level of g(alpha) but the N-scaling is weaker
- Explanation C (P=0.17): near-critical marginal basin; barrier is genuinely O(1); product narrative weakened

The MFPT (mean first passage time) experiment with Glauber dynamics is the SINGLE highest-ROI experiment available: it discriminates all three explanations, costs <2h CPU, and requires no cloud. It directly resolves whether the substrate product narrative "predictable retention barriers as function of loading" survives.

---

## Anchor candidates (rank-ordered; exp_dev picks per queue policy)

### 1. MFPT N-scaling probe via Glauber dynamics [DECISIVE]
- Anchor pointer: `notes/research_drill_pp33_activation_barrier_refutation_deep_dive_2026-06-03.md` SQ4 section (a)
- Substrate-product reading: measure mean first-passage time tau(alpha, N) under stochastic Glauber dynamics at T > 0; extract ln(tau) vs N and ln(tau) vs N^{1/3}; better linear fit identifies whether substrate is in AGS-RS phase (Explanation A) or 1-RSB phase (Explanation B); tau N-independence flags Explanation C. Alpha range should span tested territory. Multiple temperatures needed to extract barrier E_a = T * ln(tau * nu_0).
- Tier hint: Local CPU smoke (quick discriminator); scale to Remote CPU if smoke shows non-trivial N-dependence.
- Why now: closes PP-33 affirmatively OR definitively; no other pending experiment addresses this gap; <2h cost makes it the immediate next dispatch.

### 2. Basin-volume alpha-slope probe [COMPLEMENTARY to #1]
- Anchor pointer: `notes/research_drill_pp33_activation_barrier_refutation_deep_dive_2026-06-03.md` SQ4 section (d)
- Substrate-product reading: count fraction of RANDOM initializations (not boundary-initialized) converging to retrieval vs spin-glass attractors across alpha range; a clear alpha-slope in this ratio directly confirms that the substrate physics is intact (Explanation A) even if nf_crit was a broken proxy. This test does NOT saturate at 0.5 by construction.
- Tier hint: Local CPU smoke (random-start retrieval counts; no Glauber dynamics needed).
- Why now: fastest possible PP-33 physics check; complements MFPT; should be dispatched in same batch.

### 3. FFS (Forward Flux Sampling) basin-escape rate probe [CLEAN BARRIER MEASUREMENT]
- Anchor pointer: `notes/research_drill_pp33_activation_barrier_refutation_deep_dive_2026-06-03.md` SQ4 section (b); field advisor D7 (tier-1, score=5.0)
- Substrate-product reading: partition state space by overlap m with target pattern; measure conditional crossing probabilities across interfaces; extract escape rate k_FFS(alpha, N); compute E_a = -T * ln(k_FFS). Works for non-equilibrium dynamics (no Boltzmann assumption). Directly tests E_a(alpha) slope.
- Tier hint: Remote CPU (1-2 day implementation + multi-alpha sweep); lower priority than #1 and #2 since MFPT gives the same discriminator faster.
- Why now: FFS gives the most theoretically clean barrier measurement; implement after MFPT confirms non-trivial barriers exist.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_pp33_activation_barrier_refutation_deep_dive_2026-06-03.md`
- Field advisor D7 FFS candidate: `d:/AI/hd-instrument/notes/research_meta_map_and_adjacencies_*.md` (most recent)
- PP-33 prior experiment history: grep `PP-33` or `nf_crit` in `d:/AI/hd-instrument/data/decisions_log.jsonl`
- Non-equilibrium stat-mech cap_map row: `d:/AI/hd-instrument/notes/substrate_capability_map.md`
- AGS barrier formula derivation: SQ1 and SQ5 sections in research note above

---

## Contract

exp_dev MUST:
- Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND thresholds BEFORE coding
- Run smoke gate before FULL submission
- Self-test any closed-form formula used (formula-selftests requirement)
- Verify no `nf_crit` proxy reuse -- use direct MFPT / basin-count observables
- Check ship-name-collision uniqueness before queue_add.sh
- Post-ship REMOTE VERIFY

## Autonomy declaration

exp_dev decides ALL of: anchor names, N/T/alpha grids, seed counts, threshold numbers, queue routing (Tier A/B/C), ETA estimates, and smoke vs FULL profile. This file provides WHY and WHAT to measure; exp_dev owns HOW.
