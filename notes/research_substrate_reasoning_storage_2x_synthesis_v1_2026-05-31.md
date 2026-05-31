# Research: substrate reasoning storage 2x deep synthesis (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- "re your research of storing reasoning chains on substrate - do 2x deep research" (per [[feedback-2x-means-depth]] = level-2 operational deepening, not verification re-run)
Method: 3 Sonnet drills run in parallel; main-thread synthesis. Drill A = encoding-scheme question (Scheme A vs B vs C); Drill α = structured-key Path D envelope analysis; Drill β = operational worked example with explicit bipolar math.

## HEADLINE

The 2x deepening produced a SHARPER and MORE HONEST picture than the original "substrate-as-reasoning-store" framing. Combining the 3 drills:

1. **Scheme B encoding works exactly** under bipolar MAP-B algebra: `k_step = r_type ⊙ k_premise1 ⊙ k_premise2` decomposes to recover any component via element-wise multiplication. Three-way binding gives EXACT audit decomposition (HRR's circular convolution is only approximate). P_def 0.62 that Scheme B unlocks capabilities Scheme A cannot.

2. **Path D's validated 32N envelope DOES NOT transfer** to structured-key reasoning chains without explicit mitigation. P_def 0.35 unmitigated. Theoretical literature (De Marzo-Iannelli Physica A 2023; Amit-Gutfreund-Sompolinsky 1985) shows pattern correlation strictly decreases α_c. Depth-50 chain accuracy compounds: even 2% per-hop bias → (0.98)^50 ≈ 0.36 chain accuracy.

3. **The operational worked example surfaces 6 GAPS the abstract framing hid.** Most important: **the substrate is a RETRIEVAL primitive, not a REASONING primitive.** After hop 1 retrieves v_BookA, the substrate CANNOT autonomously construct q_1 = bind(v_BookA, v_author) — the relation v_author must come from OUTSIDE the substrate (LLM-orchestration OR pre-stored rule-atoms via Scheme B's Proposal 2).

**The honest product framing** (replaces the original doc's "substrate as reasoning store"):

> "The substrate is a fast, algebraically-auditable fact store that can execute PRE-SPECIFIED reasoning chains (rule-memory Proposal 2) with microsecond-per-hop latency and unbinding-based audit, WHEN orchestrated by an external agent that supplies the initial query and rule-activation markers. Open-ended reasoning remains LLM-driven; the substrate's contribution is speed, isolation, and audit fidelity for the retrieval steps."

This is **substrate-distinctive but narrower than the original framing suggested.** The competitive moat is real (algebraic audit + ~1000x latency vs LLM CoT for pre-stored chains + edit-isolation) but the substrate doesn't autonomously DISCOVER new reasoning chains.

## The 6 operational gaps the original framing hid (drill β findings)

| # | Gap | Implication |
|---|---|---|
| 1 | **Inter-hop key construction is external** | Substrate emits v_BookA; LLM or pre-stored rule-atom must supply v_author for hop 2; pure substrate-side reasoning impossible |
| 2 | Composition atom blowup (Proposal 1) | Pre-storing composed-relation codewords gives 5-20x capacity blowup even at N=16384; infeasible for realistic R×F products |
| 3 | Control flow is external | Path D = Bayesian posterior over K candidates per hop; WHICH hop to execute, when to stop = external scheduler |
| 4 | Unbinding exact for stored codewords; approximate after retrieval noise | Chains beyond depth ~5 require hop-by-hop cleanup (nearest-neighbor snap to codebook); accumulated variance D*(M-1)/N overwhelms signal otherwise |
| 5 | Grounding gap | Audit verifies codeword consistency, not semantic correctness; v_Alice = "Alice the person" is an enrollment-time guarantee external to substrate math |
| 6 | Capacity saturation | F=10K facts × R=100 rules needs N≥65K to stay sub-capacity in modern Hopfield regime |

## Combined verdict: what substrate CAN and CANNOT do

| Claim from original doc | After 2x deepening |
|---|---|
| Substrate stores reasoning chains | ✓ via Scheme B three-way binding at N≥16384, sub-saturation; pre-stored chains only |
| Path D retrieves reasoning chains | ✓ but envelope must be RE-VALIDATED under structured keys; not inherited from random-key 32N envelope |
| Substrate does compositional reasoning autonomously | ✗ requires LLM cooperation OR pre-stored rule-atoms (Proposal 2); not from first principles |
| 100-1000x latency improvement | ✓ for PRE-STORED chain retrieval (~1ms vs ~1s LLM CoT); ✗ for novel reasoning |
| 10-100x cost reduction via amortization | ✓ for repeated reasoning patterns; still substrate-distinctive only via audit + edit-iso + del-cert overlay |
| Verifiable derivation chains | ✓ algebraic audit via element-wise unbinding is exact under MAP-B; LLM-CoT cannot match this |
| Reasoning chains compose | ✗ pre-stored compositions only; substrate cannot derive A→C from stored A→B + B→C without external chain construction |

## Critical pre-registered thresholds for any reasoning-storage Phase 1 experiment

From drill A (encoding):
- **HARD-FAIL at >~44K shared-rule-atoms at N=4096** (the 32N/3 threshold for three-way binding interference): if more than 44K modus-ponens steps in W, shared rule_code component dominates spectrum

From drill α (structured-key Path D):
- HARD-FAIL: per-hop accuracy drops >15% below random-key baseline at same M/N
- HARD-FAIL: top singular value of W > 3× Marchenko-Pastur edge (spectral collapse from rule concentration)
- HARD-FAIL: posterior entropy elevation >0.5 bits for high-reuse keys
- MIDDLE-BAND: 5-15% accuracy drop, 1.5-3× MP spike, 0.2-0.5 bit entropy elevation
- HARD-PASS: within 5% of random-key baseline

From drill β (worked example):
- HARD-PASS: 5-hop chain at N=4096, W<200 entries → ≥85% retrieval accuracy per hop (combined chain ~77%)
- HARD-FAIL: hop 3+ accuracy <60% (noise accumulation overwhelms three-way binding capacity)

## Mitigations available if structured-key envelope fails (ranked from drill α)

1. **Conclusion re-encoding via binding transform (HIGHEST LEVERAGE)**: `k_{n+1} = ρ(v_n)` where ρ is a deterministic permutation. Severs forced equality between conclusion-of-N and premise-of-N+1. Steinberg-Sompolinsky (Sci Reports 2022) use exactly this. Cost: 1 binding op per hop; no W changes.
2. Per-rule subspace allocation via orthogonal codebooks
3. Sparse encoding (Hersche-style k-of-N activation, k/N ≈ 0.05)
4. Pseudoinverse learning rule (replaces Hebbian outer product; eliminates crosstalk for M<N)
5. Weighted-pattern Hopfield (downweight high-reuse keys)

## Proposed Phase 1 reasoning-storage smoke experiment

Spec sketch for exp_dev refinement:

**Anchor**: `reasoning_storage_scheme_b_smoke_v1_n16384`

**Setup**:
- N=16384 (must be ≥ 16K to avoid composition blowup; drill β capacity math)
- Codebook: BSC bipolar; 5 inference-rule codewords (modus ponens, transitive, abductive, analogical, causal) drawn once; 200 entity codewords; 20 relation codewords
- Corpus: 500 reasoning chains, depth=3-5, structured-key (genuine reasoning structure with shared rule_codes and shared intermediate entities)
- MATCHED random-key corpus for differential measurement

**Scheme B encoding test**:
- Encode each reasoning step as `k_step = r_type ⊙ k_premise1 ⊙ k_premise2`, store as `W += (1/N) v_conclusion k_step^T`
- Verify exact audit decomposition: for each stored step, unbind to recover r_type, k_premise1, k_premise2 independently; HARD-PASS if all 3 components recoverable to nearest-neighbor in respective codebooks with confidence >0.95

**Structured-key Path D differential**:
- Run Path D depth=5 retrieval on structured corpus
- Run Path D depth=5 retrieval on matched random-key corpus
- Measure per-hop accuracy, posterior entropy, W spectrum (top-50 singular values)
- HARD-PASS if structured ≥ 0.95 × random baseline; HARD-FAIL if structured ≤ 0.85 × random; MIDDLE-BAND in between

**Conclusion re-encoding mitigation arm**:
- Repeat structured corpus with ρ(v_n) permutation applied between hops
- Measure same metrics
- HARD-PASS for mitigation: structured-with-mitigation ≥ 0.95 × random baseline

**Shared-rule threshold sweep**:
- Sweep #chains-sharing-modus-ponens-rule_code from {100, 1K, 10K, 44K (the threshold from drill A), 100K} at N=4096 to verify the 44K spectral-collapse threshold empirically (cheaper at N=4096 than N=16384)
- HARD-PASS: spectral concentration ratio σ_1/σ_2 < 3× MP edge at #chains ≤ 44K
- HARD-FAIL: spectral collapse evident at much lower threshold (e.g., 10K)

**Cost**: ~3 weeks engineering + ~4-8h GPU. Local GPU sufficient (Modern Hopfield N=16384 already validated on-substrate).

## Cap_map implications

NEW cap_map row proposed: **"Substrate reasoning-storage via Scheme B three-way binding"**
- Initial P-band: 0.40-0.55 (range reflects mitigation uncertainty)
  - Lower bound: structured-key Path D fails without mitigation (drill α P_def 0.35)
  - Upper bound: Scheme B encoding exact + conclusion re-encoding mitigation tractable (drill A P_def 0.62 + drill α top mitigation literature-grounded)
- Caveats: (a) requires N≥16384 to avoid capacity blowup; (b) requires conclusion re-encoding mitigation as default; (c) substrate doesn't autonomously discover new chains — pre-stored or LLM-orchestrated only

UPDATE to substrate-product-feature row: caveat addition that "reasoning storage" is scoped to PRE-STORED chains with external chain construction, not open-ended autonomous reasoning. Honest framing matters for product positioning.

NO promotion of D1 (compositional binding production scope) to reasoning storage — D1 tests Scheme A (rules-as-relations); Scheme B is a DISTINCT capability question. D1 stays as-is.

## Implications for current in-flight work

**Substrate-LLM Phase 1 build (testbed handoff)**:
- The build's Rescue C ("substrate runs Path D depth=5 autonomously; LLM emits single query") aligns with the worked-example finding that the substrate is a retrieval primitive — the Rescue C framing is HONEST.
- The build's 4 bespoke benchmarks test substrate-distinctive properties consistent with the honest framing: edit-then-query (edit-isolation), deletion-cert audit (audit fidelity), provenance citation (algebraic audit), real-time-learn-then-query (write+retrieve cycle).
- ADD to build's caveat list: "substrate-augmented LLM" claim must be scoped to LLM-orchestrated chain construction; substrate provides retrieval + audit + speed, not autonomous reasoning.

**Reasoning amortization experiment (filed earlier today)**:
- STILL VALID with reframing: amortization caches PRE-STORED chains (Scheme B via Proposal 2 rule-atoms), not "reasoning operations"
- Cost-economics argument still holds for workloads with repeated reasoning patterns
- HARD-PASS bands unchanged

**D1 compositional binding (filed earlier today)**:
- STAYS as Scheme A test; doesn't subsume Scheme B
- Scheme B reasoning-storage smoke is a SEPARATE experiment

## P-bands updated

| Claim | P_deflated |
|---|---|
| Scheme B encoding distinct from Scheme A (algebraic argument) | 0.62 |
| Path D 32N envelope transfers to structured-key reasoning chains WITHOUT mitigation | 0.35 |
| Conclusion re-encoding mitigation restores structured-key envelope to within 5% of random-key | 0.55-0.70 (lit-grounded: Steinberg-Sompolinsky precedent) |
| Substrate Scheme B reasoning storage delivers product-distinctive capability at N=16384, sub-saturation, with conclusion re-encoding | **0.40-0.55** |
| Substrate autonomously discovers new reasoning chains (the original doc's strongest claim) | 0.05-0.10 (very low; the substrate is fundamentally a retrieval primitive per drill β) |
| Substrate retrieval of pre-stored chains at ~1ms vs LLM CoT ~1s (latency claim) | 0.85-0.95 (well-grounded math) |
| Algebraic audit via exact unbinding under MAP-B (audit claim) | 0.85-0.95 (algebraically exact for atomic codewords; degrades with retrieval noise; mitigated by hop-by-hop cleanup) |
| Amortization economics for repeated reasoning patterns | 0.55-0.70 (drill A original) |

## Open synthesis questions (load-bearing; resolvable empirically during Phase 1 smoke)

1. **At what M does structured-key Path D actually break?** Drill α theoretical bound is 5-25% degradation at moderate correlation; empirical measurement at production scope tells us where the substrate operationally sits.
2. **Does conclusion re-encoding actually restore the random-key envelope?** Drill α ranks this top mitigation but acknowledges no direct empirical test in the substrate literature.
3. **What's the actual #-of-shared-rule-atoms threshold for spectral collapse?** Drill A predicts 44K at N=4096; needs empirical confirmation.
4. **Does noise accumulation actually require hop-by-hop cleanup, or does Path D's per-hop Bayesian posterior over K candidates naturally suppress it?** Drill β raises this; drill α partially addresses but empirical answer is the real test.
5. **Mixed fact-and-reasoning-step W behavior**: drill A flags as open synthesis question; drill β's capacity math suggests separate W matrices for facts and rule-atoms may be needed to stay sub-capacity at scale.

## Citations (synthesized from 3 drills)

**Encoding scheme (drill A)**:
- Kvasnička et al., "Deductive rules in HRR," Neurocomputing 2006 — direct precedent for modus ponens encoding
- Schlegel et al., "A comparison of VSAs," AI Review 2022 — MAP-B bipolar unbinding exactness theorem
- Hersche et al., NVSA Nature MI 2023 — closest published Scheme B precedent (87.7% RAVEN accuracy)
- Smolensky, "Tensor product variable binding," AI 1990 — foundational role-filler decomposability

**Structured-key Path D (drill α)**:
- De Marzo & Iannelli, "Spatial correlations on Hopfield + DAM," Physica A 2023 (arXiv:2207.05218) — capacity reduction with pattern correlation
- Amit-Gutfreund-Sompolinsky, "Spin-glass model of neural networks," PRL 1985 — classical α_c = 0.138N bound + correlation degradation
- Steinberg & Sompolinsky, "Associative memory of structured knowledge," Sci Reports 2022 — VSA chains via unbinding; conclusion re-encoding precedent
- Santos et al., "Sparse and structured Hopfield networks," arXiv:2402.13725 — modern Hopfield + structure
- Löwe, "Hopfield with correlated patterns," Ann Appl Prob 1998 — N/(γ log N) bound

**Operational worked example (drill β)**:
- Plate 1995 (HRR foundational)
- Krotov-Hopfield 2016 (Modern Hopfield capacity scaling)
- Webb et al., "Attention as binding," arXiv:2512.14709 (LLM-CoT vs VSA latency comparison)

## Internal cross-refs

- `notes/research_substrate_as_reasoning_store_audit_v1_2026-05-31.md` (the 8-experiment audit that flagged the encoding question as prerequisite)
- `notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (Exp 2 reasoning amortization still valid; reframed in this synthesis)
- `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md` (D1 stays as Scheme A test; doesn't subsume Scheme B)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (Rescue C honest framing aligns with worked-example finding; caveat list update recommended)
- `notes/substrate_capability_map.md` v297 (no row changes proposed in this note; new row recommendation for orchestrator)

## Method note

3 Sonnet drills parallel ~45 min wall each, ~135K tokens total. Main-thread synthesis ~25 min. The 2x deepening was significantly more valuable than the original encoding-scheme drill alone — without drills α + β, the encoding finding would have created false confidence that "Scheme B works algebraically therefore substrate reasoning storage works." Drills α + β surfaced (a) the structured-key envelope problem and (b) the inter-hop key construction gap — both load-bearing operational constraints that the abstract Scheme B argument alone wouldn't have caught.

Per [[feedback-2x-means-depth]]: 2x = depth not verification. Confirmed: the 2x drills did NOT re-run the encoding-scheme question; they OPERATIONALIZED it from different angles. This is the right pattern when a user invokes "2x research."
