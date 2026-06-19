# Strategy request: PP-11 alternative encoding experiment (4-way binding + per-hop cleanup; FHRR as fallback)

## Trigger: research 2x deep drill 2026-05-31 (2 parallel Sonnet drills synthesized)

Origin: user 2026-05-31 -- shared PP-11 borderline result + "deploy research 2x" on alternative encodings (FHRR / 4-way binding with cleanup). Full save at `notes/research_pp11_reasoning_storage_borderline_save_2026-05-31.md`. Per [[feedback-2x-means-depth]] = operational depth on the specific candidate mechanisms.

## Finding (one paragraph)

Drill B (4-way binding + per-hop cleanup) is the **clear primary recommendation** -- it beats drill A (FHRR) on every axis: higher P_def for closing the 5% structured-key gap to <2% (**0.30-0.45 vs 0.15-0.30**), 10-20x cheaper engineering (**~1-2 days vs 1-2 weeks**), **audit moat fully preserved** (vs weakened to ~85-92% audit accuracy in FHRR's approximate unbinding), and no substrate pivot risk. Drill B's mechanism: extend `k_step = r ⊙ k1 ⊙ k2` to `k_step = r ⊙ k1 ⊙ k2 ⊙ k_hop_id` (adds hop-identifier codeword); per-hop cleanup via nearest-neighbor snap to value codebook between hops (Steinberg-Sompolinsky 2022 direct precedent). Drill B identified an important ablation: run 4-way alone (without cleanup) FIRST to test whether hop-id addresses the same interference class as the failed permutation mitigation (+0.7% only) -- if yes, 4-way may cap at ~1% improvement too. FHRR is the fallback IF drill B's combined arm doesn't close gap; **GHRR (Generalized HRR, Yeung-Zou-Imani 2024) is a stronger candidate than vanilla FHRR** (P_def 0.30-0.45 for closure; non-commutative binding better for compositional/nested structures) but requires more engineering.

## Recommended action

**1. Cap_map: PP-11 row updated with explicit next-experiment caveat (no band move yet).**

PP-11 caveat list extension: "Alternative-encoding candidate identified for closing 5% structured-key gap: 4-way binding (`k_step = r ⊙ k1 ⊙ k2 ⊙ k_hop_id`) + per-hop cleanup (Steinberg-Sompolinsky 2022 direct precedent). Engineering cost ~1-2 days; audit moat fully preserved (4-way unbinding still exact under MAP-B; cleanup is auditable codebook-lookup not algebraic). P_def 0.30-0.45 for HARD-PASS (gap <2%); 0.45 for MIDDLE-BAND (2-3% residual); 0.10-0.15 for HARD-FAIL. FHRR DEPRECATED as next-experiment candidate (P_def 0.15-0.30 closure + audit-moat-weakening to ~85-92% accuracy is unacceptable cost). GHRR (non-commutative HRR) is the stronger algebra-change fallback IF 4-way+cleanup fails."

PP-9 amortization-economics row: unchanged for now (5% quality-degradation budget stays caveated); update IF 4-way+cleanup HARD-PASSes.

**2. NEW experiment to dispatch.**

**Anchor**: `reasoning_storage_4way_cleanup_v1_n16384`

**Spec sketch (exp_dev refines)**:

Setup (matches PP-11 Phase 1 smoke for direct comparability):
- N=16384, BSC bipolar codebook
- 500 reasoning chains depth 3-5; structured-key + matched random-key
- Same evaluation harness as PP-11

3 Arms (the ablation matters per drill B open question 5):
- **Arm A: 4-way binding ALONE** (no cleanup) -- isolates hop-id contribution; tests whether hop-id addresses same interference class as failed permutation mitigation. If Arm A gives only ~1% improvement, drill B's "hop-id disambiguates structured interference" hypothesis is partially refuted.
- **Arm B: Per-hop cleanup ALONE** (3-way binding + cleanup) -- isolates cleanup contribution; tests whether cleanup alone handles the structured-key noise component.
- **Arm C: Combined 4-way + cleanup** -- tests super-additivity. Primary deliverable arm.

Hop-id codebook constraints (per drill B Axis 1 self-binding pathology check):
- D=10 hop codewords drawn INDEPENDENTLY from r_type, k_premise1, k_premise2 codebooks
- No reuse across hop indices (must avoid k_hop_id_i ⊙ k_hop_id_j collapsing to identity)
- Optional refinement: Hadamard or Gram-Schmidt orthogonalization (drill B open question 3)

Cleanup implementation:
- Nearest-neighbor snap to value codebook via cosine similarity
- Hopfield-update implementation per drill B (Ramsauer 2020); GPU-friendly; <1ms per hop at codebook size 200
- Audit trace records: hop_index, raw_retrieved (or hash), cleaned_codeword_index, cosine_similarity

**Pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND** (combined Arm C; per drill B):

| Band | Condition |
|---|---|
| **HARD-PASS** | Arm C closes structured-key gap to <2% (>3pp reduction from baseline 5%); ALL 3 SEEDS pass strict bar; audit completeness 100% on algebraic decomposition + cleanup-step verification rate >0.95 |
| **MIDDLE-BAND** | Arm C gives 2-3% gap; at least 2/3 seeds pass; partial closure (recommend: dispatch GHRR follow-on instead of FHRR per drill A's GHRR flagging) |
| **HARD-FAIL** | Arm C gives <1% improvement (substantively same as failed mitigation arm); 5% quality budget LOCKS IN permanently for PP-9 economics |

**Pre-reg ablation reads** (Arms A and B):
- If Arm A (4-way alone) gives <1.5% improvement → hop-id addresses same interference class as failed permutation; combined arm's improvement is mostly from cleanup
- If Arm B (cleanup alone) gives <1% improvement → cleanup snaps to wrong codeword under structured-key noise (drill B Axis 2 concern materializing); combined arm's improvement is mostly from hop-id
- Both signals inform whether GHRR or FHRR is the better fallback IF Arm C MIDDLE-BANDs

**Audit-trace verification arm** (free; piggybacks on Arm C eval):
- Verifier re-runs Hopfield cleanup lookup for sample of audit traces; confirms `cleaned` is argmax
- Counts: borderline cases (cosine sim < threshold 0.7); ambiguous retrievals (multiple codebook entries near argmax)
- Documents two-layer audit (algebraic + cleanup) as substrate-distinctive product capability

**Cost**: ~2-3 days engineering (1-2 days for 4-way binding + cleanup; 1 day for ablation harness) + ~2-3h GPU eval. Local 8GB sufficient. **NO cloud spend.**

**Routing**: orchestrator → exp_dev → queue.

**3. Sequencing.**

Recommended dispatch:
- PARALLEL to substrate-LLM Phase 1 build (different machine workload; minimal contention)
- IMMEDIATELY after this routing is read (no dependencies; existing PP-11 harness already built so this is delta engineering)
- Before D1 compositional binding production-scope (~2-3w) and PP-9 amortization economics (~2-3w + API spend) — both depend on PP-11 verdict

**4. Routing-file lifecycle.**

- Move `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` to `notes/routed_completed/` (PP-11 verdict landed; original Phase 1 routing closed)
- Move `notes/research_pp11_reasoning_storage_borderline_save_2026-05-31.md` to remain in `notes/` (this is the context-recovery save; superseded by this synthesis but useful for audit trail)
- This routing file (`notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md`) becomes the active routing for orchestrator

**5. IF Arm C MIDDLE-BANDs or HARD-FAILs: next-step decision.**

Drill A flagged GHRR (Generalized HRR; Yeung-Zou-Imani 2024) as a stronger algebra-change candidate than vanilla FHRR — non-commutative binding shows higher capacity + better decoding accuracy than FHRR on compositional/nested structures (exactly the structured-key three-way-binding case). P_def 0.30-0.45 deflated for GHRR closing gap; higher than FHRR.

Recommendation IF this experiment MIDDLE-BANDs:
- Skip vanilla FHRR (P_def too low; audit-moat-weakening unacceptable)
- File GHRR side-by-side comparison experiment as the next escalation (~1-2 weeks engineering)
- Audit-moat pre-registration: ANY alternative encoding must maintain audit accuracy ≥95% under structured keys

Recommendation IF this experiment HARD-FAILs:
- PP-11 stays INCONCLUSIVE permanently at 0.40-0.55
- PP-9 amortization economics LOCK IN with 5% quality-degradation budget
- Substrate's "reasoning storage" positioning narrows to "audit-grade fast retrieval over pre-stored chains at known quality cost"
- The morning's honest framing (substrate is retrieval primitive, not full reasoning primitive) remains correct; the 5% gap becomes a documented product property

## Confidence

P_deflated estimates per arm:
- **Arm A (4-way alone)**: 0.20-0.30 — addresses ONE interference class; possible saturation at ~1% if hop-id is same class as permutation
- **Arm B (cleanup alone)**: 0.15-0.25 — Steinberg-Sompolinsky precedent strong but cleanup may snap to wrong codeword under structured noise
- **Arm C (combined)**: **0.30-0.45** — super-additive if independent noise sources; saturating if overlapping
- **Audit moat preserved (Arm C, ≥95% audit accuracy)**: 0.90-0.95 (algebraic argument exact; cleanup audit is codebook lookup with verifiable trace)
- **Joint HARD-PASS (Arm C closes gap to <2% AND audit moat preserved)**: 0.30-0.45

Calibration penalty: -0.15 applied per [[feedback-lit-scan-calibration-penalty]] (cleanup precedent strong; 4-way binding has indirect precedent via position binding; uncharted combined interaction with structured-key noise).

## Critical open empirical risks

1. **Drill B open question 1**: at what hop depth does per-hop cleanup flip from beneficial to harmful for structured-key chains? If structured noise concentrates near WRONG codewords, cleanup snaps to wrong attractor at later hops. Per-depth accuracy reporting required.
2. **Drill B open question 5**: is the hop-id approach addressing the same interference class as the failed permutation mitigation (+0.7%)? Arm A ablation directly tests this.
3. **Drill A open question 1 (carries forward)**: is structured-key spectral concentration a CAPACITY effect (M/N ratio; both algebras degrade similarly) or an ALGEBRA effect (bipolar-specific; FHRR/GHRR help)? Empirical comparison still needed before substrate pivot.
4. **Hop-id codebook orthogonality**: drill B Axis 1 flagged self-binding pathology if k_hop_id reused or aligned with other components. Codebook construction matters; explicit orthogonalization may be worth +1-2% over random draw.
5. **Audit moat under cleanup**: cleanup snaps to a codebook entry; if multiple entries are near argmax (cosine sim within 0.05), the audit becomes ambiguous. Borderline-case reporting in audit trace flags this.

## Files of interest

- `notes/research_pp11_reasoning_storage_borderline_save_2026-05-31.md` (state capture for PP-11 result + next-drill plan; this routing supersedes)
- `notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md` (morning's prerequisite drill; structured-key envelope theory)
- `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` (Phase 1 smoke routing; CLOSE to `routed_completed/` when this routing accepted)
- `notes/substrate_capability_map.md` (PP-11 at 0.40-0.55 INCONCLUSIVE; PP-9 caveated with 5% quality budget; PP-9 caveat tightens IF this experiment HARD-PASSes)
- Drill A return (FHRR): P_def 0.15-0.30; AUDIT-MOAT-WEAKENING to 85-92%; 1-2 weeks engineering; GHRR flagged as stronger alternative
- Drill B return (4-way + cleanup): P_def 0.30-0.45; AUDIT-MOAT FULLY PRESERVED; 1-2 days engineering; Steinberg-Sompolinsky 2022 direct precedent
- Memory: [[feedback-2x-means-depth]], [[feedback-no-padding-experiments]], [[feedback-no-smoke]], [[feedback-lit-scan-calibration-penalty]]

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Whether to update PP-11 caveat list with next-experiment candidate
- (b) Experiment dispatch timing (recommend IMMEDIATE; cheap + parallel to other in-flight work)
- (c) Whether to accept the 3-arm structure (ablation A + B + combined C) or skip ablations and dispatch only Arm C
- (d) Whether to ACCEPT the fallback ladder (GHRR > FHRR if Arm C MIDDLE-BANDs; FHRR DEPRECATED as next-experiment due to audit-moat-weakening)
- (e) Whether to move PP-11 Phase 1 smoke routing to `routed_completed/` (verdict landed; supersession via this routing)

No engineering work begins without orchestrator queueing.

Acted-on 2026-05-31: anchor `reasoning_storage_4way_cleanup_v1_n16384` shipped to remote_cpu_queue; orchestrator dispatched after PP-11 RSB_MIDDLE_BAND verdict (cap_map v303).
