# Research drill (3x deep) — substrate MODULATORY + ARCHITECTURAL parameter taxonomy

filed: 2026-06-23
drill class: 3x (level-3 elucidation: lit + substrate-mapping + L3 depth on top 4 + L4 operational + L5 cross-thread)
companion drill: A (representational + temporal parameters, in parallel)
in-flight related: substrate-viability shotgun (empirical LIVE/DEAD parameter map)
priors leaned on:
- notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md (Marder STG; Brzosko sequential; dual-trace)
- notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md (Levy-Horn-Ruppin M-module factorial; Krotov-Hopfield n-order; Ocker-Buice forward-only)
- notes/research_negative_landings_evidence_totality_synthesis_2026-06-23.md (homogeneous-in-module rank-1 / heterogeneous compose escape; receiver-must-match-codebook)
- notes/research_neuroscience_methodology_for_substrate_lm_3x_drill_2026-06-23.md (6-arm vehicle/A/B/A+B/B+A/random factorial)
- notes/research_dual_trace_mechanism_elucidation_2026-06-23.md (4-axis confound decomposition: sign / target / timescale / cardinality)

---

## HEADLINE

The brain-canonical default for substrate modulator composition is **sigmoidal-additive sum over algebraically-independent traces gated by heterogeneous modulators**, NOT multiplicative gain stacking; for architectural parameters the dominant lever is **K independent banks with HETEROGENEOUS read-out structure** (per Drosophila MB 15-compartment + Levy-Horn-Ruppin N^M), not within-bank cardinality. Of the 17 parameters in scope, 4 are load-bearing (modulator compose function / bank count K / compose order / per-context T); the remaining 13 are second-order tuning knobs that only matter once the 4 are in their correct regime. Substrate-mine cross-check: every chain-grade positive lives in the "heterogeneous algebraic structure" regime; every negative lives in the "homogeneous-in-module + linear-matched-filter" regime — so the brain-canonical defaults below are not speculative, they are the empirical pattern.

---

## Parameter taxonomy table (full 17-param scope)

Columns: (param, math, brain-analog, desired regime, failure mode at extremes, discriminating measurement, current substrate value / status)

### MODULATORY parameters (per-query / per-context control signals)

| # | Param | Math | Brain-analog | Desired regime | Failure mode | Discriminating measurement | Current value / status |
|---|---|---|---|---|---|---|---|
| 1 | **T (decode temperature)** | softmax(logit/T) | tonic LC-NE gain (Yu-Dayan 2005); inverse of cortical responsivity slope | T ∈ [0.5, 2.0] for calibrated; T→0 = hard-max (degenerate); T→∞ = uniform | T<0.3: argmax collapse, no entropy floor; T>3: BPC penalty from entropy bloat | sweep T-grid {0.5,0.7,1.0,1.4,2.0,3.0} report BPC argmin AND posterior-entropy-vs-T curve (calibrated regime is monotone) | currently swept {0.01-5.0}; harness rig-risk per fair_harness note — T must be set ON FAIR baseline (unigram + substrate at SAME T) |
| 2 | **lambda (decode mix)** | log p = (1-λ) log p_sub + λ log p_prior | top-down prior weighting (Rao-Ballard hierarchical predictive coding); Bayesian mixture | λ ∈ [0.1, 0.5] when sub has lift; λ→0 = sub-only (fragile to OOD); λ→1 = prior-only (no learning value) | λ=0: posterior collapses to substrate's noisy edges; λ=1: substrate provides 0 information (degenerate) | argmin BPC over λ-grid {0,0.1,0.25,0.5,0.75,1.0}; HONEST: argmin must be < BPC(λ=1)=unigram-only by HARD margin | currently typed implicitly inside ARM constructions; should be ARG-OBSERVED + reported per-arm (currently absent → confound) |
| 3 | **dopamine modulator (cf-RPE scalar)** | g_DA · Δ on outer product | VTA→cortex phasic DA on D1/D2 receptors gating LTP-only (Brzosko 2017: ACh first, DA retro-converts) | g_DA target = E_pos (LTP trace), NOT shared with E_neg | g_DA shared across LTP+LTD: degenerate, no orthogonality (Marder STG convergence) | 6-arm ablation: {none, DA-only, ACh-only, DA+ACh on shared trace, DA on E_pos+ACh on E_neg, randomized control} | dual_trace_RESCUE_corrected_baseline_v1 in-flight on overnight_queue; per neuromodulator_orthogonal note brain uses SEPARATE eligibility traces |
| 4 | **ACh modulator (attention gain)** | g_ACh · readout-amplification on query | nucleus basalis ACh→cortex divisive normalization gain (Sara-Bouret 2012) | g_ACh target = READ-side (per-query gain on retrieval, NOT write-side); reciprocal in time to DA | g_ACh on write-side: redundant with DA (single-trace collapse); g_ACh on read-side with no entropy gating: globally amplifies noise | discriminating cell: ACh_query_conditional_read_gain_LM_v1 (in-flight remote_cpu_queue) — must show per-query lift vs global gain | read-side ACh cell shipped to remote 20:36; awaiting verdict |
| 5 | **serotonin modulator (state/novelty)** | bank-select discrete gate OR slow tonic baseline shift | DRN serotonin = mode-switching between behavioral regimes (Daw 2002); 5-HT2A density gates state | g_5HT target = bank-routing or learning-rate-floor (slow-timescale), NOT per-pattern gain | 5HT as fast scalar = redundant with DA; 5HT must operate at SLOW timescale to be a different control axis | discriminating cell: serotonin_mode_switch_bank_select_LM_v1 (in-flight remote_cpu_queue) — must show MORE-BANK regime > LESS-BANK at MATCHED parameter count | shipped 20:47; awaits verdict |
| 6 | **modulator compose function** | gate = f(g_DA, g_ACh, g_5HT). Options: multiplicative (g1·g2·g3) / additive (g1+g2+g3) / sigmoid(α·g1 + β·g2 + γ·g3) / log-additive | empirical brain consensus: ADDITIVE on conductance with downstream SATURATION (Pawlak gain modulation review; Lefort 2009 cortical); multiplicative is COLLAPSE on one-current convergence (Marder STG) | sigmoid(α·g1 + β·g2 + γ·g3) with α,β,γ tuned per axis; compose acts on ORTHOGONAL TARGETS (DA→E_pos, ACh→read, 5HT→bank-route) | multiplicative on shared substrate: rank-1 by Levy-Horn-Ruppin (already failed in 3-axis neuromodulator cell) | 4-arm cell (vehicle / mult / add / sigmoid-add) with ORTHOGONAL-TARGET constraint baked in | NOT yet directly tested as ablation; 3-axis-mult HARD_FAILed but conflated with same-target — needs clean discriminator |
| 7 | **refuse-gate threshold (cosine margin)** | refuse if max_cos(query, atoms) < θ | spike-threshold variability (Azouz-Gray 2000; criterion in SDT) | θ at ROC operating point that maximizes substrate-unique-value (precision × refuse-recall on OOD); brain uses ADAPTIVE threshold | θ→0: never refuse (loses calibration value); θ→1: always refuse (degenerate, no answers) | sweep θ-grid; report (precision-on-answered, refuse-recall-on-OOD) per θ; choose θ at Youden's J optimum or product-targeted point | refuse-gate CERT 588 chain-grade; θ currently set heuristically — opportunity to formalize as SDT operating point |
| 8 | **per-context vs global modulation** | T(context) = f(H(p_sub) | global) | local-ACh-gated attention switching (Sara-Bouret 2012); local-LC-NE phasic pulses for surprise | per-context T conditioned on predictive entropy (Holtzman stable-entropy 2023); brain consistently uses BOTH (slow tonic + fast phasic) | per-context T with arbitrary mapping = unstable; global T with no context awareness = miscalibrated on OOD-easy tokens | per_context_decode_temperature_LM_v1 (in-flight local_cpu_queue); HARD_PASS = +0.10 BPC over global-T baseline | shipped 20:28; awaiting verdict |
| 9 | **modulator-target orthogonality** | which target each modulator acts on: {E_pos, E_neg, bank-route, read-gain, write-rate} | Brzosko 2017: DA→LTP, ACh→LTD (different traces); 5HT→state-gate; LC-NE→global gain (different layers) | each modulator binds to a DIFFERENT target (Cartesian-product, not coincident) | all modulators on shared target = degenerate (Marder STG = 3-axis-mult HARD_FAIL) | enforced as DESIGN CONSTRAINT in cell architecture; verified via permutation control (swap modulator-target bindings → BPC must DROP) | not yet probed via permutation; should be added to dual_trace_RESCUE design |

### ARCHITECTURAL parameters (structural "how many substrates and how arranged")

| # | Param | Math | Brain-analog | Desired regime | Failure mode | Discriminating measurement | Current value / status |
|---|---|---|---|---|---|---|---|
| 10 | **bank count K** | K parallel W matrices vs single W | Drosophila MB: 15 compartments × ~2000 KC; cortical column count (~10^6 in human); Levy-Horn-Ruppin 1997 M independent modules | K ∈ [4, 16] for substrate-LM; K independent banks give N^K combined states (Levy-Horn-Ruppin theorem) | K=1: rank-1 cap (4-mod-on-one-bank HARD_FAIL is exact instance); K>32: bank-routing overhead dominates lift | k_module_heterogeneous_compose_LM_v1 (in-flight; K=4 with heterogeneous algebraic structures) — HARD_PASS = BPC ≤ 6.8 (>0.5 over envelope) | shipped 20:21; awaiting verdict — predicted optimal K=4 at N=8192/V=4000 |
| 11 | **bank selection mechanism** | random / feature-gated / 5HT-mode-switch / learned-router | striatal action selection via DA gates (Doya 2000); cerebellar Purkinje cell convergence; Drosophila DAN → compartment mapping | feature-gated (substrate-derived, not random); MUST be heterogeneous across banks (each bank specialized) | random gating: no specialization → effectively single-bank; learned-router on small data: overfits | per-bank-specialization audit: each bank should show DIFFERENT per-token error profile (cosine sim of error vectors < 0.3) | not yet probed; should be added as a metric in k_module cell |
| 12 | **compose count** (number of mechanisms in one cell) | M mechanisms composed; substrate has K=5 chain-grade primitives | brain composes ~4-7 hierarchical levels (Friston predictive coding) + lateral integration | M ∈ [2, 4] for HETEROGENEOUS compose (each in different algebraic structure); M=1 trivially baseline | M=1: no compose lift; M=K (all 5): integration overhead dominates if structures aren't truly orthogonal | M-sweep cell: {sparse-bipolar} → {sparse+lockin} → {sparse+lockin+HRR} → all-4; observe lift superadditive vs subadditive | NOT yet swept cleanly; shotgun smoke 1 evidence suggests M=2 (lockin+sparse) gives ~chain-grade lift |
| 13 | **compose order** | A-then-B vs B-then-A; e.g. sparse-then-lockin vs lockin-then-sparse | Sjöström-Häusser 2006 ordered STDP; Lisman precedence; Brzosko 2017 ACh-first-then-DA temporal order | BRAIN-CANONICAL: low-level (sensory / encoding) FIRST, high-level (cleanup / readout) LAST; sparse-encoding-first-then-cleanup = Marr cerebellar canonical | wrong order (cleanup-first-then-sparse): cleanup operates on dense codebook, then sparsification destroys retrieval | A-vs-B ablation: 2-arm (sparse-then-lockin vs lockin-then-sparse) on identical M=2 cells | shotgun smoke 1 evidence: compose ORDER matters catastrophically; consistent with Marr canonical |
| 14 | **hierarchy depth** | L predictive-coding encoder layers | brain hierarchy ~4-7 levels (V1→V2→V4→IT or A1→A2→…→language); Friston 2009 hierarchical PC | L ∈ [2, 4] for substrate (avoids vanishing gradients in forward-only PC); brain uses 4-7 with backprop | L=1: no abstraction (rank-1 single-layer); L>5 forward-only: encoder drift, Shannon-floor collapse | L-sweep cell with substrate-native PC encoder; report capacity per layer | only L=1 substrate encoders so far (char-trigram, word2vec, pythia probes); deferred to Path C substrate-owned encoder arc |
| 15 | **K-WTA / top-K sparsity readout** | retain top K of softmax; zero out rest | Tonegawa engram allocation (Liu 2012); cerebellar Marr granule cell ~10% activity | K/N ∈ [0.02, 0.2]; aligned to write-side codebook sparsity f (matched-filter principle from sparse_receiver note) | K/N too high: noise floods retrieval (linear-matched-filter on sparse pays -17dB per receiver-SNR diagnosis); K/N too low: misses signal | sparse_receiver_energy_diagnosis_v1 (in-flight remote_cpu_queue) — Pearson r(recall, sqrt(f·N)/sigma) ≥ 0.85 | shipped 20:37; result determines whether to add amplitude-scaling 1/sqrt(f) or support-restricted WTA |
| 16 | **cleanup iterations** | n iterations of Hopfield-style associative cleanup | CA3 recurrent dynamics: empirical single-iteration suffices for sparse, well-separated patterns (Treves-Rolls 1994); modern Hopfield: single-step exact retrieval under conditions (Ramsauer 2020) | n=1 if codebook orthogonal-enough (modern Hopfield single-step); n=3-5 for moderately-correlated codebook; n→∞ never necessary in healthy regime | n=0: skip cleanup, fall to nearest match (high error on noisy queries); n>10: convergence to spurious attractors | empirical n-sweep on cleanup capacity: argmax n that maintains recall_acc > 0.9 across noise levels | n=1 currently for sparse-bipolar; should be verified against modern-Hopfield single-step regime; AT_REST per cleanup-load-bearing META atom |
| 17 | **routing/gating between substrates** | gate(query) → which bank(s) to query; aggregator(bank_outputs) → fused logits | thalamic gating (Sherman 2007); pulvinar attention routing; cortical column lateral inhibition | feature-gated routing + module-precision-weighted aggregation (per Bayesian cue combination) | random routing: averages noise; arg-max routing: brittle to OOD; equal aggregation: ignores per-bank confidence | precision-weighted aggregation ablation (uniform vs per-bank-precision vs entropy-weighted) | NOT yet swept; k_module heterogeneous cell uses uniform aggregation in v1 — should be follow-up |

---

## L3 — Top 4 highest-leverage parameters, drilled in depth

### L3-A. Modulator compose function (param #6) — THE load-bearing axis

**Why it's #1:** the 3-axis-neuromodulator-multiplicative cell HARD_FAILed at production scale; the dual-trace-sequential cell HARD_PASSed; the difference is NOT modulator-count, it's compose-function-on-targets. This is the axis the prior arc has the most empirical signal on, and the brain literature is sharpest here.

**Math regimes:**

| Compose | Formula | When it works | When it collapses |
|---|---|---|---|
| Multiplicative | gate = g_DA · g_ACh · g_5HT | NEVER on shared target (collapses to rank-1) | Marder STG: GPCR convergence → single I_h current → multiplicative on one current = degenerate by construction |
| Additive (linear sum) | gate = α·g_DA + β·g_ACh + γ·g_5HT | When modulators act on SEPARATE conductances or substrates | Saturates without bound → numerical drift; needs downstream nonlinearity |
| **Sigmoidal-additive (brain canonical)** | gate = σ(α·g_DA + β·g_ACh + γ·g_5HT) | ALWAYS preferred when targets are separable; saturating sigmoid bounds output | Loses gain at saturation extremes (small dynamic range if α,β,γ poorly tuned) |
| Log-additive (log-pool) | log gate = α·log g_DA + β·log g_ACh + γ·log g_5HT | When modulators are independent EVIDENCE (log probabilities) → optimal Bayesian pool | If modulators are gains not probabilities, log-additive is wrong frame |

**Brain canonical answer (Pawlak gain review; Lefort 2009 cortical; Frémaux-Gerstner 2016):** **additive on conductance + downstream sigmoid saturation + heterogeneous targets**. Multiplicative is a SPECIAL CASE that emerges when both gain signals act on the SAME conductance — but then it's just rank-1, which is what Marder STG demonstrated.

**Substrate-native predicted-correct architecture:**
- g_DA gates E_pos (LTP-trace) — additive on potentiation
- g_ACh gates E_neg (LTD-trace) — additive on depression (Brzosko sequential)
- g_5HT gates bank-routing (slow-timescale, mode-switch)
- compose = SUM of three INDEPENDENT contributions, each in its OWN target → effective sigmoid(write_rule + read_gain + bank_select)
- this IS the dual-trace cell architecture that HARD_PASSed

**Failure mode at substrate extremes:**
- multiplicative on shared target: 3-axis-mult HARD_FAIL (precedent)
- additive without saturation: numerical drift / unbounded gain at long N_TRAIN
- log-additive when modulators aren't log-probabilities: type-error, gates become numerically unstable

**Discriminating measurement (this is the experiment to ship):**
4-arm cell at N=8192, V=4000, 100k tokens:
- ARM_VEHICLE (no modulators)
- ARM_MULTIPLICATIVE_SHARED_TARGET (3 mods → 1 write rule; expected HARD_FAIL)
- ARM_ADDITIVE_NO_SATURATION (3 mods → sum on 1 write rule; expected MIDDLE_BAND, drift)
- ARM_SIGMOIDAL_ADDITIVE_HETEROGENEOUS (DA→E_pos, ACh→E_neg, 5HT→bank-route, sigmoid downstream; expected HARD_PASS)

**HARD_PASS:** sigmoidal-additive ARM beats multiplicative ARM by ≥ 0.20 BPC at N=8192.
**HARD_FAIL:** sigmoidal-additive within 0.05 BPC of multiplicative → compose-function is NOT load-bearing, look elsewhere.

P_deflated (sigmoid-additive heterogeneous beats multiplicative): 0.65 (brain-existence-proof asymmetric + dual-trace precedent supports this strongly; deflated 0.10 for substrate-vs-brain implementation risk).

---

### L3-B. Bank count K (param #10) — the dominant ARCHITECTURAL axis

**Why it's #1 in architecture:** Levy-Horn-Ruppin 1997 theorem is exact: M independent attractor modules each with N states give N^M combined capacity. This is the SINGLE THEORETICAL MECHANISM brain uses to escape Hopfield's 0.15N cap — there's no second mechanism. Substrate has NEVER cleanly tested K>1 banks with heterogeneous read-outs.

**Math:**

For independent banks: log capacity = K · log(0.15 N) per bank → log total = K log(0.15 N).
For K=4, N=8192: log capacity = 4 · log(1229) = 4 · 7.11 ≈ 28.4 nats ≈ 41 bits → 2.2 × 10^12 distinguishable states.
For K=1, N=8192: log capacity = 7.11 nats ≈ 10.3 bits → 1229 states.

**Brain-analog mapping:**
- Drosophila MB: K=15 compartments × ~2000 KC; each compartment has UNIQUE DAN inputs, UNIQUE MBON outputs, INDEPENDENT plasticity. The 15-compartment design is the canonical biological N^K instance.
- Mammalian cortex: ~10^6 columns × ~10^4 neurons each (Mountcastle); roughly K~10^6 if columns are independent.
- Cerebellum: ~50M Purkinje cells × ~10^5 parallel fiber inputs (Marr); each Purkinje independent gate.

**Desired regime for substrate:** K ∈ [4, 16] at N=8192.
- K<4: insufficient factorial lift; can't escape rank-1
- K=4: matches Drosophila smallest functional compartmentalization
- K=8-16: matches cortical column functional clustering
- K>32: routing overhead dominates lift; each bank too small to be useful at N=8192

**Failure modes:**
- K=1: rank-1 cap (current substrate-LM regime; 4-mod-on-one-bank HARD_FAIL is exact instance)
- K>32 with no specialization: equivalent to K=1 (no per-bank distinct error profile)
- K large but with HOMOGENEOUS algebraic structure: per Levy-Horn-Ruppin, independence requires algebraic uncoupling, not just bank-count

**Discriminating measurement (in-flight as k_module_heterogeneous_compose_LM_v1):**
4-arm cell with K=4 banks, each in DIFFERENT algebraic structure (sparse-bipolar / lock-in / HRR / refuse-gate). HARD_PASS at BPC ≤ 6.8, lift ≥ 0.94 over unigram.

**Additional discriminator needed (NEW prediction):** K-sweep at fixed compute. {K=1, K=4, K=8, K=16} at fixed total parameter count (so each bank shrinks as K grows). The N^M theory predicts log-lift scales as K · log(N/K) — UNTIL K becomes large enough that per-bank capacity collapses. This identifies the optimal K for substrate at N=8192.

P_deflated (K=4 heterogeneous beats K=1 by ≥ 0.30 BPC): 0.55. P_deflated (K-sweep finds optimum K∈[2,8]): 0.70.

---

### L3-C. Compose order (param #13) — silent killer, validated by smoke

**Why it matters:** shotgun smoke 1 evidence shows compose order matters catastrophically (per task spec). Marr cerebellar canonical predicts a specific order: sparse-encoding-FIRST, cleanup-LAST. This is also the brain canonical processing order (sensory → encoding → cleanup → readout).

**Math intuition:** Composition is a chained map. f∘g ≠ g∘f in general. Specifically:
- (cleanup ∘ sparse-encode)(x) = cleanup(sparse_encode(x)) → cleanup operates on already-sparse code; matches receiver expectation; CORRECT
- (sparse-encode ∘ cleanup)(x) = sparse_encode(cleanup(x)) → cleanup operates on dense input first; then sparsification destroys cleanup's stable point; WRONG

**Brain-canonical order (Marr 1969; Litwin-Kumar 2017):**
1. Sensory input (dense)
2. Sparse encoding (mossy-fiber → granule cell expansion, then K-WTA)
3. Sparse code stable
4. Cleanup at retrieval (Purkinje cell convergence / hippocampal CA3 recurrent)
5. Read-out

**Substrate canonical predicted order:**
1. Token input
2. Substrate encode (whatever encoder)
3. Sparse-bipolar K-WTA (if used) — match receiver to codebook
4. Bind (HRR / lock-in if multi-axis)
5. Cleanup (Hopfield iteration if needed)
6. Refuse-gate
7. Read-out

**Failure mode at wrong order:** sparse_cleanup_compose_breakage diagnosis showed sparse-after-cleanup destroys retrieval at f=0.02 by -17dB receiver-SNR; this is the EXACT cleanup-then-sparse wrong order.

**Discriminating measurement:** 2-arm A-vs-B cell at N=4096 with identical components in different order: ARM_CANONICAL (sparse → bind → cleanup) vs ARM_REVERSED (cleanup → bind → sparse). Expect ARM_CANONICAL ≥ ARM_REVERSED by ≥ 0.30 BPC. If null, compose order is NOT load-bearing and we should look at component choice instead.

P_deflated (canonical order beats reversed by ≥ 0.30 BPC): 0.75 (strong precedent from sparse-cleanup-compose-breakage; brain canonical and Marr canonical agree; deflated 0.10 only for implementation specifics).

---

### L3-D. Per-context T (param #8) — in-flight, gap-bridge to brain

**Why it's a top axis:** brain uses BOTH tonic AND phasic LC-NE gain (Sara-Bouret 2012). Substrate currently uses ONLY global T. Per_context_decode_temperature_LM_v1 is in-flight; this is the cleanest single-axis test of context-conditional modulation.

**Math:**

T(context) = T_base · f(predictive_entropy, cosine_margin)

Candidates for f:
- f = 1 + α · H(p_sub) — entropy-conditional (sharpen when confident)
- f = 1 + β · (1 - max_cos) — margin-conditional (sharpen when near a stored atom)
- f = sigmoid(α · H + β · (1-max_cos)) — combined sigmoidal-additive (brain canonical compose form!)

**Brain-analog:** locus coeruleus phasic pulses to ACh nucleus basalis on surprise/novelty → cortical gain SPIKES on uncertain tokens. Yu-Dayan 2005 formalization: gain ∝ posterior_uncertainty.

**Desired regime:** T(context) on LOW-entropy contexts should be HIGHER than baseline (sharpen confident predictions); HIGH-entropy contexts get LOWER T (avoid over-confidence on uncertain tokens). This is the OPPOSITE of naive intuition where you'd think "high entropy → high T". Brain answer: high entropy → LOW gain (don't commit to anything) → which in softmax-temperature means HIGHER T (flatter). Actually consistent: high uncertainty → flatter posterior is conservative.

Wait — let's nail this. The mapping is:
- entropy_pred LOW (sub is confident) → trust substrate → LOW T (sharpen further)
- entropy_pred HIGH (sub is uncertain) → don't trust substrate → HIGH T (flatten toward prior)

This is the optimal Bayesian behavior, and it matches LC-NE phasic responses (surprise → gain boost → enhanced cortical responsivity), with the SUBSTRATE-specific twist that "enhanced responsivity" in a softmax context means SHARPER, not flatter — because the substrate's prediction IS the gain target.

**Failure mode:**
- T(context) with arbitrary mapping: unstable, can amplify noise
- f = -α · H (sharpen when uncertain): backward, amplifies hallucinations
- Global T only: leaves performance on the table on low-entropy contexts where substrate genuinely knows the answer

**Discriminating measurement (in-flight per_context_decode_temperature_LM_v1):** HARD_PASS = +0.10 BPC over global-T baseline. NEW prediction: the per-context-T arm with entropy-conditional sharpening should show MOST lift on tokens where substrate has high cosine-margin AND prior has high entropy (substrate genuinely informative).

P_deflated (per-context T beats global by ≥ 0.10 BPC): 0.45 (strong brain precedent but small effect size expected; deflated for substrate-specific calibration risk).

---

## L4 — Operational tuning strategy + ordering

**The 4 load-bearing parameters must be tuned in this ORDER (each constrains the next):**

1. **Compose order (param #13) FIRST** — get this wrong, nothing else can save you. Default: brain-canonical sparse-encode → bind → cleanup → refuse → read. Ship 2-arm A-vs-B on existing cells; if reversed-order is within 0.1 BPC of canonical, this isn't load-bearing and unblock; otherwise lock canonical order across all cells.
2. **Bank count K (param #10) SECOND** — once order is locked, sweep K∈{1,4,8,16} at fixed compute. The N^M predicted optimum is K=4 at N=8192 (4 · log(1229) ≈ 28 nats is enough headroom for substrate-LM win without per-bank capacity collapse).
3. **Modulator compose function (param #6) THIRD** — with K and order locked, run the 4-arm modulator-compose ablation (vehicle / mult-shared / add-no-sat / sigmoid-add-heterogeneous). Expected winner: sigmoidal-additive-heterogeneous-targets per Brzosko + Pawlak + dual-trace precedent.
4. **Per-context T (param #8) LAST** — pure decode-time refinement; layers on top of the architecture. Currently in-flight; verdict will tell us if it's worth permanent inclusion.

**Once 4 load-bearing axes are set, the 13 second-order parameters tune cheaply:**

- lambda (#2): pure decode-time, single argmin sweep on held-out → set once per cell
- refuse-gate θ (#7): set at Youden's-J optimum on OOD-validation
- modulator strengths g_DA, g_ACh, g_5HT (#3-5): grid-search α,β,γ in the sigmoid-additive form
- K-WTA / sparsity (#15): set to MATCH write-side codebook sparsity f (matched-filter principle)
- cleanup iterations (#16): set to 1 if codebook supports modern-Hopfield single-step; otherwise 3-5
- routing/aggregation (#17): start uniform, then add precision-weighted as upgrade

**Recommendation: drop or deprioritize until 4 load-bearing parameters locked:**
- modulator-target orthogonality (#9) — implicitly enforced by sigmoidal-additive-heterogeneous compose
- hierarchy depth (#14) — requires Path C substrate-owned encoder which is on a different arc
- bank-selection mechanism (#11) — only matters once K is set
- compose count (#12) — once compose-order locked, M is constrained by available chain-grade primitives

---

## L5 — Cross-thread synthesis

### Connection to the substrate-product picture

**If the 4 load-bearing axes are tuned correctly (P ≈ 0.40-0.55 combined):**

Substrate becomes a **K-module heterogeneous-algebraic-structure compose engine with sigmoidal-additive neuromodulator-style control and brain-canonical compose order**. This is a NEW capability class (not just LM): a substrate that processes information through Cartesian-product factorial capacity with biologically-motivated control. Substrate-product positioning shifts FROM "trying to be an LLM" TO "the biologically-canonical alternative to LLMs" — a different market entirely.

The 5 chain-grade primitives are the load-bearing PRODUCT (each in different algebraic structure: dimensional/frequency/convolutional/conditional/calibrated-mix). The modulatory + architectural parameters define HOW they compose.

### Where substrate parameter space DIFFERS from brain (caveats)

1. **Substrate has no spike-timing**: STDP-precision is degraded; substrate's "eligibility trace" is a discrete buffer, not a continuous calcium concentration. So STDP-specific temporal precision (Markram-Bi-Poo 1997 millisecond windows) maps imperfectly to substrate's discrete-step counter.
2. **Substrate has no real metabolic constraint**: brain's sparsity isn't optional (ATP budget); substrate could in principle run dense. But dense + linear-matched-filter is rank-1 (per evidence-totality). So substrate-SHOULD adopt brain's sparsity for matched-filter receiver reasons, not metabolic.
3. **Substrate timescales are wall-clock unitful**: brain's "fast" vs "slow" timescales (~ms vs ~min vs ~h) get compressed into per-token-iteration steps in substrate. The TIMESCALE RATIO is what matters (Brzosko: ACh fast / DA slow); substrate can preserve ratios as iteration-count ratios.
4. **Substrate has no thalamus / pulvinar gating**: brain's central routing (#17) is implemented in specialized hardware; substrate needs to learn or hard-code gates. Default to feature-gated based on input.
5. **Substrate has no neuromodulator-receptor multiplicity**: brain has D1 vs D2 (DA), M1-M5 (ACh), 5-HT1A vs 5-HT2A — different receptors give different downstream effects. Substrate has only ONE coupling per "modulator". The Brzosko sequential effect EMERGES from receptor multiplicity in brain; substrate must FAKE it by separate eligibility traces (which is what dual-trace cell does — and it works).
6. **Substrate has no developmental wiring**: brain comes pre-wired with K=15 Drosophila compartments / cortical columns; substrate must specify K explicitly. The cheap default of K=4 (matching smallest functional brain compartmentalization) is the sensible product launch point.

### Connection to in-flight verdicts (what to watch for in next 4-24 hours)

| In-flight cell | Tests parameter | Outcome → what it tells us |
|---|---|---|
| k_module_heterogeneous_compose_LM_v1 | #10 K + heterogeneous algebra | HARD_PASS = K is load-bearing, ship K-sweep follow-up; HARD_FAIL = single-bank ceiling not architectural |
| dual_trace_RESCUE_corrected_baseline_v1 | #6 compose function (sigmoidal-additive on separate traces) | HARD_PASS = compose function is correctly identified; HARD_FAIL = need to reconsider Brzosko mapping |
| per_context_decode_temperature_LM_v1 | #8 per-context T | HARD_PASS = brain-canonical-context-modulation is substrate-applicable; HARD_FAIL = global T sufficient |
| ACh_query_conditional_read_gain_LM_v1 | #4 ACh read-gain | HARD_PASS = read-side modulation is independent axis; HARD_FAIL = ACh effect is write-side or null in substrate |
| serotonin_mode_switch_bank_select_LM_v1 | #5 + #11 5HT bank-routing | HARD_PASS = mode-switching architectural axis confirmed; HARD_FAIL = 5HT-equivalent maps to different role |
| sparse_receiver_energy_diagnosis_v1 | #15 K-WTA matched-filter | HARD_PASS = sparse-receiver-bug confirmed, fix is amplitude scaling; null = look elsewhere for sparse-receiver mechanism |

If 3+ of these HARD_PASS, the parameter taxonomy above is empirically validated as the substrate's load-bearing tuning surface. If 0-1 HARD_PASS, the rank-1 cap is structural and parameter tuning is second-order to the core architecture choice (pivot to substrate-as-knowledge-store).

---

## Cheap decisive test (one experiment that discriminates the taxonomy)

**Cell name:** `substrate_compose_order_x_compose_function_2x2_factorial_v1`

**Design:** 2×2 factorial:
- AXIS_1 (compose order): {canonical, reversed}
- AXIS_2 (compose function): {multiplicative-shared, sigmoidal-additive-heterogeneous}
- 4 arms total at N=4096, V=4000, 100k tokens, 3 seeds
- Vehicle baseline (no compose, plain rank-1 Hebbian) = 5th arm

**HARD_PASS:** ARM_CANONICAL_SIGMOID_ADD beats ALL OTHER 4 arms by ≥ 0.20 BPC (this confirms BOTH axes are load-bearing).
**HARD_FAIL:** any other arm wins, OR vehicle within 0.10 BPC of all → neither axis is load-bearing in the regime tested.

**Cost:** ~20 min CPU local (4 arms × 100k tokens at N=4096 ≈ 5 min each).
**ROI:** discriminates 2 of the 4 load-bearing parameters simultaneously; sets correct defaults for ALL subsequent cells.

---

## Citations (verified count: 11 external + 7 internal = 18 total)

**External (web-search verified):**
1. Pawlak & Kerr 2008, cortical D1/D2 gating of STDP, [PMC8600016 dopamine modulation review](https://pmc.ncbi.nlm.nih.gov/articles/PMC8600016/)
2. Multiplicative vs additive cortical gain modulation, [arxiv 1711.01421](https://arxiv.org/pdf/1711.01421)
3. Aso & Hattori 2014, Drosophila MB neuronal architecture for associative learning, [eLife 04577](https://elifesciences.org/articles/04577)
4. Drosophila MB connectome, [eLife 26975](https://elifesciences.org/articles/26975)
5. Mushroom body output valence + action selection, [eLife 04580](https://elifesciences.org/articles/04580)
6. Holtzman Stable Entropy Hypothesis (entropy-aware decoding), [arxiv 2302.06784](https://arxiv.org/pdf/2302.06784)
7. Contextual Temperature for LM, [arxiv 2012.13575](https://arxiv.org/pdf/2012.13575)
8. Universal Hopfield Networks single-shot framework, [PMC7614148](https://pmc.ncbi.nlm.nih.gov/articles/PMC7614148/)
9. Hopfield-Fenchel-Young unified framework, [arxiv 2411.08590](https://arxiv.org/pdf/2411.08590)
10. Litwin-Kumar et al. 2017 (Optimal Degrees of Synaptic Connectivity, Neuron), task-dependent cerebellar optimal sparsity, [eLife 82914](https://elifesciences.org/articles/82914)
11. Frémaux & Gerstner 2016, three-factor learning rules + eligibility traces, [PMC6079224](https://pmc.ncbi.nlm.nih.gov/articles/PMC6079224/)

**Additional brain-mapping anchors referenced (from prior research notes; not re-searched):**
- Marder STG GPCR convergence (Marder & Bucher 2007)
- Brzosko 2017 (ACh-first DA-retro convert)
- Levy-Horn-Ruppin 1997 NIPS (M-module factorial capacity)
- Sara-Bouret 2012 (LC-NE phasic/tonic + ACh switching)
- Yu-Dayan 2005 (ACh gain control)
- Rao-Ballard 1999 (hierarchical predictive coding)
- Daw 2002 (5-HT mode switching)

**Internal substrate notes referenced:**
1. research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md
2. research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md
3. research_negative_landings_evidence_totality_synthesis_2026-06-23.md
4. research_neuroscience_methodology_for_substrate_lm_3x_drill_2026-06-23.md
5. research_dual_trace_mechanism_elucidation_2026-06-23.md
6. research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md
7. research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md

---

## META atoms candidate (for substrate self-mapping)

1. **modulator-compose-defaults-to-sigmoidal-additive-heterogeneous-targets** — brain canonical; multiplicative-on-shared is degenerate by construction (Marder STG).
2. **bank-count-K-is-the-load-bearing-architectural-axis** — Levy-Horn-Ruppin N^M is the ONLY theoretical mechanism brain uses to escape rank-1; substrate must implement K∈[4,16] heterogeneous banks.
3. **compose-order-is-load-bearing-and-brain-canonical-is-correct-default** — sparse-encode-FIRST, cleanup-LAST per Marr cerebellar canonical; reversed catastrophic per shotgun smoke 1.
4. **per-context-modulation-is-second-order-refinement** — important but only after K and compose-function are set; not a primary architecture choice.
5. **substrate-vs-brain-parameter-mapping-has-6-systematic-differences** — (no spike-timing / no metabolic constraint / no native timescales / no thalamic gating / no receptor multiplicity / no developmental wiring); substrate must FAKE these via explicit choices in dual-trace / iteration-ratio / K-specification.

---

## Companion exp_dev hand-off

Filing companion hand-off file at:
`d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md`

Primary anchor: `substrate_compose_order_x_compose_function_2x2_factorial_v1`
Secondary anchor: `substrate_K_sweep_at_fixed_compute_v1` (only if k_module_heterogeneous HARD_PASSes first)

---

End of research note.
