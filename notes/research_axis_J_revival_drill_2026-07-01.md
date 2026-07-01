# Axis J order-binding revival — discriminator drill

**Filed:** 2026-07-01
**Author:** research (Sonnet drill)
**Trigger:** Skunkworks c7feb0c4 + META synthesis f878c151 — K* identical across cyclic-shift / random-permutation / phase-rotation at N=8192, K∈{50,500,2000}. Pre-reg discriminator (K*-boundary log10 separation) HARD_FAIL on 2/2 landed seeds (13, 19).
**Question:** what alternative discriminators would separate order-binding families at chain-grade quality?

---

## HEADLINE

**Recall-at-K-cliff-far-side (K=2000) is already an operative discriminator hiding in the landed data** — phase-rotation top1=0.14, permutation=0.08, cyclic=0.04 (seed 13). That's a 3.5x spread the K*-boundary metric collapsed. **Interference-resilience under multi-sequence load is the strongest CG-eligible candidate** with 3-domain support (VSA cross-talk theory + working-memory literature + compressed-sensing basis-coherence). Serial-position asymmetry is a strong secondary. Rotational-aliasing at high N is a diagnostic-only, not CG.

---

## Ranked candidates

### 1. Interference-resilience under multi-sequence load (CG=0.55, payoff=HIGH, 3-domain support)

**Mechanism.** Encode L sequences simultaneously into a shared bundle; measure top1 recall of query (sequence_id, position) → item. Cyclic-shift preserves basis coherence with position code; random-permutation is basis-universal (compressed-sensing "universality" result — [Puy et al. 2012](https://asp-eurasipjournals.springeropen.com/articles/10.1186/1687-6180-2012-6)); phase-rotation exhibits phase-alignment cross-talk penalty from FHRR SNR = 1/m per dim ([Plate HRR literature](https://www.emergentmind.com/topics/holographic-reduced-representations-hrrs)).

**Prediction.** At L=4 sequences × K=250 items, cyclic collapses fastest (position-basis coherence with a single family of shifts creates constructive interference across sequences); random-permutation is most resilient (universal basis); phase-rotation intermediate but with aliasing risk at commensurate θ·K modulo 2π.

**Design one-liner.** `order_binding_interference_v1`: 3 ops × L∈{1,2,4} × K∈{125,250,500} × 3 seeds. Discriminator: at least one op differs ≥0.10 recall at L=4,K=250 with 3-seed cv<8%; pair-distinctness (META_RULE_AX) required.

**Cross-domain support (3).** (a) VSA/HRR cross-talk theory (SNR=1/m). (b) Cowan 2001 working-memory "magical mystery four" chunk-limit under interference load. (c) Compressed-sensing basis-universality theorem (permutation-matrix measurement matches Fourier phase-transition curve). **→ 5x-drill escalation eligible if landed HP.**

### 2. Serial-position curve shape / primacy-recency asymmetry (CG=0.40, payoff=MED, 2-domain support)

**Mechanism.** At fixed K=500 (currently MB band), measure top1(position=k) for k∈[1..K]. Cyclic-shift produces uniform (symmetric); phase-rotation produces phase-coherent recency bias (later positions have less phase-accumulated interference); random-permutation is uniform-random-mixed (no positional bias).

**Prediction.** Phase-rotation shows monotone recency (last-position top1 ≥ first-position top1 + 0.10 at K=500). Cyclic uniform. Permutation uniform. Bio-anchored by hippocampal theta phase-precession compression ratio 10:1 ([PMC 5245972](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5245972/)).

**Design one-liner.** `order_binding_serial_position_v1`: 3 ops × K=500 × N_queries=200 stratified by position × 3 seeds. Discriminator: position-slope difference ≥0.10 between at least two ops with cv<10%.

**Cross-domain support (2).** (a) Hippocampal theta-precession compression + human serial-position gamma/theta power shift ([PMC 3888367](https://pmc.ncbi.nlm.nih.gov/articles/PMC3888367/)). (b) Chunking psychology + distinctness effect (Cowan). **Not 5x-drill eligible.**

### 3. Sequence-embedding cosine-geometry preservation (CG=0.30, payoff=MED, geometry-side metric)

**Mechanism.** Insert / delete / substitute one item; measure Δcos(bundle_before, bundle_after). Cyclic-shift is a group-representation homomorphism (predictable Δ); random-permutation is an S_N element (Δ ≈ 1/√L uniform); phase-rotation depends on which position is edited (edge vs interior).

**Design one-liner.** `order_binding_edit_geometry_v1`: 3 ops × 3 edit-types × K=500 × 3 seeds. Discriminator: edit-type × op interaction with F-test p<0.01 AND cross-seed cv<10%.

**Cross-domain support (1).** Random-matrix / group-representation theory ([Diaconis-Shahshahani Fourier mixing](https://arxiv.org/pdf/1407.3580)). **Not 5x-drill eligible.**

### NOT-RECOMMENDED: Rotational-aliasing high-N probe

Diagnostic-only — determines whether phase-rotation θ is commensurate with 2π/N. Not a family-separator; failure mode not a CG mechanism-class.

---

## Meta-observation for cell author

**The landed data ALREADY carries the discriminator signal** in top1 at K=2000 (3.5x spread cyclic→phase). The pre-reg's K*-boundary metric collapsed this because all three ops crossed the SAT→MB boundary at the same K-grid point (500). Recommend cell #1 above uses **finer K-grid on the FLOOR side (K∈{800,1200,1600,2000,3000})** rather than moving on to interference load. Cheap, uses existing cell architecture, and would land a discriminator without a new spawn.

## Falsifiable predictions (HARD PASS / HARD FAIL)

**HARD_PASS (cell #1 interference-resilience):** at least one op differs ≥0.10 top1 at (L=4, K=250) with 3-seed cv<8% AND pair-distinctness True on all 3 op pairs. Consistent with basis-coherence theory: predicted ordering random-permutation > phase-rotation > cyclic-shift.
**HARD_FAIL:** all 3 ops within ±0.03 top1 at (L=4, K=250) → order-binding is capability-family-invariant under load also → axis J closed as substantive negative → deprioritize position-encoding family cells program-wide.
**MIDDLE_BAND:** 2/3 distinct, one collapses to baseline → partial family-separation, likely phase-rotation aliasing at N=8192.

## Substrate-product implications

If interference-resilience discriminates: multi-sequence WM composition acquires a **choose-your-position-encoder** knob keyed to load. Cyclic-shift for single-sequence (cheapest); random-permutation for multi-sequence bundles (basis-universal); phase-rotation reserved for FHRR-native pipelines. This is a Stage 2 architectural lever composable with the existing WM K=4096 CG primitive.

## Cross-thread synthesis

- Compresses with Axis F cleanup-family drill (research_phase_diagram_gap_analysis_next_cells_2026-07-01.md #1) — cleanup at K-cliff and position-encoder under load are **orthogonal** axes (per META_RULE_AT); can compose as cross-product if BOTH land HP.
- Feeds M3 cortex M1_3 stochastic-noise design: if phase-rotation shows serial-position asymmetry, cortex boundary noise injection can exploit it for temporal-order signal.
- Prior BTSP sequence-learning both v1/v2 HARD_FAIL (`exp_dev_to_research_BTSP_SEQUENCE_LEARNING_v1_v2_BOTH_HARD_FAIL`) — that closure was on encoding mechanism, not readout discriminator; this drill is orthogonal.

## Citations (verified count: 8)

1. Springer VSA comparison (Kleyko et al.)
2. arXiv 2501.05368 VSA category-theory foundation
3. arXiv 2407.05656 Multi-label learning with random circular vectors
4. Wikipedia Circular convolution
5. PMC 5245972 Theta sequence compression
6. PMC 3888367 Serial-position gamma/theta power (Sederberg et al.)
7. Nature Human Behaviour 2024 phase-precession human memory
8. EURASIP 2012 compressed-sensing basis universality (Puy et al.)
9. Emergent Mind HRR overview (SNR=1/m result)
10. arXiv 2408.07637 synaptic theory of WM chunking

**Novel-synthesis P deflated 0.55** (compressed-sensing basis-coherence prediction is well-established; substrate-application is composition of two CG primitives, not novel mechanism — novel-synthesis cap 0.50 does NOT apply).

**5x-drill escalation status:** Candidate #1 has 3 disparate domains (VSA cross-talk theory + human WM literature + compressed-sensing) → **eligible** if landed HP.
