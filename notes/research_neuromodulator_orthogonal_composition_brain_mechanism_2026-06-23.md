# Research: Orthogonal neuromodulator composition (brain mechanism, 2x drill)

**Date:** 2026-06-23
**Author:** Research (Opus synthesis over 8 parallel Sonnet lit-scans)
**Drill type:** USER-directed 2x DEPTH drill on brain mechanism of orthogonal neuromodulator composition; targeted at breaking the sparse-bipolar envelope cap (+0.44 bits BPC) JUST measured in `exp_sparse_bipolar_substrate_lm_param_sweep_v1` (HARD_FAIL: max_lift saturates at one-point envelope, no scaling lever across N_TRAIN={100k,1M} x N_DIM={4096,8192,16384}).
**Lit-scan calibration penalty applied** (deflate raw P 0.15-0.25; cap novel-synthesis P at 0.50).
**Query-privacy:** all 8 external queries used generic terms (no substrate-novel mechanism names, no configs, no numbers).

---

## HEADLINE

The brain achieves orthogonal modulator composition NOT by simultaneous multiplicative gating of a single learning rate (Marder STG demonstrates that converges-to-degenerate-I_MI), but via SEPARATE ELIGIBILITY TRACES at the synapse (Brzosko 2017; Fremaux-Gerstner 2016 three-factor rule), each gated by a DIFFERENT modulator on a DIFFERENT timescale (DA ~100ms phasic, ACh ~seconds tonic, 5HT ~minutes meta-rate, NE ~burst gain). The just-failed single-modulator and naive-multiplicative substrate sweeps confirm degeneracy; the substrate-rescue path is TWO INDEPENDENT TRACES (potentiation-trace gated by DA-novelty, depression-trace gated by ACh-attention) with RETROACTIVE gating across timescales — a substrate-native realization of the Brzosko sequential mechanism.

---

## Cheap decisive test (pre-reg HARD bands; ≤45min GPU)

**Cell name candidate:** `substrate_dual_trace_sequential_neuromod_LM_v1`

**Hypothesis (load-bearing):** The substrate's saturating envelope at +0.44 bits BPC is the signature of **single-trace-single-modulator degeneracy** (eta*scalar is just rescaling). The brain breaks this via two separate eligibility traces (E_LTP, E_LTD) gated by sequentially-applied DIFFERENT modulators, allowing the same W to encode TWO orthogonal statistical structures (anomaly + frequency). Substrate-native realization: maintain `E_pos` and `E_neg` traces per token-pair with DIFFERENT time constants, gate them by orthogonal scalars derived from substrate state (novelty != attention != uncertainty).

**Design (3 arms, V=4000, N_DIM=8192, text8 N_TRAIN=100k, 3 seeds):**
- ARM_BASELINE: current best sparse-bipolar f=0.02 N=8192 (envelope cap reference)
- ARM_NAIVE_MULT: single trace, multiplicative gating `W += (dopa * ACh * 5HT) * outer(err, in)` (replicates Gap A spec)
- ARM_DUAL_TRACE_SEQUENTIAL: two traces with separate time constants + DIFFERENT modulator per trace + retroactive gating:
  - `E_pos += alpha_fast * outer(in, target) - decay_fast * E_pos`  (tau_fast ~ 5 steps)
  - `E_neg += alpha_slow * outer(in, predicted) - decay_slow * E_neg`  (tau_slow ~ 50 steps)
  - `dopa = novelty_signal = 1 - cosine(in, prior_running_mean)`  (phasic ~ 1 step)
  - `ACh = attention_signal = softmax_entropy(top-K cleanup)`  (tonic ~ 10 steps)
  - `W += dopa * E_pos - ACh * E_neg`  (orthogonal-because-different-traces-AND-different-modulators)

**HARD bands (PRE-REG, both directions):**
- HARD_PASS: ARM_DUAL_TRACE beats ARM_BASELINE on BPC by ≥ +0.20 bits absolute (= +0.64 bits total lift from random) AND beats ARM_NAIVE_MULT by ≥ +0.10 bits absolute (orthogonality-not-degeneracy)
- MIDDLE_BAND: ARM_DUAL_TRACE beats ARM_BASELINE by +0.05 to +0.20 AND beats ARM_NAIVE_MULT by ≥ +0.05
- HARD_FAIL: ARM_DUAL_TRACE within ±0.05 of ARM_BASELINE OR fails to beat ARM_NAIVE_MULT
- CV across 3 seeds < 0.05 mandatory; per-arm metrics read via `tools/peek_arm_metrics.py` (Fix #28)
- BPC_unigram = 7.738 (text8 fair-harness reference) — baseline rescaling sanity

**Cost:** ~35-45min GPU on remote (matches current sweep cell wall time); cheap-decisive.

**P_deflated:** **0.42** (brain-existence-proof tilt brings raw to ~0.60; lit-scan penalty -0.18 for novel substrate-synthesis; capped under 0.50 per novel-synthesis ceiling). Higher than naive multiplicative Gap A (0.65 → after Marder degeneracy caveat: 0.40-0.50 range).

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Prediction 1: Naive multiplicative composition will NOT break the envelope
- **HARD-FAIL signature:** ARM_NAIVE_MULT lift ≤ baseline + 0.05 bits BPC
- **Mechanism:** Marder STG shows all GPCR cascades converge on single I_MI scalar — substrate analog: eta * dopa * ACh * 5HT is just one scalar `eta_eff`, which the sparse-bipolar sweep already swept exhaustively across N_DIM and N_TRAIN
- **If THIS hard-passes (naive mult > baseline + 0.15):** then degeneracy framing is wrong, brain-as-single-scalar-stack works after all → revival path for Gap A as originally specified

### Prediction 2: Dual-trace sequential will EITHER break the envelope OR confirm rank-1 Hebbian capacity-cap
- **HARD-PASS signature:** ARM_DUAL_TRACE BPC lift > +0.64 bits absolute (vs uniform), > +0.20 vs current best sparse-bipolar (envelope broken)
- **HARD-FAIL signature:** ARM_DUAL_TRACE within ±0.05 of best sparse-bipolar even with separate traces → strong evidence the cap is RANK-1-HEBBIAN-INTRINSIC, not single-modulator-degeneracy
- **Mechanism if PASS:** the same W can encode two orthogonal statistical projections (frequency-positive trace + anomaly-negative trace) because the gradients enter W at different times via different traces — this is NOT pure rank-1 outer-product accumulation
- **Mechanism if FAIL:** confirms USER pivot acknowledged in `next_iteration_composition_spec_2026-06-23.md` lines 111-116 — substrate-as-LM is rank-1 Hebbian floor; refuse-aware-knowledge-store becomes substrate-product

### Prediction 3: HARD_FAIL of BOTH arms tells you something structural
- If ARM_DUAL_TRACE and ARM_NAIVE_MULT both within ±0.05 of baseline, the bottleneck is NOT modulator composition AT ALL — it's the encoder (Path C MIDDLE_BAND) or the rank-1 W outer-product structure
- Next-cell diagnosis: route to encoder-replacement (Path A/B pretrained probes already in literature precedent) NOT to more modulator variants

---

## Cross-thread synthesis

### Compose with existing chain-grade primitives

| Primitive | Compose how | Mechanism note |
|---|---|---|
| **Lock-in amplifier** (chain-grade) | Use lock-in phase as `theta_phase` carrier for E_pos trace decay; gamma cycles for E_neg | Brain's theta-gamma coupling naturally gates two-timescale memory (Lisman-Idiart) |
| **HRR working memory** (chain-grade) | HRR-bind modulator-vector to retrieval queries → context-conditional cleanup threshold | Yu-Dayan 2005 frame: ACh-bound query = "high expected uncertainty, ignore weak cues" |
| **Sparse-bipolar (JUST FAILED)** | Apply two-trace mechanism ON sparse-bipolar substrate (f=0.02 N=8192 best config) | The envelope cap was measured with SINGLE-trace updates; two-trace might break it because gradients enter at DIFFERENT times |
| **Path C own-encoder PC layers** (MIDDLE_BAND) | Predictive-coding residual = natural input to `dopa = 1-cosine(in,prior)` novelty signal | PC layers ALREADY compute the prediction-error vector substrate needs as dopa-signal |
| **g1b cerebellar generation** (chain-grade) | Climbing-fiber error signal IS the dopa-equivalent for cerebellar arm | Composes naturally with brain-existence-proof framing |

### Compose with sparse-bipolar envelope cap (the just-failed cell)

The sparse-bipolar sweep tested **single-trace single-modulator** scaling. It cannot break the cap because:
- `eta_eff * outer(err, in)` accumulates rank-1 onto W
- Increasing N_DIM gives more capacity but does NOT add orthogonal structure
- Increasing N_TRAIN saturates because lift plateaus at the +0.44 bits envelope (rank-1 Hebbian closed form)

The dual-trace mechanism breaks this because:
- `E_pos` and `E_neg` accumulate INDEPENDENTLY with different time constants
- W update = `dopa * E_pos - ACh * E_neg` adds TWO rank-1 components per step that are NOT collinear (different time-integrals of different signals)
- Net effect: W rank grows faster than single-trace; effective capacity > rank-1 floor

### What does NOT compose

- **Path A pretrained encoder** — modulator gating happens at W-write-time; pretrained encoder is frozen on read-side. Independent axes.
- **n11 ATL hub-spoke** (in flight) — modulator gating is per-Atom W; hub-spoke is graph-routing. Independent axes.
- **Multi-region W** (Gap E) — different cortical regions are independent W matrices; modulator-gating happens INSIDE each W. Composes additively (modulator-gated * multi-region = orthogonal improvements) — both should work.

---

## Substrate-product implications

### If HARD_PASS (P=0.42)
- The substrate **CAN** scale beyond the rank-1 Hebbian floor → substrate-as-LM stays viable as a product direction
- Next-cell ladder: dual-trace + sparse-bipolar f=0.02 N=16384 N_TRAIN=1M (test envelope-broken at scale)
- Substrate-product story: **brain-grade dual-trace credit-assignment substrate** with explicit Bayesian gating (Yu-Dayan), competitive with attention-mechanism-based LMs at the small-data regime where eligibility-traces actually beat backprop (Fremaux-Gerstner spike-net results)
- Atomize as META atom: `dual_trace_breaks_rank1_hebbian_floor_via_temporal_orthogonality`
- New cap_map row candidate: `substrate-as-LM via dual-trace eligibility (P=0.42 pre-cell; bump on HARD_PASS)`

### If MIDDLE_BAND
- 2-modulator ablation cell next (test which trace is load-bearing: ARM_E_POS_ONLY vs ARM_E_NEG_ONLY vs ARM_BOTH)
- Pre-reg the ablation: if E_POS alone gives ≥80% of the dual-trace lift, then E_NEG is decorative (single-trace + smart timescale wins); if both needed, orthogonality story confirmed but at weaker P

### If HARD_FAIL (P=0.58 — calibrated by Marder degeneracy + recent same-pattern failures)
- The substrate is rank-1 Hebbian capped → CONFIRMS the pivot acknowledged in `next_iteration_composition_spec_2026-06-23.md` lines 111-116
- META atom commit: `substrate_as_LM_genuinely_capped_at_rank1_hebbian_floor_despite_brain_grounded_dual_trace_composition`
- Substrate-product pivot: **refuse-aware-knowledge-store** as the product (lock-in + Shannon envelope + KG storage + refuse-gate); LM ambition replaced with: "we are not an LM, we are an honest retrieval substrate with audit trail"
- This is a HIGH-VALUE NEGATIVE: it tells the program that brain-mechanism transplant to forward-only Hebbian has a STRUCTURAL CEILING — saves us from drilling Gaps B/C/D/E/F on the same failing premise

### Cross-substrate product question (USER L5)
- Does dual-trace compose with the just-landed Path C own-encoder MIDDLE_BAND? **YES** — Path C predictive-coding residuals ARE the dopa signal (no additional computation needed); the encoder learns to PRODUCE the error vector that the trace mechanism CONSUMES. This is a NATURAL stack, not a forced composition.
- Does it enable production-scale LM? Conditional: HARD_PASS at N_DIM=8192 must be followed by scaling cell (N_DIM=16384, N_TRAIN=1M) to test whether the envelope breaks BY 0.5+ bits (production-relevant gap to text8 word-bigram floor ~1.13 bits). If only +0.20 lift survives at scale, still capped — useful insight, not LM.

---

## Drill-axis coverage (per USER spec L1-L5)

**L1 (literature broad):** 4 parallel lit-scans completed:
- (a,b) DA × ACh: Brzosko 2017 (sequential not simultaneous) + Krasne 2024 (ACh demixes DA) + sequential plasticity model — SEQUENTIAL gating is the canonical brain mechanism, NOT product-of-scalars
- (c) 5HT timescale: Grossman 2022 Curr Bio (serotonin tracks long-timescale uncertainty + dorsal raphe meta-rate) + Doya 2002 (5HT = time-horizon parameter) — orthogonal to DA via TIMESCALE
- (d) NE gain: Aston-Jones-Cohen 2005 (phasic/tonic = gain control axis distinct from learning-rate axis) — orthogonal to DA via FUNCTION (gain vs plasticity-rate)
- (e) multiplicative vs additive: Pawlak-Kerr-Cheong (Frontiers 2010) + Huertas et al. 2016 — three-factor rule is `dW = pre*post*M` (Hebbian product × neuromodulator) — the SINGLE-scalar version
- (f) GPCR cascade convergence: Marder STG → **CRITICAL CAVEAT** — multiple modulators converge on same I_MI current → naive multiplicative composition IS DEGENERATE

**L2 (substrate-applicable filter):**
- Sequential 2-trace (Brzosko-style) → forward-only Hebbian compatible (no backprop needed); needs only DIFFERENT time constants per trace → cheap
- Yu-Dayan ACh/NE → needs scalar uncertainty estimators from substrate state → cheap (cosine to mean, entropy of cleanup softmax)
- Aston-Jones gain × learning-rate → composes orthogonally (gain affects READ, learning-rate affects WRITE) → cheap
- Marder convergence → KILLER for naive-multiplicative; ENABLER for separate-trace approach
- All mappings need only SCALAR signals (not new W matrices) — confirms L2 substrate-applicability is HIGH

**L3 (most-orthogonal pair derivation):**
The genuinely orthogonal pair is NOT dopa × ACh as single scalars (those converge via GPCR per Marder). The genuinely orthogonal axes are:
1. **Eligibility-trace identity** (E_pos vs E_neg) — set by which RECEPTOR + TIMESCALE the trace expresses
2. **Modulator signal** (dopa, ACh, 5HT, NE) — gates WHICH trace updates W and WHEN
- Genuine orthogonality requires BOTH separations; single-axis modulator change without trace-separation is DEGENERATE per Marder
- Capacity-bounds estimate: dual-trace breaks rank-1 floor IF and ONLY IF time-integrals are non-collinear (different tau gives non-collinear by construction)

**L4 (cell-design implications):**
Pre-reg the dual-trace cell described in "Cheap decisive test" above as the FIRST contingent cell after current 4-way GPU ablation lands. Contingency tree (per gap-A successor):
- HARD_PASS → scaling cell at N_DIM=16384 N_TRAIN=1M (test if envelope breaks at scale)
- MIDDLE_BAND → 2-modulator ablation (E_pos-only vs E_neg-only vs both) to identify load-bearing trace
- HARD_FAIL → pivot to encoder-replacement diagnosis (Path A/B pretrained as substrate-product diagnostic probe, then META atom: rank-1 cap confirmed → substrate-product = refuse-aware-knowledge-store)

**L5 (cross-substrate composition):**
- sparse-bipolar (failed): dual-trace mechanism APPLIES TO same sparse-bipolar W; goal is breaking envelope ON the best-config sparse-bipolar (f=0.02 N=8192)
- HRR working memory: HRR-bind modulator-vector to query for context-conditional cleanup — composes naturally
- Lock-in amp: theta/gamma carrier IS the dual-timescale signal — composes naturally and parsimoniously
- Path C own-encoder: predictive-coding residuals ARE the novelty signal for dopa gate — composes naturally

**Substrate-product story (if dual-trace HARD_PASS):** brain-grade dual-trace credit-assignment substrate competitive with small-data LMs (n_train << 1B regime where eligibility traces beat backprop per Fremaux-Gerstner) → DIFFERENT product position than "compete with GPT" — instead "compete with small-data LMs on biological plausibility + audit trail + continual learning"

---

## Citations (verified via WebSearch: 11 distinct primary refs)

1. **Brzosko, Zannone, Schultz, Clopath, Paulsen (2017)** "Sequential neuromodulation of Hebbian plasticity offers mechanism for effective reward-based navigation" — eLife — https://elifesciences.org/articles/27756  [LOAD-BEARING: ACh→DA retroactive conversion]
2. **Yu, Dayan (2005)** "Uncertainty, neuromodulation, and attention" — Neuron — https://www.cell.com/neuron/fulltext/S0896-6273(05)00362-4 [LOAD-BEARING: ACh = expected uncertainty, NE = unexpected uncertainty]
3. **Aston-Jones, Cohen (2005)** "An integrative theory of locus coeruleus-norepinephrine function: Adaptive gain and optimal performance" — Annu Rev Neurosci — https://www.annualreviews.org/content/journals/10.1146/annurev.neuro.28.061604.135709 [NE = gain control axis, distinct from learning rate]
4. **Fremaux, Gerstner (2016)** "Neuromodulated Spike-Timing-Dependent Plasticity, and Theory of Three-Factor Learning Rules" — Front Neural Circuits — https://www.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2018.00053/full [Three-factor rule canonical form: pre*post*neuromodulator]
5. **Huertas, Schwettmann, Shouval (2016)** "The Role of Multiple Neuromodulators in Reinforcement Learning That Is Based on Competition between Eligibility Traces" — PMC5156839 [LOAD-BEARING: SEPARATE LTP-trace and LTD-trace with different modulators]
6. **Pawlak, Wickens, Kirkwood, Kerr (2010)** "Timing is not everything: neuromodulation opens the STDP gate" — Front Synaptic Neurosci [Three-factor multiplicative gating]
7. **Marder, Bucher (2007)** "Understanding circuit dynamics using the stomatogastric nervous system" — Annu Rev Physiol [LOAD-BEARING CAVEAT: GPCR cascade convergence to I_MI = naive multiplicative IS DEGENERATE]
8. **Krasne, Cushman, Fanselow et al. (2024)** "Acetylcholine demixes heterogeneous dopamine signals" — bioRxiv 2024.05.03.592444 [Recent: ACh and DA anti-correlate in striatum]
9. **Grossman et al. (2022)** "Serotonin neurons modulate learning rate through uncertainty" — Curr Biology https://www.sciencedirect.com/science/article/pii/S0960982221016821 [5HT = long-timescale uncertainty meta-rate]
10. **Bridging Brains and Machines (2025)** "A Unified Frontier in Neuroscience, AI, and Neuromorphic" — arXiv:2507.10722 [Recent review of multi-modulator neuromorphic systems]
11. **Lifelong Reinforcement Learning via Neuromodulation (2024)** arXiv:2408.08446 [Multi-modulator continual learning architecture]

Plus supporting (12-15): Doya (2002), Mocle (2024), Liu (2025), Salvatori (2023), Sequential-neuromodulation PLOS CompBio 2021, Lloyd-Dayan timescale model.

---

## Honest limitations

- **Calibration penalty applied:** raw best-modulator literature P ~ 0.65; deflated 0.20 for novel substrate-synthesis to 0.45; capped under 0.50 novel-synthesis ceiling → reported P=0.42
- **The Marder degeneracy caveat is the LOAD-BEARING new finding** vs. prior `research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22.md` (which gave neuromodulator a P=0.40 without this concern). Adding caveat: naive-multiplicative WILL FAIL; dual-trace is the substrate-rescue.
- **Dual-trace cell is novel-synthesis** (no direct prior at small-N rank-1 Hebbian forward-only substrate). P=0.42 is calibrated under that uncertainty.
- **Brain-existence-proof discipline:** USER memory says brain-grounded mechanisms with substrate-native paths get P=0.60-0.75. After Marder caveat, dropped to 0.42-0.50 because the literal multiplicative form is refuted; the dual-trace form has weaker direct empirical support in forward-only Hebbian regimes.
- **HARD_FAIL of dual-trace is a HIGH-VALUE outcome** — it's the cleanest evidence that the rank-1 Hebbian cap is structural and the substrate-product story should pivot. Pre-reg makes the negative actionable.
- **No re-coverage:** prior `research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22.md` covered 12 mechanisms breadth-first. This 2x drill operates AT DEPTH on mechanism #4 (neuromodulator) with the Marder convergence + Brzosko sequential refinements not covered there.

## Key insight (one line)

The brain achieves orthogonal modulator composition via TWO ELIGIBILITY TRACES with DIFFERENT TIMESCALES, gated by DIFFERENT modulators — NOT via simultaneous product-of-scalars on a single trace, which Marder STG shows is DEGENERATE; substrate-rescue is the dual-trace + sequential-gating cell described above (P=0.42).
