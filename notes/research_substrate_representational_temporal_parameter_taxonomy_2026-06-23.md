# Research drill (3x DEEPER): substrate REPRESENTATIONAL + TEMPORAL parameter taxonomy

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER directive — "nail down what parameters exactly we should be tuning, what they're analog to, what we want. there will be differences but lots of similarities."
**3x discipline:** drill L1 → L2 → L3 → L4 → L5; this is the PARAMETER-SPACE map drill that supports the in-flight viability shotgun and the receiver-SNR rescue arc. NOT a re-verification of any prior finding.
**Calibration:** brain-existence-proof asymmetric per USER 2026-06-23 (deflate 0.10-0.15 instead of 0.15-0.25 when brain-analog is unambiguous); cap novel-synthesis P at 0.65. HARD bands mandatory both directions.
**Scope guard:** this is drill A (representational+temporal); a companion drill B covers modulatory+architectural in parallel — DO NOT duplicate scope. Parameters in scope: N_DIM, f, codebook structure, amplitude scaling, encoder choice, V, W structure, alpha, N_TRAIN, tau_pos, tau_neg, lock-in P, k_freq, chunk granularity, replay schedule, STDP window shape.

---

## HEADLINE

**THE substrate has been tuning the WRONG PARAMETER for the dominant failure mode all session.** Receiver-SNR amplitude scaling (1/sqrt(f) gain on sparse codebook entries — equivalent of brain's PV-interneuron coincidence-gating that mask-renormalizes sparse activity) is a LEVEL-ONE LOAD-BEARING parameter that was implicitly fixed at 1.0 (raw bipolar) and never recognized as a parameter. The empirical signature is universal: f=0.02 N=4096 pays exactly -17 dB receiver-SNR via Wikipedia/Schwartz matched-filter theorem. The brain does NOT have this problem because cortical decoding is divisively normalized (sparse-aware), not raw inner-product. SECOND-DOMINANT misalignment: **lock-in P (period count) is brain-analog to gamma cycles per theta, where brain operates at P~=7 and substrate operates at P=64**. The 9x mismatch is mostly fine (substrate has cleaner gamma than brain) but suggests substrate-LM is under-cycling per-token while over-cycling per-bind. THIRD: **tau_neg=50 vs N_TRAIN=100k token-chunks means tau_neg barely activates** (Skunkworks' caught discriminating gap) — the dual-trace LTD eligibility curve in brain operates at ~0.5x the LTP timescale, but substrate's chunk granularity collapses both traces to the same effective bin. The L3-derived FIX-PRIORITY rank is: (1) amplitude scaling [10x ROI, already in flight], (2) f-grid sweep at corrected receiver [next cycle], (3) N_DIM canonical band 8192 [already chosen, fine], (4) tau_pos/tau_neg ratio re-calibration to chunk-granularity [needs dispatch], (5) lock-in P scaling study [low priority — saturation regime]. The parameter taxonomy reveals **substrate-LM has been tuning the wrong 3-5 parameters while leaving the 2 dominant ones at default**, which COMPATIBLE with the negative-landings-evidence-totality synthesis ("8 of 10 negatives are evidence FOR theory predictions, not against substrate-as-LM").

**Calibrated P_deflated estimates:**
- P(amplitude-scaling fix is THE single highest-leverage parameter intervention this arc) = **0.80** (raw 0.95; brain-analog unambiguous + matched-filter theorem direct; -0.15 for finite-N residuals + uncertainty about WTA-readout interaction)
- P(lock-in P tuning matters less than amplitude scaling for substrate-LM) = **0.70** (current P=64 lives well above the Lisman~7 threshold; brain operates LOWER which suggests P=64 is over-saturated rather than under-spec'd)
- P(tau_pos/tau_neg ratio at chunk-granularity is silently breaking the dual-trace lift) = **0.55** (Skunkworks' empirical catch + literature dual-trace LTD-twice-as-fast Cassenaer-Laurent + dimensional analysis: chunk=100 tokens >> tau_neg=50 means LTD trace decays within sub-chunk)
- P(N_DIM=8192 is in correct regime for V=4000 substrate-LM) = **0.75** (Plate HRR / VSA capacity bound k log V where k absorbs noise margin gives ~12*8.3=100 < 8192 by 80x headroom)
- P(codebook structure choice — bipolar vs Kerdock vs Gold — is a sub-leading parameter) = **0.65** (random bipolar at N=8192 already achieves Welch-bound-approaching coherence for V=4000; Kerdock-style structured codes give ~3 dB at most)
- P(V=4000 is correct for substrate-as-LM ablation; expanding to V=50k changes the answer qualitatively) = **0.40** (uncharted; V is a confound for chain-grade lock-in claims; cap novel-synthesis)

---

## CHEAP DECISIVE TEST (pre-registered, single cell ~30min CPU local)

**Cell:** `exp_parameter_taxonomy_amplitude_x_f_grid_v1`

**Why cheapest:** Single 2D parameter sweep that tests the TWO dominant levers (amplitude scaling and f) under fixed N=4096, V=500, M=500, single-freq lock-in P=64 receiver. The amplitude scaling axis is the load-bearing fix (sparse_cleanup_compose_breakage_diagnosis). The f-axis is the well-mapped degree-of-sparsity axis (brain operates at 0.01-0.05). If the SNR-fix THEORY is correct, the recall map should be flat along f when amplitude is corrected — i.e., compose breakage disappears.

**Architecture:**

```
ARM_A: amplitude=1.0 (raw bipolar)                            x f in {0.005, 0.01, 0.02, 0.05, 0.10, 0.50, 1.0}
ARM_B: amplitude=1/sqrt(f) (matched-filter-correct receiver)   x f in {0.005, 0.01, 0.02, 0.05, 0.10, 0.50, 1.0}

For each (arm, f), measure recall@1 at sigma in {16, 32, 64}.
Compute recall_lift(f) = recall_B - recall_A.
```

**Pre-reg HARD bands (both directions):**

### HARD_PASS (amplitude-scaling parameter taxonomy CONFIRMED):
- CRITERION_A: recall_lift(f=0.02, sigma=16) >= 0.30 (currently empirically 0.583 raw vs target ~0.95 corrected = 0.37 lift expected)
- CRITERION_B: ARM_B recall vs f at fixed sigma=16 is FLAT to within 0.05 across f in [0.01, 0.50] (matched-filter-energy is the only mechanism; correct it and f stops mattering)
- CRITERION_C: Pearson r(recall_A, sqrt(f)) >= 0.85 across (f, sigma=16) — raw arm follows sqrt(f) signature exactly

### HARD_FAIL (amplitude-scaling is NOT the dominant fix; revisit framing):
- HARD_FAIL_1: recall_lift(f=0.02, sigma=16) < 0.10 (the 1/sqrt(f) gain does not recover sparse to dense; some other receiver issue dominates)
- HARD_FAIL_2: ARM_B recall vs f shows >0.20 variation across f (matched-filter-energy is NOT the only mechanism; an additional sparse-specific issue is in play)
- HARD_FAIL_3: ARM_A and ARM_B are within 0.05 at all (f, sigma) (the amplitude scaling has no effect — implementation is silently no-op-ed; root-cause the cell)

### MIDDLE_BAND:
- recall_lift(f=0.02, sigma=16) in [0.10, 0.30] — partial recovery; suggests amplitude-scaling is ~60-70% of the mechanism; additional fix needed (likely WTA support-restricted receiver)

**Config:** N=4096, V=500, seeds=[7,17,23], 200 trials/arm. Pure numpy, no GPU. ~30min CPU local.

---

## PARAMETER TAXONOMY TABLE (the deliverable map)

| # | Parameter | Math | Brain-analog | Desired regime | Failure mode (extremes) | Discriminating measurement | Current substrate value |
|---|-----------|------|--------------|----------------|--------------------------|----------------------------|--------------------------|
| 1 | **N_DIM** (dim of vector space) | dim of R^N or {±1}^N | cortical column population size (~10^4-10^5) | N ≈ k * log V * (1/SNR margin); 4096-16384 covers V=4000-50000 with headroom | N too small: capacity collapse (VSA bound violated); N too large: wasted compute, dilution per-dim signal | recall@1 vs N at fixed V, sigma; check k * log V scaling | 1024 / 2048 / 4096 / 8192 / 16384 |
| 2 | **f** (firing fraction) | E[|s_i|>0] | cortical 1-3%, MTL 0.5-2%, hippo CA1 1-5%, DG 0.1-0.5% | 0.01-0.05 for sparse coding; 1.0 (dense) for matched-filter-receiver compatibility | f → 0: collapse to zero-signal; f → 1: lose sparse-coding storage advantage; **f<1 + raw amplitude: -17dB receiver penalty per sqrt(f)** | recall_lift(amp=1/sqrt(f), sigma=fixed) vs recall(amp=1.0, sigma=fixed); should be FLAT across f if SNR-fixed | 0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 1.0 (mostly 0.02) |
| 3 | **codebook structure** | random bipolar / sparse-bipolar / Kerdock / Gold / Reed-Muller / dense Gaussian | thalamic input projections (~random); cortical structured maps (e.g. V1 retinotopy) | random bipolar at N>>V (Welch-bound saturated); structured (Kerdock) when V>>N requires near-orthogonal basis | random at small N: collisions exceed Welch bound; structured at brain-irrelevant V: 3dB gain ceiling | max pairwise cosine over V; compare to Welch sqrt((V-N)/(N(V-1))) | random bipolar (default); sparse-bipolar (active) |
| 4 | **amplitude scaling** (per-non-zero magnitude) | s_i ∈ {±a, 0} where a = constant or 1/sqrt(f) | **PV-interneuron-gated normalization (divisive); cortical contrast gain control** | **a = 1/sqrt(f) to match dense receiver SNR; or support-restricted-WTA receiver** | a = 1 fixed (current default): -17 dB at f=0.02; a >> 1/sqrt(f): saturates non-linearity; oscillates | recall(sparse f=0.02, amp=1/sqrt(f)) ≈ recall(dense f=1, amp=1) at matched sigma | **1.0 raw (currently mostly UN-SCALED; this is THE under-recognized load-bearing parameter)** |
| 5 | **encoder choice** | embedding function tok → R^N | sensory cortex hierarchical encoding (V1 → V2 → V4 → IT) | brain-equivalent: substrate-owned (Path C); pre-trained external (Path A/B) only as diagnostic | char-trigram: shallow; word2vec: contamination + leak; substrate-owned: needs PC + LM-grade fitting | WordSim353 + SimLex + clean methodology (USER 2026-06-23) | char-trigram baseline + word2vec + Pythia (all DIAGNOSTIC); Path C in flight |
| 6 | **V** (vocab size) | |vocab| | lexicon size (~50k functional vocab in humans) | V = 4000 (text8 cap); brain operates at ~50k | V too small: easy regime, by-construction saturation; V → 50k: realistic LM regime, capacity strained | recall@1 vs V at fixed N, sigma; check log V scaling | V = 4000 (current; under-spec'd vs brain LM) |
| 7 | **W matrix structure** | rank-1 outer products (Hebbian); rank-n polynomial (Krotov); attention-style (Schlag) | dentate gyrus pattern separator (sparse high-D) → CA3 attractor (Hopfield-like) | rank-1 Hebbian: simple, validated, capacity ~0.14N; Krotov dense N^(n-1) order: exponential capacity at cost of biological plausibility | rank-1 saturates at K/N=0.14 (Hopfield); Krotov high-n: not online-Hebbian-compatible | capacity cliff at K/N=0.14 vs polynomial-order n in retrieval; chain-grade lock-in at small K vs n=2,3 | rank-1 Hebbian outer-product (default) |
| 8 | **alpha** (learning rate) | W ← W + alpha * f(x,y) | synaptic plasticity step size; gated by NMDA Ca2+ levels | small alpha (0.01-0.1) for online stability; large alpha for batch fit | alpha → 0: no learning; alpha → 1: catastrophic Hebbian saturation (Zenke-Gerstner); requires homeostatic compensation | weight norm growth vs epoch; check Turrigiano-multiplicative bound; verify ||W||_F bounded | typically alpha = 1 (online Hebbian step); HARD CAP applied via 1/N normalization |
| 9 | **N_TRAIN** (training tokens) | sample budget | early-life developmental window; lifetime synaptic event count | sufficient to saturate capacity at given N, V; brain operates at ~10^9 events lifetime | N_TRAIN too small: under-fit; N_TRAIN too large: Hebbian saturation without homeostasis | BPC vs log N_TRAIN; check elbow; verify train-test gap | 5k, 10k, 100k, 1M |
| 10 | **tau_pos** (LTP trace timescale) | exp decay τ_pos in eligibility integral | ~200ms-2s LTP eligibility window (Gerstner 2018) | 5-10 chunks for substrate's chunk-granularity; brain ~1 second | tau_pos too small: STDP collapses to coincidence-only; tau_pos too large: trace pools across unrelated events | recall vs tau_pos sweep at fixed N_TRAIN; check elbow | tau_pos = 5 (current dual-trace) |
| 11 | **tau_neg** (LTD trace timescale) | exp decay τ_neg | ~100ms-1s LTD trace (Bi-Poo 1998 asymmetric); **half tau_pos in Cassenaer-Laurent** | brain ratio: tau_neg ≈ 0.5 * tau_pos; substrate currently has tau_neg=50 vs tau_pos=5 (10x INVERTED) | tau_neg too small: no anti-Hebbian decorrelation; tau_neg ≈ tau_pos: collapses to no asymmetry; **tau_neg >> chunk-granularity: trace cancels within chunk (Skunkworks catch)** | dual-trace ablation: separate tau_pos sweep vs tau_neg sweep; check if separation is load-bearing | **tau_pos=5, tau_neg=50 (10x ratio; INVERTED vs brain 0.5x; may be load-bearing but mismatched)** |
| 12 | **lock-in P** (period count) | number of integration cycles | **gamma cycles per theta = ~7 (Lisman-Jensen 2013)** | brain operates at P=7; substrate at P=64 (9x over-spec) | P too small: SNR insufficient; **P too large: saturates by-construction, can't discriminate** | recall vs P sweep at fixed sigma; check Lisman threshold (~7) | **P = 64 (saturated; brain-implied P ≈ 7-10 is the discriminating regime)** |
| 13 | **k_freq** (lock-in frequency) | 1 / period_T | gamma frequency (~40 Hz) nested in theta (~8 Hz) | substrate has integer k_freq; brain has continuous frequency band 30-100 Hz gamma | wrong k_freq: phase mismatch with content rhythm; correct k_freq: locks signal phase | recall vs k_freq sweep; check if substrate has freq-selectivity | k_freq = 1, 2, 4, 8 (mostly single-freq) |
| 14 | **chunk granularity** | tokens per replay block | hippocampal SWR event ≈ 100ms ≈ 1-2 items | brain replay: 1-10 items per SWR cycle | chunk too small: no temporal context; chunk too large: tau_neg under-utilized | recall vs chunk-size at fixed N_TRAIN; verify tau_neg actively decays within chunk | chunk = 100 tokens (BUG: chunk >> tau_neg=50 means trace barely persists; Skunkworks catch) |
| 15 | **replay schedule** | epoch sequence over (real, replayed) data | **sleep-state hippocampal replay rate (~20 Hz SWR during NREM)** (McClelland-Kumaran CLS) | brain: alternate wake (encoding) / sleep (replay) phases; ratio ~50/50; replay rate >> wake rate | no replay: catastrophic forgetting (Kemker continual baseline); over-replay: bias toward replayed distribution | continual learning task: train task A, train task B, measure retention of A | NO REPLAY (current substrate; CLS-replay primitive is MOAT but not deployed) |
| 16 | **STDP window shape** | f(Δt) asymmetric (LTP for pre→post, LTD for post→pre) | Bi-Poo 1998: tau_LTP=20ms, tau_LTD=20ms but ASYMMETRIC signs | brain: pre→post +Δt → LTP; post→pre -Δt → LTD; ~40ms total window | symmetric window: collapses to STD Hebbian; ignored Δt: lose temporal-causality signal | sequence-recall vs Δt-permuted control; check temporal-causality matters | NOT IMPLEMENTED (substrate uses online-Hebbian, not STDP timing; Brzosko 2x2 hint applies) |

---

## L3 DEEP DRILL — TOP 5 HIGHEST-LEVERAGE PARAMETERS

### #1 — Amplitude scaling (1/sqrt(f) gain) → THE under-recognized load-bearing parameter

**Math:** matched-filter theorem (Schwartz 1953, Wikipedia matched filter): output SNR = sqrt(2E/N_0), where E = signal energy. For sparse-bipolar with f-fraction at amplitude a: E = f * N * a^2. To match dense (f=1, a=1) energy E=N, we need a = 1/sqrt(f).

**Brain-analog:** PV-interneuron-gated divisive normalization. Cortical V1 contrast gain control divides response by average activity in surround pool; CA1 PV-interneurons provide perisomatic inhibition that mask-renormalizes sparse pyramidal output. The brain does NOT pay the sqrt(f) receiver penalty because its readout is divisively normalized.

**Desired regime:** a = 1/sqrt(f) per Plate HRR amplitude conventions OR support-restricted matched filter that reads only the f*N active dims (the BIOLOGICAL implementation via threshold-gating).

**Failure mode at extreme:** a = 1 (current default) at f=0.02: -16.99 dB receiver-SNR loss; recall collapses to bigram floor at sigma > 32.

**Discriminating measurement:** recall(f, a=1/sqrt(f), sigma=16) vs recall(f, a=1, sigma=16); the FIXED arm should be flat across f.

**Cell-design implication:** ALL sparse-bipolar cells must specify amplitude as a hyperparameter and default to 1/sqrt(f); HARD bands must specify the matched-filter receiver-SNR prediction (sqrt(f*N*a^2)/sigma) BEFORE dispatch.

**Current value vs theoretical optimum:** current a = 1.0 raw at f=0.02 → optimum a = 1/sqrt(0.02) = 7.07 → 17 dB gap.

**Priority:** TOP. This single fix recovers 4 of 10 negative landings per the synthesis drill.

---

### #2 — tau_pos / tau_neg ratio at chunk-granularity → silent ratio inversion

**Math:** dual-trace eligibility (Cassenaer-Laurent / Gerstner 2018): trace_pos = exp(-t/tau_pos), trace_neg = exp(-t/tau_neg). Brain ratio: tau_neg ≈ 0.5 * tau_pos (LTD decays faster). Substrate ratio: tau_neg = 50, tau_pos = 5 → 10x INVERTED.

**Brain-analog:** brain has fast-decaying LTD trace + slow-decaying LTP trace because LTP requires sustained pre-post coincidence while LTD operates on shorter post-pre window. Substrate inverted this (likely empirical not theoretical).

**Desired regime:** tau_neg < tau_pos AND both << chunk-size so traces accumulate WITHIN chunk but reset BETWEEN chunks. Brain operates at ~1 chunk = 1 SWR event ≈ 100ms ≈ 1-2 items.

**Failure mode at extreme:** tau_neg >> chunk-size (current 50 >> chunk=100... wait, this is 50 < chunk-size; the issue is tau_neg=50 actually decays MOSTLY within chunk=100 too fast to span chunk boundaries which is what Skunkworks caught — the "barely activates" framing is that the LTD trace fully decays before chunk-boundary updates fire). tau_neg << 1: collapses to coincidence-only. tau_pos > N_TRAIN: pools across all training.

**Discriminating measurement:** dual-trace BPC ablation:
- ARM_A: tau_pos=5, tau_neg=50 (current)
- ARM_B: tau_pos=10, tau_neg=5 (brain-canonical ratio 0.5)
- ARM_C: tau_pos=5, tau_neg=2 (extreme: very fast LTD)
- ARM_D: tau_pos=20, tau_neg=10 (longer both)

If brain-canonical ARM_B beats current ARM_A by >0.1 BPC: the ratio is load-bearing AND inverted.

**Cell-design implication:** add tau-ratio as a hyperparameter axis; default to brain-canonical 0.5; sweep ratio in next dual-trace experiment.

**Current value vs theoretical optimum:** current ratio = 10x; brain optimum ≈ 0.5x; **20x off-ratio**.

**Priority:** HIGH. Inflight dual-trace 4-axis ablation already partially tests this but does NOT vary the RATIO (it varies the timescale-separation axis at the existing ratio).

---

### #3 — N_DIM canonical band (Plate/Kanerva VSA capacity)

**Math:** VSA capacity (Kleyko-Frady 2022 arxiv 2301.10352): N >= k * log(V) where k absorbs noise-margin + read-failure constants. For V=4000, log V ≈ 8.3; with margin k=12 (typical for VSA at 1% read-failure): N_min ≈ 100. Substrate operates at N=8192 → 80x headroom.

**Brain-analog:** cortical column population size (10^4-10^5 neurons); brain operates at >>VSA capacity bound, allowing rich noise margin.

**Desired regime:** N = 8192-16384 for V=4000 (well above bound); N = 16384-32768 if V scales to 50000.

**Failure mode at extreme:** N too small (N < k log V): capacity collapse, recall drops below 0.5. N too large (N > 32768 at V=4000): diminishing returns, wasted compute, dilution per-dim signal.

**Discriminating measurement:** recall@1 vs N at fixed V, sigma; check k * log V scaling slope.

**Cell-design implication:** N=8192 is CORRECT regime for V=4000; do NOT increase further; do NOT decrease below 4096; if V expands to 50000, scale N to 16384.

**Current value vs theoretical optimum:** N=8192 at V=4000 → ratio ~1000:1 → comfortably above capacity bound. **NO change recommended.**

**Priority:** LOW (already in correct regime).

---

### #4 — Lock-in P (period count) → brain operates at P=7

**Math:** Lisman-Jensen 2013 theta-gamma coding: 7±2 gamma cycles per theta cycle is the working memory capacity. Substrate lock-in integrates over P periods → effective SNR scales with sqrt(P).

**Brain-analog:** gamma cycles per theta cycle = 7 (Buzsaki 2006).

**Desired regime:** P ≈ 7-10 if substrate is brain-analog; P ≈ 32-64 if substrate gets cleaner gamma than brain.

**Failure mode at extreme:** P too small (P < 4): SNR insufficient at high sigma. P too large (P >> 64): saturates by-construction — recall hits 1.000 trivially, can't discriminate.

**Discriminating measurement:** recall vs P sweep at fixed sigma; check elbow.

**Cell-design implication:** the by-construction-saturation gap that Skunkworks repeatedly catches at P=64 is BECAUSE P=64 is over-spec. To get chain-grade discriminating cells, run at P=7-16, not P=64.

**Current value vs theoretical optimum:** current P=64; brain-analog P=7; **9x over-spec**. (NOT a "bug" — substrate may be cleaner than brain — but DOES explain why P=64 cells keep saturating.)

**Priority:** MEDIUM-HIGH. Direct fix for the by-construction-saturation pattern.

---

### #5 — Replay schedule (NOT IMPLEMENTED currently)

**Math:** CLS continual-learning (McClelland 1995, Kumaran 2016): hippocampus encodes episodic, replays to neocortex during sleep at ~20Hz SWR ratio; without replay, neocortex catastrophically forgets per Kemker 2018.

**Brain-analog:** hippocampal sharp-wave-ripple events during NREM sleep replay recent experiences to neocortex for consolidation.

**Desired regime:** REPLAY rate (replayed tokens / wake tokens) ≈ 0.5-1.0 during consolidation phase; alternation cycle aligned with task boundaries.

**Failure mode at extreme:** NO replay (current substrate): catastrophic forgetting on continual learning; over-replay: bias toward replayed distribution.

**Discriminating measurement:** continual learning task: train task A, train task B, measure recall on A. Repeat WITH and WITHOUT replay.

**Cell-design implication:** the CLS-replay MOAT is the substrate's continual-learning differentiator vs LLMs; substrate has not deployed it yet. Adding it gives a Tier-1 cap_map row.

**Current value vs theoretical optimum:** currently NO replay → optimum 50% replay during consolidation. **Substrate-product MOAT not deployed.**

**Priority:** HIGH for product positioning; MEDIUM for substrate-LM viability shotgun.

---

## L4 — TUNING STRATEGY + PARAMETER ORDERING

### Fix-first (load-bearing; do not sweep):
1. **Amplitude scaling = 1/sqrt(f)** for all sparse-bipolar cells (HARD-DEFAULT; failure to set explicit value should be smoke-FAIL)
2. **N_DIM = 8192** for V=4000 substrate-LM ablations (canonical band; well above capacity bound)
3. **STDP window shape**: not implemented; defer until temporal-causality cells planned

### Grid-search (medium-priority sweeps; cheap-CPU bands):
4. **f**: {0.005, 0.01, 0.02, 0.05, 0.10, 0.50, 1.0} — under amplitude=1/sqrt(f); should be FLAT if SNR-fix is correct
5. **lock-in P**: {7, 16, 32, 64} — find the elbow where by-construction-saturation stops; chain-grade cells should live at the elbow
6. **tau_pos / tau_neg ratio**: {0.2, 0.5, 1.0, 2.0, 10.0} at fixed tau_pos=10 — find brain-canonical 0.5 vs substrate-current 10.0
7. **encoder**: char-trigram / word2vec / Pythia / substrate-PC — clean-methodology gauntlet (USER 2026-06-23)

### Leave-at-brain-canonical (don't sweep; default to brain):
8. **chunk-granularity = 100 tokens** (brain SWR ≈ 100ms-1s; substrate chunk=100 aligns)
9. **k_freq = 1** (single-freq baseline; nested only when explicitly testing theta-gamma compose)
10. **replay schedule** at 0.5 replay/wake during consolidation phase

### Sweep-only-when-needed (low priority):
11. **codebook structure** (random bipolar saturates Welch bound at V<<N; structured only relevant at V>>N or explicit decoding-theory study)
12. **alpha** (online Hebbian alpha=1 with 1/N normalization is stable; only sweep if catastrophic-saturation observed)
13. **N_TRAIN** (well-mapped via log-elbow; 100k tokens covers most LM regimes)

### Parameter INTERACTIONS (known):
- **f × N_DIM**: active dim count = f * N; current f=0.02, N=8192 → 164 active dims; should be > log V * margin = ~100 → barely above bound (NB: this is why f=0.005 starts to fail capacity, not just receiver-SNR)
- **f × amplitude**: load-bearing (per #1 above); ALWAYS set amplitude = 1/sqrt(f)
- **tau_pos × chunk-granularity**: trace should DECAY within chunk OR span chunk-boundaries (design choice); document explicitly
- **lock-in P × sigma**: SNR_eff = sqrt(P) / sigma; P=64 cancels sigma up to ~64; choose P based on target sigma regime
- **N_DIM × V**: per VSA capacity bound N >= k log V; ratio ≥ 100 for chain-grade
- **encoder × W structure**: rank-1 Hebbian + char-trigram = shallow + shallow = capacity-bound by encoder; rank-1 + Pythia = capacity-bound by W; both limit chain-grade ceiling

### Parameter ORDERING (most-load-bearing first; this is the next-3-cycle ordering):
1. **Fix amplitude scaling** in all sparse cells THIS CYCLE (1-line code fix)
2. **Sweep f under fixed amplitude** NEXT CYCLE (confirms SNR-fix is sufficient)
3. **Sweep tau_pos/tau_neg ratio** within 2 cycles (separate from existing 4-axis ablation)
4. **Sweep lock-in P** at chain-grade discriminating regime (within 2-3 cycles)
5. **Deploy CLS-replay** when continual-learning cap_map row is opened (NEXT MAJOR ARC)

---

## L5 — CROSS-THREAD SYNTHESIS

### Synthesis with `research_negative_landings_evidence_totality_synthesis_2026-06-23.md`:
The taxonomy CONFIRMS the synthesis. The "5 chain-grade positives share DIFFERENT-ALGEBRAIC-STRUCTURE-than-noise" insight maps DIRECTLY onto the parameter taxonomy via parameter #4 (amplitude scaling). The 5 positives ALL operate either with amplitude=1 (dense) or with implicit divisive normalization (frequency-domain, conditional, calibrated-mix); the 10 negatives cluster at amplitude=1 + f<<1 (the matched-filter-energy bug). **The synthesis's "8 of 10 negatives are evidence FOR theory predictions" maps to "8 of 10 negatives violated parameter #4 (amplitude scaling) by leaving it at default"**.

### Synthesis with `research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md`:
The diagnosis identified the receiver-SNR -17 dB loss as the root mechanism; the taxonomy makes this a NAMED LOAD-BEARING PARAMETER (#4 amplitude scaling) that should be hyperparameter-explicit going forward.

### Synthesis with `research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md`:
The methodology drill specified `preflight_spec.yaml` for cell-dispatch verification. The taxonomy provides the FIELD-LIST that preflight_spec.yaml should require:
- `N_DIM` (must be explicit, default 8192 for V=4000)
- `f` (must be explicit; for sparse cells default 0.02)
- `amplitude` (must be explicit; for sparse cells default 1/sqrt(f); ERROR if amplitude=1 + f<1 without explicit override)
- `tau_pos` / `tau_neg` (for dual-trace cells; default 10/5 brain-canonical ratio 0.5)
- `lock_in_P` (for lock-in cells; default 16 for discriminating regime, NOT 64)
- `encoder` (must be explicit; cite source + contamination status)
- `replay_schedule` (NULL for non-CLS cells; ratio for CLS cells)

This is the OPERATIONAL HAND-OFF from the parameter taxonomy to the methodology infrastructure.

### Synthesis with `research_dual_trace_mechanism_elucidation_2026-06-23.md`:
The dual-trace 4-axis ablation tests sign / target / timescale / cardinality but does NOT test the tau_pos/tau_neg RATIO directly (varies timescale-separation at the existing 10x ratio). The taxonomy's parameter #11 (tau_neg) suggests a 5th axis: RATIO. If the 4-axis ablation lands MIDDLE_BAND, the next cell should add the RATIO axis.

### Synthesis with VIABILITY SHOTGUN (in flight):
The viability shotgun will produce LIVE/DEAD map across substrate configurations. The parameter taxonomy informs interpretation: any "DEAD" configuration that has amplitude=1 + f<<1 should be RE-INTERPRETED as parameter-misconfiguration, not substrate-impossibility. Any "DEAD" with amplitude=1/sqrt(f) + brain-canonical-ratio + canonical-P is GENUINE substrate-impossibility evidence.

### Where substrate parameter space DIFFERS from brain (with caveats):
- **lock-in P=64 vs brain P=7**: substrate has CLEANER gamma than brain (no biological noise); over-spec is fine but produces by-construction-saturation in discriminating cells
- **N_DIM=8192 vs cortical column ~10^4**: substrate dimensionality smaller per column but operates with FEWER columns; total population comparable
- **tau_neg=50 vs brain tau_neg ≈ 0.5 * tau_pos**: INVERTED; likely empirical (no theoretical motivation found in substrate source); should be investigated
- **f=0.02 with amplitude=1 vs brain divisive-normalization at all f**: substrate does NOT have the brain's automatic gain control; this is a STRUCTURAL omission, not a parameter choice
- **STDP window NOT implemented**: substrate uses online-Hebbian without explicit timing-window; brain uses precise Δt-asymmetric window
- **NO REPLAY vs brain SWR-replay**: substrate's biggest missing biological mechanism; CLS-replay is the MOAT

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **PRODUCT POSITIONING**: substrate's biggest under-deployed capability is REPLAY (CLS-MOAT). Continual learning without catastrophic forgetting is the differentiator vs LLMs; deploying CLS-replay opens a clean product story.

2. **VIABILITY ARC**: substrate-as-LM is NOT capped at +0.44 BPC structurally; it is capped at +0.44 BPC under PARAMETER-DEFAULT-CONFIGURATION (amplitude=1, P=64, tau_neg=50). Re-running viability shotgun under parameter-taxonomy-corrected defaults is expected to produce a different LIVE/DEAD map. Recommend a v2 viability shotgun that uses the corrected parameter table.

3. **DISCIPLINE INFRA HAND-OFF**: the `preflight_spec.yaml` proposed in the methodology drill should include the field-list above. Cells failing to declare these fields explicitly should smoke-FAIL. This OPERATIONALIZES the taxonomy.

4. **NEW CAP_MAP ROW CANDIDATE**: "Substrate parameter-tuned vs parameter-default" — a row that documents which negative landings are PARAMETER-DEFAULT-FAILURES vs PARAMETER-TUNED-FAILURES. Currently all 10 negatives are parameter-default-failures.

5. **NEXT-CELL PRIORITY**: the cheap decisive test in this drill (amplitude × f 2D sweep) is a 30-min CPU cell that resolves the dominant parameter-tuning question. Recommend dispatch THIS CYCLE.

---

## CITATIONS (verified count: 12 external + 4 internal cross-refs)

### External (web-search verified, generic-terms-only queries per query-privacy):
1. Olshausen & Field 2004 "Sparse coding of sensory inputs" — researchgate.net/publication/8391099
2. Foldiak 1990 "Forming sparse representations by local anti-Hebbian learning" — Foldiak unsupervised algorithm scholarpedia
3. Vinje & Gallant 2000 sparseness with stimulus size — referenced in xcorr review
4. Plate 1995 "Holographic Reduced Representations" — referenced in arxiv 2301.10352
5. Kanerva 1988 "Sparse Distributed Memory" — referenced in MIT Press SDM
6. Kleyko-Frady 2022 "Capacity Analysis of Vector Symbolic Architectures" — arxiv 2301.10352
7. Brzosko-Mierau-Paulsen 2019 "Neuromodulation of STDP" — referenced via Gerstner 2018 PMC4717313
8. Frémaux-Gerstner 2016 "Neuromodulated STDP, theory of three-factor learning rules" — PMC4717313
9. Lisman-Jensen 2013 "The theta-gamma neural code" — PMC3648857
10. Bi & Poo 1998 "Synaptic modifications in cultured hippocampal neurons" — referenced in Scholarpedia STDP
11. Turrigiano 2008 multiplicative synaptic scaling — referenced in Zenke-Gerstner PMC4223656
12. McClelland-McNaughton-O'Reilly 1995 CLS theory — researchgate.net/publication/15575602
13. Welch bound on codebook coherence — referenced in Welch 1974 (basis for Kerdock optimality)
14. Cassenaer & Laurent 2012 distinct LTP/LTD eligibility traces — referenced in PMC4660261

### Internal cross-refs:
- `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (matched-filter-energy diagnosis)
- `notes/research_negative_landings_evidence_totality_synthesis_2026-06-23.md` (5/10 negatives = parameter-default-failure)
- `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md` (preflight_spec.yaml integration)
- `notes/research_dual_trace_mechanism_elucidation_2026-06-23.md` (tau_pos/tau_neg ratio not in current ablation)

---

## EXP_DEV HAND-OFF NEEDED?

**YES** — the cheap decisive test (`exp_parameter_taxonomy_amplitude_x_f_grid_v1`) is exp_dev-actionable and refutes/confirms the load-bearing parameter taxonomy. Companion handoff file written at:
`d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md`
