# Research 2x drill — SWS/REM cyclic-eta readout redesign (associative recall)

Filed-by: research (Opus 4.7)
Date: 2026-06-27
Topic: Replace classification readout in `cyclic_sws_rem_eta_schedule_v1` so the substrate-level frob_ratio=12.63 cycling signal becomes measurable.
Triggered-by: Skunkworks verdict commit `22f8d905` (agent `a0534a89`) — TEST_DESIGN_FAILURE; baseline=0.026 = chance 1/N_CAT(=50).
Per-rule context: META_RULE_AA fairness-before-tier; META_RULE_K discriminator-must-fire; META_RULE_AC HYPOTHESIZED vs MEASURED.

---

## HEADLINE

The cell's substrate-level mechanism is real (MEASURED frob_ratio=12.63 at high/low eta — Diekelmann-Born 2010 SWS/REM rate alternation reproduced on substrate W). The TEST_DESIGN_FAILURE is exclusively at the classification readout: with `N_CAT=50` one-hot keys + class-averaged W, top-1 cosine to class-centroid sits at 1/50=0.02 = chance because the W primitive bundles 50 patterns per category into 1 row (each row sees 10 noisy versions of the same prototype; after replay the rows are noisy near-copies of prototypes and class-centroid argmax is at floor). The fix: stop averaging across class members, store each pair as its own (key, value) trace, and READ OUT by direct key-cued recall against the full M=N_CAT*N_TRAIN bank. The `replay_cycle` primitive already expects this layout (`keys[M, K_DIM]`, `values[M, V_DIM]`); we just need to swap classes for trace-IDs in the key encoding and adopt one of the 3 readouts below.

**TOP-1 PICK:** Option A (associative recall against held-out keys with per-pair random key encoding). **P(HARD_PASS) deflated = 0.45.**
**TOP-2 PICK:** Option C (capacity-at-fixed-recall sweep over N_PAIRS — discriminator: does cycling EXTEND the capacity knee?). **P(HARD_PASS) deflated = 0.32.**

---

## Cheap decisive test (TOP-1: Option A)

**Readout:** replace `heldout_acc_via_proto_match` with key-cued associative recall.

1. Encode M = N_PAIRS pairs as `(k_i, v_i)` where `k_i, v_i ∈ {-1,+1}^N` are independent bipolar random vectors (NOT class one-hot). Use M=512 at smoke (matches old M=500 = 50*10).
2. Seed W = sum_i v_i ⊗ k_i / sqrt(N) (initial Hebb with eta_constant).
3. Run replay_cycle N_PULSES=20 across {constant_eta, cyclic_high_low_short(period=1), cyclic_high_low_long(period=5)} arms.
4. **Readout (held-out probe):** for each stored pair, present a NOISY key `k_i' = k_i + sigma*z` (sigma=PROTO_NOISE=0.85, identical noise statistic to original prototype-noise), compute `v_hat = W @ k_i'`, score top-1 by cosine to all M stored values, plus top-5.
5. Baseline = constant-eta replay (NOT raw Hebbian; that already fired in original cell at 0.026 = correctly out-of-band).

**Chance** = 1/M = 1/512 = 0.002 (negligible — much further below operating regime than 1/50=0.02 was).
**Substrate band** = [0.30, 0.70] at sigma=0.85 with alpha=M/N=512/1024=0.5 (per peek_arm_metrics typical HRR key-cued recall regimes).

**Discriminator firing check (META_RULE_K):** at smoke N=1024, M=512, alpha=0.5, sigma=0.85, the substrate should land top-1 cosine recall in band — if either arm hits >=0.95 (saturation) or both at <=0.05 (regime broken), tune M down or sigma down BEFORE dispatch.

---

## Falsifiable predictions

### HARD_PASS (joint, all required) — Option A
- baseline_constant_eta top-1 ∈ [0.30, 0.70] (fair-band gate; META_RULE_AA)
- best_cyclic top-1 - constant_eta top-1 >= **+0.10** absolute
- frob_ratio_high_over_low >= 3.0 (sanity: cycling IS happening at synapse level)
- top-5 of cyclic also lifts >= +0.05 over constant (rules out "cycling just sharpens 1 trace, hurts others")
- entropy(eigenspectrum) cyclic > entropy(constant) by >= +0.05 nats (cycling preserves W rank diversity — supports Walker-Stickgold "spread-then-prune" reading)
- cv across seeds < 0.10

### HARD_FAIL (any one) — Option A
- baseline_constant_eta >= 0.95 (saturated; not in discriminating regime — drop M or raise sigma)
- baseline_constant_eta <= 0.10 (substrate dead; over-aggressive sigma — drop sigma)
- best_cyclic - constant_eta within ±0.03 (no measurable cycling effect at THIS readout either)
- frob_ratio < 1.5 (synapse-level mechanism vanished — cell broken)
- cyclic_long arm outperforms cyclic_short by > +0.10 with NO theoretical prediction (suggests period-5 is hitting a confound, not a Diekelmann-Born regime)

### MIDDLE_BAND (informative; not chain-grade)
- 0.03 <= (best_cyclic - constant_eta) < 0.10 with frob_ratio >= 3.0 — mechanism reproduces but lift is small. Re-tune to alpha=0.25 (drop M) and re-test.

---

## The 3 readout options — full comparison

### Option A: Associative recall against held-out (noisy) keys [TOP-1]

- **Brain-grounding:** Wilson-McNaughton 1994 hippocampal replay re-activates (place, context) pairs; Stickgold 2005 + Ji-Wilson 2007 show NREM ripples consolidate pair-associates; the readout (noisy-cue → retrieve value) is the CA3 autoassociation operation (Rolls 2013 review — recurrent CA3 collateral pattern completion is the canonical hippocampal-MTL substrate analog).
- **Cycle freq:** human SWS/REM ~90-min macro-cycle; ripple density within SWS is ~0.5-3 Hz; we already collapse this to "high-eta vs low-eta per pulse" which the substrate analog is `period=1` (per-pulse alternation) and `period=5` (5-pulse SWS-eta-low then 5-pulse REM-eta-high, matching the within-cycle SWS:REM ratio of ~4:1 in NREM-dominant late-night sleep — Walker 2017 ch 3).
- **Discriminator regime:** at alpha=M/N=0.5, sigma=0.85, expect constant_eta top-1 ~0.45-0.60 (Hopfield + replay-stabilized). Cycling should give +0.10-+0.20 lift if Volkov-Sapir 2024 cyclic-annealing is real at this layer. If cycling gives lift <+0.05, the mechanism is real at synapse level (frob_ratio) but doesn't propagate to retrieval.
- **Fair baseline:** constant_eta = sqrt(eta_high*eta_low) = 0.316 (or prereg literal 0.5). The replay_frac=0.2 is held constant across arms — only `lr` schedule varies.
- **Compute cost:** smoke (N=1024, M=512, N_PULSES=20, seeds=[11], 4 arms + 1 diag) ~ 8-15 CPU-sec on laptop. Full (N=2048, M=1024, N_PULSES=50, 5 seeds, 4 arms) ~ 4-7 CPU-min. Cheap.
- **P(HARD_PASS) deflated:** **0.45** (raw 0.65 minus 0.20 calibration penalty — substrate-novel layer mapping, no published direct precedent of synapse-level eta-cycling → CA3-recall benefit on bipolar HRR-style memories).

### Option B: Pattern completion from masked key

- **Brain-grounding:** Tonegawa lab masked-cue pattern-completion paradigms (Liu et al. 2012 engram); CA3 attractor dynamics (Wills-Lever-Cacucci-Burgess-O'Keefe 2005). Same hippocampal cleanup mechanism as A but with PARTIAL-not-noisy probe.
- **Discriminator regime:** mask 50% of dimensions of `k_i` to zero; query `W @ k_masked`. Top-1 cosine recovery to true `v_i`. At 50% mask, expect constant_eta in [0.25, 0.45] — substrate W under bipolar HRR has known scale-with-overlap-fraction (atom 587 Cap-2 generation cell saw similar regime). Substrate band: [0.20, 0.55].
- **Why NOT TOP-1:** pattern-completion adds a confounding variable (mask fraction); the cycling-vs-static contrast at smoke could be confounded by mask-density-vs-active-write-density interaction (we already saw THIS exact confound in `engram_dropout_v1` density-confound bug). Option A keeps the noise statistic identical to original cell's prototype-noise machinery — minimal change, maximally interpretable.
- **Fair baseline:** same constant_eta; same mask fraction across arms.
- **Compute cost:** ~ same as A (1.0-1.1x).
- **P(HARD_PASS) deflated:** **0.30** (raw 0.45; confound risk higher).

### Option C: Capacity-at-fixed-recall sweep [TOP-2]

- **Brain-grounding:** McClelland 1995 CLS — sleep consolidation SHIFTS capacity (more traces survive); Buzsaki 2015 — ripple-density correlates with future recall capacity; closer to "does cycling extend the knee of the storage-recall curve?" rather than "fixed-M lift."
- **Discriminator regime:** sweep M ∈ {128, 256, 512, 1024, 2048} (5 points). For each M and each arm, measure top-1 recall via Option A's readout. Find M_50% = highest M where top-1 >= 0.50. **Discriminator: M_50%(best_cyclic) / M_50%(constant_eta) >= 1.2** (i.e. cycling extends capacity by >=20%). This is a STRONGER claim than fixed-M lift because it isolates capacity-extending vs accuracy-sharpening.
- **Why TOP-2 not TOP-1:** more compute (~5x Option A); needs 2 dispatches (smoke just verifies discriminator fires at one M, then full sweeps). But it's the cleanest mapping to Diekelmann-Born "spread-then-consolidate" since it directly measures the capacity gain.
- **Fair baseline:** static-eta sweep across same M-grid.
- **Compute cost:** smoke (single M=512, all 4 arms, 1 seed) ~ Option A cost. Full (5-point M sweep × 5 seeds × 4 arms) ~ 25-40 CPU-min.
- **P(HARD_PASS) deflated:** **0.32** (raw 0.50; if cycling lift IS real, capacity-knee extension is a more robust READOUT but a stronger demand; calibration penalty applied for the stronger claim).

---

## Cross-thread synthesis with prior substrate evidence

**MEASURED priors (verified on disk this drill):**
- `replay_cycle` primitive (atom 588, hdlab/continual.py) — proven-bound at +0.57 drift_reduction (forward direction, replay_frac=0.2). MEASURED.
- `cyclic_sws_rem_eta_schedule_v1_smoke/metrics.json` — frob_ratio=12.63, baseline=0.026 (out of band), constant=0.040, cyclic_short=0.030. MEASURED.
- Wave 2 redesign pattern (commit 2546e96e): `engram_dropout_v2_density_matched` fixed an analogous test-design bug (density confound) by per-pattern density-matched control + fair-baseline alignment. Cell 2 there reached MIDDLE_BAND with +0.015 lift in band. Same pattern applies here — fix the readout layer, expose the true signal size.

**HYPOTHESIZED links (lit-supported, NOT yet measured on substrate):**
- Diekelmann-Born 2010 / Stickgold 2005 SWS-eta-low + REM-eta-high alternation IS the brain analog; rodent ripple-density × associative-recall correlation (Girardeau-Benchenane-Wiener-Buzsaki-Zugaro 2009) supports A's pair-association readout as the closest neural-substrate analog. HYPOTHESIZED.
- Volkov-Sapir 2024 cyclic-annealing connection: the literature substantiates cycle-vs-static benefits in spin-glass / Hopfield-class energy landscapes; the substrate primitive is HRR-bipolar variant which is in the Hopfield-adjacent regime; transfer P ~ 0.40-0.55 (calibration-deflated). HYPOTHESIZED.

**Saturation guard (META_RULE_K + Fix #28):** if Option A baseline lands at 0.95+ at smoke, drop M to 256 or raise sigma to 0.95 BEFORE dispatching full. Skunkworks correctly pinged this in original verdict — replicating that discriminator-must-fire-at-smoke discipline.

---

## Substrate-product implications

If Option A delivers HARD_PASS:
- **Capability:** chain-grade evidence that the substrate exhibits sleep-physiology-grounded consolidation (cycling > static replay). Adds an atom to the continual-learning landscape complementary to atom 588 (which proved replay-fraction effects; this would prove rate-cycling effects).
- **Product-relevant:** Substrate-as-Director-KB dogfood (active project) eventually wants long-horizon memory consolidation that beats simple replay. If cycling pays off here, it's a candidate to fold into the KB ingest scheduler (eta-cycle the embedding refresh rate across ingest batches).
- **Stage:** Stage 1 base capability (memory primitive); does NOT skip toward Stage 4 LM equivalence (per USER stage-progression directive).

If Option A delivers HARD_FAIL (no readout-level lift despite synapse-level cycling):
- Closure-rescue path: synapse-level cycling is real but doesn't propagate; this points to the encoding layer (bipolar HRR may flatten the cycling benefit). Adjacent drill = Option C capacity-knee + plus separate cell with sparse-coded keys (Tonegawa-style 5-10% active) to test whether the readout-propagation gap closes under sparser representations.

---

## Calibration notes (META_RULE_AC)

- All P(HARD_PASS) estimates DEFLATED by 0.20 (substrate-novel layer mapping; no direct precedent in published lit for synapse-level eta-cycling → HRR-bipolar key-cued recall benefit).
- Novel-synthesis cap P=0.50 honored (top picks at 0.45 and 0.32 below cap).
- Brain-grounding citations are HYPOTHESIZED transfer to substrate layer; the brain literature itself is MEASURED in vivo (Diekelmann-Born, Wilson-McNaughton, Girardeau et al., Rolls hippocampus review).
- frob_ratio=12.63 is MEASURED on this cell at smoke 2026-06-27T22:16:41Z; per_arm metrics path absolute = `d:/AI/hd-instrument/data/exp_cyclic_sws_rem_eta_schedule_v1_smoke/metrics.json`.

---

## Citations (verified count: 6 brain-physiology + 2 substrate-internal MEASURED)

1. Diekelmann S, Born J. The memory function of sleep. Nature Reviews Neuroscience 11:114-126 (2010). [SWS/REM cycling consolidation]
2. Stickgold R. Sleep-dependent memory consolidation. Nature 437:1272-1278 (2005). [cycle-rate-dependent consolidation]
3. McClelland JL, McNaughton BL, O'Reilly RC. Why there are complementary learning systems in the hippocampus and neocortex. Psychological Review 102:419-457 (1995). [CLS hippocampal-cortical replay theory]
4. Wilson MA, McNaughton BL. Reactivation of hippocampal ensemble memories during sleep. Science 265:676-679 (1994). [replay paradigm]
5. Girardeau G, Benchenane K, Wiener SI, Buzsaki G, Zugaro MB. Selective suppression of hippocampal ripples impairs spatial memory. Nature Neuroscience 12:1222-1223 (2009). [ripple-density × behavioral recall]
6. Rolls ET. The mechanisms for pattern completion and pattern separation in the hippocampus. Frontiers in Systems Neuroscience 7:74 (2013). [CA3 attractor / pattern-completion lit support for Option A and B]
7. SUBSTRATE-MEASURED: `d:/AI/hd-instrument/data/exp_cyclic_sws_rem_eta_schedule_v1_smoke/metrics.json` (frob_ratio=12.63, alpha=0.0488, snr=4.53).
8. SUBSTRATE-MEASURED: `d:/AI/hd-instrument/hdlab/continual.py` `replay_cycle` primitive proven-bound docstring (atom 588 — +0.57 drift reduction).

---

## Hand-off pointer

Cell-author (exp_dev) should base the redesign on `experiments/exp_cyclic_sws_rem_eta_schedule_v1.py` lines 312-360 (run_replay_arm) — the `replay_cycle` call already takes `(keys, values)` in the right layout. The required surgical changes:
1. In `build_class_data` replace per-class one-hot keys with `M` independent bipolar random keys (drop the `train_y` class structure; keep `M = N_CAT * N_TRAIN = 500` at smoke for compute parity).
2. Replace `heldout_acc_via_proto_match` with `assoc_recall_top1(W, keys_noisy, values)` that computes `cosine(W @ k_i', v_j)` and reports argmax==i rate plus top-5.
3. Update HARD-PASS thresholds to those listed above (key change: baseline band shifts from [0.20, 0.70] to [0.30, 0.70]).
4. Update CONFIG_VERSION and EXPECTED_ARMS to reflect "associative_recall_readout" labels.
5. Cardinality unchanged (5 arms × 1 seed at smoke).

Pre-reg path proposal: `preregs/2026-06-27_cyclic_sws_rem_eta_schedule_v2_associative_recall_readout.md`.
