# 2x-drill: h4 revival — confidence-calibration predictor for M3 cortex routing

**Date:** 2026-07-02
**Session:** Research Director drill
**Context:** h4 GLOBAL mean-clipped-cosine cluster-density predictor failed FULL 3-seed at commercial scale (AUC=0.528 chance; bimodal per-seed 0.359 / 0.541 / 0.681). Skunkworks filed HF_STRUCTURAL_BOUND with 4 revival criteria. `lap3_12_confidence_calibration_cpu_v1` is a SIBLING un-dispatched cell targeting POST-HOC isotonic score calibration (different lane). Goal: derive highest-P_CG next cell for the *uncertainty-prediction* (not post-hoc calibration) angle, complementary to lap3_12.

**Deliverable framing:** M3 cortex uses this signal to route to REFUSE / CLARIFY / ACCEPT / RE-QUERY. Substrate is memory+composition+retrieval+audit; predictor must be substrate-native scalar-per-query. Not a language benchmark.

**Cost/priority axes:** P_CG (deflated 0.15-0.25 per lit-scan penalty; capped 0.50); implementation cost; scale-survival (must survive smoke→full-N); complementarity to lap3_12.

---

## Drill A — verification of 4 Skunkworks-filed revival criteria

### 1. Local k-NN density (top-K nearest-neighbor density around query point)

**Mechanism-class prior:** Standard OOD-detection technique (Sun et al 2022 kNN-based OOD; Lee et al Mahalanobis; ODIN). Distinguishes IN-distribution vs OUT-of-distribution.
**Substrate-KB priors:** None direct for contamination detection via local density.
**Bio-analog:** Local field potential / lateral inhibition proximity — weak signal.
**Failure-mode analysis:** h4's problem was NOT OOD, it was contamination (in-distribution items with wrong label). Local density does not discriminate "true fact" from "well-formed contaminating fact" if both draw from same latent distribution — which is exactly the KG-contamination case. Local vs global is a resolution shift, not a mechanism change.
**Scale-survival caveat:** local averaging over K=10-30 neighbors gives sqrt(120) ~11x SNR gain over global 3600 — better but still averaging.
**P_CG estimate:** **0.20** (raw lit-scan prior 0.35-0.40; deflate 0.15-0.20 for mechanism-class-same-as-failed-h4 and scale-only-shift; not novel synthesis)

### 2. Top-1 vs top-2 similarity gap (margin)

**Mechanism-class prior:** STRONG.
- ML classic: margin classifier / max-margin softmax; entropy-based selective classification (El-Yaniv & Wiener 2010; Geifman & El-Yaniv 2017 SelectiveNet).
- Bio-analog: **Ma et al 2006 probabilistic population code** — posterior width from tuning-curve overlap; ACC contradiction-detection uses top-k margin computation.
- Direct substrate observable — one scalar per query, no new mechanism.

**Substrate-KB prior — LOAD-BEARING:**
- `notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md` (cosine 0.30):
  > "Calibrated confidence intervals (probabilistic population code, Domain 2): MEDIUM priority. Add gap score (top-1 minus top-2 similarity) as second output alongside confidence score. Cheap. Improves downstream reasoning."
- `notes/exp_dev_handoff_research_biology_capabilities_5x_2026-06-08.md` (cosine 0.30):
  > "Anchor pointer: bio-calibrated-confidence-B1 ... Large gap = high confidence + low uncertainty. Small gap = low confidence + high uncertainty. Maps to neural uncertainty representation via width of the posterior in population coding (Ma et al. 2006). Tier 1 (changes only the output format; no retrieval mechanism change; < 1 w[eek])"

Anchor `bio-calibrated-confidence-B1` was FILED as MEDIUM priority Tier-1 in June, NEVER SHIPPED. h4 revival is the direct dispatch of this pre-existing hand-off.

**Failure-mode analysis:** Two potential concerns:
- (a) Same cos-sim compression that hurt h4? Answer: **NO** — h4 averaged over 3600 items; gap uses only the *top two* items (which by construction are the most-discriminated). ROLE-level tasks in the session showed ρ~0.79-0.83 preserved discrimination at top-1/top-2 level.
- (b) Ceiling at very-high N where top-1/top-2 both saturate near 1.0? Mitigated by 3-seed FULL preview at commercial N=3600 (discriminator-must-survive-scale discipline).

**Complementarity to lap3_12:** lap3_12 is **post-hoc isotonic calibration** on top-1 similarity alone (rescales an existing scalar). Gap adds a **new input signal** (the top-2 similarity). These COMPOSE cleanly — lap3_12 calibrates top-1; gap enriches the input feature set. Not overlapping.

**P_CG estimate:** **0.42** (raw prior ~0.55 given explicit substrate-KB precedent; deflate 0.13 for scale-survival unproven; below 0.50 novel-synthesis cap since this is revival of a filed atom, not novel; scale-survival gate distinguishes from novel-synthesis)

### 3. Per-cluster density restricted to argmax cluster

**Mechanism-class prior:** Density-based, restricted to retrieved cluster ~30 items. sqrt(30/3600) ~10x SNR gain over h4.
**Substrate-KB priors:** None direct.
**Failure-mode analysis:** Still averaging, still density. If contamination is 1-in-30 within a cluster, per-cluster density signal is diluted 1/30 = 3.3%. This IS meaningfully above the 1/3600 = 0.028% signal h4 was chasing, so may cross discriminator threshold. But it's the SAME mechanism scoped tighter; substrate learning is minimal.
**Cortex integration:** requires (a) cluster assignment mechanism and (b) per-cluster density statistic; slightly more machinery than a pure similarity gap.
**P_CG estimate:** **0.25** (raw prior 0.40; deflate 0.15 for mechanism-family-same-as-h4)

### 4. Multi-fact contamination (density may work when fraction >> 1/M)

**Mechanism-class prior:** This is a REGIME test, not a mechanism revival. Runs same h4 mechanism in a favorable-SNR regime (e.g. 10% contamination fraction instead of 0.028%).
**Substrate-KB priors:** None direct; conceptually related to "regime-invariance" META atoms filed today (SPARSITY_FREE_AXIS).
**Cortex value:** LOW — cortex confidence-routing needs per-query score. "Density works when many things are contaminated" doesn't give cortex a per-query signal; it gives a batch-level anomaly detector. Wrong grain.
**P_CG estimate:** **0.15** (validates h4 failure characterization but doesn't produce a cortex-routing signal; more of a scope-limit atom than a revival cell)

### Ranking (Drill A):
| Rank | Criterion | P_CG | Cost | Cortex-fit | Notes |
|------|-----------|------|------|------------|-------|
| 1 | Top-1/top-2 gap | 0.42 | Tier 1 (~1 day) | High | Substrate-KB precedent; Ma 2006; complementary to lap3_12 |
| 2 | Per-cluster density | 0.25 | Tier 2 (~3 days) | Medium | Mechanism-family-same-as-h4 risk |
| 3 | Local k-NN density | 0.20 | Tier 2 (~3 days) | Medium | Still averaging; OOD ≠ contamination |
| 4 | Multi-fact regime | 0.15 | Tier 1 (~1 day) | Low | Wrong grain for cortex |

---

## Drill B — alternative revival lanes (beyond the 4 criteria)

### Lane X: cleanup-iteration-count-to-converge (energy-landscape depth)

**Mechanism-class prior:** Hopfield attractor basin theory — deep basin = fast convergence = high confidence; shallow basin = slow convergence or oscillation = low confidence. Iteration count (or energy delta trajectory) is a direct DYNAMICAL observable. Distinct from spatial-margin (top-1/top-2 gap).

**Substrate-KB priors — LOAD-BEARING:**
- `preregs/2026-06-23_substrate_iterative_cleanup_cue_clamped_v1.md` (cosine 0.37)
- `preregs/2026-06-23_substrate_multi_iteration_cleanup_LM_v1.md` (cosine 0.37) — 4 arms (0 / 1 / 3 / 10 iterations)
- `notes/research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04.md` "Convergence iterations" (cosine 0.37)
- Session lead-out CG: "cleanup latency operating curve CG" landed 2026-07-01

So substrate-KB already has THREE cleanup-iteration primitives shipped or pre-reg'd; the confidence-predictor angle has NOT been dispatched.

**Bio-analog:** Cortical settling time / N400 latency correlates with prediction uncertainty (Kutas & Federmeier 2011). Attractor basin depth = confidence.

**Complementarity:** ORTHOGONAL to top-1/top-2 gap (spatial) and to lap3_12 (post-hoc). Two-observable combined predictor may exceed either alone.

**Failure-mode:** At commercial scale, dense-Hopfield may converge in ≤2 iterations regardless (saturation observed in dense-HF underloaded-regime today per Sonnet Dim H drill — CLT washout convergent finding). Mitigation: use ENERGY DELTA (continuous) not iteration COUNT (integer), which retains signal below saturation.

**P_CG estimate:** **0.35** (raw prior 0.50 for well-motivated substrate observable; deflate 0.15 for dense-HF-saturation risk explicitly logged today)

### Lane Y: top-K softmax entropy over cleanup-output soft-assignment (retrieval sharpness)

**Mechanism-class prior:** Shannon entropy over top-K cosine-normalized weights. Extends top-1/top-2 gap from 2 scalars to K scalars (typically K=5-10). Standard practice in selective classification (Hendrycks & Gimpel 2017 max softmax).

**Substrate-KB priors:**
- `notes/research_drill_substrate_confidence_continuous_3x_2026-06-10.md` "Does Softmax Energy Fix the Confidence Problem?" (cosine 0.29)
- Directly explored the softmax-energy angle in a 3x drill.

**Bio-analog:** Fisher information from tuning-curve overlap; Ma 2006 population code width.

**Complementarity:** MODERATELY OVERLAPPING with top-1/top-2 gap (Pearson expected ~0.7 — both measure sharpness of same distribution). Less complementary than Lane X.

**P_CG estimate:** **0.30** (raw 0.45; deflate 0.15 for gap-overlap redundancy)

### Lane Z (bonus): self-consistency retrieval mismatch

**Mechanism-class prior:** cue→retrieve→re-cue-from-cleaned→re-retrieve; divergence in second retrieval = contamination-suspect. Bootstrap self-verification (Wang et al 2022 self-consistency).
**Cost:** 2x retrieval; more expensive than Lane X/Y.
**P_CG estimate:** **0.22** (raw 0.40; deflate for cost/complexity; lower novelty)

### Ranking (Drill B):
| Rank | Lane | P_CG | Cost | Cortex-fit | Notes |
|------|------|------|------|------------|-------|
| 1 | Cleanup-iteration count / energy delta | 0.35 | Tier 2 (~3-5 days) | High | Orthogonal to Drill-A top pick; substrate-KB primitives shipped |
| 2 | Top-K softmax entropy | 0.30 | Tier 1 (~1 day) | Medium | Overlaps top-1/top-2 gap |
| 3 | Self-consistency mismatch | 0.22 | Tier 3 (~1 week) | Medium | Higher cost, moderate novelty |

---

## Top-1 pick — MECHANISM CLASS + RATIONALE + CELL DESIGN

### Pick: **Top-1 vs top-2 similarity gap** (Skunkworks criterion #2 = bio-calibrated-confidence-B1)

**Rationale:**
1. **Highest P_CG (0.42)** across all seven candidates evaluated.
2. **Explicit substrate-KB precedent** — anchor `bio-calibrated-confidence-B1` filed 2026-06-08 as Tier-1 / MEDIUM priority / cheap, referring to Ma et al 2006 probabilistic population code. NEVER shipped. h4 revival = filing an eight-month-old hand-off.
3. **Complementary to lap3_12** — lap3_12 post-hoc-calibrates top-1 similarity alone (one scalar rescaled); gap adds top-2 as a NEW input feature. They compose (calibrate the gap too if useful).
4. **Cheapest** — Tier 1 output-format change; no new retrieval mechanism; ~1 day cell + 3-seed FULL.
5. **Cortex-consumable** — single scalar per query; routes cleanly to REFUSE/CLARIFY/ACCEPT/RE-QUERY thresholds.
6. **Distinct mechanism-class from h4** — h4 averaged over 3600 items (density); gap uses only top-2 (discrimination). Discriminator-survives-scale gate MUST be enforced (see cell design below).

**Minimum-viable cell design (5 lines):**
1. **Anchor:** `h4b_margin_top1_top2_gap_predictor_v1`
2. **Setup:** Reuse h4 3600-item substrate + contamination-injection harness (one contaminating fact per 30-item cluster).
3. **Predictor:** For each query, compute `gap = sim(top-1) - sim(top-2)`; hypothesis `AUC(gap, is_contaminated_target)` significantly > 0.5 at commercial N=3600.
4. **Scale-survival gate:** Smoke at N=200 AND N=3600 preview arm; reject FULL dispatch if AUC at N=3600 preview <=0.55 (per USER-locked discriminator-must-survive-scale).
5. **Bands (SCHEMA-VET pre-reg):** HARD_PASS AUC>=0.70 (3-seed cv<=0.03); MIDDLE_BAND 0.60-0.70; HF <0.60. 3-seed FULL after smoke gate. CARDINALITY_OK: EXPECTED_N_QUERIES=3600×3=10800 across seeds.

**Complementarity note for exp_dev / Skunkworks:** the cell MUST NOT overlap `lap3_12_confidence_calibration_cpu_v1` (post-hoc isotonic calibration on top-1). If lap3_12 lands first, this cell's downstream cortex integration should compose the two (gap → isotonic → cortex threshold). Cell smoke can be run in parallel; do not sequence-block.

---

## Secondary recommendation

If h4b lands PASS, next candidate (parallel-track, not blocking) is **Lane X: cleanup-iteration/energy-delta predictor** — orthogonal DYNAMICAL observable to h4b's spatial-margin observable. Together they form a two-signal confidence vector for cortex, richer than either alone. But h4b ships first (higher P_CG, cheaper, filed hand-off).

---

## Hand-off to exp_dev

**Ready-to-ship cell:** `h4b_margin_top1_top2_gap_predictor_v1`
- **Reuse:** h4 harness (contamination-injection + eval)
- **Diff from h4:** replace mean-clipped-cosine density computation with `gap = sim[argsort_desc[0]] - sim[argsort_desc[1]]` per query
- **Envelope-fail-bands pre-reg fields required:** discriminator (AUC), N_QUERIES = 3600 × 3 seeds, MECHANISM_CLASS = spatial-margin (distinct from h4 mechanism-class density-averaging), CARDINALITY_OK, SCALE_SURVIVAL_GATE (smoke at N=200 AND N=3600 preview arm)
- **Expected wall:** ~1-2 hr smoke + ~4-6 hr 3-seed FULL on remote_cpu_queue (h4-scale substrate)
- **Route:** smoke on local_cpu; FULL on remote_cpu_queue (per USER-locked SMOKE-ONLY-on-local discipline)

**Priors cited:**
- `notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md` (anchor bio-calibrated-confidence-B1)
- `notes/exp_dev_handoff_research_biology_capabilities_5x_2026-06-08.md` (Tier 1 filing)
- Ma, Beck, Latham & Pouget 2006, "Bayesian inference with probabilistic population codes," Nature Neuroscience
- Geifman & El-Yaniv 2017 SelectiveNet for selective-classification margin
- El-Yaniv & Wiener 2010 selective classification theory

---

## Session context propagation

- 21 CG + 1 HF this session; Stage 3 (M3 cortex confidence-routing) active
- Complements: lap3_12 (post-hoc isotonic); h4b (spatial margin); Lane X (dynamical energy) — three-signal cortex confidence vector emerging
- Discipline compliance: substrate-KB concept-query FIRST executed (4 queries, top-3 priors cited); lit-scan penalty applied (deflated all P by 0.13-0.20); novel-synthesis cap 0.50 respected; no language-benchmark framing; no AskUserQuestion
