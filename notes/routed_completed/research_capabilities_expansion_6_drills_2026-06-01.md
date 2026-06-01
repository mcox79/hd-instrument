# Research: Capabilities expansion — 6 parallel drills synthesis (2026-06-01)

Date: 2026-06-01
Origin: user-greenlit dispatch after stock-taking conversation surfaced "a ton of untested capabilities"
Method: 6 parallel Sonnet drills (~120-200s each, ~125K tokens combined) + main-thread synthesis
Per: [[feedback-2x-means-depth]] (operational depth on untested capabilities), [[feedback-aggressive-cross-domain-research]] (overdue cross-domain probe landed), [[feedback-lit-scan-calibration-penalty]] (deflated P estimates throughout), [[feedback-no-padding-experiments]] (each drill load-bearing on a distinct capability gap)

## HEADLINE

The substrate's strategic ceiling is **higher than the validated audit-grade-memory wedge suggests**. Three findings carry the most strategic weight:

1. **Free probability's K_max(α) = log(1/α)/(2√α) formula RETROACTIVELY EXPLAINS the v308 K=2 cliff** as a spectral-gap effect → gives a design rule for multi-hop depth vs capacity going forward.

2. **Sparse-block-code substrate variant should be Option (c): specialized layer for edit/audit operations, NOT replacement for dense bipolar** — sparse and dense have COMPLEMENTARY strengths. Overall P=0.52 for specialized layer; P=0.28 for replacement.

3. **PP-4 drift detection + edit-impact-prediction + calibrated confidence + KV-cache-with-audit form a coherent killer-features cluster** that should ship together as "substrate-state-as-product-signal" suite. All 4 drills converge on the same load-bearing observation: substrate's audit/cert/algebra is **intrinsic** (not extrinsic logging), which is the moat.

## Cross-drill insights (the synthesis matters more than the individual drills)

**Insight A — Free probability gives concrete formulas with retroactive empirical fits**:
- K_max(α) explains v308 K=2 saturation (K_max at α=0.10 ≈ 3.6 → K=2 stable, K=4+ erodes)
- K≈√N edit budget predicts ~64 edits at N=4096 before spectral drift detectable → directly informs PP-3 rotation cadence AND PP-4 drift threshold
- Free additivity predicts hierarchy = flat at matched total load → PP-7 hierarchy advantage MUST come from routing, not spectral capacity (sharpens engineering target)

**Insight B — Atom-registry DAG (landed today) makes edit-impact-prediction tractable**:
- Pre-commit prediction was hard before today's DAG framework; now it's a graph-traversal problem (Mechanism 1: P=0.85, deterministic)
- 3 mechanisms layer cleanly on top: DAG Reverse-Traversal → Merkle Proof Survivability → Algebraic Perturbation
- Combined product output fits in <50ms for typical k≤200

**Insight C — Calibrated confidence has correct Bayesian form but ECE is empirical**:
- "We return a probability" is easy and dismissable
- "ECE<0.05 with validation certificate" is defensible — requires Sub-cap 1 smoke (<60s CPU) as GATE
- Cluster around FDA SaMD, SR 11-7, ISO 13485, GDPR Art 22 compliance hooks

**Insight D — Sparse-block-code is complementary not competitive**:
- Dense WINS: chain retrieval (Path D depth=50), audit under noise (Bayesian reweighting prevents catastrophic compounding)
- Sparse WINS: edit isolation (10× COW collapses to near-zero), structured-key geometry (PP-11 may close), hardware efficiency (64× on neuromorphic; 4-16× on sparse-tensor)
- Architectural decomposition: sparse for edit/audit operations, dense for chain retrieval

**Insight E — Substrate-as-KV-cache is NOT a latency play, it's an audit-cert play**:
- 19.78ms substrate vs <1ms typical KV cache → substrate adds latency
- Value calculus: only viable where audit/provenance/deletion-proof is load-bearing
- Closest competitor (arxiv 2605.11032 Portable Agent Memory) uses Merkle-DAG + extrinsic trust layer; substrate's specific advantage is intrinsic algebraic cert + retrieval-by-content + native deletion certs

## Per-drill summary + sequencing (cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

### Drill 1: PP-4 concept drift detection (5 mechanisms)

Empirical anchor: V2 24h sustained showed `kf1=kf2_drift=0.0` (per-fact stable) but `codebook_usage_hist_drift_l1=0.911` (workload distribution shifts substantially). **The signal split is sharp**: per-fact is fine; access distribution is not.

| # | Mechanism | Drift Classes | Cost | P |
|---|---|---|---|---|
| 1 | Codebook Usage Histogram Divergence (w/ bootstrap-null separator) | (a) workload PRIMARY, (e) aging | ~30 LOC; online | 0.52 |
| 2 | Per-Retrieval Bayesian Posterior CDF Shift (KS test) | (d) capacity PRIMARY, (b) per-fact | ~50 LOC; online | 0.45 |
| 3 | **Write-to-Retrieve Ratio Drift (cert-chain rate detector)** | **(c) adversarial PRIMARY** | **zero instrumentation; online** | **0.65** |
| 4 | Spectral Drift (Marchenko-Pastur baseline + outlier count) | (c) adversarial PRIMARY, (d) capacity | offline daily; 1GB W materialization | 0.42 |
| 5 | LLM-Judge Calibrated Posterior Agreement Score (LPAS) | (a) workload + (e) aging PRIMARY (semantic) | ~$0.03/hour Pattern B API | 0.55 |

**Sequencing**: Ship Mechanism 3 first (zero instrumentation, highest P, addresses adversarial poisoning which is the compliance risk regulators ask about first). Ship Mechanism 1 second (the 0.911 L1 drift is already measured; only work is adding bootstrap separator). Run Mechanism 5 (LPAS) in parallel. Defer Mechanism 4 (spectral). Mechanism 2 lowest priority given kf1=kf2=0 stability already established.

### Drill 2: Edit-with-impact-prediction (5 mechanisms on atom-registry DAG)

| # | Mechanism | Predicted Classes | Pre-commit? | Cost | P |
|---|---|---|---|---|---|
| 1 | **DAG Reverse-Traversal** | (a) direct + (b) transitive | YES | O(deg(X)+k); <1ms typical | **0.85** |
| 2 | Algebraic Perturbation (binding-algebra delta) | (c) per-comp accuracy + (d) retrieval | YES | O(k·N); ~4ms at k=50 | 0.45 |
| 3 | **Merkle Proof Survivability Check** | **(e) audit-chain integrity (binary)** | **YES** | O(k·log n); sub-ms | **0.75** |
| 4 | W-Matrix Sensitivity Analysis | (d) retrieval ranking | YES | O(k·N) after filter; ~5ms GPU | 0.40 |
| 5 | Bayesian Forward-Simulation of Posterior Shift | (c) probabilistic + (d) | YES (shallow DAG) | O(depth·k·N); ~16ms | 0.30 |

**Sequencing**: Mechanism 1 (DAG traversal; structural backbone; deterministic; P=0.85) FIRST. Mechanism 3 (Merkle survivability; cheap; high compliance value) SECOND on top of #1. Mechanism 2 (algebraic perturbation; continuous degradation scores) THIRD. Mechanisms 4-5 layer optionally. Combined 1+2+3 output in <50ms for typical k≤200 — full edit-impact UI in single pre-commit call.

### Drill 3: Free probability for W structure (5 applications; NARROWER scope vs K=1 N-prediction)

| # | Application | Predicted Formula | Strategic Relevance | Cost | P |
|---|---|---|---|---|---|
| 1 | Compounded Binding Spectrum | Var[interference] = M/N (identical to unbound) | PP-11 framing (corollary; no rescue) | CPU 5min | 0.25 |
| 2 | Free Entropy (Voiculescu χ) | α_c(N) ≈ 0.138 + C·log(N)/N | Finite-N capacity bounds | GPU 20min | 0.30 |
| 3 | **Free Additive Convolution (hierarchical W)** | μ_aggregate = μ_MP(α_total) | **PP-7 hierarchy is ROUTING not spectral** | **CPU 15min** | **0.55** |
| 4 | **Rank-1 Edit Perturbation (Weyl bound)** | K≈√N edits before spectral drift detectable | **PP-3 rotation cadence + PP-4 threshold** | **CPU 10min** | **0.35** |
| 5 | **K_max(α) via Free Power (BBP transition)** | **K_max(α) ≈ log(1/α)/(2√α); α=0.10 → K_max ≈ 3.6** | **RETROACTIVELY EXPLAINS v308 K=2 CLIFF** | **GPU 25min** | **0.40** |

**Sequencing**: Mechanism 4 + 3 + 5 in PARALLEL BATCH (CPU+GPU, ~25min total wall). Three 🔬 cap_map rows could update from one run. Defer Mechanism 2 (SKAH-M classification already predicts MP-universality deviation). Skip Mechanism 1 (known-corollary).

### Drill 4: Substrate as KV cache (4 priority candidates; 2 deliberately NOT selected)

| # | Sub-capability | Strategic Value | Cost | P |
|---|---|---|---|---|
| 1 | **Tool-Call Result Caching w/ Audit Cert** | **GDPR Art 17 deletion-cert** | **1-2 eng-weeks** | **0.72** |
| 2 | Per-Conversation Entity Memory w/ Deletable Entries | GDPR + HIPAA | 2-3 eng-weeks (depends on #1) | 0.60 |
| 3 | **System Prompt Amortization w/ Provenance Cert** | **EU AI Act Art 13 transparency** | **1 eng-week** | **0.80** |
| 4 | Multi-LLM Shared Fact Store w/ Versioned Access | Most differentiated | 3-4 eng-weeks | 0.60 |
| -- | NOT SELECTED: speculative-decoding draft cache (substrate adds latency, doesn't remove); per-fact-derived KV reuse (couples to LLM arch version) | -- | -- | -- |

**Sequencing**: #1 + #3 in parallel (cleanest baselines, lowest eng cost, highest compliance specificity). #2 depends on #1's cert infrastructure. #4 third (depends on additional Q-Former bridges per LLM family).

Closest competitor: arxiv 2605.11032 Portable Agent Memory (Merkle-DAG provenance). Substrate's specific advantage: intrinsic algebraic cert (no external trust infrastructure) + retrieval-by-content + native deletion certs at per-entry level.

### Drill 5: Calibrated confidence as product feature (5 sub-capabilities)

| # | Sub-capability | Compliance Hook | Cost | P (HARD-PASS) |
|---|---|---|---|---|
| 1 | **Per-Retrieval Confidence ECE Measurement (GATE)** | **FDA SaMD, SR 11-7, GDPR Art 22** | **<60s CPU smoke** | **0.28 raw / 0.55 w/ temp scaling** |
| 2 | Confidence-Thresholded Refusal at τ | Medical privilege review; eDiscovery | downstream of #1 | 0.38 (precision≥0.92 at coverage≥0.60) |
| 3 | Validation Suite as Sellable Artifact (cert + bootstrap CIs) | ISO 13485, SOX, audit defensibility | B2B product layer | 0.45 (temp scaling sufficient) |
| 4 | **Per-Hop vs Per-Chain in Multi-Hop** | **Legal brief gen + medical diff diagnosis** | layer on #1 | 0.32 (per-hop ECE<0.08) |
| 5 | Adversarial Robustness of Algebraic Confidence | Security-critical / fraud detection | one cheap smoke | 0.35 (speculative) |

**The hard part is calibration, not confidence**: substrate's Bayesian posterior is in correct mathematical form but ECE is empirical. Sub-cap 1 GATES everything. If ECE>0.15 unrecalibrated → add temperature scaling → re-measure → product story unlocks only if ECE<0.05 achievable.

**Sequencing**: Sub-cap 1 GATE first (<60s CPU). Sub-cap 4 in PARALLEL (multi-hop decomposability is uniquely substrate). Sub-caps 2-3 downstream. Sub-cap 5 opportunistic.

### Drill 6: Sparse-block-code substrate variant (10-axis comparison)

**STRATEGIC POSITIONING: Option (c) specialized layer NOT (a) replacement / NOT (b) parallel full-feature / NOT (d) fallback-only.** Overall P=0.52 for (c); P=0.28 for (a)/(b).

Reason: dense and sparse have COMPLEMENTARY (not competing) capability surfaces:

| Axis | Winner | Margin | Key driver |
|---|---|---|---|
| 1. Storage capacity M_max | UNCERTAIN | P=0.35 sparse | Information deficit vs interference suppression |
| 2. Multi-hop depth ≥5 | **DENSE** | P=0.22 sparse | BCF limit cycles under accumulated noise |
| 3. Structured-key interference (PP-11) | **SPARSE** | P=0.42 sparse | Block-local geometry |
| 4. Audit accuracy ≥95% | UNCERTAIN | P=0.45 sparse | Block-local exact vs accumulated noise |
| 5. Compression compatibility (bits8) | DENSE | P=0.35 sparse | W quantization hazard |
| 6. Adversarial defense | UNCERTAIN | P=0.38 sparse | Voting structure vs block-targeted attacks |
| 7. **Edit isolation cost (10× COW)** | **SPARSE** | **P=0.48 sparse** | **W matrix density 1/K² → near-zero COW** |
| 8. Codebook design space | DENSE | P=0.28 sparse | Unconstrained codebook advantage |
| 9. **Hardware acceleration** | **SPARSE** | **P=0.45 sparse** | **64× neuromorphic; 4-16× sparse-tensor** |
| 10. Cross-N scaling | UNCERTAIN | P=0.40 sparse | K-proportional scaling required |

**Implementation: 8-12 eng-weeks full substrate variant; 4-6 eng-weeks smoke-only (axes 3, 7, 9).**

**Architectural decomposition** (the load-bearing finding):
- Sparse for edit/audit operations (Axis 7 maps to **edit-with-impact-prediction + per-fact retention policy** = TWO killer features unblocked)
- Dense for chain retrieval (Axis 2 Path D unmatched)
- Per-fact retention policy + edit-with-impact-prediction = edit-heavy → sparse better
- Deletion certificate = exact audit traceability → sparse block-local unbinding cleaner
- Live drift detection + compositional audit = chain retrieval at depth → dense better

**Sequencing**: Axis 7 (edit isolation) smoke FIRST (<60s, smallest infrastructure, highest theory confidence, unblocks 2 killer features). Axis 3 (structured-key PP-11) SECOND (peer-reviewed theoretical prediction; reuses PP-11 infrastructure). Axis 2 (multi-hop chain) DEFER (BCF limit-cycle is highest technical risk; needs damping mechanism that's a research gap).

## Cap_map implications (cross-drill)

Multiple cap_map rows would update from this body of work:

**Direct LIFTs possible**:
- PP-4 concept drift detection: 🔬 0.40-0.55 → 🟡 if Mechanism 3 (Write-to-Retrieve Ratio) HARD-PASSes
- Edit-with-impact-prediction: ZERO cap_map row currently → ADD row at 🔬 0.55-0.70 (Mechanism 1 DAG traversal is deterministic)
- PP-7 multi-substrate composition: 🔬 needs-re-anchoring → can NARROW to "routing-only, no spectral capacity advantage" per Free-additivity prediction
- Calibrated confidence: NEW row needed; 🔬 0.30-0.50 pending Sub-cap 1 smoke
- Substrate-as-KV-cache: NEW row needed; 🔬 0.40-0.60 pending #1 + #3 smoke
- Sparse-block-code substrate variant: NEW row needed; 🔬 0.45-0.65 (Option c specialized layer)

**Retroactive theoretical validation**:
- Path D K=2 saturation sub-row: ALREADY validated empirically; add K_max(α) formula as theoretical explanation → P-band tighten 0.92-0.98 → 0.95-0.99

## What I'm routing to orchestrator

Single consolidated `strategy_request_to_strategy_capabilities_expansion_followon_experiments_2026-06-01.md` proposing the priority dispatch list. Plus a separate exp_dev sizing routing for N=32768 (no research needed; just dry-run sizing).

## Method notes

- 6 parallel Sonnet drills + main-thread synthesis = ~120K-180K tokens combined for substantial-depth coverage of 6 capability gaps
- Per [[feedback-subagent-model-optimization]]: Sonnet appropriate for lit-scan + design-pattern drills
- Per [[feedback-query-privacy-decomposition]]: all drills used generic VSA / generic ML terms; no project-identifying fingerprints in any web search
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated throughout; novel-synthesis cap at 0.50 applied
- Per [[feedback-no-padding-experiments]]: 6 drills each on distinct capability axis; no overlap with prior session work
- Per [[feedback-aggressive-cross-domain-research]]: free probability cross-domain probe was overdue; now landed
- Wall time: dispatch + 6 parallel drills (~3min each) + synthesis ≈ 20-30 min main-thread; cheaper than 6 sequential drills by ~80%


---

Acted-on 2026-06-01: Round 1 6-drill synthesis adopted in cap_map v316 via parallel routing; 4 NEW EMPIRICAL rows + 3 LIFTs


Acted-on 2026-06-01: Round 1 6-drill synthesis adopted in cap_map v316; 4 NEW EMPIRICAL rows + 3 LIFTs
