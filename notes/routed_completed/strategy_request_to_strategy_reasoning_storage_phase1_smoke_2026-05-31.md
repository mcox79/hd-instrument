# Strategy request: substrate reasoning-storage Phase 1 smoke (Scheme B + structured-key Path D differential)

## Trigger: research 2x deep drill 2026-05-31 (3 parallel Sonnet drills synthesized)

Origin: user 2026-05-31 "re your research of storing reasoning chains on substrate - do 2x deep research" (per [[feedback-2x-means-depth]] = operational depth not verification). Full synthesis at `notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md`.

## Finding (one paragraph)

3 parallel Sonnet drills (encoding scheme + structured-key Path D analysis + operational worked example) produced a sharper and more honest picture than the original "substrate-as-reasoning-store" framing. Substrate reasoning storage IS a distinct capability under bipolar MAP-B algebra (Scheme B three-way binding `k_step = r_type ⊙ k_premise1 ⊙ k_premise2` is EXACTLY decomposable; P_def 0.62) BUT Path D's validated 32N envelope does NOT transfer to structured-key reasoning chains without explicit mitigation (P_def 0.35 unmitigated; De Marzo-Iannelli 2023 + Amit-Gutfreund-Sompolinsky 1985 predict 5-25% capacity degradation with structural correlation). Conclusion re-encoding via binding transform is the highest-leverage mitigation (Steinberg-Sompolinsky 2022 precedent). The substrate is a RETRIEVAL primitive not a REASONING primitive — inter-hop key construction is external; substrate cannot autonomously discover new chains. The honest product framing scopes reasoning storage to PRE-STORED chains with external chain construction (LLM-orchestrated OR Proposal-2 rule-atoms), not open-ended autonomous reasoning. Joint P_def 0.40-0.55 for substrate reasoning storage delivering product-distinctive capability at N=16384 sub-saturation with conclusion re-encoding mitigation.

## Recommended action

**1. Cap_map: NEW row proposed (research-only 🔬).**

Row name: "Substrate reasoning-storage via Scheme B three-way binding"

Initial P-band: 0.40-0.55 (range reflects conclusion-re-encoding mitigation tractability vs structured-key envelope risk)

Caveats: (a) requires N≥16384 to avoid composition blowup; (b) conclusion re-encoding mitigation needed as default; (c) substrate doesn't autonomously discover chains — pre-stored or LLM-orchestrated only; (d) audit decomposition exact for atomic codewords but degrades with retrieval noise (hop-by-hop cleanup needed for depth >5); (e) at >~44K shared-rule-atoms (N=4096) spectral concentration kicks in

**2. Cap_map: UPDATE to substrate-product-feature row.**

Add caveat: "reasoning storage" scoped to PRE-STORED chains with external chain construction; substrate provides retrieval + audit + speed for pre-specified chains, not autonomous open-ended reasoning. Honest product framing matters for positioning.

**3. NEW experiment to dispatch.**

**Anchor**: `reasoning_storage_scheme_b_smoke_v1_n16384`

**Spec sketch (exp_dev refines)**:

Setup:
- N=16384 (must be ≥16K to avoid composition blowup per drill β capacity math)
- Codebook: BSC bipolar
- Rule codebook: 5 inference-rule codewords (modus ponens, transitive, abductive, analogical, causal) drawn once
- Entity codebook: 200 entity codewords
- Relation codebook: 20 relation codewords
- Corpus: 500 reasoning chains, depth=3-5, structured-key (shared rule_codes + shared intermediate entities)
- MATCHED random-key corpus for differential measurement (same M, D, N, but randomly permuted keys breaking structural constraints)

Test arms:
- **Arm 1: Scheme B encoding exactness** — encode each reasoning step as k_step = r_type ⊙ k_premise1 ⊙ k_premise2; store via outer product; verify exact audit decomposition by unbinding each component
- **Arm 2: Structured-key Path D differential** — Path D depth=5 retrieval on structured corpus vs matched random-key corpus; measure per-hop accuracy, posterior entropy, top-50 singular values, cross-talk noise
- **Arm 3: Conclusion re-encoding mitigation** — repeat Arm 2 with ρ(v_n) permutation applied between hops; measure restoration toward random-key baseline
- **Arm 4: Shared-rule threshold sweep** — at N=4096 (cheaper), sweep #chains-sharing-modus-ponens-rule_code in {100, 1K, 10K, 44K, 100K}; locate spectral collapse threshold empirically

**Pre-reg HARD-PASS** (per drill α + drill A combined):
- Arm 1: all 3 components recoverable from k_step to nearest-neighbor in respective codebooks with confidence ≥0.95 (~exact decomposition)
- Arm 2: structured-key per-hop accuracy ≥0.95 × random-key baseline; top σ_1/σ_2 <3× Marchenko-Pastur edge; posterior entropy elevation <0.5 bits
- Arm 3: structured-with-mitigation ≥0.95 × random-key baseline (mitigation restores envelope)
- Arm 4: spectral collapse at #chains ≤44K consistent with theoretical prediction

**Pre-reg HARD-FAIL**:
- Arm 1: any component fails to decompose to nearest-neighbor with confidence ≥0.85 (encoding broken)
- Arm 2: structured-key accuracy <0.85 × random; σ_1/σ_2 >3× MP edge (spectral collapse); entropy elevation >0.5 bits
- Arm 3: mitigation doesn't restore envelope (residual gap >10% vs random-key baseline)
- Arm 4: spectral collapse at #chains <10K (4.4× earlier than predicted; severe capacity issue)

**Pre-reg MIDDLE-BAND**:
- Arm 2 accuracy in [0.85, 0.95] × random; σ_1/σ_2 in [1.5, 3]× MP edge; entropy in [0.2, 0.5] bits — partial generalization, mitigation likely required
- Arm 3 mitigation in [85%, 95%] restoration — partial mitigation, may need stacking with sparse encoding (Hersche-style)

**Cost**: ~3 weeks engineering + ~4-8h GPU. Local GPU sufficient (Modern Hopfield N=16384 already validated on-substrate per v297 cap_map). NO CLOUD SPEND.

**Routing**: orchestrator → exp_dev → queue.

**4. Sequencing recommendation.**

After:
- Substrate-LLM Week 0 Missing 7 verdict (~tonight when V2 drains) — gates the LLM integration architecture
- D7 Bet B ret_A rescue (already sequenced first in `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md`)

Before:
- D1 compositional binding production scope — D1 tests Scheme A; this experiment tests Scheme B; results from this experiment INFORM whether to scope D1 to Scheme A only or extend to Scheme B comparison
- Reasoning amortization experiment (`notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md`) — amortization economics depends on Scheme B working at all; this experiment is the prerequisite

In parallel with:
- D6 hierarchical concept formation (CPU-bound instrumentation; different machine resources)

**5. Caveat list update for substrate-LLM Phase 1 build.**

Add to `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`:
- "Substrate-augmented LLM" claim scoped to LLM-orchestrated chain construction; substrate provides retrieval + audit + speed for pre-specified chains, not autonomous open-ended reasoning
- The 4 bespoke benchmarks (edit-then-query, deletion-cert audit, provenance citation, real-time-learn-then-query) test substrate-distinctive properties consistent with the honest framing — no changes needed to those benchmarks
- Rescue C ("substrate runs Path D depth=5 autonomously; LLM emits single query") is HONEST per worked-example finding — substrate runs the iteration mechanically per pre-stored chains, LLM constructs initial query

## Confidence

P_deflated for the proposed experiment delivering definitive verdicts:
- Arm 1 (Scheme B encoding exactness): 0.85 — algebraic argument is exact under MAP-B; empirical verification should be near-certain unless bugs
- Arm 2 (structured-key envelope differential): 0.65 — drill α theory predicts measurable degradation; empirical measurement at production scope is the open question
- Arm 3 (conclusion re-encoding mitigation): 0.55-0.70 — Steinberg-Sompolinsky precedent strong but no direct empirical test in this substrate class
- Arm 4 (shared-rule threshold): 0.70 — theoretical prediction (44K at N=4096) testable directly; the threshold IS empirically locatable

Joint P_def for HARD-PASS across all 4 arms: 0.40-0.55. This matches the cap_map row band.

## Files of interest

- `notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md` (full synthesis of 3 drills; 6 operational gaps; mitigation rankings; pre-registered thresholds)
- `notes/research_substrate_as_reasoning_store_audit_v1_2026-05-31.md` (initial 8-experiment audit; encoding-scheme drill prerequisite identified)
- `notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (Exp 2 reasoning amortization; still valid; reframed in synthesis as caching pre-stored Scheme B chains)
- `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md` (D1 stays as Scheme A; this experiment is Scheme B separate)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (build Rescue C aligns with worked-example honest framing; caveat list update recommended)
- `notes/substrate_capability_map.md` v297 (Modern Hopfield N=16384 max_M=16N empirically confirmed; provides the substrate-side capacity headroom for this experiment)
- Memory: `feedback_2x_means_depth` (validated this turn's drill discipline), `feedback_lit_scan_calibration_penalty`, `feedback_no_smoke`

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Whether to add the cap_map row (NEW: "Substrate reasoning-storage via Scheme B three-way binding" at 0.40-0.55)
- (b) Whether to update substrate-product-feature row with the honest-framing caveat
- (c) Experiment dispatch timing (recommended after D7 + Week 0; before D1 + amortization)
- (d) Whether to update substrate-LLM build handoff with the caveat-list addition

No engineering work begins without orchestrator queueing.

---
Acted-on 2026-05-31: reasoning_storage Phase 1 smoke already shipped as `reasoning_storage_scheme_b_smoke_v1_n16384` + `reasoning_storage_threshold_sweep_v1_n4096` in commit 35fa239; routing acknowledged + closed.
