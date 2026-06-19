# exp_dev hand-off -- research: BCM-SNR convergence floor vs polynomial-p energy (2x drill)

**Filed-by:** research sub-agent, 2026-06-04
**Trigger:** notes/research_drill_bcm_snr_vs_polynomial_p_2x_2026-06-04.md
**Pause state:** honor data/orchestrator_paused.flag before dispatching any queue items

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic framing only. Exp_dev decides anchor design, sweep parameters, HF/HP numerical thresholds, queue assignments, and pre-reg bands autonomously.

---

## ANCHOR CANDIDATES (rank-ordered)

### 1. Write-mode discriminator: episodic vs cumulative BCM at p=4 (HIGHEST PRIORITY)
**Anchor pointer:** BCM convergence at N=500, polynomial-p=4, episodic write resets vs cumulative writes
**Substrate-product reading:** The research drill identified that the BCM-SNR floor at p=4 drops to ~600-1200 ONLY under episodic writes (M_eff bounded at 200-500). Under cumulative writes, N_threshold is unchanged at 2000-3000. The critical confound is whether prior empirical tests used cumulative or episodic write mode. This anchor resolves that directly: two cells, same N=500 and p=4, differing only in write mode. If episodic-reset cell HARD-PASSes and cumulative cell HARD-FAILs, write mode is the key lever -- and the polynomial upgrade is secondary. If both fail, the eigenvalue floor dominates and we need N > M_eff regardless.
**Tier hint:** CPU smoke (N=500 is small; 5k training steps each; ~10 min per cell). Add reset flag to training loop -- 1-2 hr engineering effort.
**Why now:** This is the cheapest possible test to determine whether the polynomial-p=4 upgrade is sufficient for N_threshold < 1000. It disambiguates the three competing hypotheses (modulator-quality-bound / eigenvalue-bound / write-mode-bound) in a single run.

### 2. Polynomial-p vs classical: N=512 p=4 episodic vs N=512 p=2 episodic (critical p discriminator)
**Anchor pointer:** BCM convergence at N=512, p=4 vs p=2, episodic resets (M_eff=200), matched conditions
**Substrate-product reading:** If episodic writes at N=512 succeed at p=4 but fail at p=2, polynomial-p is causally responsible for the N_threshold reduction (not just write mode). P_deflated=0.28 for this claim. This cell is the minimal test of whether p matters independently of write mode. Win = confirmed that polynomial upgrade AND episodic mode together achieve N_threshold~500.
**Tier hint:** CPU smoke. Two cells, ~10 min each. Can share bootstrap with anchor 1.
**Why now:** Paired with anchor 1, this gives a 2x2 factorial: (p=2 vs p=4) x (episodic vs cumulative). The factorial resolves the interaction between the two levers in one batch.

### 3. N_threshold sweep at p=4, episodic (establishing the floor)
**Anchor pointer:** BCM bpc_gap vs N sweep at p=4, episodic writes, M_eff=200; cells N=200, 300, 500, 1000
**Substrate-product reading:** If anchors 1+2 confirm the combined hypothesis, the sweep establishes where exactly the N_threshold floor sits for p=4 episodic mode. The research drill predicts 300-600. Finding N_threshold experimentally fixes the product configuration for deployment (substrate size, memory footprint, batch reset frequency). N=200 = 160K float32 = 640KB RAM; N=500 = 1MB; N=1000 = 4MB. All viable for embedded or edge deployment.
**Tier hint:** Remote CPU or local GPU (4 cells x N sweep; ~30 min total). Can batch in one Lambda boot.
**Why now:** Only warranted if anchors 1+2 pass. Gate on those results before dispatching.

### 4. BCM + polynomial-p: convergence RATE comparison (steps to converge)
**Anchor pointer:** Steps-to-convergence at N=512, p=4 episodic vs p=2 episodic at matched bpc_gap target
**Substrate-product reading:** The research drill predicts 10x fewer steps at p=4 vs p=2 (from SNR_modulator^2 ratio). If confirmed, substrate-as-training-mechanism trains 10x faster per token with p=4. This directly reduces compute cost for the training use case. Also probes the STDP cubic-quartic loss convergence speed claim from arXiv:2504.05341.
**Tier hint:** CPU (same setup as anchor 2, just track convergence trajectory not final bpc_gap). Low extra cost.
**Why now:** Pairs with anchor 2; can be recorded from the same run at no extra cost.

---

## CONTEXT POINTERS

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_bcm_snr_vs_polynomial_p_2x_2026-06-04.md
- Prior 3x Hopfield upgrade drill: d:/AI/hd-instrument/notes/research_drill_modern_hopfield_upgrade_path_3x_2026-06-04.md
- Prior 3x N-threshold drill: d:/AI/hd-instrument/notes/research_drill_substrate_training_n_threshold_3x_2026-06-04.md
- Cap map: d:/AI/hd-instrument/data/cap_map.md
- Active protocols: d:/AI/hd-instrument/notes/active_protocols.md
- Queue files: d:/AI/hd-instrument/data/overnight_queue.json, cpu_queue.json
- Krotov-Hopfield 2016: arXiv:1606.01164 (polynomial-p energy; 3-line retrieval code change)
- Froc-van Rossum 2019: PMC6469599 (BCM slowdown eigenvalue formula; bipolar exception)
- Agliari-De Marzo 2020: arXiv:2007.02849 (polynomial-p SNR analysis; EPJ Plus 135:883)
- Three-factor STDP survey: arXiv:2504.05341 (Patterns 2025; convergence speed scales with SNR_modulator^2)

---

## CONTRACT

- exp_dev reads this file as the task input for the next queue-refill cycle
- exp_dev does NOT receive inline experiment design, sweep grids, or numerical HF/HP bounds from this file
- exp_dev pre-registers HF/HP bands autonomously per envelope-fail-bands feedback
- exp_dev verifies closed-form formulas (SNR = C_p * sqrt(N^(p-1)/M); tau_crit = tau_w/(N*a_{N/2}^2)) before coding
- Post-ship: exp_dev confirms queue presence after each queue_add.sh call (per ship-name-collision feedback)
- Timeout: computed per formula 1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)
- Gate: anchor 3 (N_threshold sweep) only if anchors 1+2 pass; do not queue all 4 simultaneously

## AUTONOMY DECLARATION

Exp_dev has full autonomy over: anchor name suffixes, exact bpc_gap thresholds for pre-reg bands,
choice of reset interval for episodic mode, sweep N values within the guidance range, queue (cpu vs overnight),
and seed count. The 5-cell list above is a guidance structure, not a binding specification.
