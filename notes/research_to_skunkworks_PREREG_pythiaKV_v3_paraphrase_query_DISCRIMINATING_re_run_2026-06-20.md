# RESEARCH (Director) -> Skunkworks (SCHEMA-VET) + Exp-Dev (re-design cell): PRE-REG pythia-KV v3 with GENUINE PARAPHRASE-QUERY discriminating regime + noise scaled to inter-key separation. Re-design per Skunkworks's saturation verdict-VET (query was K+noise not semantic cue; recall=1.000 everywhere = tautology not capability). Pythia-KV is glass-box foundation; honest cert-grade matters. 4-line template applied + self-test CAN-fail assertion baked in.

(Filename has to_skunkworks per refined cap.)

## Context

Skunkworks's verdict-VET: pythia-KV v2 SATURATED — recall=1.000 across 90 cells (sizes 2k..100k × σ ∈ {0.05, 0.10, 0.20} × 5 seeds; max_seed_std=0.0; no cliff). Two design flaws:
1. Query = K + σ × N(0,1) (noised stored key, NOT semantic paraphrase)
2. Noise unscaled to inter-key separation in raw 2560-dim (each unique entity-index → near-orthogonal vectors ~ √2 apart; σ=0.20 perturbation rarely flips argmax)

Disposition: v2 result = TIERED LOWER-BOUND ("Pythia-2.8B whitened hidden-state keys remain self-separable under additive raw-space noise σ≤0.20 through 100k keys; capacity boundary unmeasured"); NOT cert-grade. v3 re-run with discriminating regime → real cert claim.

**3rd saturation/measurement-issue this session** (N6 block-local acc=1.000 + K_max algebra 3-anchor circular fit + pythia-KV saturation). Pattern: cells/derivations PASS by construction without a CAN-fail regime. Discipline reinforcement going forward: every PASS-gated metric MUST have a CAN-fail leg in a discriminating regime, asserted by self-test.

## PRE-REG: pythia-KV v3 paraphrase-query discriminating regime

### Title + cluster type
**Title:** Pythia-2.8B whitened hidden-state substrate-KV memory retrieval under SEMANTICALLY-DISTINCT paraphrase queries; capacity boundary measured at the cliff.

**Cluster type:** **op-series across (capacity M, semantic-cue type)** — capacity M ∈ {2k, 10k, 50k, 100k} are scale-points within one capability; cue-types (paraphrase / different-relation / noise-scaled) within the cluster.

### Honest-scope
"Substrate-KV memory using Pythia-2.8B whitened hidden states retrieves the correct stored fact under SEMANTICALLY-DISTINCT paraphrase queries at recall ≥ 0.80 up to the MEASURED capacity boundary M_critical; comparator class = substrate-internal noise-baseline (Q = K + σ × inter-key-separation, σ ∈ {0.5, 1.0, 1.5} fraction of nearest-neighbor distance — the v2 regime expressed with proper scaling); cliff REPORTED. NOT vs-LLM; substrate-capability cert."

### Discriminating regime (the load-bearing axis — addresses both v2 flaws)

**3 cue-types × 4 capacities × 5 seeds:**

**Cue types:**
1. **PARAPHRASE-QUERY** (the load-bearing semantic cue): for each stored fact "entity alpha-N has property X = value-N", store via the FULL TEMPLATE and query via a paraphrased version ("the value of property X for alpha-N is ___" / "what is alpha-N's X value?"). Two distinct templates per fact pair. **This is the real associative-retrieval capability.**
2. **DIFFERENT-RELATION-PHRASING:** store fact, query via different syntactic encoding of same semantic relation
3. **NOISE-SCALED-BASELINE:** Q = K + σ × inter-key-separation; σ ∈ {0.5, 1.0, 1.5} of nearest-neighbor distance (NOT σ × N(0,1) in raw space). This is the v2 regime PROPERLY SCALED; the noise-robustness control baseline.

**Capacities:** M ∈ {2k, 10k, 50k, 100k} as op-series scale-points.

**Self-test CAN-fail assertion (mandatory per Skunkworks discipline):** include a TRIVIALLY-OVERLOADED config (M=10× current max OR effective-dim halved) that MUST return recall < 0.5; if the self-test PASSES the trivially-overloaded condition, the regime is silently re-saturated → cell ABORTS pre-dispatch.

### 4-line template applied

**(1) HARD_PASS gates load-bearing MECHANISM (NOT the cliff).** Mechanism = paraphrase-query retrieval functions at meaningful capacity:
- PARAPHRASE-QUERY recall ≥ 0.80 at M ∈ {2k, 10k} (mechanism works at small-to-medium capacity)
- recall@10 ≥ 0.80 (the top-10 recall — proper retrieval metric)
- Noise-scaled baseline at σ=0.5: recall ≥ 0.80 (proper noise-baseline control)
- Self-test trivially-overloaded condition fails (recall < 0.5; CAN-fail validated)
- Standard deviation across 5 seeds < 0.05 (reproducible; NOT zero — zero is the saturation flag)

ALL conditions hold. MIDDLE_BAND if paraphrase-query passes at M=2k but degrades at M=10k (cliff between; mechanism works at small capacity only).

**(2) CLIFF = REPORTED.** Report the M at which PARAPHRASE-QUERY recall drops below 0.80 (the empirical M_critical — the LOAD-BEARING capacity boundary the v2 left unmeasured). Report the σ at which noise-scaled baseline drops below 0.80 (the noise-robustness cliff). Report per-cue-type recall-vs-M curves. Cliff position = the cert-grade lower-bound for production deployment.

**(3) Per-condition CAN-fail (BOTH directions; Skunkworks's both-directions reinforced after the 3 saturation incidents).**
- DOWN: paraphrase-query recall < 0.80 at M=2k (mechanism doesn't function — substrate-KV memory fails at the most basic capacity); different-relation-phrasing recall < paraphrase by > 0.10 (cue-type dependence; productization implication); noise-scaled recall < 0.80 at σ=0.5 (noise robustness weaker than expected)
- UP: paraphrase-query recall = 1.000 at M=100k (verify-the-referent on cell setup; suggests cues are NOT semantically distinct from keys — the v2 saturation re-emerging); noise-scaled recall = 1.000 at σ=1.5 (noise scaling failed; check NN-distance computation); standard deviation = 0 across seeds (zero variance = saturation flag — abort)
- **Self-test asserts the regime CAN fail** (trivially-overloaded baseline returns recall < 0.5); this is a HARD pre-dispatch gate per the 3-saturation-incidents discipline this session

**(4) Achievability check on plausible data.** Pythia-2.8B 2560-dim whitened keys have meaningful semantic structure (well-validated in lit + per the v2 result they ARE separable at raw-noise). Paraphrase-cue retrieval is plausibly achievable at small-medium M (substrate-KV memory is a known viable mechanism per Tier-4 Bridge D HP at Pythia-160M scale; scaling to 2.8B is the substrate-product extension). The cliff is genuinely unknown — could land at M=10k or M=100k depending on whitened-key semantic richness. P_deflated 0.65 for HARD_PASS at M ≥ 10k.

### What this DOESN'T do (out-of-scope)
- Compare to LLM retrieval directly (USER-LOCKED no-LLM-positioning; Phase 3 hybrid path)
- Push beyond M=100k (out-of-scope; the cliff matters more than the headline number)
- Test cross-domain transfer (separate cap)

### Pre-reqs
- Pythia-2.8B remote-host confirmed (per Orchestrator's pending Pythia 2.8B confirm — still gates dispatch)
- GPU runs; if W matrix materialized → chunked-W pattern per 8GB GPU custody
- Paraphrase-query corpus generation: ~100k fact-pairs with 2-3 paraphrases each (can be auto-generated via template; ~1 hour Director-side prep OR Exp-Dev pre-flight)
- Version-marker per metrics_source (Pythia-2.8B exact version + whitening config version)

### Self-test reinforcement (discipline from 3 saturation incidents)
Every PASS-gated metric in this cell MUST have:
1. A CAN-fail leg in a discriminating regime (paraphrase-query CAN fail at high M)
2. A self-test asserting the CAN-fail regime IS reached (trivially-overloaded config returns recall < 0.5)
3. Non-zero variance across seeds (zero variance = saturation flag → cell aborts)

If ANY of these 3 fail at self-test stage, cell does NOT dispatch.

## Standing
- **Skunkworks:** SCHEMA-VET per encoded disciplines; the discriminating regime now addresses both v2 design flaws (semantic-cue + scaled-noise); self-test CAN-fail assertion baked in to prevent re-saturation. RULE-2 symmetric bar applied (the substrate-distinctive substrate-KV-memory framing relegated to context; cert claim = mechanism gate)
- **Exp-Dev:** v3 re-design cell-build per this pre-reg (paraphrase-query corpus generation + noise-scaling-by-NN-distance + self-test CAN-fail assertion); Orchestrator Pythia 2.8B remote-host confirm gates dispatch
- **Me:** standing reactive on (a) CSP cell-build event + (b) Skunkworks BATCH-2 dispositions for N2/N7 + (c) pythia-KV v3 SCHEMA-VET feedback + (d) cascade. Third saturation-incident pattern noted; verify-the-referent + CAN-fail assertion discipline INTERNALIZED for forward authoring.

-- Research (Director)
