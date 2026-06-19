# Strategy request: capabilities-expansion follow-on experiments (6-drill consolidated routing)

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_capabilities_expansion_6_drills_2026-06-01.md` (full 6-drill synthesis with calibrated P estimates + smoke designs per drill)
**Trigger**: User stock-taking surfaced "a ton of untested capabilities"; user greenlit dispatch on all surfaced items

## TL;DR

6 capability drills produced concrete experimental proposals across 4 strategic clusters. Total proposed work: ~20-30 cheap diagnostic smokes + 2 medium-cost engineering tracks, sequenced cheapest-first. **Three findings carry the most strategic weight**:

1. Free probability K_max(α) formula retroactively explains v308 K=2 cliff → theoretical scaffold for multi-hop design rules
2. Sparse-block-code substrate as **specialized layer** (Option c, P=0.52) NOT replacement → unblocks 2 killer features (edit-with-impact-prediction + per-fact retention policy) via 65,000× edit-isolation cost reduction
3. PP-4 + edit-impact + calibrated confidence + KV-cache-with-audit form coherent killer-features cluster around substrate's intrinsic algebraic cert (vs extrinsic logging)

## Strategic clusters + proposed sequencing

### CLUSTER A — "substrate-state-as-product-signal" (4 killer features)

Each is a distinct product capability; combined they extend the validated audit wedge into operational/inference-time signals.

**Tier 1 dispatchable now** (cheap diagnostics; high info gain regardless of PASS/FAIL):

| Item | Source | Cost | Pre-reg HARD-PASS |
|---|---|---|---|
| **Calibrated confidence ECE gate smoke** (Drill 5 Sub-cap 1) | Drill 5 | <60s CPU; N=1024, K=100, 200 test queries | ECE<0.05 raw OR ECE<0.05 after temperature scaling |
| **PP-4 drift detection: Write-to-Retrieve Ratio** (Drill 1 Mech 3) | Drill 1 | ~30 LOC; online (no new compute) | ρ_t > μ+3σ within 1000 ops of synthetic 5× write burst; <5% false-alarm rate |
| **PP-4 drift detection: Codebook Histogram Divergence** (Drill 1 Mech 1) | Drill 1 | ~50 LOC; online | KL(H_t \|\| H_baseline) > bootstrap 95th-pct τ within 800 ops; <5% false-alarm |
| **Edit-impact: DAG Reverse-Traversal** (Drill 2 Mech 1) | Drill 2 | <1ms typical; deterministic | Precision≥0.95, Recall=1.00 |

**Tier 2 contingent on Tier 1** (~1-2 eng-weeks each):

| Item | Depends on | Cost | Pre-reg HARD-PASS |
|---|---|---|---|
| Calibrated confidence refusal gate at τ (Drill 5 Sub-cap 2) | ECE<0.05 GATE | downstream cost only | Precision≥0.92 at coverage≥0.60 at τ=0.7 |
| Calibrated confidence per-hop in multi-hop (Drill 5 Sub-cap 4) | ECE<0.05 GATE | layer cost | Per-hop ECE<0.08; chain precision≥0.88 at min-hop τ=0.7 |
| Edit-impact: Merkle Proof Survivability (Drill 2 Mech 3) | DAG framework | sub-ms; deterministic | Precision=1.00, Recall≥0.95 on cert-break prediction |
| Edit-impact: Algebraic Perturbation (Drill 2 Mech 2) | DAG framework | ~4ms at k=50 | MAE<0.05 on score shift; cert-survival accuracy≥0.90 |
| PP-4 drift detection: LPAS LLM-judge (Drill 1 Mech 5) | Pattern B API ready | ~$0.03/hour | KS(LPAS) >3σ within 150 samples; <5% false-alarm |

### CLUSTER B — "free probability theoretical scaffold"

Three CPU/GPU smokes that each independently validate (or falsify) a published-math prediction. Run in parallel batch.

| Item | Predicted formula | Cost | Pre-reg HARD-PASS |
|---|---|---|---|
| **Rank-1 Edit Perturbation (Drill 3 C4)** — K≈√N edit budget | KS distance between empirical eigenspectrum and MP grows linearly with K/√N | CPU ~10min | √N crossover detectable at K=64 ± 1 for N=4096 |
| **Free Additivity (Drill 3 C3)** — hierarchy = flat at matched load | μ_aggregate = MP(α_total) | CPU ~15min | Flat retrieval ≈ hierarchical-collapsed retrieval at matched α within 1% |
| **K_max(α) formula (Drill 3 C5)** — explains v308 K=2 cliff | K_max ≈ log(1/α)/(2√α) | GPU ~25min | K_max crossover at α=0.10 within ±1 hop of predicted K≈3.6 |

If all three HARD-PASS: 3 cap_map rows update from 🔬 to 🟢 in single run. PP-7 hierarchy narrows to "routing-only no spectral advantage"; PP-3 + PP-4 get concrete K≈√N rotation cadence; Path D K=2 saturation gets theoretical scaffold.

### CLUSTER C — "substrate-as-KV-cache" (LLM integration product layer)

Two parallel engineering smokes; both ship audit-cert as the moat (NOT latency improvement).

| Item | Compliance angle | Cost | Pre-reg HARD-PASS |
|---|---|---|---|
| **Tool-call result caching w/ audit cert** (Drill 4 #1) | GDPR Art 17 deletion-cert | 1-2 eng-weeks; ~50ms p99 vs <1ms Redis | 100% exact-key hit + cert generated + deletion cert valid + <50ms p99 |
| **System prompt amortization w/ provenance cert** (Drill 4 #3) | EU AI Act Art 13 transparency | 1 eng-week; ~30ms overhead | Version-cert zero cross-contamination + deletion cert valid + <30ms overhead |

NOT recommended now (deferred to weeks 3-4): per-conversation entity memory (depends on Tool-call #1 cert infrastructure) + multi-LLM shared fact store (needs additional Q-Former bridges per LLM family).

NOT selected (honestly rejected with rationale): speculative-decoding draft cache (substrate adds latency not removes it); per-fact-derived KV reuse (couples to LLM architecture version which is unstable).

### CLUSTER D — "sparse-block-code substrate variant" (specialized layer for edit/audit operations)

**Strategic positioning recommendation: Option (c) specialized layer** (sparse for edit/audit, dense for chain retrieval). NOT (a) replacement. NOT (b) parallel full-feature. P=0.52 (c); P=0.28 (a)/(b).

Three smoke validations to bracket the strategic case before committing to 8-12 eng-week full substrate variant:

| Item | Strategic justification | Cost | Pre-reg HARD-PASS |
|---|---|---|---|
| **Axis 7 Edit Isolation smoke (Drill 6)** | If W fill <5% at M=500, COW collapses to near-zero → unblocks edit-with-impact-prediction + per-fact retention policy | <60s CPU; minimal infrastructure | W nonzero fraction <5% at M=500 N=8192 K=32 |
| Axis 3 Structured-Key PP-11 smoke (Drill 6) | Tests block-local geometry hypothesis on PP-11 gap; reuses PP-11 infrastructure | CPU 10-15min; substitute DSBC binding for Hadamard | Per-hop accuracy gap <2pp on 5/5 seeds at N=4096 |
| Axis 9 Hardware Efficiency smoke (Drill 6) | Validates 4-16× sparse-tensor accelerator advantage on GPU | GPU 10-15min; block-sparse GEMV vs dense GEMV at M=500 | Sparse FLOP count <10% of dense FLOP count at M=500 N=8192 |

If 2 of 3 HARD-PASS → commit to full sparse substrate variant build (~8-12 eng-weeks). If 1 of 3 HARD-PASS → smoke remaining axes opportunistically. If 0 of 3 HARD-PASS → close sparse variant direction; cap_map row 🔴.

## Cap_map implications (consolidated)

Direct LIFTs / new rows possible from this body of work:

| Cap_map row | Current state | Conditional movement |
|---|---|---|
| PP-4 concept drift detection | 🔬 0.40-0.55 | → 🟡 0.50-0.65 if Cluster A Tier 1 PP-4 smokes HARD-PASS |
| Edit-with-impact-prediction (NEW) | (no row) | ADD 🔬 0.55-0.70 (Mechanism 1 deterministic) |
| Calibrated confidence (NEW) | (no row) | ADD 🔬 0.30-0.50 pending Sub-cap 1 ECE gate |
| Substrate-as-KV-cache (NEW) | (no row) | ADD 🔬 0.40-0.60 pending #1 + #3 smokes |
| PP-7 multi-substrate composition | 🔬 needs-re-anchoring | NARROW to "routing-only, no spectral capacity advantage per free-additivity" if Cluster B HARD-PASSes |
| PP-3 audit rotation | 🟡 0.55-0.70 | Add caveat: "K≈√N edits cadence per free-probability rank-1 perturbation theory" if Cluster B C4 HARD-PASSes |
| Path D K=2 saturation sub-row | ✅ 0.92-0.98 | Tighten to 0.95-0.99 with K_max(α) theoretical scaffold if Cluster B C5 HARD-PASSes |
| Sparse-block-code substrate variant (NEW) | (no row) | ADD 🔬 0.45-0.65 (Option c specialized layer) if Cluster D ≥2/3 HARD-PASS |

## Contract for strategy

Strategy decides:

1. **Cluster A dispatch immediate?** (4 cheap Tier 1 diagnostics; total wall <3 hours; research strongly recommends YES)
2. **Cluster B parallel batch dispatch?** (3 smokes; total wall ~25min; cap_map clarifies 3 rows in one run)
3. **Cluster C engineering routing to testbed?** (Tool-call cache + System prompt amort; 2-3 eng-weeks combined)
4. **Cluster D edit-isolation smoke first?** (Axis 7 only; <60s; gates strategic decision on sparse variant)
5. **Are NEW cap_map rows authorized?** (Edit-with-impact-prediction, Calibrated confidence, Substrate-as-KV-cache, Sparse-block-code variant — 4 new rows under proposal)
6. **N=32768 envelope sizing routing acceptable?** (Filed separately; sizing-only; not research)

## Files referenced

- `notes/research_capabilities_expansion_6_drills_2026-06-01.md` (full 6-drill synthesis)
- `notes/research_atom_registry_design_review_v1_2026-06-01.md` (atom-registry DAG that makes edit-impact tractable)
- `notes/research_pp11_reasoning_storage_borderline_save_2026-05-31.md` (PP-11 baseline for Cluster D Axis 3)
- `notes/research_negative_results_2x_deep_2026-06-01.md` (today's percolation drill that scoped free-probability narrower)
- `notes/substrate_capability_map.md` (rows referenced above)
- `notes/strategy_request_to_strategy_n32768_envelope_sizing_2026-06-01.md` (parallel exp_dev routing)

## Method notes

- Per [[feedback-no-padding-experiments]]: each cluster maps to a distinct capability gap surfaced in stock-taking; not padding
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest diagnostic tests sequenced first within each cluster
- Per [[feedback-no-experiment-design-in-prompts]]: routing hands TASK + WHY + CONTRACT + AUTONOMY; sweep grids and threshold formulas remain exp_dev's call where details aren't load-bearing
- Per [[feedback-substrate-value-framing-matured-2026-05-26]]: clusters are weighted by strategic-positioning impact, not theoretical interest

## Closing

Move to `routed_completed/` when strategy decides Cluster A/B/C/D dispatch sequencing AND authorizes (or declines) the 4 proposed new cap_map rows.


---
**ROUTED-COMPLETED**: Acted-on 2026-06-01: 4 NEW cap_map rows from this routing (Edit-with-impact PP-17, Calibrated confidence PP-18, Substrate-as-KV-cache PP-19, Sparse-block-code PP-20) ADOPTED in v314; Cluster A+B+D Tier 1 dispatch filed for exp_dev
