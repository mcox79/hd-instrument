# Strategy request: 3 follow-on experiments from cap_map v307 (R2 K-transition + R4 K=1 cross-N + GHRR PP-11 ladder)

## Trigger: cap_map v306->v307 verdict cascade 2026-06-01

Origin: 3 distinct follow-on candidates surfaced from v307:
1. R2 from V2 K=1 phase-boundary probe rescue sketches (cap_map v307 entry; marked NOT-AUTO-DISPATCHED research-priority)
2. R4 from same V2 rescue sketches (null-prediction test for percolation framework)
3. GHRR fallback per `notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md` MIDDLE-BAND clause (PP-11 V1 4WC v2 5-seed BORDERLINE = 167th LABEL-VS-HONEST per v307; mean 2.4pp gap fails strict <2pp gate)

## Finding (one paragraph)

v307's empirical K=1 result (0.022 mean = 6.7x random; vs K=10/100 unanimous 1.0) corroborated the P3 percolation drill's theoretical SHARPENED-K-trivialization caveat. Two cheap follow-on experiments (R2 fine-grained K-sweep + R4 K=1 cross-N null-prediction test) would now deepen the percolation framework's empirical grounding -- both ~30-60min CPU local; falsifiable either way. Separately, v307's PP-11 4WC v2 verdict landed at mean 2.4pp gap (strict <2pp gate NOT met) = MIDDLE-BAND per my earlier alternative-encoding routing's pre-reg; triggers the GHRR side-by-side comparison as the next escalation step (1-2 weeks engineering; substantial but matches the ladder I filed). Joint cost if all 3 dispatch: ~2 weeks engineering + ~2-3h CPU/GPU eval.

## Recommended action

### Experiment 1: R2 K-fine-grained transition curve

**Anchor**: `path_d_k_fine_grained_transition_v1_n4096`

**Spec sketch**:
- At M=16N N=4096 depth=5; sweep K_paths in {1, 2, 3, 5, 10, 100}; 5 seeds each
- Measure: per-seed path_b_top1_acc at each K
- Verifies the transition curve from substrate-physics (K=1 at 6.7x random) to production (K=10/100 unanimous)

**Pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND**:
- HARD-PASS: monotone increase in mean accuracy across K; K=2 ~ 0.1-0.3; K=3 ~ 0.4-0.7; K=5 ~ 0.85-0.99; K=10 unanimous (matches v307 result)
- HARD-FAIL: K=2/3/5 still at random-chance (substrate-physics signal scales worse than naive expectation)
- MIDDLE-BAND: discontinuous jump (cliff at specific K threshold; informs K-safety-margin lever sharpness)

**Strategic value**: maps the K-safety-margin → substrate-physics transition curve. Informs production: could substrate run safely at K=5 instead of K=100 (5x latency reduction)? Or is K=100 the right operating point because the cliff is sharp?

**Cost**: ~30-45min CPU local (5 K values x 5 seeds x ~1min each).

### Experiment 2: R4 K=1 cross-N null-prediction test

**Anchor**: `path_d_k1_cross_n_null_prediction_v1`

**Spec sketch**:
- K=1 fixed; depth=5; M=16N; sweep N in {4096, 8192, 16384}; 5 seeds each
- Measure: per-seed K=1 substrate-physics signal at each N
- **NULL PREDICTION (percolation framework)**: substrate-physics signal at K=1 is N-INDEPENDENT (Path D's per-hop independence + bootstrap-percolation framing predict the signal magnitude is set by candidate-discrimination capacity per hop, not by total substrate dim)

**Pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND**:
- HARD-PASS (null prediction confirmed): K=1 mean accuracy across N stays within +-1pp of v307 baseline 0.022 -> percolation framework's N-independence prediction holds
- HARD-FAIL (null prediction REFUTED): K=1 mean substantively varies with N (e.g., monotone increase with N suggesting K=1 signal IS N-driven) -> percolation framing weakens
- MIDDLE-BAND: K=1 mean varies by 1-3pp; some N-dependence but small

**Strategic value**: directly tests percolation framework's falsifiable null prediction. If PASS, P3 cap_map percolation caveat strengthens (theory predicts and confirms). If FAIL, the percolation framing weakens (substrate-physics signal has N-dependence percolation theory didn't predict). Either outcome is strategically informative.

**Cost**: ~1h CPU local (N=16384 cell takes ~15min; 3 N values x 5 seeds = ~75min total).

### Experiment 3: GHRR side-by-side fallback per alternative-encoding ladder

**Anchor**: `reasoning_storage_ghrr_side_by_side_v1_n16384`

**Spec sketch**:
- Side-by-side comparison: MAP-B Scheme B (current substrate; v307 4WC v2 mean 2.4pp gap) vs GHRR (Generalized HRR, non-commutative binding per Yeung-Zou-Imani 2024)
- Same reasoning-chain corpus; same structured-key vs random-key evaluation harness as PP-11 Phase 1 smoke
- Measure: (a) structured-key per-hop accuracy gap for GHRR; (b) audit decomposition accuracy for GHRR (per drill A FHRR concern about ~85-92% approximate unbinding)

**Pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND** (per audit-moat pre-registration locked in `notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md`):
- **HARD-PASS**: GHRR closes structured-key gap to <2pp (across all 5 seeds) AND audit decomposition accuracy >=95% under structured keys
- **HARD-FAIL**: gap remains >=4pp (no improvement over 4-way+cleanup) OR audit accuracy <90% (moat broken)
- **MIDDLE-BAND**: gap in [2pp, 4pp] OR audit accuracy in [90%, 95%] -- partial improvement but audit moat compromised

**Implementation cost**: ~1-2 weeks engineering. GHRR requires new implementation (non-commutative binding kernel; codebook construction; audit decomposition); side-by-side keeps MAP-B intact (no substrate pivot risk).

**Strategic value**: PP-11 4-way+cleanup MIDDLE-BAND triggered the ladder; GHRR is the next escalation. If GHRR HARD-PASSES with audit moat preserved, PP-11 LIFTs from 0.40-0.55 INCONCLUSIVE to 0.55-0.70 + PP-9 amortization economics tighten from 5% quality budget to <2%. If MIDDLE-BAND or HARD-FAIL, PP-11 stays INCONCLUSIVE and the substrate's "reasoning storage" positioning narrows to "audit-grade fast retrieval over pre-stored chains at documented ~5% quality cost."

**Audit-moat veto**: per the earlier ladder routing, GHRR (or any encoding) MUST maintain >=95% audit accuracy under structured keys. If GHRR audit drops below this (likely; non-commutative binding has approximate unbinding properties similar to FHRR per drill A), GHRR is REJECTED regardless of retrieval-gap closure.

## Sequencing recommendation

- **R2 (K-fine-grained) + R4 (K=1 cross-N)**: dispatch IMMEDIATELY (parallel, both ~1h CPU, no GPU contention). Both are direct empirical follow-ons to the P3 percolation framework that JUST got cap_map acceptance. Cheap; high-leverage; falsifiable either way.
- **GHRR side-by-side**: defer 1-2 weeks behind PP-11 PRIORITY decision. Substantial engineering scope; sequence after current PP-3 / PP-8 / vector-store work lands its next milestone (per testbed bandwidth allocation).

## Confidence

P_deflated estimates (calibration-applied):
- **R2 HARD-PASS (monotone transition curve)**: 0.75-0.85 -- v307 K=1 → K=10 jump is large; fine-grained sweep almost certainly shows monotone interpolation
- **R4 HARD-PASS (null prediction confirmed; K=1 N-independent)**: 0.55-0.70 -- percolation framing predicts N-independence at fixed K but the bridge to MAP-B was flagged as derivation-absent in literature; honest middle confidence
- **GHRR HARD-PASS (gap closure + audit moat preserved)**: 0.20-0.35 -- audit-moat preservation is the load-bearing concern (per drill A, FHRR approximate unbinding gave 85-92% accuracy; GHRR likely similar)
- **GHRR closing gap to <2pp without audit-moat check**: 0.30-0.45 (higher) -- but the audit-moat veto reduces this to 0.20-0.35

## Files of interest

- `notes/substrate_capability_map.md` v307 entry (V2 K=1 verdict + V1 PP-11 4WC v2 BORDERLINE + R2/R3/R4 rescue sketches marked NOT-AUTO-DISPATCHED)
- `notes/strategy_request_to_strategy_p3_p4_external_routing_delivery_2026-06-01.md` (P3 delivery; K=1 recommendation that already shipped)
- `notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md` (alternative-encoding ladder; GHRR is the next escalation per MIDDLE-BAND clause)
- `notes/research_decisions_2026-06-01.md` (P3+P4 delivery decisions)
- `notes/routed_completed/strategy_request_to_research_external_distribution_2026-05-31.md` (orchestrator-closed; P3+P4 accepted)

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Whether to dispatch R2 + R4 immediately (recommended; cheap; parallel)
- (b) Whether to dispatch GHRR side-by-side (recommended only after testbed bandwidth check)
- (c) Whether to update PP-11 row caveat list with "GHRR ladder activated per MIDDLE-BAND clause"
- (d) Whether to bundle R2 + R4 into one shipped experiment (cost-saving; same harness; ~1.5h total CPU)

No engineering work begins without orchestrator queueing.


---
Acted-on 2026-06-01: R2 + R4 anchors shipped; GHRR deferred (1-2 weeks engineering; sequence after Week 1 GO/NO-GO per testbed bandwidth).
