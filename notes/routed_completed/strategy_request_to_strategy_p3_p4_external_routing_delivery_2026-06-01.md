# Strategy request: P3 + P4 delivery from external-distribution routing (with P2 source-verification finding)

## Trigger: research session processing 2026-06-01 of orchestrator routing `strategy_request_to_research_external_distribution_2026-05-31.md`

Origin: orchestrator filed 2026-05-31 15:53 with 6 research priorities. This routing delivers research-owned P3 + P4 outputs; P2 source-verification result included; P1/P5/P6 status noted.

## Finding (one paragraph)

3 priorities processed this turn:
- **P3 cross-framework probe (percolation theory on Path D)** -- partial theoretical home (P_def 0.30-0.40); bootstrap-percolation / Hopfield coincidence theorem is real precedent but established for classical Hopfield not MAP-B; **critical operational finding**: depth=50 result is mostly mixing-time-floor regime (~18 hops at M=262K per O(log^2 M) Benjamini-Kozma-Wormald 2008); the K=100 trivialization concern is SHARPENED (predicts K=1 sweep would actually probe phase boundary, K=500/1000 would further trivialize); structured-key 5% gap directionally consistent with correlated-edge percolation; predicted actual ceiling at M ≈ 100N-300N (order-of-magnitude bound, not derived).
- **P4 compositionality audit API design** -- ALL 6 HARD-PASS criteria MET. 3 primary calls (`audit()` / `audit_cert()` / `verify_audit()`); ~664 bytes/query medium granularity, ~13-15 KB deep mode; <3% latency overhead; 4 compliance use cases mapped (GDPR Art 17 / HIPAA §164.312(b) / SOC 2 CC7 / EU AI Act Art 50); engineering effort ~1650 LOC + ~7 person-weeks; key substrate advantage over W3C PROV-DM: "standard PROV-DM traces are assertions; substrate traces are PROOFS."
- **P2 TCFT degradation source verification** -- BLOCKING FINDING: external doc cited var_ratio 0.20→0.33→0.50→0.66 across M/N=0.25→2.0 at N=16384; **cap_map measurement (v245+v247 N=8192 5-seed FULL) shows mean_var_ratio = 3.2e-8** — six orders of magnitude below the doc's cited values. Source anchor unidentified. P2 cannot proceed against doc's numerics; needs orchestrator clarification (which dataset? hypothetical degradation curve? data from a probe I haven't found?).

## Recommended action

### P3 (percolation theory) — cap_map updates + recommended next experiment

**Cap_map row updates proposed**:

1. **Path D production-default sub-row caveat list** — add explicit theoretical framing:
   - "Empirical 'no ceiling at 64N depth=50' is consistent with deep supercritical percolation regime; bootstrap-percolation / Hopfield coincidence theorem (Albanese et al. 2014 PMC) provides theoretical scaffold for classical Hopfield; **bridge to MAP-B with Bayesian posterior reduction is not yet in literature**."
   - "Depth=50 is past mixing-time floor O(log² M) ≈ 18 hops at M=262K (Benjamini-Kozma-Wormald 2008); per-hop iteration beyond ~18 hops is mostly mixing-floor regime, not deep-iteration novelty."
   - "Predicted actual ceiling at M ≈ 100N-300N (order-of-magnitude bound from Hopfield α_c=0.14 extrapolation; not derived for MAP-B + K=100 posterior reduction)."
   - "K=100 trivialization concern SHARPENED: p_eff = K/M = 3.8×10⁻⁴ at M=64N is 100× above ER threshold 1/M; deep supercritical safety margin."

2. **Structured-key sub-annotation** — link to correlated-edge percolation:
   - "Structured-key 5% per-hop gap (PP-11 verdict) is directionally consistent with correlated-edge percolation prediction (assortative correlations reduce giant-component coverage; Goltsev-Dorogovtsev-Mendes 2008 + Valdez-La Rocca 2026). Magnitude (5%) within 10-20% threshold-shift range documented for assortative networks. Not a tight quantitative derivation; directionally correct."

**Recommended next experiment** (file as `strategy_request_to_exp_dev_*` when orchestrator queues):

**Anchor**: `path_d_k1_phase_boundary_probe_v1_n4096`

**Spec sketch**: vary K_candidates from K=1 → K=10 → K=100 at fixed M=16N, depth=5, N=4096, K=100 random keys. **At K=1**, the walk probes the actual substrate phase boundary (no candidate-count safety margin). **At K=100**, we replicate the validated regime. At intermediate K we should see the transition. Pre-reg HARD-PASS: K=1 retrieval shows graceful degradation (substantive accuracy at <50% but >random); K=10 closes most of the gap to K=100; K=100 hits unanimous. HARD-FAIL: K=1 already at random-chance accuracy (substrate Path D was operating entirely in the candidate-safety-margin regime, not the substrate-physics regime). Cost: ~30-60min CPU OR ~10-20min Lambda. Local 8GB GPU sufficient.

**Why this matters**: it's the cleanest empirical probe of whether Path D's validated envelope is the substrate-physics envelope vs the K-safety-margin envelope. Without this experiment, the cap_map's "trivialization-on-K=100" caveat stays vague; with it, we either close the caveat or precisely locate where the substrate-physics begins.

### P4 (audit API design) — testbed engineering spec

**Cap_map row updates proposed**:

NEW row: "Compositionality audit API (algebraic-exactness + PROV-DM-compatible + W3C-CT-style chain)" at 🔬 0.60-0.75 P-band

Caveats: substrate audit advantage over standards = "PROV-DM traces are assertions; substrate traces are PROOFS via element-wise unbinding exactness." Engineering effort ~1650 LOC, ~7 person-weeks. 4 compliance use cases empirically mapped (GDPR / HIPAA / SOC 2 / EU AI Act).

**Recommended testbed engineering routing**: file as `testbed_handoff_compositionality_audit_api_2026-06-01.md` with the drill P4's full deliverable as the engineering spec. Testbed-owned; ~7 person-weeks; depends on atom registry existing (or +2 person-weeks for schema design + backfill if not present).

Storage cost summary at N=4096, depth=5, M=10^6 entries:
- Medium granularity audit: ~664 bytes/query
- Deep audit (on-demand): ~13-15 KB/query
- Certificate (pre-computed): ~300 bytes/entry
- Total certificate store at 10^6 entries: ~300 MB (tractable)

Latency: <3% overhead at medium granularity; <10% in deep mode (drill P4's quantified estimate; matches the pre-reg HARD-PASS criterion).

**Why this matters**: this is the prerequisite for testbed's killer-feature engineering work. The drill's headline finding — "substrate traces are PROOFS not assertions" — is the strongest defensible product moat claim for regulated-industry deployment.

### P2 (TCFT mechanism analysis) — BLOCKING; routing back to orchestrator

The external doc's cited var_ratio sequence (0.20→0.33→0.50→0.66) does NOT match cap_map measurements (3.2e-8 across v245+v247 at N=8192 5-seed). Possibilities:

(a) **Doc cited a hypothetical degradation curve**, not measured data. P2 was framed against a curve that doesn't exist in the substrate's measurements. Would need re-framing against actual v245/v247 numerics.

(b) **Data from a probe I haven't found** (smoke-only? local-only? not in cap_map?). Would need orchestrator to identify the source dataset.

(c) **Different metric definition** — maybe the doc's "var_ratio" is a different quantity than v245/v247's tcft_variance_ratio. Would need disambiguation.

**Recommendation**: orchestrator clarifies (a/b/c) before P2 dispatches. Until then, P2 STAYS OPEN as research-owned but BLOCKED on source verification. P2 Phase 1 analysis would build on potentially-wrong foundation if started against doc's numerics without verification.

## Confidence

P_deflated estimates (calibration-applied):

- **P3 percolation framework provides defensible theoretical home for Path D**: 0.30-0.40 (range reflects 3 gaps: coincidence theorem is for classical Hopfield not MAP-B; mixing-time floor reduces depth=50 novelty; no closed-form transition derivation)
- **P3 recommended K=1 sweep delivers strategic information**: 0.65-0.75 (clean experimental design; cheap; falsifiable either way)
- **P4 audit API design meets all 6 HARD-PASS criteria**: 0.85-0.90 (design drill verdict is HARD-PASS as filed)
- **P4 production deployment within 7 person-weeks at 1650 LOC**: 0.55-0.70 (engineering estimate; depends on atom registry pre-existing or +2 weeks)
- **P2 source clarification resolvable by orchestrator**: 0.70-0.85 (orchestrator likely has visibility into where the doc's numerics came from)

## Files of interest

- `notes/strategy_request_to_research_external_distribution_2026-05-31.md` (the routing being processed; CLOSE to `routed_completed/` after orchestrator accepts this delivery)
- Drill P3 return: percolation theory analysis (full 800-word report; 6 axes; 6 citations including Albanese et al. 2014 PMC bootstrap-percolation coincidence theorem)
- Drill P4 return: compositionality audit API design (full deliverable with API spec, storage/latency cost, 4 compliance use cases, engineering effort estimate)
- `notes/substrate_capability_map.md` v245+v247 entries (TCFT FULL N=8192 5-seed HARD_PASS at mean_var_ratio=3.2e-8; not matching doc's 0.20-0.66 sequence)
- Memory: [[feedback-aggressive-cross-domain-research]] (P3 was overdue per 24-48h cadence; this delivery closes that), [[feedback-no-padding-experiments]] (P3 K=1 sweep is the strategically most-valuable experiment, not K=500/1000 which would further trivialize)

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Whether to accept P3 cap_map caveat updates (Path D sub-row + structured-key annotation)
- (b) Whether to dispatch P3's recommended K=1 sweep experiment (file as `strategy_request_to_exp_dev_*`)
- (c) Whether to accept P4 NEW cap_map row "Compositionality audit API" at 0.60-0.75
- (d) Whether to file P4 testbed engineering routing (~7 person-weeks)
- (e) Whether to clarify P2 source dataset (which path: a/b/c above?)
- (f) Whether to close `strategy_request_to_research_external_distribution_2026-05-31.md` to `routed_completed/` (P3+P4 delivered; P1/P5/P6 remain pending; P2 blocked)

Pending priorities from the original routing:
- **P1 substrate-LLM Week 1 feasibility smoke**: testbed-owned, gated on Phi-3 Missing 7 verdict (status_log shows still pending)
- **P5 substrate-LLM Build Week 1 detailed planning**: contingent on P1 GO
- **P6 Path B sub-capacity production characterization**: stays open as future exp_dev anchor; verify T5's latest characterization first per orchestrator pre-filing flag
- **P2 TCFT mechanism analysis**: BLOCKED on source verification

No engineering work begins without orchestrator queueing.


---
**Acted-on 2026-06-01:** all P3+P4 cap_map updates accepted (cap_map v305->v306; PP-11 caveat + Path D percolation caveats + NEW PP-12 row); K=1 phase boundary probe noted as pending exp_dev dispatch (separate strategy_request_to_exp_dev_* when orchestrator queues); P2 blocked-on-source-verification acknowledged.
