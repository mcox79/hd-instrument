# Research: PP-8 Round 4 — 3-drill synthesis of paths beyond A/B/C (2026-06-01)

Date: 2026-06-01
Origin: user asked "should we also do 2x deep research to see if there are other paths that could be uniquely beneficial here?" after recommending A/B/C sequence
Method: 3 parallel Sonnet drills (~95-200s each, ~95K tokens combined) + main-thread synthesis

## HEADLINE

**Three orthogonal axes for paths uniquely beneficial vs A/B/C identified.** Each drill addresses a distinct question that A/B/C (generalization / HP-tuning / multi-hop validation) cannot answer:

1. **M1 vs M2 mechanism decoupling** — IS Phi-3 necessary at all? If M1 (projection smoothness via SimHash/JL) dominates, architecture collapses to "any embedding + random projection works" → no Phi-3 dependency, much cheaper architecture.

2. **Architecture vs HP origin of 98%→35% oscillation** — is the oscillation HP-fragility (Option B fixes it) OR quantization-induced gradient corruption (arxiv 2603.10444 mean-bias hypothesis)? Different remedies; needs disambiguation.

3. **Production-deployment paths** — does Path 1a extend beyond toy-task batch retrieval to (a) KV-cache integration, (b) streaming workload, (c) multi-LLM portability, (d) LLM-initiated writes? A/B/C never address production scope.

**Cumulative threshold for Round 4 dispatch decisions**: $25-30 Lambda combined for ALL TIER-1 cheap smokes across the 3 drills. Highest information-per-dollar items:
- **D1 Design 1 frozen-random control** ($0.50-1; tests M1/M2 dominance — PIVOT EXPERIMENT)
- **D2 Design 1+2 layer × precision combined** ($12-15; resolves architecture vs HP)
- **D3 Path A KV-cache integration smoke** ($10-15; tests highest-P production extension)

## PER-DRILL SUMMARY

### Drill 1: M1 vs M2 mechanism decoupling

| Design | Mechanism controlled | Cost | P(M2 load-bearing) |
|---|---|---|---|
| **D1-1 Frozen-random hidden state control** | M2 surgically removed (random N(0,I) instead of Phi-3) | **$0.50-1 CPU** | **PIVOT TEST** |
| D1-2 Layer ablation (1 / 16 / 32) | M2 contribution as function of transformer depth | $3-6 | Probing literature predicts monotone with depth |
| D1-3 Embedding-layer-only control | Token-level vs contextual M2 contribution | $1-2 | If embedding ≈ final layer → 30-50× inference cost reduction |
| D1-4 Cross-LLM Phi-3 → Llama-3 / Mistral | M2 portability across LLM family | $4-8 | LQMP family cross-cosine +0.79 prior |

**Sequencing**: D1-1 first (PIVOT — if val_random ≈ 38%, M1 dominates, Phi-3 unnecessary). D1-3 second (token vs contextual). D1-2 + D1-4 conditional on M2 confirmed.

**Calibrated Ps**:
- P(val_random < 15%, M2 load-bearing) = 0.45
- P(M1-dominant, Phi-3 unnecessary) = 0.35
- P(both contribute comparably) = 0.20

**Strategic implication**: If D1-1 shows M1-dominant, architecture simplifies DRAMATICALLY — any embedding + random projection works; no need for 7B-param Phi-3 inference. Could ship with cheap sentence encoders.

### Drill 2: Layer × precision isolation (98%→35% oscillation origin)

| Design | Mechanism controlled | Cost |
|---|---|---|
| **D2-1 Layer probe (1 / 16 / 32, same 4-bit)** | Mean-bias depth-dependence (arxiv 2603.10444) | $6-9 |
| **D2-2 bf16 vs 4-bit at layer 32** | Direct FM-6 quantization × gradient test | $4-6 |
| D2-3 Layer × precision 2×3 matrix combined | Interaction term resolution | $10-15 |
| D2-4 Pooling variation at best layer | Last-token vs mean-pool vs attention-pool | $6-9 |

**Sequencing**: D2-1 + D2-2 in parallel ($12-15 combined) resolves "architecture vs HP" question. D2-4 conditional on Tier 1 unclear. **Option B LR-tweak (orchestrator's existing option) is Tier 3 fallback only if architectural fixes fail.**

**Calibrated Ps**:
- P(layer 16 × bf16 stably holds ≥90%) = 0.35-0.45
- P(architectural fix fails entirely, Option B required) = 0.30-0.40

**Strategic implication**: If architectural fix works (layer + precision), it's strictly preferable to schedule tuning — more reproducible, transfers across HP configs. Literature anchors strong: arxiv 2603.10444 (FP4 mean-bias) + arxiv 2602.00969 (spectral flattening) + arxiv 2412.09563 (mid-layer dominance for MTEB).

### Drill 3: Production-deployment paths (orthogonal to A/B/C validation)

| Path | Mechanism | Cost | P |
|---|---|---|---|
| **A KV-Cache Integration** | Audit-grade tool-call result cache with cert chain | **$10-15 Lambda / 3-4 eng-days** | **0.52** |
| B Streaming Inference | Continuous write/retrieval over hours/days | $15-20 / 4-5 eng-days | 0.45 |
| D LLM-Initiated Writes | LLM authors writes (MemLLM/GradMem precedents) | $12-18 / 4-5 eng-days | 0.35 |
| C Multi-LLM Portability | Joint-calibrated R_A / R_B for shared substrate | $20-25 / 5-6 eng-days | 0.25 |

**Sequencing**: Path A first (highest P, lowest cost, GDPR Art 17 deletion-cert differentiator). Path D second (active knowledge substrate vs passive cache — highest strategic leverage if passes). Path B third (frozen LLM = stable R, likely PASS). Path C last (cross-architecture projection collapses across reasoning domains per "Thinking in Different Spaces" 2026; mean R²=-3.83).

**Threshold verdict**: Path A + (Path B OR Path D) PASS = sufficient production-extension coverage to justify productization sprint.

**Competitive landscape gaps (what Path 1a uniquely adds across all 4)**:
- Cryptographic deletion certificates (GDPR/HIPAA differentiator) — LangChain Memory / Mem0 / Anthropic Memory cannot match
- Semantic near-match caching without exact-sequence matching (TVCACHE requires identical tool-history sequences)
- Cross-LLM key alignment via joint-calibrated R matrices (no existing product)
- LLM-initiated writes with audit-grade provenance (MemLLM/GradMem precedents but no production product)

## INTEGRATED TIER-1 DISPATCH PLAN (Round 4 cheap diagnostics)

If all 3 drill recommendations are dispatched in parallel, total Tier 1 cost ≈ $25-30 Lambda + ~3-4 eng-days. Each test answers a qualitatively different question:

| Test | Cost | Question answered | Decision driven |
|---|---|---|---|
| **D1-1 frozen-random control** | **$0.50-1** | Is Phi-3 necessary? | If M1-dominant → simplify architecture |
| **D2-1+D2-2 layer × precision** | **$12-15** | Architecture or HP origin of oscillation? | Architectural fix (preferred) vs Option B LR tweak |
| **D3-Path-A KV-cache smoke** | **$10-15** | Does Path 1a extend to audit-grade tool-call caching? | Validates first production-extension path |

Combined: $22-30 for three decisive cheap tests that give qualitatively different information than A/B/C.

## RECOMMENDED SEQUENCE (research-side)

Given the orchestrator's existing A/B/C decision is pending and CPU+GPU queues are now empty per status update:

1. **D1-1 frozen-random control FIRST** ($0.50-1; CPU; <30min). PIVOT — outcome determines whether subsequent investment goes into Phi-3-specific optimization or embedding-agnostic simplification. **Highest info-gain per dollar of any test surfaced today.**

2. **In parallel with D1-1**: orchestrator's **Option A (generalization test on held-out keys)** as already recommended. Both are cheap; both decisive.

3. **Conditional on D1-1 + Option A outcomes**:
   - If M1 dominant (D1-1 val_random ≈ 38%): skip Phi-3-specific layer/precision investigation; focus on simplification + portability
   - If M2 load-bearing AND Option A held-out PASS: dispatch D2-1+D2-2 ($12-15) for architecture vs HP resolution + D3-Path-A KV-cache smoke
   - If Option A held-out FAIL: M2 generalization claim narrows; D1-2 layer ablation becomes more important to understand what M2 is doing

## CONNECTING TO EARLIER FRAMEWORK REFUTATIONS

Today's v316 cap_map verdict swept in TWO mean-field framework refutations:
- Percolation N-independence at v312 (covered by my morning negative-results 2x-drill — predicted depth-composition cliff which empirically validated)
- Free-probability framework at finite-N (3 axes today: rank1-edit HF + free-additivity MID + kmax-formula MID)

**Pattern**: substrate's finite-N regime is unmapped territory; mean-field frameworks (equilibrium-class) consistently fail at predicting substrate behavior. Substrate sits in non-equilibrium stat-mech territory per `[[project-substrate-non-eq-stat-mech-class-2026-05-27]]`.

**For Round 4 PP-8 calibration**: the 3 drill Ps above already include 0.15-0.25 deflation per `[[feedback-lit-scan-calibration-penalty]]`. Given today's two framework refutations, consider deflating an ADDITIONAL 0.05-0.10 on the production paths (Drill 3) since they assume Path 1a's algebraic structure behaves as the design review predicted, which itself is uncharted-regime claim.

## CALIBRATION PRACTICE UPDATES

Per [[feedback-no-preframe-batch-all-pass]] (saved today after PP-8 v316 over-claim catch #173):
- All Tier 1 designs above include explicit HARD-PASS / MIDDLE-BAND / HARD-FAIL bands per design
- No batch-level expectation stated
- Cheap-smoke framing foregrounds MIDDLE-BAND and HARD-FAIL as fully legitimate verdicts

Per today's framework-refutation pattern:
- Mean-field literature priors are weakly informative at substrate finite-N
- Direct adjacent precedents (NVSA for derived-codeword; FP4 mean-bias for quantization; MemLLM for LLM-initiated writes) are stronger evidence than abstract framework predictions

## CLOSING

This synthesis is research's contribution to the strategy A/B/C decision: 3 ADDITIONAL paths uniquely beneficial vs A/B/C, with combined Tier-1 cost ~$25-30. Strategy/orchestrator picks dispatch sequencing.

Note path: `notes/strategy_request_to_strategy_pp8_round4_3_drills_synthesis_2026-06-01.md` (routing forthcoming).

---

**ROUTING STATUS**: Acted-on 2026-06-01: 3-drill synthesis adopted; framework-refutation-aware calibration noted in cap_map v317 intro; production-path conditional dispatch tree authorized
