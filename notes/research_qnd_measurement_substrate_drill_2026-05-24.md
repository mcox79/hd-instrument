# Research drill — QND / Weak measurement / Interaction-free measurement → substrate

Date: 2026-05-24. Drill type: 2x-depth Research drill (per [[feedback-2x-means-depth]]). Trigger: user note "Measurements that acquire information about a system without collapsing or altering its original state are primarily referred to as quantum nondemolition (QND) measurements. Related: Interaction-Free Measurement (IFM), Weak Measurement."

Framing per [[feedback-brain-inspired]] and [[feedback-unbiased-research]]: not "QND for AI?" — the question is "what do QND-class measurement theorems actually do, and what classical primitive of the substrate sits in the analogous structural role?" The mapping is the contribution.

---

## 1st-level: three concepts → three substrate primitives (one line each)

- **QND ↔ Cap 8 VAMP-on-chain readout**: Cap 8's substrate-novel claim is that the VAMP iterative-inference readout extracts (byte, position) atoms from a bundle WITHOUT disturbing the codebook state. That is structurally a non-demolition measurement on the substrate's "stored" state. 1-edge mapping; the analogy is `codebook_state ↔ quantum_state`, `VAMP_iteration ↔ measurement_apparatus`, `bundle ↔ system_observable`.
- **Weak measurement ↔ low-α inference (overcomplete codebook regime)**: at α = M/N < 1 / near substrate's RS-phase capacity envelope, each VAMP iteration extracts a *weak* signal per atom; cumulative averaging across iterations is the AAV-style boost. Maps onto "low-coupling-per-trial, post-selection-amplified" structure.
- **IFM (Elitzur-Vaidman) ↔ counterfactual presence detection**: substrate could in principle encode a "(byte, position) is bound vs not bound" yes/no without firing the full VAMP cleanup — a Mach-Zehnder-style interference test on the binding op. Speculative; no substrate primitive currently fills this slot.

---

## 2nd-level: drill the strongest mapping (QND ↔ Cap 8)

### Mechanism in our terms

Cap 8 ships VAMP-on-chain + hard-cleanup as a substrate-novel readout primitive. The structural claim of QND is:

> there exists a measurement coupling that returns information about observable A while leaving the eigenstates of A undisturbed (Braginsky-Khalili, Rev Mod Phys 1996; Wiseman-Milburn QMF textbook).

The classical analog the substrate ships:

> VAMP-on-chain iteration returns the (byte, position) atom estimate while leaving the codebook unchanged (codebook = the fixed Kerdock-RM column basis); only the iterate's belief-state evolves.

In substrate terms: the codebook is the "QND-protected" object (eigenstates of the binding op); the iterate's posterior is the "meter pointer." The substrate's iteration is the analog of Braginsky's repeated-coupling protocol.

### What QND theorems would license (load-bearing)

1. **Repeated-measurement convergence bound (Bauer-Bernard 2011, arXiv:1106.4953 — "Convergence of repeated QND measurements and wave function collapse")**: gives a martingale-convergence rate for the meter pointer to the true eigenvalue under repeated coupling. *If* the VAMP-iteration → atom-recovery dynamic is structurally a classical-analog QND repeated measurement, this theorem licenses a closed-form bound on Cap 8's iteration-count → recovery-accuracy curve. This is a substantive payoff: today Cap 8 is empirically validated but lacks a clean rate theorem.
2. **Back-action-evading bound (Caves 1980, Braginsky-Khalili 1996)**: gives a Heisenberg-style lower bound on what fraction of the state is disturbed per bit of info extracted. The classical analog is a covariance inequality: Var(estimator) · Disturbance(codebook) ≥ const. The substrate currently claims Disturbance = 0 (codebook is fixed). The bound asks: is the codebook *truly* invariant under VAMP, or is there latent drift the substrate isn't measuring? **This is a falsifiable probe.**
3. **Holevo-type ensemble bound (Holevo 1973; Wilde QIT textbook)**: classical analog limits how much info a single VAMP readout can extract per pass given codebook entropy. Connects directly to Bet S K-ceiling — Holevo says you can't extract more than χ(ensemble) bits, regardless of cleverness of the readout.

### What the literature says about classical-analog QND

The search did not surface published classical-information-theoretic versions of Braginsky-Khalili bounds applied to AMP/VAMP. This is the substrate-novel hole. Two adjacent results exist:
- Quantum-mechanics-free subsystems (QMFS, Tsang-Caves 2012, arXiv:1203.2317) give a recipe for engineering subsystems that obey *classical* dynamics under continuous quantum measurement — i.e. the classical analog already exists at the meta-level, but not specifically applied to iterative belief-propagation readouts.
- Waveform estimation from approximate QND (Tsang et al PRL 2021) gives a Cramér-Rao-type bound mixing measurement back-action with classical estimation; this is the closest published precedent for what the substrate would need.

Net: there IS a literature scaffold; nobody has applied it to VAMP-on-chain specifically. Substrate is in adjacent-but-novel territory (per [[feedback-lit-scan-calibration-penalty]] this caps P at ~0.50 for "novel synthesis").

### Anchor experiment proposal (FUTURE shipping, NOT now)

Per [[feedback-ship-before-dependency-verified]] this is a Research-output anchor, not a queue-add.

**Name**: `cap8_qnd_codebook_invariance_probe_v1`

**Mechanism**: instrument the existing Cap 8 VAMP-on-chain experiment to measure codebook-column drift across iterations. Specifically: snapshot the Kerdock-RM codebook before VAMP iteration 0, again after iteration k, compute Frobenius norm of difference, plot vs k for k ∈ {1, 2, 5, 10, 20}. Classical-analog QND predicts ZERO drift. Any nonzero drift falsifies the "codebook-invariant readout" framing and forces a back-action-evading rewrite of the Cap 8 claim.

**Queue**: CPU sweep, ~5 GPU-min equivalent, runs on cpu_runner_0 once revived. Reuses existing VAMP-on-chain test harness; only adds codebook-snapshot diff instrumentation (~30 LOC).

**ETA**: 2 hours wallclock if queued immediately; depends on cpu_runner_0 status.

**Hard-pass**: Frobenius-norm drift < 1e-10 (numerical-precision floor) for all k. Codebook-invariance verified empirically. Cap 8 row gets the QND annotation in cap_map.

**Hard-fail**: Frobenius-norm drift > 1e-6 at any k. Codebook IS being perturbed; Cap 8 needs reframing as "approximate-QND" (Tsang-style waveform-estimation bound applies, not pure QND). NOT a Cap 8 retraction — it's a tightening.

**Inconclusive**: drift in 1e-10 to 1e-6 band; needs higher-precision arithmetic or longer iteration sweep.

### P estimate

P(QND framework yields a CLOSED-FORM bound on Cap 8 readout that improves on current empirical fits) = **0.35**

Reasoning: framework is adjacent and lit-validated (Bauer-Bernard, Tsang); substrate is in uncharted regime for direct application; per [[feedback-lit-scan-calibration-penalty]] novel-synthesis ceiling is 0.50, and the lack of any direct prior application to AMP/VAMP family deflates by another 0.15. The 0.35 reflects "more likely than not that SOMETHING useful drops out, but most likely a tightening framework, not a new theorem."

P(anchor experiment lands hard-pass, codebook-invariant) = **0.70**: Cap 8 evidence strongly suggests codebook is fixed; the experiment is mostly confirmatory instrumentation.

P(IFM mapping yields a substrate primitive worth shipping) = **0.15**: too speculative; the Mach-Zehnder analog is suggestive but no clear binding-op-as-interferometer construction exists today. Park; revisit only if QND mapping lands.

P(weak-measurement / low-α framework yields a low-α envelope theorem for substrate) = **0.25**: the AAV SNR result (PRA 2020, arXiv:1010.1155) explicitly shows SNR degrades when weak-value gets large — this CUTS AGAINST a clean substrate result at very low α. But the mid-α regime might be tractable.

---

## Honest accounting

This drill is in the "mathematically adjacent" territory flagged by [[feedback-dont-dismiss-adjacent-methods]] — same algebra family (iterative measurement → posterior update is the structural core of both QND and VAMP). That makes the mapping non-frivolous. But there is no direct published precedent applying QND theorems to classical iterative inference; the substrate would be doing novel synthesis. Per [[feedback-lit-scan-calibration-penalty]] this gets a 0.50 ceiling.

The anchor experiment is cheap (5 GPU-min, ~30 LOC instrumentation) and yields a hard YES/NO on whether Cap 8 is true-QND or approximate-QND. Either outcome is informative; neither is a Cap 8 retraction.

Next step if priority allows: dispatch Strategy to evaluate whether to slot the anchor experiment ahead of current Cap 12 BBMD followups, or defer until Cap 8 has more pressure on it. Recommend defer — Cap 8 is ✅ FULL and not currently being challenged; this is a hardening probe, not a rescue.

---

## Cross-row implications for cap_map (FYI for Strategy)

- **Cap 8 row**: if anchor passes, add annotation "verified codebook-invariant per QND-analog Frobenius-drift probe; readout is true-QND in the Bauer-Bernard sense."
- **Cap 12 row** (BBMD routing): unchanged; QND framework is one level deeper than routing.
- **Cap 11 χ4-early-warning**: weak-measurement framework might extend Cap 11's framing — early-warning signal as a "weak value" of the bulk χ4 cumulant; defer to a separate drill.
- New 🔬 row candidate (do NOT promote yet): "IFM-style counterfactual binding-op probe" — speculative; needs construction sketch before it earns a row.

---

## Sources (parallel-Sonnet WebSearch sub-agents — 3 dispatched, ~15s total wallclock)

- QND: Braginsky-Khalili (Rev Mod Phys 1996); arXiv:1106.4953 (Bauer-Bernard repeated-QND convergence); arXiv:2510.00064 (info-disturbance operator bound); arXiv:1203.2317 (QMFS, Tsang-Caves 2012); PRL 127.010502 (Tsang waveform-estimation from approx QND).
- Weak measurement: arXiv:1010.1155 (beyond-AAV formalism); arXiv:1307.4016 (weak-value amplification suboptimal); arXiv:0909.2206 (post-selected weak measurement beyond weak value); arXiv:2407.10087 (progress on weak-value amplification, 2024).
- IFM / Counterfactual: Elitzur-Vaidman 1993 original; arXiv:2005.03547 (IFM + counterfactual computation in IBM quantum computers); Mitchison-Jozsa counterfactual quantum computation.
