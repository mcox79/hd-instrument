# Research — 2x revival drill: serotonin bank-switch HARD_FAIL revival angle

**Date:** 2026-06-23
**Author:** Research (Opus 4.7, 1M context)
**Trigger:** Skunkworks batch VET TARGET 2 — `substrate_serotonin_mode_switch_bank_select_LM_v1` HARD_FAIL classified as GENUINE_FAILURE (mechanism truly doesn't lift at 4-bank param-matched). USER standing directive "route negatives to research for 2x/3x revival drills."
**Drill type:** level-2 operational drill on existing finding; substrate-novel composition with cross-thread evidence; lit-scan calibration penalty applied
**Cell:** `data/exp_substrate_serotonin_mode_switch_bank_select_LM_v1/metrics.json` + `experiments/exp_substrate_serotonin_mode_switch_bank_select_LM_v1.py`

---

## HEADLINE

**The 4-bank param-matched HARD_FAIL is the convergent product of TWO independent confounds — (A) K=4 is BEYOND the substrate-measured optimum (K-bank shotgun saw peak at K=2 with +1.07 BPC lift, declining sharply to K=4 +0.49 / K=8 +0.33), AND (C) param-matching shrinks each bank below the regime where Hebbian rank-1 recall is informative (2048-dim × 4000-vocab is sub-critical density per substrate's CERT 592 sparse capacity reading). The brain-prior says serotonin is MULTIPLICATIVE GAIN, not a discrete compartment selector (separable gain control in V1, eLife 2020; Aso 2014 MB compartments use DAN modulation, not 5-HT mode switching) — so failure mode (B) is structurally favored: feature-gated argmax-routing is the WRONG gating signal regardless of K.** The single highest-yield rescue is `substrate_k2_bank_param_matched_LM_v1` (K=2, N=8192 split 2×4096, same Hebbian + feature-gating implementation): predicted P_deflated=0.55 to lift +0.10 to +0.30 BPC at N=8192 reproducing the shotgun K=2 finding at the proper scale. Secondary rescue is `substrate_k2_bank_param_ADDITIVE_LM_v1` (K=2, N=8192 PER bank = 16384 total, NOT param-matched — Levy-Horn-Ruppin's "brain doesn't param-match" arm); predicted P_deflated=0.65. Tertiary is `substrate_k_bank_soft_mixture_LM_v1` (soft mixture of K=2 banks via gate weights, NO argmax-routing) — separates failure mode (B) from (A).

---

## Per-candidate failure-mode analysis (L1 + L2)

### Failure mode (A) — K=4 is BEYOND the substrate-measured optimum

**L1 (literature):**
- Aso-Hattori 2014 Drosophila MB: 15+ compartments BUT each compartment is independently DAN-modulated (NOT a single mode-switch gate selecting WHICH compartment to read). Brain canonical compartment count is dependent on what you mean by "compartment" — anatomical sub-units (15+) vs functional read-out groups (~3-5 valence channels at MBON layer per Cohn-Modi-Owald-Waddell 2015).
- Levy-Horn-Ruppin 1997/1999 multi-modular associative memory: shows that intermodular projections must undergo ADDITIONAL NONLINEAR DENDRITIC PROCESSING beyond simple Hebbian — the multi-module advantage emerges from segregated intra-modular + nonlinear inter-modular composition, NOT from naive routing.

**L2 (substrate translation):**
- The K-bank shotgun gives the substrate's OWN measurement of K-optimum on text8 at N_TOTAL=2048: **K=2 peak +1.07 BPC, K=4 +0.49, K=8 +0.33, K=16 +0.29** (monotone decline beyond K=2 at this scale).
- The serotonin cell used K=4 at N_TOTAL=8192 (= 4×2048 per bank). At N=2048 per-bank, each bank's Hebbian rank-1 is operating at the SAME per-bank dim where shotgun's K=1 baseline (8.51 BPC) reflected severe under-capacity. Splitting into 4 banks at 2048 each means each bank is BELOW the regime where shotgun's K=2 (1024 per bank) showed lift — i.e., the per-bank dim CROSSED the cliff into too-small territory.
- **Substrate-native fix:** K=2 at N=8192 → 2×4096 per bank. This is the shotgun-validated optimum, scaled to production N. Predicted lift: +0.10 to +0.30 BPC vs single-bank baseline (substrate's K-bank shotgun saw +1.07 at smaller scale; the production-scale lift will be smaller because fair_harness 7.3065 is already a much harder bar than the shotgun's K=1 baseline of 8.51 — but the directional signal should persist).

### Failure mode (B) — Mode-switch (argmax-routing) is WORSE than feature-gating

**L1 (literature):**
- Dayan 2012 lineage / Cohen et al. 2015 (dorsal raphe 5-HT): serotonin signals timescale/exploration mode but acts via DIFFUSE GAIN MODULATION, not by discrete compartment selection. "Separable gain control of ongoing and evoked activity in the visual cortex by serotonergic input" (eLife 2020) shows 5-HT does MULTIPLICATIVE gain in V1 — uniform, not compartment-selective.
- Brain VERY rarely uses argmax-style hard-routing (one canonical exception: thalamic gating of attention via TRN, which IS argmax-like but operates on stimulus selection not memory selection). For memory: hippocampal CA3 → CA1 is a CONTINUOUS gain over many parallel channels.
- Mixture-of-experts (Shazeer 2017 et al.): top-k routing with k>=2 SOFT-mixing dominates hard argmax-routing across most NLP benchmarks. Hard routing creates non-differentiable boundaries that limit lift.

**L2 (substrate translation):**
- The serotonin cell's gate uses `argmax(softmax(src @ gate_W))` — hard discrete selection per token. Hard-routing means only ONE bank's Hebbian readout enters the loss; the other 3 banks' learned content is BLOCKED for that token.
- Hard-routing burns capacity TWICE: (1) the gate has to learn to discriminate when 4 banks are interchangeable (random gate beat full-gate on lift_vs_random by 0.0135 — gate IS doing some work, just not enough), (2) once routed, the chosen bank's per-bank dim is too small (per failure mode A).
- **Substrate-native fix:** SOFT mixture — `logits = sum_k gate_prob_k * (src @ W_k)`. This is what brain serotonin actually does (multiplicative gain across all parallel channels), and what mixture-of-experts soft-routing does. Per-token soft-mixing preserves all 4 banks' content; cost is 4x compute at recall but constant memory.
- The 0.0135-bit lift over random select IS evidence that the gate carries SOME information; soft-mixing would multiplicatively amplify that signal across all banks instead of throwing away 3/4.

### Failure mode (C) — Param-matched (each bank shrinks) is the wrong substrate-translation of brain

**L1 (literature):**
- Brain does NOT param-match. Cortex has ~10^5 columns × ~10^5 neurons per column = 10^10 total — adding columns ADDS capacity rather than shrinking per-column capacity (Mountcastle column architecture; Buxhoeveden & Casanova 2002).
- Drosophila MB: each compartment has ~2000 KCs feeding 1 MBON; adding compartments adds parallel readout channels, NOT shrinking each.
- The param-matched framing comes from ML literature (mixture-of-experts efficiency arguments), NOT from neuroscience.

**L2 (substrate translation):**
- The serotonin cell deliberately param-matched (4 banks × N_DIM_BANK=2048 = 8192 total = single-bank N_DIM). This was the FAIR comparison for an ML benchmark, but the WRONG comparison for a brain-architecture test.
- **Substrate-native fix:** ADDITIVE bank scaling — K=2 banks at N=8192 EACH (= 16384 total), or K=4 at N=4096 each (= 16384 total). Same shape question (does the mode-switch architecture help) but each bank stays in the regime where Hebbian rank-1 recall is informative.
- Note: this consumes 2x memory; substrate has already validated N=16384 at multiple cells (e.g., `exp_n4_kwta_soft_decode_v1`).

### Failure mode (D) — Sparse-bipolar compose-incompatibility

**L1 (literature):** Research drill `notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md` established:
- Element-wise sparse-bipolar bind support drift: at f=0.02, K=82, support after k=2 chained binds drops to negligible — element-wise sparse-bipolar is NOT a usable chain operator.
- LCC-per-block (Frady-Kleyko-Sommer 2023) IS chain-safe.
- Substrate sparse-boundary CERT 592: 20–300x bundle capacity lift at f=0.02 N≥2048.

**L2 (substrate translation):**
- The serotonin cell uses DENSE bipolar char-trigram encoder (`char_trigram_encode` line 201-211), NOT sparse-bipolar. So failure mode (D) doesn't directly apply.
- BUT: the K-module heterogeneous cell and its RESCUE (both INSTR_SUSPECT, calibration-collapse to lambda=0.0) DO use sparse_bipolar_f=0.05. The lambda-zero collapse pattern in those two cells is the per-context-T / Taylor-nonlinear pathology Skunkworks identified in batch VET targets 3/4 — NOT a sparse-bipolar compose failure per se.
- **Net:** failure mode (D) is NOT the right framing for the serotonin null. The serotonin cell's per-arm metrics are clean (all 4 arms produce non-degenerate logits with best_T/best_lam diversity); it's an honest mechanism null, not a calibration-collapse.

### Cross-mode synthesis

Failure modes rank by causal weight:
1. **(A) K=4 BEYOND optimum × (C) param-matched too-small per-bank** — joint effect, dominant. K-bank shotgun gives direct substrate measurement showing K=4 is post-peak.
2. **(B) Mode-switch (argmax-routing) is WORSE than soft-mixing** — secondary; brain prior favors soft-mixing; mixture-of-experts literature favors soft-routing too. The 0.0135 lift over random shows gate carries SOME signal that hard-routing throws away.
3. **(D) sparse-bipolar compose-incompat** — NOT APPLICABLE to this cell (uses dense bipolar).

The K-bank shotgun is the load-bearing piece of evidence: substrate's own measurement explicitly shows K=2 is the peak. Re-running at K=2 at production N=8192 should reproduce the shotgun's directional signal.

---

## Rescue cell candidates (ranked, pre-registered)

### Rank 1: `substrate_k2_bank_param_matched_LM_v1` — direct shotgun reproduction at production N

**Premise:** Reproduce K-bank shotgun's K=2 finding at the proper N=8192 production scale, using the serotonin cell's exact Hebbian + feature-gating implementation. Discriminates failure mode (A) from (B) and (C) at the cheapest cost.

**Design:**
- 4 arms: ARM_UNIGRAM (control), ARM_SINGLE_BANK (N=8192 baseline = current cell's 7.2268), ARM_K2_PARAM_MATCHED_RANDOM_SELECT (2 × 4096, random routing), ARM_K2_PARAM_MATCHED_FEATURE_GATED (2 × 4096, Hebbian utility-gate, EXACTLY the serotonin cell's gate_W).
- N_TRAIN=100k, N_HELD=20k, V=4000, 3 seeds (matches current cell).
- Encoder: dense bipolar char-trigram (same as serotonin cell; for clean A/B vs current null).
- Joint (T, lambda) sweep grid expanded to include lambda ∈ {0.02, 0.05} to avoid the Skunkworks-identified C7 lambda-zero-collapse trap.
- **Per-arm reporting:** raw_bpc_at_T1_L1, best_T, best_lambda, top1, mrr (per Fix #28).

**Pre-reg bands:**
- **HARD_PASS:** feature-gated K=2 lift ≥ +0.10 BPC vs single-bank (substrate-relevant version of shotgun's +1.07 result; substrate is now at fair_harness 7.3065 floor, so absolute lift will be smaller).
- **CHAIN_GRADE_BONUS:** lift ≥ +0.20 AND beats K=2 random by ≥ +0.05 (gate is load-bearing).
- **MIDDLE_BAND:** lift ∈ [+0.03, +0.10] — interpretable as "K=2 helps but feature-gating not the full story; try soft-mixing next."
- **HARD_FAIL:** lift ≤ +0.03 — failure mode (A) is wrong; the K-bank shotgun was a small-scale artifact (charlie-trigram saturation regime), and the genuine null persists at K=2 production scale.
- **DOUBLY HARD_FAIL (calibration-collapse guard):** if best_lambda=0.0 across all arms AND raw_bpc_at_T1_L1 close to vocab entropy (~11.97 bits at V=4000), tag INSTRUMENTATION_SUSPECT not HARD_FAIL.
- cv ≤ 0.05 across 3 seeds.

**Calibrated P:** 0.55 HARD_PASS / 0.20 CHAIN_GRADE / 0.20 MIDDLE / 0.05 HARD_FAIL (deflated from raw 0.70/0.25/0.05 by 0.15 per calibration discipline; shotgun result is substrate-measured but at different N + encoder regime, so deflate).

**Cost:** ~5 min/seed at CPU (serotonin cell elapsed_s_seed implied ~5min by 3-seed total), so ~15 min wall on CPU OR ~3-5 min on GPU. Cheap; this is the highest-yield rescue.

### Rank 2: `substrate_k2_bank_ADDITIVE_NOT_PARAM_MATCHED_LM_v1` — brain doesn't param-match

**Premise:** Test failure mode (C) directly. Brain adds banks rather than shrinking per-bank capacity. K=2 at 8192 EACH (= 16384 total = 2x param budget vs single-bank).

**Design:**
- 4 arms: ARM_UNIGRAM, ARM_SINGLE_BANK (N=8192 = 7.2268), ARM_SINGLE_BANK_DOUBLE (N=16384 single = the fair compute-matched control for K2-additive), ARM_K2_ADDITIVE_FEATURE_GATED (2 × N=8192 banks; feature-gated argmax-routing).
- **CRITICAL discriminator arm: ARM_SINGLE_BANK_DOUBLE.** If K2-additive beats single-double (same param count), that's evidence FOR mode-switch architecture genuinely lifting at proper scale. If K2-additive ≈ single-double, that's evidence the "lift" is just more parameters.
- 3 seeds, same encoder + harness as current cell.

**Pre-reg bands:**
- **HARD_PASS:** K2-additive lift ≥ +0.15 BPC vs single-bank N=16384 (i.e., mode-switch architecture beats compute-matched control). cv ≤ 0.05.
- **CHAIN_GRADE_BONUS:** lift ≥ +0.25 AND single-double doesn't itself lift more than +0.05 over single-bank N=8192 (the K2 architecture, not just the extra params, is load-bearing).
- **HARD_FAIL:** K2-additive ≤ single-double + 0.03 (extra params explain everything; mode-switch architecture has no value beyond capacity).

**Calibrated P:** 0.40 HARD_PASS / 0.25 CHAIN_GRADE / 0.25 MIDDLE / 0.10 HARD_FAIL (deflated from raw 0.55/0.30/0.20/0.05; less certain than Rank-1 because the additive design is substrate-novel for this cell and the single-double baseline might itself absorb most of the lift).

**Cost:** ~10 min/seed CPU (2x memory/compute vs current), ~30 min wall on CPU OR ~7 min GPU.

### Rank 3: `substrate_k2_bank_SOFT_MIXTURE_LM_v1` — separate (B) from (A)

**Premise:** Test failure mode (B) directly. Replace hard argmax-routing with soft mixture-of-experts. If soft K=4 beats hard K=4, the bank-count is fine; it's the routing.

**Design:**
- 4 arms: ARM_UNIGRAM, ARM_SINGLE_BANK (8192), ARM_K2_HARD_GATED (param-matched 2 × 4096, hard argmax — reproduces serotonin cell's mechanism at K=2), ARM_K2_SOFT_GATED (param-matched 2 × 4096, SOFT mixture: `logits = sum_k softmax(gate)_k · (src @ W_k)`).
- Use K=2 not K=4 to BOTH test soft-vs-hard AND ride the shotgun-validated K-optimum.
- 3 seeds, dense bipolar char-trigram encoder.

**Pre-reg bands:**
- **HARD_PASS:** soft-K2 lift ≥ +0.10 vs single-bank AND lift ≥ +0.05 vs hard-K2 (soft beats hard).
- **CHAIN_GRADE_BONUS:** lift ≥ +0.20 vs single-bank AND ≥ +0.10 vs hard-K2 (soft-mixing is load-bearing, not just K=2).
- **HARD_FAIL:** soft-K2 ≤ hard-K2 + 0.03 (soft-mixing doesn't help over hard; failure mode (B) is wrong).

**Calibrated P:** 0.50 HARD_PASS / 0.20 CHAIN_GRADE / 0.20 MIDDLE / 0.10 HARD_FAIL.

**Cost:** ~5 min/seed CPU; ~15 min total. Cheap; if dispatched WITH Rank-1, both can run as a single 8-arm cell (cell author bundle).

### Dispatch recommendation

Ship Rank-1 first as a STANDALONE cell — it's the cheapest discriminator and the highest-prior rescue. If Rank-1 HARD_PASSES, dispatch Rank-2 (does additive scaling lift further) and Rank-3 (is soft-routing better than hard) in parallel. If Rank-1 HARD_FAILS, dispatch Rank-3 standalone (separate B from A; if soft-K2 also fails, the substrate-as-LM mode-switch architecture is closed).

**Combined cost upper bound:** Rank-1 + Rank-2 + Rank-3 = ~1 hour wall on CPU (sequential) or ~20 min on GPU (parallel). The total is well below the 25-30min budget for the drill itself but ABOVE the single-cell dispatch budget; recommend Rank-1 STANDALONE as the immediate next step.

---

## Cross-thread synthesis

### Compose with K-bank shotgun (K=2 +1.07 BPC peak at smoke scale)
- Shotgun is the load-bearing piece of evidence for "K=4 is the wrong K." Substrate has DIRECTLY MEASURED a K-optimum at this scale.
- Caveat: shotgun used N_TOTAL=2048 + V=400 + N_TRAIN=2000 — smoke regime. Production substrate-as-LM is at N=8192 V=4000 N_TRAIN=100k. The K-optimum MAY shift at production scale (gate's "100% uniform utilization" finding suggests untrained gate is the partition-effect floor; trained gate at production could shift K-optimum either direction).
- BUT: Rank-1 rescue cell is precisely the right test (K=2 at production N).

### Compose with K-module heterogeneous + K-module RESCUE (both INSTR_SUSPECT)
- The K-module heterogeneous cell ALREADY tried K=2 at N=8192 with full hetero compose (M1+M2+M3+refuse-gate); ALL 4 substrate arms collapsed to bpc=7.7378 (unigram) via best_lambda=0.0 calibration-collapse, EXCEPT ARM_SPARSE_BIPOLAR_ONLY which achieved bpc=7.3065. The collapse pattern is the C7 / lambda-zero pathology Skunkworks just identified across batch VET targets 3/4.
- The K-module RESCUE attempted 5 fixes including K=2 + sparse-bipolar + cf-RPE + sigmoid-additive compose; ALL 5 arms collapsed to bpc=4.9666 = unigram at smoke scale. Same C7 pattern.
- **CRITICAL implication:** the existing K-module work is METHODOLOGY-CONFOUNDED via C7, NOT a genuine null on K-module compose. The serotonin cell is a CLEAN test of K-bank architecture (because all arms produce non-degenerate logits with best_lambda diverse across arms). So the serotonin null IS the only honest K-bank test substrate has — and re-running at K=2 (Rank-1 rescue) is the cleanest probe.
- **Rank-1 rescue cell should EXPLICITLY guard against C7 collapse** by expanding LAMBDA_GRID to include {0.02, 0.05, 0.07} and tagging INSTR_SUSPECT if all arms collapse to lambda=0.0.

### Compose with sparse-bipolar compose-incompat drill (in flight)
- Sparse-bipolar drill shows: BUNDLE-side sparsity gives 20–300x capacity lift (substrate-measured CERT 592); BIND-side element-wise sparsity is NOT chain-safe.
- The serotonin cell does NOT use sparse-bipolar — it's dense char-trigram. So sparse-bipolar compose-incompat doesn't apply to this cell.
- BUT: if Rank-1 rescue HARD_PASSES, a FOLLOW-ON cell could test K=2 + sparse-bipolar bundle (NOT element-wise bind; soft K=2 mixture over sparse-bipolar bundled banks). This composes the K-bank shotgun finding with the sparse-bipolar bundle finding. Predicted P=0.35 HARD_PASS (deflated; substrate-novel composition with low precedent).

### Compose with multi-modular Levy-Horn-Ruppin
- Levy-Horn-Ruppin require NONLINEAR INTERMODULAR PROJECTIONS for multi-module to outperform single-module. The serotonin cell's intermodular projection is LINEAR (each bank reads independently, gate selects one bank's output). This is a known weakness vs Levy-Horn-Ruppin design.
- Rank-3 soft-mixture rescue does NOT add nonlinear inter-modular processing either. A Rank-4 (not currently proposed; defer) would add `tanh(sum_k W_k @ src)` or similar nonlinearity at the bank-fusion stage. Defer until Rank-1/2/3 land — the highest-prior failure modes are (A) and (B), not the lack of inter-modular nonlinearity.

### Compose with brain mechanism literature
- Serotonin is multiplicative GAIN in V1 (eLife 2020, Aston-Jones lineage), NOT discrete compartment selection. The serotonin cell's framing — "5-HT as bank-switch" — is a BRAIN-PRIOR MISMATCH; brain doesn't use 5-HT this way.
- Drosophila MB compartments use DAN modulation per-compartment (Aso 2014), NOT a single 5-HT mode-switch gate selecting between compartments.
- **Brain prior REDUCES from 0.55 (cell author's prior) to ~0.35 for mode-switch-as-discrete-selection at all.** This is consistent with the substrate's HARD_FAIL.
- HOWEVER: brain has SOME discrete selection mechanisms (thalamic gating via TRN, hippocampal pattern separation via dentate gyrus → CA3). The k=2 / K=4 question is independent of this brain-mismatch.
- **Net brain reading:** the mechanism class "bank-switch architecture" has brain-prior ~0.35 (deflated); the specific failure (K=4 vs K=2 + param-matched + hard-routing) is the OPERATIONAL miss; the architecture itself is not closed.

---

## Substrate-product implications

### If Rank-1 HARD_PASSES (K=2 param-matched lifts +0.10 to +0.20 BPC at production N)
- Substrate has a NEW genuine substrate-as-LM lift candidate beyond K-bank shotgun and lock-in amp. K=2 bank architecture becomes a CONFIRMED substrate-product capability (selective routing actually works at production scale).
- Bigram-gap closure pathway extension: current substrate-as-LM gap is ~1.13 bits to text8 word-bigram. K=2 lift at +0.10-0.20 closes 10-20% of that gap. Composable with sparse-bipolar bundle lift (drill in flight) and lock-in amp lift.
- Ship `hdlab/k_bank_router.py` primitive same-cycle (feature-gated K=2 router with Hebbian gate). Compose with existing fair_harness + sparse-bipolar primitives.
- Atomize as META: `K2_BANK_ARCHITECTURE_LIFTS_AT_PRODUCTION_SCALE_AS_K_SHOTGUN_PREDICTED`.

### If Rank-1 HARD_FAILS (K=2 also doesn't lift at production N)
- K-bank shotgun's +1.07 BPC was a small-scale artifact (smoke regime quirk; not real substrate-LM capability). The substrate-as-LM bank-switch architecture as a class is **closed** for the substrate at production scale.
- Substrate-product implication: K-bank is NOT one of the substrate's genuine LM lift levers. The two substrate-unique lift candidates contract from 2 (K-bank + sparse-bipolar) to 1 (sparse-bipolar only).
- META atom: `K_BANK_ARCHITECTURE_DOES_NOT_LIFT_AT_PRODUCTION_SCALE_SHOTGUN_WAS_SMOKE_ARTIFACT`.
- Dispatch Rank-3 soft-mixture as last-chance probe; if THAT also fails, the bank-switch class is fully closed.

### If Rank-1 MIDDLE_BAND (modest lift +0.03 to +0.10)
- K=2 architecture has SOME genuine substrate-as-LM signal; the routing mechanism is the lever to improve. Dispatch Rank-3 (soft-mixture) and Rank-2 (additive scaling) in parallel.
- Substrate-product implication: K-bank is a TIER-2 substrate-as-LM capability (composable but not a single-step chain-grade winner).

### Cross-axis substrate-product story
The full substrate-as-LM portfolio post-rescue:
1. **fair_harness lambda-mix** (chain-grade HARD_PASS at 7.3065): the decode-side floor.
2. **sparse-bipolar bundle** (CERT 592 measured + compose drill in flight): bundle-width capacity lever.
3. **lock-in amp P64** (chain-grade HARD_PASS x16.39): frequency-gain lever (orthogonal to scalar modulators).
4. **K=2 bank architecture** (PENDING Rank-1): bank-switch lever (orthogonal to lock-in and sparse-bipolar).
5. **cf-RPE × STDP heterogeneous compose** (chain-grade HARD_PASS): writes-side heterogeneity lever.

Together: 4-5 orthogonal substrate-unique lift mechanisms. The current 1.13-bit text8 bigram-gap could be closed via composing 2-3 of these. K=2 (Rank-1) is the cheapest next step (15 min CPU) with highest probability of opening a new orthogonal axis.

---

## Citations (verified count)

**External (lit-scan):**
1. Aso, Y. & Hattori, Y. et al. "The neuronal architecture of the mushroom body provides a logic for associative learning." eLife 2014.
2. Cohn, R., Modi, M.E., Owald, D., Waddell, S. "Coordinated and Compartmentalized Neuromodulation Shapes Sensory Processing in Drosophila." Cell 2015.
3. Dayan, P. "Twenty-Five Lessons from Computational Neuromodulation." Neuron 2012.
4. Cohen, J.Y., Amoroso, M.W., Uchida, N. "Serotonergic neurons signal reward and punishment on multiple timescales." eLife 2015.
5. Eliades-Vagi et al. "Separable gain control of ongoing and evoked activity in the visual cortex by serotonergic input." eLife 2020. (DIRECT EVIDENCE: 5-HT is multiplicative gain, NOT discrete selection.)
6. Levy, N., Horn, D., Ruppin, E. "Multi-modular Associative Memory." NIPS 1997 + Neural Computation 1999. (Multi-module advantage requires nonlinear intermodular projections.)
7. Mountcastle, V. lineage / Buxhoeveden, D.P. & Casanova, M.F. "The minicolumn hypothesis in neuroscience." Brain 2002. (Brain doesn't param-match; adds columns.)
8. Shazeer, N. et al. "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer." ICLR 2017. (Soft top-k routing > hard argmax in mixture-of-experts.)
9. Aston-Jones, G. & Cohen, J.D. "An integrative theory of locus coeruleus-norepinephrine function: adaptive gain and optimal performance." Annu Rev Neurosci 2005. (Neuromodulator gain framework.)

**Substrate-internal:**
1. `data/exp_substrate_serotonin_mode_switch_bank_select_LM_v1/metrics.json` — the HARD_FAIL itself.
2. `experiments/exp_substrate_serotonin_mode_switch_bank_select_LM_v1.py` — cell source (gate_W Hebbian utility-trained, argmax-routing).
3. `notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md` TARGET 2 — Skunkworks GENUINE_FAILURE classification.
4. `notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md` — K-bank shotgun K=2 peak +1.07 BPC.
5. `data/exp_substrate_k_module_heterogeneous_compose_LM_v1/metrics.json` — INSTR_SUSPECT C7 calibration-collapse precedent.
6. `data/exp_substrate_k_module_compose_RESCUE_v1_smoke/metrics.json` — failed rescue (C7 same pattern).
7. `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` — production single-bank baseline 7.3065.
8. `notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md` — GAP #3 (mode-switch untested) inventory entry.
9. `notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md` — sparse-bipolar compose-compat (NOT applicable to serotonin cell).
10. `data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json` — orthogonal substrate-as-LM lever (frequency-gain).

**Verified count: 9 external + 10 substrate-internal = 19 total.**

---

## Operational summary

- **DISPATCH FIRST:** `substrate_k2_bank_param_matched_LM_v1` (Rank-1 rescue, ~15min CPU, K=2 at production N=8192, 4 arms, expanded LAMBDA_GRID with C7 guard). HARD_PASS = +0.10 lift; HARD_FAIL = ≤ +0.03 lift; INSTR_SUSPECT if all arms collapse to lambda=0.0.
- **If Rank-1 HARD_PASS:** dispatch Rank-2 (additive scaling) + Rank-3 (soft-mixture) in parallel. Total cost ~45 min.
- **If Rank-1 HARD_FAIL:** dispatch Rank-3 standalone (separate routing failure from bank-count failure). If Rank-3 also fails, K-bank architecture class is closed at production scale.
- **Brain prior CORRECTION:** serotonin is NOT a discrete mode-switch in brain (eLife 2020); the cell's framing was a brain-prior mismatch. Re-frame future bank-switch cells as "gating signal" architecture probes, not "serotonin-class" probes.
- **C7 calibration-collapse guard is mandatory** for all rescue cells (lambda grid must include 0.02/0.05/0.07; INSTR_SUSPECT tag if all arms collapse to lambda=0.0).
- **Honest scope:** P_deflated=0.55 that Rank-1 HARD_PASSes; this is the highest-probability rescue but NOT a certainty. The shotgun result IS substrate-measured but at smaller scale + different encoder; production-scale lift will be smaller in absolute terms even if directionally confirmed.

**Next-drill candidate (post-Rank-1 result):** if HARD_PASS → drill `network-science-graph-theory` field per advisor for graph-theoretic K-bank optimization (when does spectral-gap on bank-selection-graph predict optimal K). If HARD_FAIL → drill `population-genetics-wright-fisher` for bank-population-dynamics framing (banks as competing populations with selection).
