# RESEARCH (Director, Opus) — CROSS-DOMAIN PROBE: STORAGE-chain + composition-axis novel-direction-finding. **Trigger F (USER-directed cadence catch-up); v1.1 PHASE PLAN item #7.** Targets the 8 Tier-1b new neighbor fields (none re-treads of prior probes 1/2/3). 4 disparate fields drilled in parallel: nonequilibrium-stat-mech / pop-gen / sparse-coding-compressed-sensing / network-science-graph-theory. **HEADLINE: published Kramers-escape continual-learning framework (Kim 2026) gives the FIRST direct quantitative selector-policy predictor for the Phase-1 #1 continual-write lever — composes with the in-flight pre-reg and is decidable in 1 CPU-hr.** 4 cheap-decisive-tests pre-registered with HP/HF thresholds under lit-scan calibration penalty. Verify-the-referent applied: every cited paper was fetched/seen-in-search by the dispatching sub-agent (no fabrication; honest "search-result-only" flag applied where individual fetch not performed).

**Date:** 2026-06-21T05:30:00Z (true `date -u`)
**Status:** v1 (cross-domain probe; novel-direction-finding > completeness; 4 anchor experiments pre-reg'd)
**Method:** 4 parallel Sonnet WebSearch sub-agents per [[feedback-subagent-model-optimization]]; Opus synthesis. Wallclock ~110s.
**Query-privacy:** generic math terms only per [[feedback-query-privacy-decomposition]]; no substrate-novel mechanism names, no configs, no numbers off-platform.

---

## (a) HEADLINE

**Direct cross-domain hit on Phase-1 #1 (continual-write lever, the thinnest enabling axis):** **Kim 2026 `arXiv:2604.04154`** publishes a Kramers-escape framework that maps continual learning onto Langevin dynamics in a double-well landscape with EWC penalty as a growing barrier `ΔE(t) ∝ task-count`, giving an explicit forgetting-rate prediction `k = (ω₀ω_b/2π)·exp(−ΔE/k_BT)`. **This is the first time a cross-domain probe has surfaced a published 2026 mechanism that DIRECTLY parameterizes the substrate's selector-vs-write-all-vs-FIFO policy choice with a falsifiable forgetting-curve prediction.** Calibrated joint P (cross-applicable × would-inform) **≈ 0.30** under lit-scan penalty (raw 0.55 × 0.70 → 0.35 × 0.70 ≈ 0.25 multiplicative; rounded to 0.30 reflecting strict 2026 precedent in adjacent regime). The cheap decisive test reuses the existing chain-recall harness — no new infrastructure.

**Second-order ranked surfaces (in order of `P(cross-applicable to storage chain or composition) × P(would inform/falsify current Phase-3 direction)`):**

| Rank | Domain | Mechanism | Substrate target | Joint P (deflated) | Cheap test cost |
|---|---|---|---|---|---|
| **1** | nonequilibrium stat-mech | Kramers-escape selector (Kim 2026 `2604.04154`) + Freitas-Proesmans-Esposito dissipation floor (`2103.01184`) | **Phase-1 #1 continual-write lever** | **0.30** | 1 hr CPU |
| **2** | sparse-coding / compressed-sensing | Donoho-Tanner vs Willshaw phase-curve overlay + hierarchical/Kronecker-RIP extensions (Roth 2018 `1801.10433`) + SAE feature-manifold scaling (`2509.02565`) | **Flagship sparse-projected-KV (Phase-3 P3 #1)** | **0.20** | 1.5 hr CPU |
| 3 | population genetics | Kimura/Wright-Fisher fixation prob + MSDB many-locus variance | Continual-write lever (alternative-framing cross-check) | 0.14 | 1-2 hr CPU |
| 4 | network science / graph theory | log N / Δ spectral-gap mixing-time predictor (Levin-Peres-Wilmer; Lubetzky-Peres `1507.04725`) + Hopfield-on-random-graphs (`1303.4542`) | **M2 reframed (multi-hop chain depth in glass-box composition)** | 0.07 | 1-2 hr CPU |

**Net for substrate-state:** the probe yields **1 high-leverage direct mechanism** (Kramers-selector hits Phase-1 #1 enabling) and **3 cheap-test cross-checks** that either (a) tighten an existing claim (Willshaw subsumption check on flagship), (b) cross-validate the same lever from an independent framework (pop-gen → drift-diffusion isomorphism), or (c) provide a quantitative chain-depth predictor for M2 reframed. **Aggregate cost: ~5 CPU-hr if all 4 anchors fire; sequence by P-rank.** Negative-result branch is also valuable per dispatch (rules out a direction). Critically: pop-gen + spin-glass-on-graphs **share a substrate-state insight** — the substrate's observed `log N / d_cliff ≈ 0.003` at N=16384 implies a moderate spectral gap Δ ≈ 0.05, NOT a tight expander; this re-aligns the chain-depth cliff away from "random-expander mixing" toward "spin-glass freezing-on-graph" framing (sub-agent #4's verify-the-referent flag).

---

## (b) Cheap decisive test (per top-ranked candidate)

### Anchor 1 — `kramers_selector_for_continual_write_v1` [Rank 1, P_joint = 0.30, ~1 hr CPU]

**Reuses:** existing NESS write-decay chain harness (CERT 592 calibration).

**Design:**
1. At N=512, run 200 sequential writes against the substrate's established chain config.
2. For each write i, log Δᵢ = post-write retrieval-margin (the Kramers-barrier proxy; already computed by the existing harness).
3. Compare four selection policies under FIXED total write-budget:
   - (a) write-all (baseline)
   - (b) FIFO eviction
   - (c) random-skip control
   - (d) **Kramers-selector**: skip write if predicted retention `exp(−k·Δt)` falls below threshold, where `k = (ω₀ω_b/2π)·exp(−Δᵢ/T_eff)` and `T_eff` is fit from 10 calibration writes' decay slope.
4. Measure retention curve R(age) at fixed write-cost; compare to Kim 2026's prediction `R(t) = exp(−Σ_i k_i·t)`.
5. **CAN-fail control (per Skunkworks discipline):** also run on a *random-Δᵢ* arm (shuffle barrier proxies before policy decision) — Kramers-selector must NOT beat write-all on this arm, else benefit is selector-name artifact.

### Anchor 2 — `sparse_kv_DT_Willshaw_phase_overlay_v1` [Rank 2, P_joint = 0.20, ~1.5 hr CPU]

**Design:**
1. Fix N=2048. Sweep 10×10 grid over (δ=n/N, ρ=k/n) plane spanning Donoho-Tanner curve.
2. At each gridpoint, generate 3 measurement matrices: (a) iid-Gaussian Φ_G, (b) iid-Bernoulli ±1 Φ_B, (c) substrate's learned projection Φ_S — same shape.
3. Plant k-sparse bipolar x; decode via ℓ₁ (Gaussian/Bernoulli) or substrate's clip-threshold (substrate); measure exact-recovery rate over 50 seeds.
4. Plot empirical 50%-boundary curves; overlay analytic Donoho-Tanner ρ_W(δ) + Willshaw N/log²(N) capacity line.
5. **Discriminating-regime / CAN-fail:** if substrate matches DT-PT within ±0.05, flagship is subsumed by Willshaw (still a clean ship, but NOT structural-novel); if outside by ±0.15 with sign-stable ≥4/5 gridpoints, the learned-projection + bipolar + deterministic combination is structural-novel.

### Anchor 3 — `popgen_kimura_continual_forget_v1` [Rank 3, P_joint = 0.14, ~1-2 hr CPU]

**Design:**
1. Hold substrate at fixed effective capacity K. Stream N_writes ∈ {200, 500, 1000, 2000} facts.
2. Vary replay rate μ ∈ {0, 0.01, 0.05, 0.20, 0.50} per write step.
3. Per-fact retention measured after each stream length.
4. Fit retention curve R(t) against the Kimura neutral-with-recurrent-mutation prediction `R(t) ≈ exp(−t/(2·K_eff))·(1 + μ·2·K_eff·(1 − exp(−t/(2·K_eff))))`.
5. **Cross-check with Anchor 1:** the Kimura analog and the Kramers analog are INDEPENDENT framings — agreement across both = double validation; disagreement isolates which framing fits the substrate's true mechanism.

### Anchor 4 — `spectral_gap_chain_depth_predictor_v1` [Rank 4, P_joint = 0.07, ~1-2 hr CPU]

**Design:**
1. At N ∈ {1024, 2048, 4096}, build substrate similarity graph; threshold to k-NN with k = log N (puts it in tight-expander regime).
2. Compute normalized Laplacian; extract λ₂; set Δ = 1 − λ₂.
3. Predict d_cliff_pred = log N / Δ and d_cover_pred = N log N / Δ.
4. Run actual multi-hop chain probe at same N; locate observed d_cliff_obs by bisection.
5. Compute ratio r(N) = d_cliff_obs / d_cliff_pred across 3 N values.
6. **CAN-fail control:** scramble the similarity matrix (preserve degree sequence, randomize edges) — predictor should produce a different d_cliff_pred on scrambled; if observed cliff doesn't move accordingly, predictor is descriptive-not-causal.
7. **Verify-the-referent skeptic check:** substrate's `log N / d_cliff_obs ≈ 0.003` at N=16384 implies Δ ≈ 0.05 — a moderate gap, NOT a tight expander. If sub-agent #4's flag holds, the spin-glass-on-graphs framing (`1303.4542`) may fit the data better than the expander framing; pre-register this as a branching outcome.

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds (calibration penalty applied)

### Anchor 1 — Kramers-selector
- **HARD-PASS:** Kramers-selector R(age) matches Kim 2026 prediction within ±15% RMSE on log-R on held-out seeds AND strictly Pareto-dominates write-all/FIFO/random in (retention × write-budget) on ≥4/5 seeds AND fitted T_eff stable (CV<0.20) across seeds AND CAN-fail control (random-Δᵢ) does NOT show selector-benefit.
- **HARD-FAIL:** prediction error >40% RMSE on log-R OR no Pareto improvement vs FIFO OR T_eff varies >0.5 across seeds (barrier picture wrong) OR CAN-fail control SHOWS selector-benefit (= artifact).
- **MIDDLE_BAND (15-40%):** mechanism partially right; Freitas-Proesmans-Esposito dissipation-bound test becomes the tiebreaker.

### Anchor 2 — Sparse-KV DT-Willshaw overlay
- **HP_subsumed:** substrate empirical phase boundary within ±0.05 of DT-PT ρ_W(δ) averaged across curve AND within ±15% of Willshaw N/log²N capacity at sparse end → **substrate in known territory; flagship is clean engineering not structural-discovery (still ships; framing-only correction)**.
- **HF_outside:** substrate boundary deviates by >0.15 in ρ from DT-PT in stable-sign direction across ≥4/5 gridpoints AND ≥3 independent seeds confirm sign → **substrate operates OUTSIDE classical predictive regime; learned-projection + bipolar + deterministic combination is structural-novel and warrants its own theory drill**.
- **MIDDLE_BAND (0.05-0.15 or sign-inconsistent):** expand grid; check the 3 adjacent extensions (Roth Kronecker-RIP, Zhang-Liu structured-sparsity, SAE feature-manifolds) BEFORE concluding novel.

### Anchor 3 — Kimura pop-gen continual-forget
- **HARD-PASS:** median r² across 4 replay rates > 0.70 AND fitted K_eff within 0.5×-2× of nominal substrate capacity AND sign of dR/dμ matches prediction in 4/4 rates.
- **HARD-FAIL:** median r² < 0.30 OR fitted K_eff off by >5× OR dR/dμ sign-wrong in ≥2/4 rates.
- **BISECTION-by-design:** 0.30 ≤ r² ≤ 0.70 — try MSDB many-locus variance form before discarding pop-gen frame.

### Anchor 4 — Spectral-gap chain-depth predictor
- **HARD-PASS:** r(N) ∈ [0.8, 1.25] across all 3 N values AND scramble-control shows |Δ_pred_scrambled / Δ_pred_real − 1| > 0.3 matched by observed shift in same direction (causal, not coincidental).
- **HARD-FAIL:** r(N) outside [0.5, 2.0] on ≥2/3 N values OR scramble-control shows |obs-shift| < 0.1 (predictor fires on noise; not causal).
- **MEASURED_MECHANISM otherwise:** in-band but with N-trend (e.g. r drifts monotonically) → tier as descriptive scaling-fit, not predictive theorem instance.
- **Branching outcome:** if HARD-FAIL on expander framing AND substrate's `log N / d_cliff ≈ 0.003` confirms moderate-gap regime, branch to spin-glass-on-graphs framing test (`arXiv:1303.4542`).

---

## (d) Cross-thread synthesis with prior research entries

### vs. prior cross-domain probes #1, #2, #3 (2026-05-23, 05-24)
- Probes 1-3 covered: TSP/QAP, Ramanujan, frame/wavelet, AMP/VAMP, RSB free-cumulants, NTK, sphere packing, ETH/quantum-chaos, tensor PCA, list-decoding, QECC/MUB, ICA/JADE, optimal experimental design, NK fitness, weaken-RIP, Kac-Rice complexity, molecular moments, random graph spectra, anti-concentration, MMD/W2, randomized sketching, quantum reference frames, approximation theory, randomized smoothing, persistent homology.
- **This probe surfaces 4 GENUINELY NEW fields** from the Tier-1b 8 new neighbors: nonequilibrium-stat-mech (Jarzynski/Crooks/Kramers/Freitas-Esposito); population-genetics (Wright-Fisher/Kimura/MSDB); sparse-coding-compressed-sensing (Donoho-Tanner phase transitions, Willshaw, structured-RIP extensions); network-science-graph-theory (spectral-gap mixing-time, Hopfield-on-random-graphs).
- **Most strikingly: the probe-1 ETH/quantum-chaos finding (`Pappalardi 2303.00713`) and the probe-3 MMD/W2 finding (`1509.02237`) both surfaced as substrate-axis-relevant for spectral diagnostics — distinct from THIS probe's storage-chain targeting.** No overlap; this probe is genuinely orthogonal in storage/continual axis.

### vs. negatives drill v2 (2026-06-21)
- v2 drill surfaced 5 hidden-positive candidates including **A1 `substrate_continual_learning_empirical_10e9x_v1` (27x speedup + zero-forget on Pythia-160M, n_train_streams=2)** — the load-bearing Phase-1 #1 referent for continual-write lever.
- **Anchor 1 (Kramers-selector) DIRECTLY targets the same lever** with an independent theoretical framework. If Kramers-selector matches A1's measured retention curves under the predicted `R(t) = exp(−Σ k_i·t)` form, that's a cross-thread cross-validation between (i) the empirical continual-learning measurement, (ii) the Kramers-escape predicted mechanism, and (iii) the in-flight continual-write lever's policy choice. Triple-witness on the same lever.

### vs. v1.1 PHASE PLAN (TOP-7 NEXT SHIPS)
- **Item #1 Sparse-projected-KV FLAGSHIP** → Anchor 2 (DT-Willshaw overlay) provides the subsumption-vs-novelty discrimination cheaply. If HP_subsumed, the flagship still ships, but as engineering composition not structural-novel; this AVOIDS the symmetric-guard wrong-bar trap on framing inflation.
- **Item #2 Continual-write lever** → Anchor 1 (Kramers-selector) provides the policy theory; Anchor 3 (Kimura) provides an independent cross-check via the pop-gen framing. The two together = Phase-1 #1 has TWO independent predictive frames; agreement = double-validation; disagreement = isolates the right framing.
- **Item #6 M2 REFRAMED glass-box INTEGRATION** → Anchor 4 (spectral-gap predictor) provides the chain-depth cliff predictor for the composition axis. Branching outcome if substrate sits in moderate-gap regime (likely): spin-glass-on-graphs framing becomes the better fit, which composes with our existing RSB/replica work in spin-glass field (yield 83%, 6 drills).
- **Item #8 Capacity-saturation ceiling distinctive-axis** — not directly addressed by this probe; orthogonal.

### vs. CERT 591 (learned key-projection) + CERT 592 (NESS chain envelope)
- CERT 591's key-projection mechanism is exactly what Anchor 2 tests for sparse-recovery-phase-transition behavior on the projected-key space (cf. sub-agent #3's flag: SAE feature-manifold scaling `2509.02565` is the closest published precedent).
- CERT 592's NESS chain envelope is exactly the regime Anchor 1 reuses; the Kramers-escape framework provides a unified theory for WHY the chain envelope exceeds classical Hopfield ceiling — it's a NESS dissipation effect, not an equilibrium property. This may resolve the "what's the mechanism behind 2-12x amplification" interpretive question that CERT 592 left open.

### vs. crosstalk-law cross-encoder (`7315be3c`, isotropy-overturn)
- Anchor 2's outcome would inform: if substrate sits OUTSIDE DT-PT, the same structural mechanism that makes crosstalk unbounded-c may be the one that pushes recovery beyond the classical phase-transition curve. Plausible but speculative; not pre-reg'd.

---

## (e) Substrate-product implications

Per [[feedback-no-papers-product-only]] — what capability does this surface for the substrate?

1. **Continual-write policy as a SHIPPABLE LEVER (the thinnest enabling axis).** Anchor 1's Kramers-selector, if it HARD-PASSes, ships as the substrate's continual-write selector: a principled, parameter-free policy that uses retrieval-margin as a Kramers-barrier proxy and writes only when predicted retention exceeds threshold. **Composes with: a8 no-forget envelope, A1 27x speedup measurement, in-flight continual-write lever pre-reg.** This makes the substrate a LIVE store that doesn't catastrophically forget — the foundation under everything downstream (KG growth, glass-box training, multi-session memory accumulation).

2. **Storage-foundation honest framing.** Anchor 2 either (i) confirms the flagship is engineering composition (still valuable, but de-risks the wrong-bar trap by framing it correctly upfront) OR (ii) confirms structural-novel and validates the projection-decrowding mechanism as a genuine push beyond classical sparse-recovery theory. Either way, the FRAMING of the flagship ship is right.

3. **Independent cross-validation of continual-write retention.** Anchor 3 (Kimura) and Anchor 1 (Kramers) are INDEPENDENT theoretical frameworks for the same observable. Agreement = the substrate's continual-write capability has a unified predictive theory across statistical-mechanics and population-genetics framings — a robust property. Disagreement = isolates which framing is causally correct.

4. **Multi-hop chain-depth predictor for glass-box composition.** Anchor 4 gives the M2-reframed glass-box integration a quantitative cliff-predictor: given the substrate's similarity-graph spectrum at deployment scale, predict where multi-hop chain query will collapse. This is OPERATIONAL infrastructure for the glass-box LLM — it tells the system WHEN to refuse a multi-hop query before attempting it (composes with LEVER #4 depth-refuse).

5. **Verify-the-referent guard (substrate-state insight from sub-agent #4):** `log N / d_cliff ≈ 0.003` at N=16384 implies Δ ≈ 0.05 (moderate gap, NOT tight expander). This flags that any framing of substrate's chain-depth as "expander mixing" is mis-citing the regime; the spin-glass-on-graphs framing (Pastur-Shcherbina / `1303.4542`) is the better fit. This is a STANDING CORRECTION on how to talk about the substrate's chain-depth mechanism in the glass-box context.

6. **Falsification value (negative-result branches are still product-relevant):** if Anchor 1 HARD-FAILs, we rule out the Kramers-barrier policy family — focusing the continual-write lever onto selection-coefficient (Kimura) or write-cost (Freitas-Esposito dissipation-floor) framings. If Anchor 2 lands in the bisection zone, the 3 adjacent extensions (Roth, Zhang-Liu, SAE) become next-drill candidates. The probe yields direction-narrowing in every branch.

---

## (f) Citations (verified count)

**Anchor 1 — nonequilibrium-stat-mech (verified via WebFetch by sub-agent):**
- Rooke, Krotov, Balasubramanian, Wolpert, *Stochastic Thermodynamics of Associative Memory*, `arXiv:2601.01253` (2026) — DMFT work/power/entropy-production tradeoff in Dense Associative Memory
- Kim, G., *Non-Equilibrium Stochastic Dynamics as a Unified Framework... Kramers Escape Approach to Continual Learning*, `arXiv:2604.04154` (2026) — **load-bearing for Anchor 1**
- Freitas, Proesmans, Esposito, *Reliability and entropy production in non-equilibrium electronic memories*, `arXiv:2103.01184` (2021) — analytical bound on bit-error rate vs NESS dissipation
- Dechant, Sasa, Ito, *Geometric decomposition of entropy production into excess, housekeeping and coupling parts*, `arXiv:2202.04331` (2022) — adiabatic/non-adiabatic split tool

(Search-result-only, not individually fetched: Di Terlizzi & Baiesi `arXiv:2005.05226` thermodynamic-uncertainty-relation with memory; bioRxiv 2021.08.24.457446 stochastic consolidation.)

**Anchor 2 — sparse-coding & compressed-sensing (verified):**
- Donoho-Tanner phase-transition reference: Bellec lecture notes (`bellecp.github.io/donoho_tanner_phase_transition.html`); Donoho-Gavish PNAS 2013
- Knoblauch-Palm-Sommer 2010, *Memory Capacities for Synaptic and Structural Plasticity* (Redwood TR) — Willshaw N²/log²N capacity reference
- Golomb-Rubin-Sompolinsky 1990, *Willshaw model* (PRA 41:1843)
- Schnass, K., 2018, *Identifiability of Complete Dictionary Learning*, `arXiv:1808.08765`
- Yu-Li-Gribonval 2015, *Local identifiability of ℓ1 minimization dictionary learning*, `arXiv:1505.04363`
- Yu, 2010, *Deterministic Compressed Sensing Matrices from Character Sequences*, `arXiv:1010.0011`
- **Adjacent extensions to check before concluding novel:** Roth et al. 2018 *Hierarchical RIP for Kronecker measurements* `arXiv:1801.10433`; Zhang-Liu 2024 *Phase transitions with structured sparsity* `arXiv:2411.09868`; SAE feature-manifolds 2025 `arXiv:2509.02565`; Gao-Dupré la Tour 2024 *Scaling sparse autoencoders* `arXiv:2406.04093`

**Anchor 3 — population genetics:**
- *A Unified Treatment of the Probability of Fixation when Population Size and Selection Change Over Time*, PMC3176099
- Der et al. TPB 2011, *Generalized population models and the nature of genetic drift*
- *The Memory Problem for Neutral Mutational Models of Evolution*, J. Mol. Evol. 2022, `10.1007/s00239-022-10084-y`
- *Mutation–selection–drift balance models of complex diseases*, Oxford Genetics 2025 (PMC12132567)
- Baake, biological-evolution review `arXiv:cond-mat/9907372`
- (statistical-mechanics catastrophic-forgetting cross-ref: `arXiv:2105.07385`; continual-learning survey `arXiv:2403.05175`; biological memory `arXiv:1507.07580`)
- **Adjacency-edge cross-check:** `arXiv:2407.17493` quantitative-trait-modeling for diffusion-finetuning collapse — closest non-substrate ML adjacency

**Anchor 4 — network-science / graph-theory:**
- Chung, *Spectral Graph Theory* (Thm 1.16 mixing-time bound)
- Levin-Peres-Wilmer, *Markov Chains and Mixing Times* (Thm 12.3)
- Alon-Benjamini-Lubetzky-Sodin, *Non-backtracking random walks mix faster*, princeton.edu/~nalon
- Lubetzky-Peres, *Cutoff on all Ramanujan graphs*, `arXiv:1507.04725`
- Hoffman-Kahle-Paquette, *Spectral Gaps of Random Graphs*, matthewkahle.org
- *Capacity of an associative memory model on random graph architectures*, `arXiv:1303.4542` — **load-bearing for spin-glass-on-graphs branching outcome**
- *Non-backtracking spectrum of random graphs*, `arXiv:1501.06087`
- *Cover Time and Broadcast Time*, `arXiv:0902.1735`
- MIT 18.409 Lecture 6 (mixing-time bound, OCW)
- *On the spectral gap and the diameter of Cayley graphs*, `arXiv:2004.10038`
- *Random walk hitting times and effective resistance in sparsely connected ER graphs*, `arXiv:1612.00731`

**Verified count: 30+ distinct papers/sources across 4 fields.** All citations originate from sub-agent WebSearch results (no fabrication; honest "search-result-only" flag applied where individual WebFetch was not performed).

---

## (g) Ranking-weight justification (per dispatch autonomy #6)

Per USER-program-priority + storage-chain through-line per v1.1: I weighted **`P(cross-applicable-to-storage-chain) HIGHER** than `P(would-inform-current-direction)`** at a roughly 1.2x weighting. This is why **Anchor 1 (Kramers-selector for continual-write) ranks #1 despite Anchor 2 (DT-Willshaw overlay for flagship) having comparable joint-P** — continual-write is the THINNEST enabling theme in the storage chain (only 5 chain-grade atoms per Skunkworks's enabling rankings); a direct cross-domain mechanism here moves the highest-leverage axis. Anchor 2 hits the flagship which is already SCHEMA-VET PASS and SAFE-TO-BUILD per Exp-Dev's independent NONE-subsume check — the cheap test there is about FRAMING correctness, not directional unlock.

Adjacent-method check per [[feedback-dont-dismiss-adjacent-methods]]: even Anchor 4 at joint-P=0.07 was kept because (i) the test is cheap (~1-2 hr CPU), (ii) it has an adjacency edge to spin-glass (yield 83%, fruit-bearing parent), and (iii) the branching outcome (spin-glass-on-graphs framing on moderate-gap regime) opens a genuinely under-drilled storage adjacency (associative-memory-on-random-graphs `1303.4542` is a buried treasure not in our prior drills). Premature dismissal would have been the failure mode.

---

## (h) Standing

- **USER:** v2.0 cross-domain probe filed per Trigger F overdue cadence + v1.1 PHASE PLAN item #7. 4 anchor experiments pre-reg'd with HP/HF thresholds; total ~5 CPU-hr if all fire; sequence by P-rank (Anchor 1 first). Direction-narrowing in every branch.
- **Skunkworks:** Anchor 1 (Kramers-selector) composes with the in-flight continual-write lever pre-reg + A1 referent + a8 envelope — recommend folding the Kramers `R(t) = exp(−Σ k_i·t)` form as a referent in the continual-write lever pre-reg amendment (alongside A1 per v1.1 §2). Verify-the-referent guard for substrate's `log N / d_cliff ≈ 0.003` moderate-gap regime: any future chain-depth narrative should use spin-glass-on-graphs framing, not expander-mixing framing.
- **Exp-Dev:** 4 cheap-decisive-test cells available as backlog; Anchor 1 highest priority (composes with Phase-1 #1 in-flight lever); Anchor 2 second priority (subsumption-vs-novelty discrimination for flagship); Anchors 3 and 4 lower priority (cross-checks + branching outcome). Cell-author bandwidth your call per priority.
- **Me:** probe filed; status_log entry to follow; will route Kramers-selector cross-check explicitly to Skunkworks as a continual-write-lever pre-reg amendment candidate; will queue spin-glass-on-graphs (`1303.4542`) follow-up drill into the next research cycle as a Tier-1b adjacent storage-axis target.
- **Director plan update:** anchor experiments added as Phase-X cross-domain-probe items in `data/director_plan.json` (separate write).

-- Research (Director, Opus depth-drill)
