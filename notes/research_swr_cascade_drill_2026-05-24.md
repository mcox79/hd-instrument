# Research drill — Hippocampal SWR-driven systems consolidation: discrete vs continuous cascade depth

**Date**: 2026-05-24
**Role**: Research (2x adjacency-cascade follow-up to PT-cascade drill, biology side)
**Calibration**: lit-scan penalty applied (P estimates deflated 0.15-0.25; novel-synthesis P capped at 0.50) per [[feedback-lit-scan-calibration-penalty]]. Substrate-specific framing held out of all WebSearch queries per [[feedback-query-privacy-decomposition]].
**Drill discipline**: 2x = depth on the discrete-vs-continuous question raised by the PT drill, not re-verification of prior drill per [[feedback-2x-means-depth]].
**Companion / prior**: [research_pt_cascade_drill_2026-05-24.md](research_pt_cascade_drill_2026-05-24.md). Physics found CONTINUOUS sqrt(N) scaling, no discrete depth optimum. This drill asks: does biology differ?

---

## TL;DR (for orchestrator triage)

**Biology DOES differ from PT physics on cascade depth — moderate corroboration of basin-discrete framing, with one important caveat.**

1. **Discrete bands with log-spacing.** Penttonen & Buzsaki 2003 N3L law: brain oscillations form a geometric progression on linear frequency scale, ratio r ≈ 2–3 between neighboring bands. Crucially: **neighboring bands have non-integer (incommensurate) frequency ratios**, so they cannot entrain each other — they remain functionally distinct. Confidence 0.65 (calibration-deflated from 0.85; the N3L is empirical pattern-matching, not derived from first principles; 1/f spectrum critique persists).

2. **Three-level cascade for consolidation is genuinely hierarchical, not a continuum sampled at convenient frequencies.** SO (~0.75 Hz) → spindle (~14.5 Hz) → ripple (~86 Hz) with measured phase preferences and sparse coupling (Staresina et al 2015, Nature Neuro). Cascade depth N=3 is universal across human, rodent, non-human primate. Confidence 0.55 (deflated from 0.75; depth-3 may reflect measurement convenience for cortical surface EEG/iEEG; deeper-level oscillations exist at <0.1 Hz infra-slow but rarely included).

3. **SWR-theta anticorrelation IS the gating mechanism — mutually exclusive brain states.** Theta during exploration/REM (encoding), SWR during quiet wake/SWS (replay). Confirmed across Buzsaki lab and many others. This maps to PARALLEL multi-timescale OPERATION via state-gating rather than concurrent multi-band replay. Confidence 0.70 (well-established phenomenology).

4. **Causality (the load-bearing part for basin-discrete framing):**
   - **Bayesian meta-analysis of SO-spindle coupling correlates with memory (BF=58–111, r~0.07).** Strong association, small effect, NO causality from meta-analysis alone.
   - **Optogenetic causality DOES exist for the triple coupling**: Latchoumane et al 2017 (Neuron) showed in-phase triple-coupling stimulation improves consolidation; out-of-phase does NOT. This is the single strongest causal demonstration that the DISCRETE cascade structure matters, not just any oscillatory input.
   - **SWR silencing (Girardeau 2009, Ego-Stengel & Wilson 2010): impairs spatial memory.** But more recent work (eLife 2023, Yamamoto lab) shows disruption of awake SWRs does NOT affect repeated-acquisition tasks — so causality is task-specific. Confidence 0.45 (deflated from 0.65; mixed literature).

5. **NEGATIVE finding (matters for our framing):** No literature directly establishes that depth = 3 is OPTIMAL versus depth = 2 or depth = 4. The 3-level cascade is what's MEASURED, not what's been compared against alternative cascade depths in vivo. The "discreteness" is empirically there; the "optimality at N=3" is a claim biology cannot answer (you can't add a 4th oscillation to the brain to test). Confidence 0.50 (cap from novel-synthesis ceiling).

**Net answer to PT-drill's open question**: Biology corroborates that DISCRETE cascade structure exists and has functional/causal consequences (Latchoumane optogenetic triple-coupling). But it does NOT independently corroborate that the cascade DEPTH is optimized at a particular integer — only that the depth that exists in biology is causally engaged. **Moderate but not strong support for basin-discrete framing.**

---

## (a) Discrete bands: the Penttonen-Buzsaki N3L law and its limits

### A1. The N3L claim

Penttonen & Buzsaki 2003 (in *Neural Networks*) proposed: brain oscillations form a linear hierarchy of distinct frequency bands when transferred to the natural-log scale. Empirically, f_{k+1} = f_k × r with r ≈ 2–3 (so log-spacing is ln(r) ≈ 0.7–1.1).

Key consequence: **neighboring bands have non-integer (incommensurate) ratios** so they cannot phase-lock for extended periods. Instead, oscillatory interference between them generates "perpetual fluctuation between unstable and transiently stable states."

Bands identified in mammalian brain (representative center freqs): ~0.1 Hz (ultra-slow) → 0.75 Hz (SO) → 4 Hz (delta-theta boundary) → 8 Hz (theta) → 14 Hz (spindle/sigma) → 30 Hz (beta) → 80 Hz (gamma) → 150–200 Hz (ripple). Roughly 7–9 discrete bands depending on convention; log-ratio between neighbors averages ~2.

### A2. Critique / continuum view

Counterarguments exist:
- **1/f power-law spectrum**: brain LFP power decreases smoothly with frequency, suggesting continuous generative process.
- **Band definitions vary across labs**: classical EEG bands (delta/theta/alpha/beta/gamma) have inconsistent boundaries; spindle low/high split varies; ripple range 80–250 Hz lumps multiple distinct phenomena.
- **Within "gamma" alone, three sub-bands exist** (slow ~30–50, mid ~50–90, fast ~90–150) — so even what looks like one band may decompose further.

**Synthesis**: bands are FUNCTIONALLY distinct (different spatial networks, different states, different content) but the underlying spectrum is mathematically continuous. The discreteness is at the LEVEL of which oscillator generates which band, not at the level of the spectral support.

**Substrate implication**: maps cleanly to our basin-discrete framing IF basins correspond to GENERATIVE-MECHANISM discreteness (different physical processes generating different timescales), not to gaps in spectral support. This is consistent with our internal framing — different basins = different attractors = different generators — but it shifts the load: the cascade depth is determined by HOW MANY GENERATIVE MECHANISMS exist, which is an architecture-class question.

### A3. Theta-gamma sub-cascade as a worked example

Lisman & Jensen working-memory model: theta phase modulates gamma amplitude with n:m ratios of 5:1 or 9:1 — i.e., 5–9 gamma cycles per theta cycle, mapped to ~4–7 working-memory item capacity (Miller's number). Each gamma burst within a theta cycle corresponds to a discrete memory item.

This is a CONCRETE example of cascade-depth = small integer (5–9) tied to functional consequence. But it operates within a single brain state (encoding/active maintenance) and doesn't speak to multi-state cascades like SO/spindle/ripple.

---

## (b) The three-level consolidation cascade: structural details

### B1. Measured frequencies and ratios (Staresina et al 2015, Nat Neuro PMC4625581)

Human hippocampal iEEG during slow-wave sleep:

| Band | Center freq | Detection range | Source/locus |
|---|---|---|---|
| SO | 0.75 Hz | 0.16–1.25 Hz | Neocortical (orbitofrontal lead) |
| Spindle | 14.5 ± 2.8 Hz | 12–16 Hz | Thalamo-cortical |
| Ripple | 86.8 ± 12.2 Hz (humans) / 140–200 Hz (rodents) | 70–110 Hz / 140–200 Hz | Hippocampal CA1/CA3 |

**Frequency ratios**: spindle/SO ≈ 19, ripple/spindle ≈ 6 (human) or 12 (rodent). These are NOT close to a constant log-ratio — the spindle-to-SO gap is much wider than ripple-to-spindle. So the N3L geometric-progression rule does NOT hold tightly for these three; they are picked out by functional specificity, not by a single universal log-ratio.

### B2. Phase-locking and nesting strength

- **SO-spindle**: spindle power +45.6% during SO up-states (p=0.003). Preferred phase clusters at SO up-state peak (V=7.78, p=0.0007). STRONG.
- **Spindle-ripple**: ripple power +17.9% around spindle centers (p=0.001). Preferred phase clusters at spindle troughs (V=5.71, p=0.009). MODERATE.
- **Triple coupling**: 24% of ripples occur in conjunction with both spindle and SO; chance level 8% (p<0.001). SPARSE but significantly above chance.

**Critical**: only ~6% of SOs trigger ripples (via spindles); only 21% trigger spindles. So the cascade is SPARSE/PROBABILISTIC, not deterministic. Most SOs do NOT propagate down the cascade. This is consistent with a SELECTIVE replay mechanism — only some content is consolidated per cycle.

### B3. Directional flow (Helfrich/Knight 2025 hierarchical cascade paper)

Orbitofrontal SO → thalamus & hippocampus → spindle generation on down-to-up transition → ripple generation during up-states.

Hippocampal ripple rate and coupled hippocampal-orbitofrontal ripples were the **strongest positive predictors of memory consolidation** in this cohort.

In epilepsy: epileptic spikes coupled to SO strongly DISRUPT spindles (compete with physiological spindles in thalamus) and impair consolidation. Discrete failure mode — knocking out one level (spindle) breaks the cascade rather than being compensated by other levels.

---

## (c) Causality — what's actually established vs correlational

### C1. Strong causal demonstrations

**Latchoumane et al 2017, Neuron** (the gold standard): Closed-loop optogenetics in mice. Stimulated thalamic spindles IN-PHASE with cortical SO up-state vs OUT-OF-PHASE.
- In-phase: increased triple coupling (SO-spindle-ripple), improved memory consolidation.
- Out-of-phase: no improvement (despite identical # of spindles induced).

This is the cleanest demonstration that the DISCRETE TEMPORAL STRUCTURE of the cascade — not the mere presence of oscillations — drives consolidation.

**Girardeau et al 2009, Nat Neuro**: Online detection of SWRs + closed-loop electrical disruption during post-training sleep. Disrupted-SWR group impaired on spatial reference memory task. Control disruptions (delayed) intact.

**Ego-Stengel & Wilson 2010, Hippocampus**: Similar SWR disruption protocol; spatial learning impaired.

### C2. Mixed / counter-evidence

**Yamamoto lab eLife 2023**: Disruption of AWAKE (not sleep) SWRs does not affect repeated-acquisition spatial memory. So SWR causality is state-specific (sleep > awake) and task-specific (initial learning > repeated practice).

**Optogenetic SWR BLOCKING (PMC5070819)**: Sleep-time SWR blockade did NOT interfere with formation of stable spatial representations in CA1 — challenging the necessity claim.

**Bayesian meta-analysis (eLife reviewed-preprint 101992, 2024)**: Aggregates 297 effect sizes from 23 studies on SO-spindle coupling-memory association.
- Coupling phase precision: r=0.07 [0.01, 0.13], BF=58
- Coupling strength: r=0.08 [0.02, 0.15], BF=111
- Spindle amplitude alone: r=0.07, BF=8

Translation: the COUPLING signal is statistically very robust (BF>100) but the EFFECT SIZE is small. Authors carefully say "predicts" not "causes" because they aggregate correlational studies. Causality must be inferred from the few optogenetic stimulation papers.

### C3. Compensation / cascade-robustness

When ONE band is disrupted, other bands do NOT seamlessly compensate — they fail. Epilepsy work (Helfrich 2025): thalamic spike intrusions compete with spindles, and the loss of spindles breaks the consolidation cascade rather than being routed around. This is DISCRETE failure (specific band ablation = specific deficit), not continuous degradation.

This is one of the strongest pieces of evidence for the cascade being TRULY discrete-functional, not just discrete-by-measurement-convention.

---

## (d) Replay timescale: spacing, refractoriness, content selectivity

### D1. Spindle refractoriness as the spaced-replay clock

Spindles recur every 3–4 seconds during trains → a slower mesoscale rhythm at 0.17–0.33 Hz. Inter-spindle intervals are REFRACTORY periods, mechanistically required to prevent interference between successive memory reactivations.

This is biology's version of "spaced replay" — discrete, narrowly-tuned interval between replay events (~3–4 s) rather than continuous replay.

**Implication for substrate replay design**: replay events should have an enforced refractory period, on the order of 3–10x the duration of a single replay event, to avoid interference between successively-replayed memories.

### D2. Sleep-stage selectivity of content

Dual-process hypothesis (older but still useful):
- SWS / NREM (slow-osc + spindle + SWR cascade): **declarative/spatial/episodic** memory consolidation.
- REM (theta + acetylcholine): **procedural** memory, schema integration, emotional memory.

Sequential hypothesis (refined): both stages contribute via cyclic alternation. SWS does the declarative initial transfer; REM does the integration/schema-binding.

**Implication**: there are TWO discrete consolidation modes (SWS-cascade vs REM-theta), not one, with different content selectivity. The substrate's replay design should distinguish "declarative-style" (high-frequency, fast-burst, hippocampal-style) vs "procedural-style" (sustained theta, slower) replay regimes.

### D3. Content selectivity within SWR

- SWRs preferentially replay RECENT experience (Wilson & McNaughton 1994 onward).
- SWR content "tags" experience for consolidation — replayed-in-awake-SWR content is preferentially replayed-in-sleep-SWR (Karlsson & Frank 2009 line).
- SWRs link to verbal report of recall in humans (Norman et al 2019 Science).
- Compressed replay: 20x faster than encoding-time experience (a 1-sec trajectory replayed in ~50 ms).

**Implication**: substrate replay should support COMPRESSED (~10–20x) playback of stored sequences, with selectivity gated by recent-experience tags.

---

## (e) Gating: SWR-theta anticorrelation

### E1. State exclusivity

**SWRs and theta are mutually exclusive brain states**:
- Walking/exploring rat: theta dominant, SWR rate near zero.
- Stationary/resting/SWS rat: SWR dominant, theta near zero.

This is a HARD STATE GATE — not a continuous balance. The brain switches REGIMES rather than mixing them.

### E2. Functional logic

- During exploration (theta): ENCODE new experiences into hippocampus.
- During quiet rest/sleep (SWR): REPLAY stored experiences for consolidation/retrieval/planning.

So the gate enforces a DUAL-MODE architecture: encoding-mode and consolidation-mode never overlap. This prevents new encoding from interfering with replay-driven consolidation (or vice versa).

### E3. Sirota line (cortico-hippocampal coupling)

Sirota et al 2008 (Neuron) — neocortical neurons & gamma oscillations are entrained by hippocampal theta during exploration. So in the encoding-mode, the cortico-hippocampal coupling is THETA-mediated; in consolidation-mode, it's SO-spindle-ripple-mediated. Two distinct coupling regimes for two distinct functional states.

**Implication for substrate**: replay subsystem should be GATED by a binary state-variable (encoding-mode vs replay-mode), not a continuous mixing of both. Mixing would predictably cause interference (and is what gets observed in disease states e.g. Alzheimer's, schizophrenia).

---

## (f) Falsifiable predictions with hard-fail bands

### Pred-1: Discrete cascade depth N=3 is special in substrate replay
**Setup**: Compare substrate continual-learning performance with replay cascades of depth N ∈ {1, 2, 3, 4, 5, 6} (single-timescale → six nested timescales).
**Prediction**: N=3 achieves >X% of N=6 performance while costing <50% of N=6 compute. Performance curve has a KNEE at N=3, not smooth sqrt(N) scaling (which would be the PT-physics-predicted shape).
**Hard-pass (HP)**: N=3 within 5% of N=6 final accuracy, and N=2 is >15% behind N=3.
**Hard-fail (HF1)**: N=3 is within 5% of N=2 (no benefit of going from 2 to 3 levels — knee is at N=2 or below; cascade-depth-3 is not special).
**Hard-fail (HF2)**: Performance scales smoothly as sqrt(N) with no knee (continuous scaling like PT physics; biology's discreteness doesn't transfer to substrate).
**Hard-fail (HF3)**: N>3 keeps improving linearly (no diminishing returns at N=3; cascade depth optimum is somewhere else).
**Middle band**: N=3 beats N=2 by 5–15% and N=6 beats N=3 by 5–15% — partial support for discreteness, but optimum unclear.

### Pred-2: Frequency-ratio of ~6x and ~12x between adjacent levels is special
**Setup**: With N=3 cascade, sweep adjacent-level timescale ratios r ∈ {2, 3, 5, 6, 10, 12, 20, 50}.
**Prediction**: Biology uses ratio ~6 (spindle/ripple in human) or ~12 (in rodent) between fastest two levels, and ~19 (SO/spindle) between slowest two. Substrate should mirror — sweet spot at ratio ~10 ± 5 between adjacent levels, NOT at r=2 (which is biology's lowest-order log-ratio between same-band sub-divisions) and NOT at r=50+ (which is order-of-magnitude separation beyond what biology uses).
**Hard-pass**: Best performance at r ∈ [5, 15]; performance at r=2 and r=50 each >10% below.
**Hard-fail (HF1)**: Performance monotonically increasing in r (no sweet spot — bigger is always better, contradicting biology).
**Hard-fail (HF2)**: Performance flat across r (no sensitivity to ratio at all — biology's ratio precision is epiphenomenal in our substrate).
**Middle band**: Sweet spot exists but at r outside [5, 15] — e.g. at r=3 or r=25 — partial corroboration with different scaling.

### Pred-3: Triple-coupling timing matters (Latchoumane-analog)
**Setup**: In substrate with N=3 cascade, compare PHASE-LOCKED replay (level-3 events triggered only during level-2 active phase, level-2 only during level-1 up-phase) vs PHASE-RANDOM replay (same event rates, random relative phase).
**Prediction**: Phase-locked condition outperforms phase-random by >15% on consolidation metric — DISCRETE timing structure matters, not just event rate.
**Hard-pass**: Phase-locked > random by 15% on declarative-style task; effect replicates with 3 seeds.
**Hard-fail (HF1)**: Phase-locked indistinguishable from random (Latchoumane optogenetic effect does NOT transfer — substrate replay is content-driven, not timing-driven).
**Hard-fail (HF2)**: Random outperforms locked (substrate has different optimal structure than biology).

### Pred-4: Inter-replay refractory ~3–10x event duration
**Setup**: Sweep inter-replay-interval τ_ref ∈ {0.5x, 1x, 3x, 10x, 30x} the duration of single replay event.
**Prediction**: Performance peaks at τ_ref ∈ [3x, 10x] (biology's spindle refractoriness ratio). Shorter τ causes interference; longer τ wastes capacity.
**Hard-pass**: Peak performance in [3x, 10x] band, with >10% degradation at 0.5x and at 30x.
**Hard-fail (HF1)**: Monotonic — shorter is always better (interference is not a real failure mode in substrate).
**Hard-fail (HF2)**: Monotonic — longer is always better (no upper bound; substrate doesn't benefit from spaced replay).

### Pred-5: Dual-mode gating beats mixed-mode
**Setup**: Compare HARD-GATED replay (encoding-OFF during replay, replay-OFF during encoding — biology's SWR-theta exclusion) vs MIXED replay (concurrent encoding + replay with reduced rates).
**Prediction**: Hard-gated outperforms mixed by >10% on a continual-learning interference benchmark.
**Hard-pass**: Hard-gated > mixed by 10% with stable advantage across 3 seeds.
**Hard-fail (HF1)**: Mixed matches or beats hard-gated (substrate doesn't suffer encoding-replay interference; biology's gating is overkill).
**Hard-fail (HF2)**: Both fail differently (e.g., gated suffers under-utilization, mixed suffers interference; partial-mix outperforms both extremes).

---

## (g) Confidence summary, with calibration penalty applied

| Claim | Raw P | Penalty | Final P | Notes |
|---|---|---|---|---|
| Brain oscillations are discrete bands with log-spacing (N3L) | 0.85 | -0.20 | 0.65 | Empirical pattern; 1/f critique exists |
| 3-level SO/spindle/ripple cascade is functionally discrete | 0.75 | -0.20 | 0.55 | Could be measurement convenience; ultra-slow & infraslow exist |
| Causality of cascade structure (Latchoumane optogenetic) | 0.70 | -0.10 | 0.60 | Single best experiment; replicated in spirit but not exact protocol |
| SWR-theta state gating is real & functional | 0.85 | -0.15 | 0.70 | Well-established phenomenology |
| Cascade DEPTH=3 is OPTIMAL (not just MEASURED) | 0.50 | -0.05 | 0.45 | At novel-synthesis cap; cannot be tested in biology |
| Spindle refractoriness implies spaced-replay optimum | 0.65 | -0.20 | 0.45 | Inferential leap from biology to substrate |
| Substrate inherits biology's discrete-depth advantage | 0.50 | 0.00 | 0.50 | At novel-synthesis cap per role contract |

---

## (h) What this means for the basin-discrete framing

Biology corroborates DISCRETENESS but not OPTIMALITY-AT-N=3. The cascade depth that exists in biology is causally engaged (Latchoumane in-phase vs out-of-phase). But biology never tested a 4th level, a 5th level, or N=2.

**Net effect on basin-discrete framing**:
- **Positive**: discrete cascades exist in nature, are causally important, and don't smoothly degrade when one level is removed (epilepsy work). This is qualitatively different from PT physics's smooth sqrt(N) curve.
- **Neutral-to-negative**: the OPTIMAL depth is not biology's job to answer. We still need substrate-side ablations (Pred-1) to find the knee.
- **New insight**: the 3-level cascade has SPECIFIC FREQUENCY RATIOS (~6x and ~19x in human, ~12x and ~19x in rodent) that are NOT the simplest log-ratio. The cascade is engineered, not generic. This suggests substrate's cascade design should also use NON-UNIFORM ratios between levels — not r=2 everywhere.

---

## (i) Open questions deferred to next drill

1. **Why is spindle/SO ratio (~19x) much larger than ripple/spindle ratio (~6x)?** Is the larger gap between SO and spindle related to a SYSTEMS-LEVEL bandwidth difference, or to dual generators (thalamic for spindle, cortical for SO)? Reading: thalamocortical loop dynamics.
2. **REM-theta consolidation cascade**: parallel cascade for procedural memory. Has it been characterized as discrete or continuous? Worth a parallel drill if substrate adds procedural-style replay.
3. **Ultra-slow oscillation (~0.1 Hz) as a 4th cascade level**: Watson, Lewis, others have argued infra-slow rhythms gate full-sleep-cycle consolidation. If true, biology's cascade may be N=4, not N=3 — and substrate's optimal depth correspondingly larger.
4. **Mathematical model of discrete-cascade optimality**: is there a theoretical reason (information-theoretic, dynamical-systems) why discrete cascades beat continuous ones for replay? The PT drill showed physics gives no such reason. Maybe biology's reason is REFRACTORINESS (each level has its own refractory period, creating natural temporal segregation). Worth investigating: connection to interval-coding / multiplexed time-codes.

---

## (j) Recommendation: file companion handoff to exp_dev

**Verdict on actionability**: findings are concrete enough to propose specific replay-design parameters. Filing companion handoff `strategy_request_to_exp_dev_swr_cascade_design_2026-05-24.md`.

Suggested experimental anchors (not specified here — Strategy and exp_dev own that translation; this file provides only the science synthesis):
- Cascade-depth sweep N ∈ {1, 2, 3, 4, 6} on a continual-learning benchmark (Pred-1).
- Frequency-ratio sweep at fixed N=3 (Pred-2).
- Phase-locked vs phase-random replay (Pred-3).
- Inter-replay refractory sweep (Pred-4).
- Hard-gate vs mixed-mode replay (Pred-5).

Note: per role contract, this file does NOT specify exact sweep grids, anchor names, queue choice, or HF1/HF2/HF3 numerical bounds in substrate units — only the falsifiable structure. exp_dev translates to substrate units when designing.

---

## Sources

Web-search synthesis. Key references:

- [Penttonen & Buzsaki 2003 — Natural logarithmic relationship between brain oscillators](https://www.sciencedirect.com/science/article/abs/pii/S1472928803000074) — N3L law foundation
- [Staresina et al 2015 Nat Neuro — Hierarchical nesting of slow oscillations, spindles and ripples in the human hippocampus during sleep (PMC4625581)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4625581/) — main human iEEG cascade paper
- [Latchoumane et al 2017 Neuron — Thalamic Spindles Promote Memory Formation during Sleep through Triple Phase-Locking](https://www.cell.com/neuron/fulltext/S0896-6273(17)30549-4) — optogenetic causality gold standard
- [Girardeau et al 2009 — Selective suppression of hippocampal ripples impairs spatial memory](https://pubmed.ncbi.nlm.nih.gov/19749750/) — SWR causality classic
- [Bayesian meta-analysis (eLife reviewed-preprint 2024) — Does slow oscillation-spindle coupling contribute to memory consolidation?](https://elifesciences.org/reviewed-preprints/101992) — BF=58–111, r~0.07
- [Helfrich/Knight et al 2025 — A hierarchical cascade of sleep rhythms drive memory consolidation in humans and are disrupted in epilepsy](https://pubmed.ncbi.nlm.nih.gov/40654700/) — discrete failure in epilepsy
- [How coupled slow oscillations, spindles and ripples coordinate neuronal processing — Nat Neuro 2023](https://www.nature.com/articles/s41593-023-01381-w) — recent review
- [Buzsaki — The hippocampal sharp wave-ripple in memory retrieval for immediate use and consolidation, Nat Rev Neuro 2018](https://www.nature.com/articles/s41583-018-0077-1) — SWR review
- [Sleep spindle refractoriness segregates periods of memory reactivation (PMC5992601)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5992601/) — spaced-replay clock
- [Optogenetically Blocking Sharp Wave Ripple Events in Sleep Does Not Interfere (PMC5070819)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5070819/) — counter-evidence on SWR necessity
- [Disruption of awake sharp-wave ripples does not affect memorization (eLife 2023)](https://elifesciences.org/articles/84004) — state-specific SWR causality
- [Cross-frequency phase-phase coupling between theta and gamma oscillations](https://www.jneurosci.org/content/32/2/423) — theta-gamma sub-cascade
- [Brain rhythms define distinct interaction networks (PMC8639786)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8639786/) — discrete-bands-vs-continuum review
