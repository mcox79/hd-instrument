# Research state update + compaction prep (v1)

Date: 2026-06-01
Purpose: comprehensive research + capability snapshot at cap_map v308; survives context compaction
Owner: research session (Opus)

## HEADLINE STATE

**Cap_map at v308** (218 → 219 PROT-009 paired commits over 12h). Portfolio = **28 capability rows + 37 sub-features**. HONEST tally 294. LABEL-VS-HONEST tally 169 (5 new catches in last 12h). Substrate's product positioning has SHARPENED substantially in last 24h:
- **First end-to-end 3-way production-stack HARD_PASS landed (V5 AQSIM3W2)**: compression × Path D retrieval × a_query_sim defense × adversarial workload, all 5 seeds clean. CLOSES two prior LABEL-VS-HONEST DEFENSE_UNNECESSARY catches.
- **Path D's "no ceiling 16N-64N" claim got empirically REFINED**: K=1 phase-boundary probe shows substrate-physics-only signal at 6.7× random (mean 0.022); K=2 ALREADY saturates 1.0; K=10/100 unanimous. Production reliability is DEMONSTRABLY K-safety-margin-driven, not substrate-physics-only.
- **K-transition is a CLIFF not a gradient** (v308 V4 K_FINE result): substrate could safely run at K=2 (50× latency saving vs K=100) — major production-deployment implication.
- **PP-11 reasoning-storage stays MIDDLE_BAND**: 4-way + Hadamard hop-id rescue FALSIFIED (v308 V3 mean 2.0pp exactly at bound; 2/5 seeds pass strict). First encoding-ladder NEGATIVE result; GHRR is the next escalation.

## CAPABILITY MATRIX (current state)

| Row | State | P-band | Most recent verdict |
|---|---|---|---|
| **PP-1** substrate-augmented LLM vs LLM-only baseline | 🔬 Research only | 0.40-0.55 | Awaiting PP-5/PP-8 |
| **PP-2** Storage efficiency at production scale | 🔬 Research only | 0.70-0.80 | v303 C3V4 cross-N N=16384 HARD_PASS |
| **PP-3** Audit trail rotation strategy | 🔬 Research only | 0.55-0.70 | Testbed Phase 1 scoping COMPLETE (v3+ unblocked); 1 cert-chain link/10 ops; ~315 bytes/link |
| **PP-4** Concept drift detection | 🔬 Research only | 0.40-0.55 | No research filed yet |
| **PP-5** Substrate-LLM latency budget | 🔬 Research only | 0.55-0.70 | C6+C7 CPU characterized (M-invariant ~0.79s/5-hop K=100 CPU); GPU pending |
| **PP-6** Bursty-write latency optimization | 🔬 Research only | 0.55-0.70 | No experiments shipped |
| **PP-7** Multi-substrate composition | 🔬 needs re-anchoring | TBD | Per `feedback-capabilities-mapping`; v282 K=10 was Op E closure not sharding |
| **PP-8** Substrate-LLM deep integration | 🔬 Research only | 0.30-0.45 | Week 0 cloud H100 revalidation authorized (testbed routing 2026-06-01) |
| **PP-9** Reasoning amortization economics | 🔬 Research only | 0.55-0.70 | Testbed Tier 2b harness pending; PP-11 informs ~5% quality budget |
| **PP-10** Multi-hop Zipfian caching | 🟢 Validated single-N | 0.70-0.85 | v302 C2_HARD_PASS 25/25 cells; hot<cold @α≥1 only |
| **PP-11** Reasoning-store primitive (3-way binding) | 🟡 Inconclusive | 0.40-0.55 | v308 4WC v3 Hadamard FALSIFIED; mean 2.0pp exactly at bound; GHRR is next escalation |
| **PP-12** Compositionality audit API | 🔬 Design-drill HARD_PASS | 0.60-0.75 | P4 6/6 criteria met; ~7 person-weeks engineering; testbed routing pending |
| Audit-grade vector store (NEW v304) | 🟡 First-empirical | 0.45-0.65 | v305 3-of-4 arms HARD_PASS; cert FP=1% threshold gap (resolvable per v307 cert_threshold sweep) |
| **Path D no-ceiling sub-row** | ✅ Within 64N envelope | 0.92-0.98 | Empirically refined: production reliability K-safety-margin-driven (v307 K=1 + v308 K=2 saturation) |
| **Adversarial defense (a_query_sim)** | 🟡 YELLOW + composition | 0.55-0.75 | v307 V4/V5 PDAC2+AQSIM3W2 3-way HARD_PASS; multi-attack-class still open |
| **Modern Hopfield activation regime** | 🟢 N=16384 confirmed | 0.78-0.92 | 2-anchor CPU + GPU confirmed past 16N |
| **Agentic workload characterization (NEW v304)** | 🟢 Production-shape | 0.68-0.82 | G13B 3 archetypes × 5 sessions HARD_PASS; sustained 2.5h MIDDLE_BAND mem-amp 2.43× engineering item |

## RECENT RESULTS (last ~24h, cap_map v300 → v308)

**Cap_map activity (8 versions in 12 hours; 7 paired-commits 212-219)**:

| Bump | Date | Key verdicts |
|---|---|---|
| v300 → v301 | 2026-05-31 | V2 24h sustained_workload baseline FIRST 24h validation at production scope |
| v301 → v302 | 2026-05-31 | C2 Zipfian caching HARD_PASS + PP2ADV compression-under-adversary HARD_PASS + RSB reasoning-storage smoke MIDDLE_BAND |
| v302 → v303 | 2026-05-31 | RSTS threshold sweep + C3V4 PP-2 cross-N N=16384 + CPD first compositional HARD_PASS at N=4096 |
| v303 → v304 | 2026-06-01 overnight | 9-VERDICT WAVE: 4WC v1 BORDERLINE-OVER-CLAIM (163rd LABEL-VS-HONEST); G13B agentic-workload trio HARD_PASS; PDAC + AQSIM3W defense-unnecessary (164/165 catches); CPD2 cross-N HARD_PASS at N=8192 |
| v304 → v305 | 2026-06-01 | V7 continuous-embedding v2 MOAT_SURVIVAL MIDDLE_BAND (166th); NEW audit-grade-vector-store row 0.45-0.65 (3-of-4 arms HARD_PASS) |
| v305 → v306 | 2026-06-01 | ANNOTATION + NEW ROW: P3+P4 research delivery ACCEPTED; Path D percolation caveats + PP-12 audit API NEW row 0.60-0.75 |
| v306 → v307 | 2026-06-01 | K=1 phase boundary EMPIRICALLY CONFIRMED P3 percolation caveat (k1=0.022 = 6.7× random; K=10/100 unanimous); V5 AQSIM3W2 FIRST 3-way compositional HARD_PASS; PP-11 4WC v2 167th BORDERLINE |
| v307 → v308 | 2026-06-01 | K_FINE: K=2 already saturates 1.000 (CLIFF not gradient; 169th LABEL_UNDER_CLAIMS); K1_CROSSM HARD_PASS — substrate-physics M-axis phase boundary at M=2N→4N; 4WC v3 Hadamard rescue FALSIFIED (mean 2.0pp exactly at bound) |

**Big takeaways from the last 24h**:

1. **The K-safety-margin scaling lever is empirically located**: K=1 substrate-physics ≈ 6.7× random; K=2 unanimous. Production could safely run at K=2 (50× latency reduction vs K=100). The K=100 trivialization concern is now precisely characterized.

2. **First end-to-end 3-way production-stack HARD_PASS** (compression × Path D × a_query_sim defense × adversarial workload). Substrate-product positioning has its first cross-killer-feature compositional validation.

3. **PP-11 reasoning-storage encoding ladder: first NEGATIVE rescue** (Hadamard hop-id v3 mean 2.0pp exactly at strict bound; 2/5 seeds pass). 4-way + cleanup family does NOT close the 5% structured-key gap. GHRR is the next escalation per the alternative-encoding ladder.

4. **Path D M-axis phase boundary LOCATED** (v308 K1_CROSSM): substrate-physics signal collapses past M=2N (K=1 mean drops 0.966 → 0.022 at M=4N). The percolation framework's M-driven phase transition is empirically real at K=1.

5. **Continuous-embedding storage moat survival MIDDLE_BAND** at N=16384 (3 of 4 arms HARD_PASS; cert FP-rate=1% threshold gap; resolvable per v307 cert_threshold sweep). Audit-grade-vector-store NEW row at 0.45-0.65 (first empirical data).

6. **P3 + P4 research drills accepted into cap_map** (v305 → v306) with full caveat language adopted; routing closed to `routed_completed/`. P2 BLOCKED on source verification (orchestrator agreed: external doc cited hypothetical curve).

## CURRENTLY IN-FLIGHT + QUEUED (as of v308 + this turn's routings)

**Active experiments in queue** (from status_log 09:40+):
- `path_d_k1_cross_n_null_prediction_v1` (R4 from my v307 follow-on routing): tests percolation null prediction (K=1 N-independent); ~1h CPU
- Various overnight wave items completing

**Queued from my v307 follow-on routing** (filed 2026-06-01 ~09:21):
- R2 K-fine-grained — **ALREADY RAN**; result: K=2 already saturates (cliff not gradient; LABEL_UNDER_CLAIMS catch #169 in v308)
- R4 K=1 cross-N — in flight or pending
- GHRR side-by-side fallback — deferred pending testbed bandwidth

**Active testbed handoffs** (filed today):
- `testbed_handoff_dashboard_session_coordination_v1_2026-06-01.md` (latest, 09:32)
- `testbed_handoff_week0_cloud_h100_revalidation_authorized_2026-06-01.md` (cloud H100 revalidation for PP-8 Week 0)
- `testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md` (PP-3 unblocked; testbed scoping complete: 1 cert/10 ops, ~315 bytes/link)

**Research routings filed today**:
- `strategy_request_to_strategy_p3_p4_external_routing_delivery_2026-06-01.md` (ACCEPTED into v306)
- `strategy_request_to_strategy_v307_followon_experiments_2026-06-01.md` (R2 ran with surprising K=2 saturation result; R4 in flight; GHRR pending)

**Research-priority candidates from v307 rescue sketches** (NOT-AUTO-DISPATCHED):
- R3 K=1 M-sensitivity at multiple M (substantively SUPERSEDED by v308 K1_CROSSM result)
- Various other rescue branches per cap_map entries

## PRIORITY PLAN FOR NEXT 1-2 WEEKS

**TIER 1 (highest leverage; dispatchable now)**:

1. **PP-11 GHRR side-by-side experiment** (per alternative-encoding ladder MIDDLE-BAND clause). 4WC v3 Hadamard rescue NEGATIVE locks in the need to try non-bipolar algebra. ~1-2 weeks engineering. Audit-moat veto: GHRR REJECTED if audit accuracy drops <95% under structured keys (likely concern per FHRR drill A 85-92% accuracy precedent).

2. **Production-K=2 deployment validation** (NEW recommendation from v308 K_FINE result). The K-transition cliff at K=1→K=2 means production could run at K=2 instead of K=100 (50× latency reduction). Cheap empirical confirmation: ship `path_d_production_k2_validation_v1_n4096` with K=2 at production envelope M=16N, depth=5, full benchmark suite vs K=100 baseline. Pre-reg HARD-PASS: K=2 matches K=100 within 0.5pp across 5 seeds. Cost: ~30min CPU.

3. **Continuous-embedding cert_threshold v2** (per v307 V3 cert_threshold runner-FAILED label-OVER-CLAIMS): fix the runner issue + complete the threshold sweep; resolves the cert FP=1% threshold gap that's preventing audit-grade-vector-store row LIFT from 0.45-0.65 → 0.55-0.75.

**TIER 2 (medium leverage; dispatchable after Tier 1 lands)**:

4. **PP-7 multi-substrate composition re-anchoring drill** (~30-60min research). Hierarchical substrate question was filed yesterday with re-anchoring needed; P3+P4 acceptance frees research bandwidth for this drill. Per the `hierarchical_substrate_2x_synthesis` finding: hierarchy is NOT strategically superior to single-big-N within 12-month horizon (P_def 0.18) — but the re-anchoring drill should verify whether any product use case forces hierarchy.

5. **PP-4 concept drift detection design drill** (~30-60min research). Listed as Tier-2 killer feature but no research filed. Bridges to PP-9 reasoning-amortization economics (the substrate's continual-learning state COULD distinguish shift-classes).

6. **Cross-framework probe (overdue per 24-48h cadence per `feedback-aggressive-cross-domain-research`)**: P3 percolation was one. Next candidate: free-probability framework for PP-2 storage compression (orthogonal to existing percolation framing).

**TIER 3 (lower leverage; defer to subsequent cycles)**:

7. **PP-8 Phi-3-mini-4bit Week 1 feasibility smoke** (testbed-owned; gated on Phi-3 Missing 7 verdict landing — was pending overnight; check status_log for verdict)

8. **PP-9 reasoning amortization Tier 2b harness extension** (Anthropic API; ~$50-100 spend; depends on PP-11 result; with PP-11 stuck at MIDDLE_BAND, the 5% quality budget is the documented PP-9 caveat)

9. **PP-6 bursty-write latency optimization** (~2-3 weeks engineering; no current substrate-physics blocker)

## OPEN DECISIONS FOR ORCHESTRATOR / USER

1. **GHRR dispatch timing**: PP-11 ladder triggered; ~1-2 weeks engineering. Sequence with PP-8 cloud H100 build?
2. **K=2 production validation**: cheap; high-strategic-value (50× latency reduction claim). Recommend dispatch immediately.
3. **PP-12 audit API testbed engineering**: ~7 person-weeks; testbed routing pending. Sequence with PP-3 audit rotation (synergistic; both touch audit-cert chain).
4. **PP-7 re-anchoring drill timing**: ~30-60min; cheap; informs whether hierarchy ever revisits.
5. **PP-4 concept drift design drill timing**: similarly cheap.

## STRATEGIC NARRATIVE (current best framing)

The substrate's product positioning (as of v308) is:

> **Audit-grade memory + retrieval primitive with structured-key support** for regulated-industry AI deployments. Production reliability is K-safety-margin-driven (K=2 already unanimous; K=100 in current production has 50× latency headroom). Algebraic moat survives projection for continuous embeddings (3 of 4 arms HARD_PASS; cert FP threshold gap resolvable). First end-to-end 3-way production-stack HARD_PASS (compression × retrieval × defense × adversarial workload). Reasoning-storage primitive exists at ~5% per-hop quality budget (PP-11 MIDDLE_BAND; GHRR fallback queued). Compositionality audit API design-drill complete with 4 compliance use cases mapped (GDPR/HIPAA/SOC2/EU AI Act).

This is **substantively sharper** than the morning's framing because:
- K-safety-margin scaling lever empirically located (NEW)
- 3-way compositional HARD_PASS lands (NEW; closes 2 prior LABEL-VS-HONEST catches)
- Path D theoretical scaffold via percolation (NEW; bootstrap-percolation / Hopfield coincidence theorem)
- PP-11 ladder triggered with first NEGATIVE rescue (NEW; honest narrowing)

## COMPACTION-PREP NOTE

If context compacts mid-cycle, the following are sufficient to resume research session work:

**Required reading on resume (in order)**:
1. `notes/session_kickoff_research_v1.md` — role + ownership
2. `notes/session_synchronization_v1.md` — sync protocol (pull, inbox poll, status_log tail)
3. `notes/orchestrator_post_compaction_brief.md` — pause flag + wrapper table
4. THIS FILE — capability + experimental state at 2026-06-01 v308

**Active research routings** (these survive compaction):
- `notes/strategy_request_to_strategy_v307_followon_experiments_2026-06-01.md` (R2 already ran with surprising result; R4 pending; GHRR queued)
- `notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md` (PP-11 ladder; 4WC family FALSIFIED; GHRR is next per MIDDLE-BAND clause)
- `notes/strategy_request_to_strategy_substrate_llm_deep_integration_2026-05-31.md` (PP-8 build spec; cloud H100 revalidation authorized)
- `notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (PP-9 with ~5% quality budget caveat)
- `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (PP-1 through PP-7 framing)
- `notes/strategy_request_to_strategy_hierarchical_substrate_2x_synthesis_2026-05-31.md` (PP-7 re-anchoring; hierarchy deferred Phase 2+)
- `notes/strategy_request_to_strategy_continuous_embedding_storage_2026-05-31.md` (audit-grade-vector-store row source)
- `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` (PP-11 row source)

**Active testbed handoffs**:
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (PP-8 build; 9-section eval-rigor protocol + Q-Former-style bridge + 3 deviations from baseline)
- `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md` (PP-3 scoping complete; ~315 bytes/link, 1 cert/10 ops)
- `notes/testbed_handoff_week0_cloud_h100_revalidation_authorized_2026-06-01.md` (PP-8 Week 0 cloud H100 authorized)
- `notes/testbed_handoff_dashboard_session_coordination_v1_2026-06-01.md` (4-session dashboard)

**Closed routings** (consult only for historical context):
- `notes/routed_completed/strategy_request_to_research_external_distribution_2026-05-31.md` (P3+P4 delivered; P1/P5/P6 elsewhere; P2 blocked)
- `notes/routed_completed/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md`

**Key memory files** (these have load-bearing decisions; auto-loaded):
- `feedback_no_smoke` — honest framing; brutal honesty
- `feedback_2x_means_depth` — when user says 2x, drill deeper not re-verify
- `feedback_no_padding_experiments` — dispatch only what's load-bearing
- `feedback_substrate_value_framing_matured_2026-05-26` — plumbing > physics
- `project_substrate_killer_features_2026-05-26` — 5 product-layer features
- `feedback_aggressive_cross_domain_research` — periodic cross-framework probes
- `feedback_lit_scan_calibration_penalty` — deflate P 0.15-0.25 in uncharted regimes

**Outstanding research decisions** (most-recent-cycle):
- File K=2 production validation routing (recommended Tier 1 priority based on v308 K_FINE cliff finding)
- File GHRR routing (PP-11 ladder triggered; 1-2 weeks engineering; audit-moat veto)
- File PP-7 re-anchoring drill (cheap; 30-60min)
- File PP-4 concept drift design drill (cheap; 30-60min)

**Method discipline (carries forward)**:
- 2x research = operational depth not verification re-run (`feedback_2x_means_depth`)
- Audit before drill dispatch when input doc has hand-waved choices
- File ONE routing per natural-cluster of related experiments (not N separate routings)
- Pre-reg HARD-PASS/HARD-FAIL/MIDDLE-BAND with explicit thresholds before any work starts
- Calibration penalty (-0.15 to -0.25) for uncharted regimes
- Audit-moat veto: ANY alternative encoding must maintain ≥95% audit accuracy under structured keys

**End-of-cycle status_log entry written**. Routing files committed. Push complete.


---

Acted-on 2026-06-01: historical state update; superseded by ongoing session work


Acted-on 2026-06-01: historical state update; superseded by ongoing session work
