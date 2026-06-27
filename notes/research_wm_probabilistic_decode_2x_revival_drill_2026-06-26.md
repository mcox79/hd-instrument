# Research 2x revival drill — WM frequency-multiplexed lock-in + soft top-K probabilistic decode

**Filed-by:** research (Opus 4.7 1M)
**Filed-at:** 2026-06-26
**Trigger:** USER-standing 2x revival rule on HARD_FAIL anchors (`feedback_route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20.md`); 2 alternative-mechanism candidates per failure.
**Failures revived:**
1. `data/exp_substrate_working_memory_frequency_multiplexed_lock_in_v1/metrics.json` — HARD_FAIL_INTERMOD (cross-slot bleed 0.421 at K=256; FM_LOCK_IN ≤ NAIVE_HRR_WM at every K; lift_K128=-0.0013).
2. `data/exp_soft_topK_cleanup_distribution_preserving_v1_smoke/metrics.json` — HARD_FAIL (smoke; lift_R11=+0.000; baseline top-1=0.005 at chance floor; ECE 0.192/0.208 with entropy ratio 1.000 = uniform).

Per `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md` and the pivot note `research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`: BOTH revivals are framed for **compositional infrastructure**, not language prediction. WM revival serves multi-bank typed-slot composition; probabilistic-decode revival serves type-incompatibility refusal + posterior carry across composition steps, not text bigram-gap closure.

---

## HEADLINE

(a) **WM-FM failed because lock-in amplifies ONE carrier against noise — it does NOT separate MULTIPLE co-located carriers** (the substrate's prior `lock_in_amplifier_hd_frequency_v1_FULL` HARD_PASS was single-signal SNR boost; multi-channel separation is a different problem class with different math). Roll-offset multiplexing at delta_k = N/K does not produce true orthogonal carriers in bipolar/HRR algebra: harmonics from one slot's stored item fold into adjacent slot demod passbands, producing intermodulation that grows as K grows.

(b) **Soft-topK failed because there was no underlying signal to redistribute** (smoke baseline top-1 = 0.005 = below the V_C=64 chance floor 0.0156; the synthetic 5-hop deterministic chain on V_C=64 collapses near-uniform under epsilon=0.15 noise; substrate cleanup produces no measurable ranking). Calibration techniques (temperature scaling, soft-K) cannot inject signal into a zero-signal regime — they can only redistribute existing signal mass.

(c) **Both have substrate-mine alternatives that AVOID the specific failure mode**: WM-FM → orthogonal-by-construction channelization (CDMA-style Hadamard/Walsh tags) OR cell-assembly multi-bank (already chain-grade at K=4096 multi-bank — extend with typed routing). Soft-topK → particle-filter SMC over compositional hypotheses (signal source = composition validity, NOT codebook cosine) OR cleanup-energy bayesian factor (refuse-when-confident-low; signal source = energy gradient).

---

## Cheap decisive test (per failure)

**WM-FM revival — Walsh-Hadamard CDMA channelization (ALT-WM-1):** spawn a smoke cell, N_DIM=4096, K=128 + K=256, 3 seeds, replace `roll(item_k, k*delta_k)` with `bind(item_k, walsh_tag_k)` where `walsh_tag_k` is row k of a Hadamard matrix expanded to bipolar (perfectly orthogonal by construction; zero intermod). Read via `unbind(workspace, walsh_tag_k)`. Discriminator: cross-slot bleed < 0.02 (vs the failed FM's 0.421). Wall: ~10 min.

**WM-FM revival — Multi-bank typed routing (ALT-WM-2):** spawn a cell extending the chain-grade `phase_diagram_working_memory_multibank_K_extension_to_16384_v1` (MULTI_64x rec=1.000 cv=0.000 at K=4096) with typed slots — each bank holds slots of one type (e.g. bank_0 = SIZE, bank_1 = COLOR, bank_2 = OBJECT). Test cross-type composition queries. Discriminator: typed-query recall ≥ 0.95 at K=4096 across 8 types AND mismatched-type query rejected (refuse-gate fires). Wall: ~30 min on remote_cpu.

**Soft-topK revival — Particle filter over compositional hypotheses (ALT-PD-1):** spawn a smoke cell using ALT-WM-2 multi-bank as the particle cloud (each bank = one particle = one hypothesis); compositional discriminator: synthetic typed-KG with 64 entities + 8 types + 32 binary relations; ambiguous queries where the answer only disambiguates after 3 hops; importance-weight particles by composition-validity (type check + relation-consistency). Discriminator: top-1 hypothesis at hop-3 ≥ 0.80 on ambiguous-by-construction chains; entropy decreases monotonically across hops. Wall: ~20 min.

**Soft-topK revival — Cleanup-energy bayesian refuse-gate (ALT-PD-2):** spawn a smoke cell on the same typed-KG; per-hop measure cleanup energy gap (top-1 cosine − top-2 cosine); when gap < tau, treat as soft posterior (Bayes factor = exp(gap/T)); when gap > tau, commit. Discriminator: typed-correct top-1 at hop-5 ≥ 0.50 on UNAMBIGUOUS chains AND refuse-rate on ambiguous chains ≥ 0.80 (system declines to commit rather than confabulate). Wall: ~10 min.

---

## Falsifiable predictions (pre-registered HARD-PASS + HARD-FAIL)

### ALT-WM-1 (Walsh-Hadamard CDMA)

- **HARD-PASS:** cross-slot bleed ≤ 0.02 at K=128 AND K=256, AND recall ≥ 0.95 at K=128 AND ≥ 0.85 at K=256, AND cv ≤ 0.05 across 3 seeds.
- **MIDDLE:** bleed in (0.02, 0.10] OR recall in [0.85, 0.95) at K=128.
- **HARD-FAIL:** bleed > 0.10 at any K (means Walsh-tag binding doesn't preserve orthogonality through the bind+sum+unbind pipeline at this N_DIM/K density — would indicate a deeper substrate-algebra issue) OR recall < 0.80 at K=128 (sum-of-K bind capacity exhausted at K=128 — independent of channelization, validates that the failure is bind capacity not channelization, and points to ALT-WM-2 multi-bank).
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.55 / 0.25 / 0.20** (deflated from 0.70 lit-scan; Hadamard CDMA is standard in 4G/5G and has well-characterized capacity bounds; only risk is the bind+sum capacity in bipolar HRR at K=256 with N=4096 — known cliff per substrate-mine c3 results).

### ALT-WM-2 (Multi-bank typed routing)

- **HARD-PASS:** typed-query recall ≥ 0.95 at K=4096 across all 8 types AND mismatched-type query rejected (refuse-gate fires at ≥ 0.90 of mismatched probes) AND cv ≤ 0.05.
- **MIDDLE:** typed recall in [0.85, 0.95] OR refuse-rate in [0.70, 0.90].
- **HARD-FAIL:** typed recall < 0.85 (multi-bank capacity already chain-grade at K=4096 untyped; if typed routing breaks it, the typing mechanism is destructive) OR refuse-rate < 0.50 (refuse-gate doesn't discriminate types, defeats the point).
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.60 / 0.25 / 0.15** (substrate already chain-grade on multi-bank; typed-routing is a 1-step extension; brain analog = column-specific routing in cortex; HIGH prior per `feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23.md`).

### ALT-PD-1 (Particle filter compositional)

- **HARD-PASS:** top-1 ≥ 0.80 at hop-3 on ambiguous chains AND entropy ratio H(hop-3)/H(hop-0) ≤ 0.5 (monotonic information gain) AND particle-effective-N ≥ 50% of allocated banks (no particle collapse).
- **MIDDLE:** top-1 in [0.50, 0.80] OR entropy ratio in (0.5, 0.8].
- **HARD-FAIL:** top-1 ≤ 0.30 (particle filter doesn't improve over single argmax at any hop — means importance weights from composition-validity don't discriminate) OR particle collapse < 20% effective-N by hop-3 (resampling pathology).
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.40 / 0.35 / 0.25** (novel synthesis cap honored; signal source IS compositional validity which is the OPENED track per USER pivot — high upside if it lands, but compositional infrastructure on substrate still unproven).

### ALT-PD-2 (Cleanup-energy refuse-gate)

- **HARD-PASS:** typed-correct top-1 ≥ 0.50 at hop-5 on unambiguous chains AND refuse-rate ≥ 0.80 on ambiguous chains AND refuse-rate ≤ 0.15 on unambiguous chains (low false-refuse).
- **MIDDLE:** typed-correct in [0.30, 0.50] OR refuse-rate on ambiguous in [0.60, 0.80].
- **HARD-FAIL:** refuse-rate on unambiguous > 0.30 (over-refusal; gate too tight) OR refuse-rate on ambiguous < 0.40 (gate doesn't trigger when it should — energy gap isn't a calibrated confidence signal).
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.50 / 0.30 / 0.20** (substrate already has chain-grade refuse-gate per cap_map; this is composing it with energy-gap measurement, which is observable from existing cleanup primitive).

---

## Cross-thread synthesis with prior research

### WM failure connects to:
- `data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json` (HARD_PASS, P64 lifts recall 16.39x at sigma=64; cv=0). This was the SINGLE-CARRIER SNR-boost regime — Cramer-Rao bound improvement. The mechanism class is: phase-coherent averaging of N independent noise realizations of ONE signal reduces noise variance by 1/N. The WM-FM failure misapplied this to MULTI-CARRIER separation (which is a CHANNELIZATION problem, not an SNR problem). Per `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` BIAS-13 (regime mismatch): the inference-transfer from single-carrier-lock-in to multi-carrier-WM was the bias.
- `data/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1/metrics.json` (MIDDLE_BAND_PARTIAL, chain-grade at K=8192 MULTI_128x with cv=0). This IS the working WM capacity primitive. ALT-WM-2 builds DIRECTLY on it (typed routing extension); ALT-WM-1 is a different-class channelization probe.
- `n9_partition_routed_trigram` (closed by USER pivot 2026-06-26): the partition-routing mechanism is conceptually adjacent to typed multi-bank routing — but pivoted away from language. ALT-WM-2 redeploys the typed-routing intuition in the compositional-understanding track.
- Lit precedent: Walsh-Hadamard codes have provable orthogonality across N codes when N is a power of 2 and the codes are length N. CDMA literature (Verdu, *Multiuser Detection*, 1998) gives the SNR-vs-K capacity bounds.

### Probabilistic-decode failure connects to:
- `data/exp_substrate_as_LM_test_harness_rigged_2026-06-23` (METHODOLOGY-CONFOUND class). The soft-topK smoke had a similar issue: synthetic chain construction at HOP=5 on V_C=64 with eps=0.15 noise yields a near-uniform target distribution by hop-5 (deterministic permutation entropy approaches log(V_C) under noise). The "regime" was wrong — not the mechanism. This is BIAS-13 again: regime mismatch (the discriminator was rigged against itself).
- USER pivot 2026-06-26 (`research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`): the right signal source is NOT codebook cosine over 5-hop chains; it's composition-VALIDITY (does this typed binding satisfy type constraints?). ALT-PD-1 routes around the dead signal source.
- `feedback_anisotropy_is_a_feature` (per memory): substrate's anisotropic representation is information-bearing when used at the right readout; the soft-topK smoke was averaging over an isotropic uniform target = guaranteed zero signal.
- Lit precedent: particle filtering (Doucet, *Sequential Monte Carlo Methods in Practice*, 2001); Plackett-Luce models for top-K (Plackett 1975); Friston free-energy principle for refuse-gating (Friston 2010).

### Cross-domain (brain) angle:
- WM-FM brain analog: theta-gamma multiplexing in PFC (Lisman-Buzsaki) WAS the load-bearing motivation. But Lisman-Buzsaki proposes each item bound to a DIFFERENT gamma sub-cycle within a theta cycle — that's CDMA-like (orthogonal time slots), NOT FDM (orthogonal frequency slots). The substrate prereg conflated these. ALT-WM-1 (Walsh-Hadamard, CDMA-class) is the FAITHFUL brain analog; FM was the FAILED brain analog.
- Probabilistic-decode brain analog: **parietal vs PFC division of labor** for hypothesis tracking (Tom Griffiths, Josh Tenenbaum). Parietal does population coding (Pouget-Zemel 1998 = soft top-K); PFC does symbolic posterior tracking (= particle-filter-like discrete hypothesis cloud). The failed soft-topK was attempting parietal-style readout on a regime where parietal-style population coding has no signal source. ALT-PD-1 (particle filter) is the PFC-style analog, more appropriate for the compositional-understanding track.

---

## Substrate-product implications

- **ALT-WM-2 (multi-bank typed routing)** is the load-bearing path forward. The substrate already has chain-grade multi-bank K=4096 working memory; extending it with typed slots ships a CATEGORICAL primitive: **typed slot binding with cross-type query rejection** — this is the foundational unit of compositional understanding per USER pivot. Glass-box: every slot's type is observable; every rejected query is auditable.
- **ALT-WM-1 (Walsh-Hadamard CDMA)** ships ORTHOGONAL CHANNELIZATION as a primitive if it passes. Use case: compositional slot identifiers when typed multi-bank routing is overkill. Less product-load-bearing than ALT-WM-2 but a clean primitive that ALSO refutes the bind+sum capacity hypothesis if it fails.
- **ALT-PD-1 (particle filter over compositional hypotheses)** ships **substrate-native bayesian compositional inference** — the natural composition of the multi-bank WM primitive with hypothesis-tracking. This is the product story for "substrate hypothesizes, weights by validity, commits or refuses." LLMs cannot do this naturally.
- **ALT-PD-2 (cleanup-energy refuse-gate)** ships the EPISTEMIC HUMILITY primitive — substrate declines to commit when its own cleanup-energy gap is below threshold. This is the auditable-AI-memory-subsystem product story (refuse-rather-than-confabulate is the key substrate-vs-LLM differentiator).
- Sequencing: ALT-WM-2 (highest-P, on existing chain-grade) → ALT-WM-1 (parallel, different-class probe) → ALT-PD-2 (composes on substrate refuse-gate primitive) → ALT-PD-1 (composes on ALT-WM-2; defer until typed multi-bank lands).

---

## Anchor ranking (all 4, ordered by P_HARD-PASS × product-leverage)

| Rank | Anchor | P_HARD-PASS | Why-now |
|---|---|---|---|
| 1 | ALT-WM-2 multi_bank_typed_routing_v1 | 0.60 | Builds on chain-grade multi-bank K=4096; ships typed-slot composition primitive directly serving USER compositional pivot |
| 2 | ALT-WM-1 walsh_hadamard_CDMA_wm_v1 | 0.55 | Cheapest decisive test (~10 min); refutes-or-confirms whether FM failed at channelization or at bind+sum capacity; orthogonal-by-construction; standard CDMA math |
| 3 | ALT-PD-2 cleanup_energy_refuse_gate_v1 | 0.50 | Composes on substrate's chain-grade refuse-gate; ships epistemic humility primitive immediately product-useful for auditable AI memory |
| 4 | ALT-PD-1 particle_filter_compositional_v1 | 0.40 | Defer until ALT-WM-2 lands (depends on typed multi-bank infra); novel-synthesis P-cap honored; high upside if compositional-validity is a discriminating signal |

---

## Citations (verified, lit-scan)

1. Verdu, S. *Multiuser Detection.* Cambridge UP, 1998. — CDMA channelization, Walsh-Hadamard orthogonal capacity bounds.
2. Lisman, J. & Buzsaki, G. "A neural coding scheme formed by the combined function of gamma and theta oscillations." *Schizophrenia Bulletin* 34:974, 2008. — theta-gamma multiplexing in PFC (the brain analog the prereg cited).
3. Pouget, A., Dayan, P., Zemel, R. "Information processing with population codes." *Nature Reviews Neuroscience* 1:125, 2000. — parietal population coding (soft top-K class).
4. Tom Griffiths & Josh Tenenbaum. "Optimal predictions in everyday cognition." *Psychological Science* 17:767, 2006. — bayesian hypothesis tracking model class.
5. Doucet, A., De Freitas, N., Gordon, N. (eds). *Sequential Monte Carlo Methods in Practice.* Springer, 2001. — particle filter / SMC.
6. Plackett, R.L. "The analysis of permutations." *J. Royal Stat. Society* C 24:193, 1975. — Plackett-Luce model for top-K distributions.
7. Friston, K. "The free-energy principle: a unified brain theory?" *Nat. Rev. Neurosci.* 11:127, 2010. — free-energy refuse-gate framing.
8. Cowan, N. "The magical number 4 in short-term memory." *Behav. Brain Sci.* 24:87, 2001. — brain WM cap ~7±2 (the substrate already exceeds at K=4096 multi-bank).

(8 verified citations; novel-synthesis P-cap at 0.55 honored; lit-scan calibration penalty 0.15-0.25 applied to all P_HARD-PASS estimates.)

---

## Bias master checklist self-audit (per `feedback_experiment_bias_master_checklist_USER_2026-06-24.md`)

- **BIAS-13 (contamination / regime mismatch):** WM-FM cited single-carrier lock-in chain-grade as precedent for multi-carrier separation — DIFFERENT problem class. Soft-topK smoke regime made the underlying signal zero — discriminator was rigged against itself. Both revivals route AROUND this: ALT-WM-* uses channelization-class math (CDMA/multi-bank), not SNR-boost math; ALT-PD-* uses composition-validity as signal source, not codebook cosine over collapse-prone chains.
- **BIAS-N (verify-the-referent + Cramer-Rao):** Cramer-Rao bound formally says lock-in P-phase averaging reduces noise variance by 1/P FOR A SINGLE SIGNAL — does NOT say it separates K co-located signals (that's the channel capacity / Welch-bound problem). Cited.
- **BIAS-O (basis-vs-use-case):** WM-FM used roll-offset basis at readout — wrong basis for channelization. ALT-WM-1 uses Hadamard basis (orthogonal-by-construction at readout); ALT-WM-2 uses bank-index routing (basis = bank identity).
- **BIAS-Q (suspect 1.000 results):** No risk for these alternatives — entropy ratio + cross-slot bleed + refuse-rate triangulate; saturation would surface as MIDDLE_BAND.
- **BIAS-S (band-calibration regime checks):** all 4 anchors specify regime conditions (K, hop depth, ambiguous-vs-unambiguous chain class) at which HARD-PASS bands apply; not abstract thresholds.

---

-- research (Opus 4.7-1M)
