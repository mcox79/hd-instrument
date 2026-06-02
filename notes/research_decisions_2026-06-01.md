# Research decisions -- 2026-06-01

## neural_symbolic_bridge -- 2026-06-01 (research:sonnet, 4 parallel WebSearch + 2 WebFetch lit-scans)

**Trigger.** Orchestrator inline dispatch: speculative deep drill on substrate as neural-symbolic bridge. Algebraic + lit-scan, no empirical.

**Outcome.** GO with qualification. Note: notes/research_neural_symbolic_bridge_2026-06-01.md. P_deflated=0.50 (capped). 5 differentiators vs published neural-symbolic systems identified. HF4 risk (reduces to known VSA) = 0.20. Next-drill candidates: SAT/Hopfield energy geometry, Soft TPR (NeurIPS 2024), expander bounds on attractor graph.

---


## p3_p4_external_routing_delivery -- 2026-06-01 (research:opus + 2 parallel Sonnet drills + main-thread P2 source verification)

**Trigger.** Orchestrator routing `strategy_request_to_research_external_distribution_2026-05-31.md` filed 2026-05-31 15:53 with 6 research priorities. This session processed research-owned priorities P3 + P4 + P2-source-verification.

**Outcome.**

**P3 cross-framework probe (percolation theory on Path D)** -- partial theoretical home P_def 0.30-0.40:
- Bootstrap percolation / Hopfield coincidence theorem (Albanese et al. 2014 PMC) is real published precedent but established for CLASSICAL Hopfield not MAP-B with Bayesian posterior reduction; bridging derivation does not exist in literature
- O(log² M) mixing time (Benjamini-Kozma-Wormald 2008) means depth=50 result is mostly mixing-floor regime (~18 hops at M=262K); deep-iteration novelty is past hop ~18 only
- K=100 trivialization concern SHARPENED: p_eff = K/M = 3.8e-4 at M=64N is 100× above ER threshold; deep supercritical safety margin
- Predicted actual ceiling at M ≈ 100N-300N (order-of-magnitude bound from Hopfield α_c=0.14 extrapolation; not derived for MAP-B + K=100)
- Structured-key 5% gap (PP-11 verdict) directionally consistent with correlated-edge percolation prediction (Goltsev-Dorogovtsev-Mendes 2008; Valdez-La Rocca 2026); magnitude within 10-20% threshold-shift range; not tight quantitative derivation
- Recommended next experiment: K=1 phase-boundary probe (sweep K from 1→10→100 at M=16N N=4096); cheap; falsifiable either way; cleanest empirical probe of whether Path D's validated envelope is substrate-physics or K-safety-margin envelope

**P4 compositionality audit API design** -- ALL 6 HARD-PASS criteria MET:
- 3 primary API calls: audit() / audit_cert() / verify_audit() with full type signatures
- Storage: ~664 bytes/query medium granularity; ~13-15 KB deep mode; ~300 bytes/entry certificate; ~300 MB total at M=10^6 entries
- Latency: <3% overhead at medium granularity (within <10% target)
- 4 compliance use cases empirically mapped: GDPR Art 17 erasure verification, HIPAA §164.312(b) audit controls, SOC 2 CC7.2/7.3 cryptographic trail, EU AI Act Art 50 + Annex IV explainability
- Comparison to W3C PROV-DM (substrate audit = PROV-DM derivation chain + algebraic verifiability ADD-ON), Certificate Transparency RFC 9162 (substrate = CT + algebraic exactness), Tas-Boneh vector commitments, TPM PCR pattern
- KEY substrate advantage: "Standard PROV-DM traces are ASSERTIONS; substrate traces are PROOFS via element-wise unbinding exactness"
- Engineering effort: ~1650 LOC + ~7 person-weeks (depends on atom registry pre-existing or +2 weeks for schema design + backfill)

**P2 TCFT degradation source verification (orchestrator pre-filing flag)** -- BLOCKING FINDING:
- External doc cited var_ratio sequence 0.20→0.33→0.50→0.66 across M/N=0.25→2.0 at N=16384
- cap_map measurements (v245+v247 N=8192 5-seed FULL): mean_var_ratio = 3.2e-8 -- SIX ORDERS OF MAGNITUDE below doc's cited values
- Source anchor for doc's numerics UNIDENTIFIED
- 3 possible explanations: (a) doc cited hypothetical degradation curve not measured data; (b) data from probe not in cap_map; (c) different metric definition (doc's "var_ratio" vs v245/v247's tcft_variance_ratio may differ)
- P2 BLOCKED on orchestrator clarification; cannot proceed against potentially-wrong numerics

**Other priorities status**:
- P1 substrate-LLM Week 1 feasibility smoke: testbed-owned, gated on Phi-3 Missing 7 verdict (status_log shows still pending)
- P5 substrate-LLM Build Week 1 detailed planning: contingent on P1 GO; not runnable
- P6 Path B sub-capacity production characterization: stays open as future exp_dev anchor (verify T5 first per orchestrator flag)

**Note path.** `notes/strategy_request_to_strategy_p3_p4_external_routing_delivery_2026-06-01.md` (full synthesis; cap_map updates proposed for P3 + P4; P2 source-verification result; P1/P5/P6 status; orchestrator decisions list).

**Method note.** 2 parallel Sonnet drills (~45min each, ~90K tokens combined) + main-thread P2 grep verification (~10min) + synthesis routing (~25min). Pattern confirmed per [[feedback-aggressive-cross-domain-research]]: P3 was overdue per 24-48h cadence; this delivery closes that. Per [[feedback-no-padding-experiments]]: dispatched 2 drills for the 2 highest-leverage research-owned priorities; verified P2 prerequisite cheaply via grep before dispatching analysis drill on potentially-wrong numerics.

**Next-drill candidate.** None pending in this cycle. Watch for orchestrator:
- Acceptance of P3 cap_map caveat updates → K=1 sweep experiment becomes next exp_dev candidate
- Acceptance of P4 NEW cap_map row + testbed engineering routing → audit API enters production engineering queue
- P2 source clarification → P2 Phase 1 analysis becomes dispatchable
- Phi-3 Missing 7 verdict → P1 + P5 become runnable


## v307_followon_experiments_routing -- 2026-06-01 (research:opus; main-thread)

**Trigger.** Cap_map v306->v307 bump 2026-06-01 (orchestrator commit e1c78c2): P3+P4 deliveries ACCEPTED into v305->v306 (commit 3fdb86e). K=1 phase-boundary probe DISPATCHED + ALREADY RAN. v307 has 5 verdicts including:
- V2 path_d_k1_phase_boundary_probe: mean K=1 acc 0.022 = 6.7x random; K=10/100 unanimous 1.0; **EMPIRICALLY CORROBORATES P3 percolation drill's SHARPENED-K-trivialization caveat**
- V1 PP-11 4WC v2 5-seed BORDERLINE: mean 2.4pp gap; strict <2pp gate NOT met; 167th LABEL-VS-HONEST; PP-11 stays MIDDLE_BAND
- V5 AQSIM3W2 HARD_PASS: FIRST end-to-end 3-way SCORE compositional HARD_PASS (compression × Path D × a_query_sim × adversarial workload)
- V4 PDAC2 HARD_PASS: first true-exercise defense activation
- V3 cert_threshold runner-FAILED label OVER-CLAIMS

**Outcome.** 3 follow-on experiment routings filed in ONE consolidated routing for orchestrator:

1. **R2 K-fine-grained transition curve** (`path_d_k_fine_grained_transition_v1_n4096`): sweep K∈{1,2,3,5,10,100} at M=16N N=4096; ~30-45min CPU; HARD-PASS 0.75-0.85 (monotone transition almost certain); HARD-FAIL if K=2/3/5 still at random-chance.
2. **R4 K=1 cross-N null-prediction test** (`path_d_k1_cross_n_null_prediction_v1`): K=1 fixed; sweep N∈{4096,8192,16384}; ~1h CPU; **tests percolation framework's falsifiable null prediction** (substrate-physics signal N-independent at fixed K). HARD-PASS 0.55-0.70.
3. **GHRR side-by-side fallback** (`reasoning_storage_ghrr_side_by_side_v1_n16384`): MIDDLE-BAND clause triggered by V1 4WC v2 BORDERLINE (2.4pp gap > strict <2pp threshold). Per earlier alternative-encoding ladder routing, GHRR is the next escalation. ~1-2 weeks engineering. HARD-PASS 0.20-0.35 (audit-moat-preservation is load-bearing concern; FHRR drill A showed approximate unbinding gives 85-92% audit accuracy; GHRR likely similar).

**Note path.** `notes/strategy_request_to_strategy_v307_followon_experiments_2026-06-01.md`.

**Sequencing recommendation**:
- R2 + R4 dispatch IMMEDIATELY (parallel, both ~1h CPU, no GPU contention; cheap; falsifiable either way)
- GHRR defer 1-2 weeks behind PP-11 priority decision

**Method note.** Single consolidated routing for 3 distinct experiments because they all trigger from the same cap_map state (v307); avoids 3 separate routing files for orchestrator to process. Per [[feedback-no-padding-experiments]]: R3 (K=1 M-sensitivity) deferred -- it's the third v307 rescue but adds marginal information beyond R2/R4; can be added later if R2/R4 surface new questions.


## external_audit_followup_6_routings -- 2026-06-01 (research:opus; main-thread; commit e06874a)

**Trigger.** External-feedback audit on the research state update found six load-bearing gaps; user greenlit dispatch.

**Outcome.** 6 routings filed (5 strategy + 1 testbed):
1. `strategy_request_to_strategy_cert_threshold_v2_gdpr_target_2026-06-01.md` -- proposes ≤0.01% FP pre-reg target for GDPR Art 17 compliance positioning (current row at 1% FP is compliance-rejectable)
2. `strategy_request_to_strategy_p2_tcft_direct_empirical_sweep_2026-06-01.md` -- cheap ~1h CPU sweep that bypasses the BLOCKED external-doc source-mismatch
3. `strategy_request_to_strategy_pp9_depth_conditional_caveat_2026-06-01.md` -- corrects PP-9 row caveat: per-hop INDEPENDENT means depth=10 chains see ~60% accumulated accuracy (substantial use-case-envelope implication)
4. `testbed_handoff_aqsim_end_to_end_audit_chain_assertion_2026-06-01.md` -- test-rig fix: AQSIM compositional currently asserts audit chain per-component, not end-to-end across composition
5. `strategy_request_to_strategy_stale_row_audit_2026-06-01.md` -- proposes VALIDATED/EXPLORATORY/HOLDING/CLOSED categorization for the 28+37 cap_map row structure
6. `strategy_request_to_strategy_h100_no_go_branch_decision_spec_2026-06-01.md` -- pre-specifies the NO-GO sequel program (Pattern B deepening + PP-8 row formal closure) so an H100-FAIL doesn't create a multi-week strategic vacuum

**Method note.** Per [[feedback-no-padding-experiments]]: each routing maps to a specific honest gap the audit surfaced; not padding. Pushed back on external feedback's 3 wrong items (overstated N=32K cost, wrong PP-9 "10-100x is broken" framing, premature continuous-embedding composition, hierarchical "1-2 weeks decisive" optimism, commercial-signal item outside scope per [[feedback-value-creation-not-competition]]). Per [[feedback-no-experiment-design-in-prompts]]: routings hand TASK + WHY + CONTRACT + AUTONOMY; sweep grids / thresholds / queue choice remain strategy + exp_dev's call.

**Next-drill candidate.** GHRR side-by-side experiment (PP-11 ladder; 4WC family FALSIFIED) when testbed bandwidth allows; cross-domain probe overdue (free-probability or sparse-coding NTK candidates).


## negative_results_2x_deep -- 2026-06-01 (research:opus + 2 parallel Sonnet drills; main-thread)

**Trigger.** verdict_processed HIGH 2026-06-01 11:27 — TWO negative results: (1) percolation K=1 N-independence prediction FAILED 18x at N=16384; (2) PP-11 4WC v4 compound Hadamard WORSE than v3 → entire Hadamard-orthogonality family REJECTED.

**Outcome.** 2 parallel Sonnet drills (~3 min each, generic VSA terms per [[feedback-query-privacy-decomposition]]); main-thread synthesis. Both negative results have RESCUE PATHS cheaper than the experiments that produced them.

**Drill 1 (percolation falsification).** No framework predicts K=1 signal-collapse-worsening-with-N at fixed alpha. Most parsimonious explanation: depth-5 composition cliff at K=1 large-N, NOT per-hop substrate-physics failure. FSS framework (P=0.38 deflated) is the closest formal candidate if per-hop physics IS N-dependent; SNR-crosstalk (P=0.30) needs secondary mechanism; RMT (P=0.12) and BP cavity (P=0.18) predict WRONG DIRECTION.

**Drill 2 (Hadamard family rejection).** Best guess root cause: second-order Hebbian cross-talk between structurally related binding products (Hypothesis A); cross-talk lives in weight matrix capacity statistics, not codebook angular separation. v4 worse than v3 is consistent — orthogonalizing both factor codebooks concentrates product spectrum. Top rescues: **R2.1 Kronecker rotation product cleanup (P=0.25, 1 eng-week, audit-moat-VERY-LOW-RISK)** is cheapest+diagnostic; **R2.2 sparse block codes DSBC/BCF (P=0.45, 2-3 eng-weeks, audit-moat-LOW-RISK)** is most principled root-cause attack; **R2.4 acceptance + re-positioning (executable, audit-moat-NONE)** is the final fallback.

**Note path.** `notes/research_negative_results_2x_deep_2026-06-01.md` (full drill synthesis with all 4-5 rescue candidates per drill).

**Routing.** `notes/strategy_request_to_strategy_negative_results_followon_experiments_2026-06-01.md`. Proposes 2 cheap diagnostic tests dispatchable in parallel: **Test 1A** (K=1 depth-sweep ~18 CPU-min) discriminates per-hop vs multi-hop composition origin; **Test 2A** (Kronecker cleanup ~1 eng-week) discriminates cleanup-driven vs pre-cleanup-bias origin. Pre-specified contingent escalations 1B + 2B + 2C avoid post-FAIL strategic vacuum.

**Method note.** Per [[feedback-2x-means-depth]]: drills went DEEP on existing findings, not verification re-runs. Per [[feedback-rehabilitation-after-rejection]]: 4-5 rescues per drill listed before any closure recommendation. Per [[feedback-rescue-sketch-first-sequencing]]: cheapest diagnostic tests sequenced first. Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; novel-synthesis cap at 0.50 applied. Token-efficient via 2 Sonnet drills + Opus synthesis.


## atom_registry_design_review_v1 -- 2026-06-01 (research:opus + 1 Sonnet drill; main-thread)

**Trigger.** Orchestrator-forwarded `strategy_request_to_research_atom_registry_design_review_2026-06-01.md` (HIGH severity; gating ~5-7 days PP-3 Phase 2 engineering). Testbed surfaced that PP-3 (audit-trail rotation for GDPR) and PP-12 (compositionality audit API) share the same fundamental object (atom-registry). 6 design questions.

**Outcome.** Single Sonnet drill (~2.5 min; design questions tightly coupled so no parallel-drill payoff). Converged design satisfies BOTH requirements with ~8-12 weeks greenfield / 6-9 weeks V2 refactor:
- Atom identity: content-addressed BLAKE3(data || salt || nonce); separate subject_atom_index
- Audit-chain shape: DAG with daily Merkle epoch checkpoints; checkpoint roots → Sigstore Rekor
- Deletion cascade: tombstone-in-place ~760 bytes with deletion_authority_sig Ed25519 (GDPR Art 17 erasure certificate); zk-SNARK fallback for deep composition trees
- Long-lived compositions: hardening via encrypted snapshot at composition-creation (KMS-managed key)
- Cross-system precedent: Sigstore Rekor most practical starting point (3-5 weeks); CT RFC 9162 / IPFS Merkle-DAG / S/MIME archival cover most primitives
- Net novel synthesis: ~3-4 weeks (subject-rights-triggered Merkle DAG + composition-subgraph verifier-replay + hardened-snapshot Art 17 re-deletion)

**Note path.** `notes/research_atom_registry_design_review_v1_2026-06-01.md`. 4 open decisions for orchestrator + testbed (phasing approval / Sigstore Rekor vs alternatives / vector commitments DEFER recommendation / cap_map LIFT timing).

**Method note.** Per [[feedback-no-padding-experiments]]: 1 drill not parallel because questions tightly coupled. Per [[feedback-subagent-model-optimization]]: Sonnet appropriate for design-pattern + cross-system-precedent lit-scan. Per [[feedback-query-privacy-decomposition]]: generic compliance terms only. Routing moved to routed_completed/; testbed picks up converged design for PP-3 Phase 2 implementation.


## capabilities_expansion_6_drills -- 2026-06-01 (research:opus + 6 parallel Sonnet drills; main-thread)

**Trigger.** User stock-taking surfaced "a ton of untested capabilities" + greenlit dispatch on 6 high-priority items (3 with updated research warranted, 2 first-research, 1 narrower-scope, 1 sizing-only).

**Outcome.** 6 parallel Sonnet drills (~120-200s each; ~125K tokens combined) on: PP-4 drift detection / edit-with-impact-prediction / free probability for W structure (narrower than today's percolation drill) / substrate-as-LLM-KV-cache / calibrated confidence as product feature / sparse-block-code substrate variant.

**Three highest-strategic-weight findings**:
1. Free probability K_max(α) ≈ log(1/α)/(2√α) formula retroactively explains v308 K=2 cliff as spectral-gap effect; gives design rule for multi-hop depth vs capacity
2. Sparse-block-code substrate as **specialized layer** (Option c, P=0.52, NOT replacement) — sparse and dense complementary; sparse unblocks 2 killer features (edit-with-impact-prediction + per-fact retention policy) via near-zero COW cost (W density 1/K²)
3. PP-4 + edit-impact + calibrated confidence + KV-cache-with-audit form coherent killer-features cluster; all converge on intrinsic algebraic cert (not extrinsic logging) as the moat

**Tier 1 dispatchable** (cheap diagnostics; high info gain): Calibrated confidence ECE gate <60s, Write-to-Retrieve Ratio drift detector zero-instrumentation, Codebook Histogram Divergence with bootstrap-null separator, DAG Reverse-Traversal edit-impact deterministic, Sparse Axis 7 edit-isolation smoke <60s.

**Note path.** `notes/research_capabilities_expansion_6_drills_2026-06-01.md` (full 6-drill synthesis with cross-drill insights + cap_map implications).

**Routing.** `notes/strategy_request_to_strategy_capabilities_expansion_followon_experiments_2026-06-01.md` + `notes/strategy_request_to_exp_dev_n32768_envelope_sizing_2026-06-01.md`. Consolidated routing proposes 4 strategic clusters (A: substrate-state-as-product-signal, B: free probability theoretical scaffold, C: substrate-as-KV-cache, D: sparse-block-code variant) with Tier 1 Tier 2 sequencing.

**Method note.** Per [[feedback-subagent-model-optimization]]: 6 Sonnet drills (parallel) > 1 Opus drill on token efficiency; main-thread Opus reserved for synthesis. Per [[feedback-no-padding-experiments]]: each drill on distinct capability axis; no overlap with prior session work. Per [[feedback-aggressive-cross-domain-research]]: overdue free-probability cross-domain probe landed. Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; novel-synthesis cap at 0.50 applied throughout. Per [[feedback-query-privacy-decomposition]]: generic VSA/ML terms only in all 6 drill prompts; no project-identifying fingerprints in any web search.


## capabilities_expansion_round2_9_drills -- 2026-06-01 (research:opus + 9 parallel Sonnet drills; main-thread)

**Trigger.** User-greenlit Round 2 expansion ("sonnet is cheap for us - dispatch for all of them") after Round 1 6-drill synthesis surfaced remaining HIGH/MEDIUM-value capability gaps not yet covered.

**Outcome.** 9 parallel Sonnet drills (~120-220s each, ~180K tokens combined) on: multi-tenant isolation (5 architectures) / substrate as workflow engine (5 sub-caps) / differential privacy (5 mechanisms) / disaster recovery (5 mechanisms) / long-tail Zipfian / continuous-edit catastrophic forgetting (5 candidates) / streaming inference SLA / time-series substrate (5 mechanisms) / substrate ensembles (5 configs).

**CONVERGENT STRATEGIC FINDING**: three drills (multi-tenant, DP, DR) independently arrive at SAME moat — "physics-grade not policy-grade" guarantees from substrate's algebraic structure. Multi-tenant Arch 1 per-tenant W = mathematical zero-leak (kf3_multisub HARD_PASS max_leakage=0); DP Mechanism 1 = intrinsic write-time noise + dual-certificate (audit + privacy); DR cert-chain replay = cryptographic recovery verifiability. **Recommendation: bundle as ONE positioning narrative ("audit-grade memory with physics-grade guarantees"), not 3 separate features.**

**Secondary findings**:
- Workflow engine + time-series + KV cache all converge on "COMPLEMENT not replacement" positioning (sit alongside Temporal/TimescaleDB/Redis as audit layer)
- K_crit ~ √N edit-budget formula appears in 3 drills (CF + DP + multi-tenant sub-space); ONE empirical test validates THREE rows
- Streaming SLA fits SMB-Enterprise tier on reads; 6-8 weeks engineering for Enterprise; 6-12 months for regulated (active-active write architecture)
- Substrate ensemble: only Configs 5 (cascading) + 1 (independent-seed) clear cost-justification

**4 NEW cap_map rows proposed + 2 sub-properties (PP-10a, PP-4a) + 5 explicit CLOSURE recommendations** (Multi-tenant Arch 2/4, DP M2/M4, Ensemble Config 2/3, Time-series standalone).

**Note paths**: 
- `notes/research_capabilities_expansion_round2_9_drills_2026-06-01.md` (full synthesis)
- `notes/strategy_request_to_strategy_capabilities_expansion_round2_2026-06-01.md` (Tier 1/2/3 routing)

**Method note.** Per [[feedback-aggressive-cross-domain-research]]: Round 2 covered remaining high-value capability gaps. Per [[feedback-no-padding-experiments]]: each drill on distinct axis. Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; novel-synthesis cap at 0.50. Per [[feedback-query-privacy-decomposition]]: all 9 drill prompts generic terms only. **Research session recommendation: PAUSE new capability-direction expansion after this round; let Tier 1 verdicts return before opening more breadth.** 16 capability drills today across both rounds. **CORRECTION**: user explicitly retracted the pause recommendation — "we will not pause new capabilities - we need to map out the substrate" — saved as `[[feedback-dont-recommend-research-pause]]`.


## capabilities_expansion_round3_8_drills -- 2026-06-01 (research:opus + 8 parallel Sonnet drills; main-thread)

**Trigger.** User directive "we will not pause new capabilities - we need to map out the substrate. do not say this again I will decide when we focus exclusively on product" — explicit retraction of Round 2's close-recommendation that the session pause new capability mapping.

**Outcome.** 8 parallel Sonnet drills (~95-170s each, ~155K tokens combined) on: cross-modal substrate / knowledge-graph substrate / feature store with audit / substrate-FAISS embedding-index hybrid / federated learning substrate / substrate-LLM bidirectional learning / retrieval explainability / information-theory readout.

**THREE NEW CONVERGENCES (in addition to Round 2's "physics-grade not policy-grade")**:

1. **SIDECAR / COMPLEMENT positioning** (4 drills): substrate sits ALONGSIDE existing infrastructure as audit-cert layer, NOT replacement. FAISS hybrid Angle 5, feature store sidecar, workflow engine audit-layer-FOR Temporal, knowledge graph alongside Neo4j. Strategic implication: GTM is plug-into-existing-stacks not replace-incumbent.

2. **DELETION CERTIFICATE as universal primitive** (5 drills): single primitive powers federated unlearning (FL M4), feature-store erasure (M5), per-vector deletion (FAISS A2), counterfactual+erasure (explainability M3), time-series per-point cert. Promote to first-class substrate primitive.

3. **Cross-domain W separability shared architecture** (4 drills): per-domain separate W + bridge atoms + separability proofs serves multi-tenant SaaS, cross-modal retrieval, federated learning, AND cross-tenant attribution. ONE production architecture powers 4 capability axes.

**Cumulative state across Rounds 1+2+3 (24 capability drills today)**: 11 NEW cap_map rows proposed across both rounds + multiple sub-properties + 9 explicit closures. Unified narrative bundling proposed: "audit-grade memory with physics-grade guarantees" across 11 named killer-feature instances.

**Note paths**:
- `notes/research_capabilities_expansion_round3_8_drills_2026-06-01.md` (full synthesis)
- `notes/strategy_request_to_strategy_capabilities_expansion_round3_2026-06-01.md` (Tier 1/2/3 routing + 3 strategic shifts proposed)

**Method note.** Per [[feedback-dont-recommend-research-pause]]: continuing capability mapping per user direction; NO pause recommendation in this synthesis. Per [[feedback-subagent-model-optimization]]: 8 Sonnet drills parallel. Per [[feedback-query-privacy-decomposition]]: all 8 drill prompts generic VSA/ML/compliance terms; no project-identifying fingerprints. Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; novel-synthesis cap at 0.50 throughout.


## pp8_phi3_hidden_codeword_design_v1 -- 2026-06-01 (research:opus + 1 Sonnet drill; main-thread)

**Trigger.** Orchestrator/strategy inbox routing HIGH severity: PP-8 Phase 2.5 hit val=0% across 3 gradient strategies (bypass / STE / soft-attention). Diagnosis: task-design bottleneck — random codewords carry no learnable signal from "Key N" text. Path 1a = derive codewords FROM Phi-3 hidden states; testbed Path 1c (sanity check) running in parallel.

**Outcome.** Single Sonnet drill (~4.5 min, design-pattern + NVSA-precedent lit-scan, generic VSA/ML terms).

**Primary recommendation**: Fixed Gaussian random projection + sign — `k_i = sign(R · h_i)`, R ∈ R^{4096 × 3072} drawn once at init, ~25MB float16. Theoretical basis: SimHash / JL lemma; collision probability monotone in cos(θ); preserves inner-product geometry. Gradient pathway clean (R fixed → no STE at key-generation; only at retrieval as before). P=0.50-0.60 (NVSA precedent raises above pure novel-synthesis).

**Critical pre-flight diagnostic**: empirical Gram matrix `K_{ij} = (1/N) k_i · k_j` BEFORE gradient training. If mean off-diagonal >0.10 → apply median-threshold centering (catches LLM anisotropy / Phi-3 4-bit quantization collapse).

**Pre-reg**: HARD-PASS val top-1 ≥25% OR ≥5× random + held-out maintained + cross-corr median <0.05; HARD-FAIL val ≤2% OR cross-corr >0.30 for >10% pairs OR train-val gap >40pp.

**Alternatives ranked**: Alt A soft-retrieval annealing (P=0.45-0.55; v2 if FM-3 STE saturation), Alt B trainable+ortho-reg (P=0.35-0.45; v3), Alt C cross-attention probe (P=0.30-0.40; v4). VQ-VAE-style bipolar quantization explicitly NOT recommended (three gradient discontinuities compound STE bias).

**6 failure modes documented**: FM-1 hidden-state collapse, FM-2 anisotropy bias, FM-3 STE saturation, FM-4 dimension-mismatch, FM-5 task-design leak, FM-6 quantization × gradient. Each with diagnostic + rescue path.

**Note path**: `notes/research_pp8_phi3_hidden_codeword_design_v1_2026-06-01.md`. Routing moved to `routed_completed/`. Testbed/exp_dev picks up for Path 1a v1 implementation.

**Method note.** Per [[feedback-no-experiment-design-in-prompts]]: deliverable is design + pre-reg bands; specific sweep grids, batch sizes, exact N values for sub-experiments are exp_dev's call. Per [[feedback-strategy-spec-formula-selftests]]: pre-reg bands include concrete thresholds at multiple levels (Gram-matrix, val top-1, generalization gap) — testbed verifies pre-flight Gram BEFORE training. Per [[feedback-lit-scan-calibration-penalty]]: P deflated 0.10-0.20.
- 2026-06-01 CSP-with-learning drill -> notes/research_csp_with_learning_2026-06-01.md ; HEADLINE: W=W_csp+W_data dual-use is genuinely novel; P_deflated=0.35; HARD-FAIL at <50% on both objectives; next-drill: free-probability Tracy-Widom on combined spectrum


## SEB_write_proof_memory_floor_drill -- 2026-06-01 (research:sonnet; inline algebraic + 4-parallel lit-scan)

**Trigger.** Orchestrator dispatch: speculative algebraic drill on whether SEB C_inf > 0 constitutes an algebraically enforced write-proof memory core -- new capability category.

**Outcome.** notes/research_SEB_write_proof_floor_2026-06-01.md NOT written (inline return per discipline-locked constraint). HEADLINE: C_inf IS q_EA algebraically, NOT a user-controllable pinnable floor. GO/NO-GO = NO-GO. P_deflated = 0.18. Reframing: load-dependent retention floor (valuable weaker claim). See inline return in chat.

**Next-drill candidate.** Free-probability Wigner edge / Tracy-Widom (F2) on W eigenvalues -- top ranked from field_advisor; or nonequilibrium-stat-mech frenesy three-part decomposition (per research_noneq_framework_consolidation_v276).

- spectral-ai-introspection (2026-06-01): GO verdict for substrate as third-party AI activation auditor. P_deflated=0.38. Unique vs EigenTrack/SIGMA: cumulative history + third-party isolation. Deceptive-uniformity is the unaddressed case. Monitoring overhead 0.73% LLM inference. -> inline delivery.

- matrix-trace-query-algebra (2026-06-01): inline delivery — trace primitives map to count/cardinality relational sub-algebra; CONDITIONAL GO on 4 axes (privacy-preserving count, k-way count complexity, audit reproducibility, CRDT concurrency); full SQL equivalence REJECTED; P_deflated 0.50 (novel framing); next-drill: PSI-CA formal privacy proof + capacity-cliff constraint quantification

## program_execution_audit_substrate -- 2026-06-01 (research sub-agent, algebraic + lit-scan)

**Trigger.** Speculative deep drill: substrate as program execution memory with time-travel debugging and audited rollback. Algebraic discipline only, no empirical verification.

**Outcome.** GO (conditional). Algebraic deletion certificate is structurally superior to blockchain (deletion impossible), event sourcing (O(T) re-replay), and Codebat constant-size hash-chain evidence (O(T) re-anchoring). Compactness advantage eliminated by 0.138N capacity wall for realistic trace lengths. GDPR-deletion niche is real (2025/2026 industrial market confirmed by Codebat arXiv:2511.17118). Product position: substrate as query-layer + deletion-certificate generator over a conventional log, not standalone trace store.

**P_deflated(commercially deployable 24mo) = 0.28.** Regulatory acceptance of weight-space deletion is the open gate (~0.25 P separately).

**Note path:** notes/research_program_execution_memory_audit_substrate_2026-06-01.md
**Handoff path:** notes/exp_dev_handoff_research_program_execution_audit_substrate_2026-06-01.md
**Next-drill candidate:** compliance-cryptography x quantum-resistance x algebraic-deletion-cost
2026-06-01 multiagent_coordination_substrate: notes/research_multiagent_coordination_substrate_2026-06-01.md -- GO on compliance sidecar (P_deflated=0.48 unique five-property bundle); NO-GO on hot-path coordination; next-drill: network-science/graph-theory
- analog-hardware-deployment: notes/research_analog_hardware_deployment_2026-06-01.md -- GO: substrate deletion-cert is hardware-native on crossbars; ADC-free via comparator; MHN softmax bottleneck confirmed; P_deflated=0.52; 10 citations
research_timeseries_infrastructure_2026-06-01: GO for compliance sidecar niche (P_deflated=0.60); TSDB backup gap confirmed; XOR range query cheap test pending (HP-1); HopCPT adjacency needs follow-up; -> notes/research_timeseries_infrastructure_2026-06-01.md
- [substrate-graph-gnn] notes/research_substrate_graph_gnn_2026-06-01.md -- GO on audit/compliance graph niche; NO-GO on raw accuracy; P_deflated=0.45 (audit axis); 15 citations; exp_dev handoff written

- research_governance_memorization_bound_2026-06-01: Algebraic Hebbian AM as governance-memorization-bound infrastructure -- deletion-certificate and capacity-bound map to GDPR/HIPAA/EU AI Act gaps; verification-fragility gap in competitors confirmed; P_deflated=0.32; next-drill: regulatory-text search for machine-verifiable deletion proof requirement. -> notes/research_governance_memorization_bound_2026-06-01.md
