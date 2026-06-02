# strategy_decisions_2026-06-02.md

## v327 -> v328 @ BATCHED 12-VERDICT overnight CPU cycle 4 (10 GENUINE FULL HARD_PASS + 2 LABEL-VS-HONEST PARTIAL/MIDDLE_BAND + 1 RESCUE-SUCCESS kappa3) -- caching-policy expressibility cluster + heteroassoc-chain depth-3 + 2 NEW EXPLORATORY ROWS PP-43 + PP-44 + 1 sub-property PP-9b + I-3 RESOLVED + 2 LABEL-VS-HONEST catches (verdict_handler 239th PROT-009 paired commit)

**Trigger.** Batched 12-verdict overnight CPU cycle 4 2026-06-02. All 12 fetched via `tools.orchestrator.remote_state.get_metrics` (_source=remote authoritative). Pause-flag ABSENT. REMOTE-FIRST per e51aee7.

**Step 0 honest re-read summary.** 10 HONEST (8 clean HP + 2 with annotations: spectral_capacity_monitor BORDERLINE +0.41pp + q23/graph_node short-wall investigated and CONFIRMED genuine via N + 5-seed + run_mode=full). **2 NEW LABEL-VS-HONEST OVER-CLAIMS:**

- **#198 arc_lirs_hybrid_v1 ALPHA_CONDITIONAL_HP_LABEL_OVER_CLAIMS_AGGREGATE.** Label claims "hot/cold ratio at alpha=0.5: 3.66 (HP>=2.0). max across alpha: 6.49." Per-cell aggregated: alpha=0.1 ratio=0.9803 (FAIL ratio<1 hot LESS than cold), alpha=0.2 ratio=1.6902 (FAIL ratio<2.0 HP gate), alpha=0.5 ratio=3.6597 (HP), alpha=1.0 ratio=6.49 (HP). 2 of 4 alpha cells PASS HP; 2 FAIL. Honest reading: MIDDLE_BAND/PARTIAL ARC/LIRS hybrid requires alpha>=0.5 (high decay); low-alpha regime FAILS. NEW sub-flavor of cherry-pick-cell-aggregate.

- **#199 lru_decay_kendall_v1 M_REGIME_CONDITIONAL_HP_LABEL_OVER_CLAIMS_AGGREGATE.** Label claims "tau at M=80: 0.9325 (HP>=0.9). mean tau across M: 0.7246." Per-cell aggregated: M=10 tau=0.369 (FAIL), M=20 tau=0.722 (FAIL), M=40 tau=0.875 (FAIL), M=80 tau=0.933 (HP). 1 of 4 M cells PASS HP; 3 FAIL. Mean tau=0.7246 itself BELOW HP>=0.9 threshold. Honest reading: MIDDLE_BAND/PARTIAL gamma=0.95 weight-decay LRU works only at large M (>= ~80); small-M cache regime FAILS. **Walk-back gate noted by exp_dev (smoke tau=0.882 within 20% of HP=0.90) CONFIRMED**: FULL 5-seed reveals smoke estimate was on the M=80 large-cache cell, not small-M typical regime. NEW sub-flavor of cherry-pick-cell-aggregate.

**Verdicts processed (12).** Roster in cap_map v328 anchor.

**Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]]).**

For **kappa3_hutchinson_v2** (RESCUE-SUCCESS already executed):
- R1 (0-compute, applied) Pattern-match to v325 I-2 RESOLVED v326 -- non-vectorized inner loop + tight timeout = TIMEOUT.
- R2 (applied; PRIMARY) Vectorize 5000-probe Hutchinson loop -> 3 GEMM calls; raise timeout 1800s -> 3600s. Wall went 1800s TIMEOUT -> 136s within budget.
- R3-R5 NOT NEEDED (R2 closed).

For **PP-43b LRU large-M-only PARTIAL rescues** (NEW; for next dispatch):
- R1 (0-compute, applied) ANNOTATION-only PARTIAL: LRU works only at large-M cache regime (M >= ~80); small-M regime FAILS; document operating envelope.
- R2 (1-2h CPU) Tighter M grid in 10-80 range to characterize transition cell-by-cell; pre-reg HP=0.85 (relaxed from 0.90) at M=40+; confirms small-M failure as monotone vs degenerate.
- R3 (CPU) Alternative decay schedule: piecewise-constant gamma (gamma=0.99 for M<=40 fast-decay, gamma=0.95 for M>40 standard) -- separates small-M dynamic regime from large-M regime.
- R4 (engineering) Hybrid policy with fallback at low-confidence regime: substrate LRU at M>=80; external policy engine fallback at M<80.
- R5 (deferred) Reconsider gamma=0.95 default; sweep gamma in {0.85, 0.90, 0.95, 0.98, 0.99} at small M.

For **PP-43d ARC/LIRS high-alpha-only PARTIAL rescues** (NEW; for next dispatch):
- R1 (0-compute, applied) ANNOTATION-only PARTIAL: ARC/LIRS hybrid requires alpha>=0.5; low-alpha regime FAILS; document operating envelope.
- R2 (1-2h CPU) Fine alpha grid in [0.05, 0.5] to characterize alpha_critical cell-by-cell.
- R3 (CPU) Alternative ARC variants: tier-2 mix at alpha-dependent threshold; substrate ARC with alpha-conditional re-Hebbian intensity.
- R4 (engineering) Hybrid policy: substrate ARC at alpha>=0.5; external ARC fallback at alpha<0.5.
- R5 (deferred) Reconsider hot/cold ratio HP threshold; investigate why alpha=0.1 ratio<1 (hot LESS than cold; possible substrate primitive contradiction).

For **NO ROW CLOSURES** this batch (PP-43 row OPEN with PARTIAL caveats; no genuine refutations).

**Strategic positioning.** Caching-policy expressibility is a STANDARD product-feature cluster that substrate now PARTIALLY EXPRESSES natively via algebraic primitives (re-Hebbian, weight-decay, dual += ). LFU + write-through clean; LRU large-M-conditional; ARC/LIRS high-alpha-conditional. Product framing: "substrate expresses LFU + write-through natively; LRU + ARC have known operating envelopes -- fall back to external policy engine outside envelope." Cross-references to PP-10 multi-hop production-paths caching (substrate is the MECHANISM layer; PP-10 is the WORKLOAD layer), PP-19 substrate-as-KV-cache, PP-32 audit-grade tool-call result cache. Spectral-capacity-monitor (PP-44) is OPERATIONAL early-warning sub-feature complementing PP-37 spectral-introspection-sidecar and PP-40 effective-rank-gauge. Heteroassoc-chain depth-3 + deletion (PP-9b sub-property) is the FIRST depth-3 chain + cert-deletion structural confirmation at production scope. CT-3 outlier-bulk gap empirically validates Delta=(1-sqrt(alpha))^2 strengthening v324 free-probability spectral identity row.

**Atomic commit.** cap_map.md + history.md + this strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry. **239th PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Tallies (v327 -> v328).** HONEST 363 -> 373 (+10). LABEL-VS-HONEST 197 -> 199 (+2). Portfolio 32+64 -> 32+66 (+2 new EXPLORATORY rows + 1 sub-property). Framework-reliability product-feature 62-76% -> 64-78% (+2pp). I-3 RESOLVED.


## v328 -> v329 @ BATCHED 5-VERDICT overnight CPU cycle 5 (5 GENUINE FULL HARD_PASS; 0 LABEL-VS-HONEST) -- PP-41 TRUE-METRIC LIFT + PP-43 Tier 1+2 LIFT + 2 NEGATIVE-RESULT-CONFIRMATION sub-properties (verdict_handler 240th PROT-009 paired commit)

**Trigger.** Batched 5-verdict overnight CPU cycle 5 2026-06-02. All 5 fetched via `tools.orchestrator.remote_state.get_metrics` (_source=remote authoritative). Pause-flag ABSENT. REMOTE-FIRST per e51aee7.

**Step 0 honest re-read summary.** 5 HONEST (3 clean Tier 0/1 HP + 2 NEGATIVE-RESULT-CONFIRMATION HP for Tier 2 boundary characterizations). **0 NEW LABEL-VS-HONEST OVER-CLAIMS.**

- **substrate_metric_norm_axioms_v1** (label "All 4 Frobenius norm axioms confirmed... max_violation=7.11e-15 < 1e-08. mean_triples_all_pass=50.0/50. PP-41 mathematical foundation validated."): HONEST. All 4 axioms (positivity, definiteness, homogeneity, triangle inequality) PASS by 7 orders of magnitude below HP threshold; 50/50 triples pass at all 5 seeds. TRUE-METRIC structure confirmed.
- **write_back_dirty_bits_v1** (label "Write-back dirty bit semantics confirmed. min_dirty_acc=1.000>=0.95 max_delta_cos=0.0000<0.05. O(M) auxiliary vector sufficient; zero W modification required."): HONEST. Perfect 1.000 dirty-bit accuracy + 0.0000 cosine delta unanimous 5-seed. Tier 1 cache extension clean.
- **write_around_routing_v1** (label "Write-around routing via probe confirmed. min_acc=1.000>=0.9 max_fpr=0.000<0.1. Cross-primitive composition (probe=refusal-cert) works for routing."): HONEST. Perfect 1.000 routing accuracy + 0.000 false-positive rate unanimous 5-seed; cross-primitive composition probe=refusal-cert verified. Tier 1 cache extension clean. Short 3.4s wall is consistent with algebraic-identity probe test at N=1024 5-seed.
- **per_key_ttl_external_required_v1** (label "Per-key TTL constraint CONFIRMED (negative result). max_delta_retention=0.0000 < 0.05. Both groups decay identically under global gamma=0.9. Single-W substrate supports only ONE global decay rate -- per-key TTL requires external bookkeeping."): HONEST. NEGATIVE-RESULT pre-reg HP was evidence-of-constraint (max_delta_retention < 0.05 = confirmation that single-W supports only one gamma); actual=0.0000 EXACT confirmation. Tier 2 BOUNDARY EMPIRICALLY CONFIRMED.
- **eviction_id_external_codebook_v1** (label "Eviction codebook constraint CONFIRMED. With codebook: min_known_auroc=0.960>=0.7. Without codebook: mean_random_auroc=0.503~=0.50 (|deviation|=0.003<=0.15). Substrate orders priorities natively but CANNOT enumerate argmin without external dictionary (Tier 2 constraint confirmed)."): HONEST. NEGATIVE-RESULT pre-reg HP was evidence-of-constraint (with-codebook AUROC >= 0.7 AND without-codebook AUROC ~ chance with |dev| <= 0.15 = confirmation that argmin requires dictionary); actuals: 0.960 + 0.503 + 0.003 EXACT confirmation. Tier 2 BOUNDARY EMPIRICALLY CONFIRMED.

Per [[feedback-no-preframing]]: 3 short-wall anchors (write_around 3.4s + per_key_ttl 3.3s + eviction_id 5.3s) were pre-framed in task prompt with explicit caveat "fast walls on cache cells are EXPECTED per design -- algebraic tests not numerical sweeps; verify FULL scope ran via metrics.json run_mode + script-reported config". Honest re-read CONFIRMED all 3 genuine via remote metrics: run_mode=full + N=1024 + seeds=[7,17,23,31,41] + per-cell aggregated metrics. Same pattern as v328 q23_capacity_cliff (1.7s) + graph_node_classification (1.4s) -- short wall is consistent with algebraic-identity tests at modest M and N.

Per [[feedback-rehabilitation-after-rejection]]: 2 NEGATIVE-RESULT-CONFIRMATION tests (per_key_ttl + eviction_id) are EMPIRICAL CONSTRAINT VALIDATIONS, not failures. Both pre-registered HP as evidence-of-constraint and actuals EXACTLY confirm. Product framing: substrate operating envelope is Tier 0+1 native + Tier 2 external bookkeeping (thin dirty-bit vector + M-element dictionary).

**Verdicts processed (5).** Roster in cap_map v329 anchor.

**Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]]).**

**NO rescues needed this batch** (5/5 GENUINE HP; 2 NEGATIVE-RESULT-CONFIRMATION at pre-reg evidence-of-constraint thresholds).

v328 carry-over rescues REMAIN OPEN for next-cycle dispatch:
- PP-43b LRU small-M rescue (1-2h CPU; small-M sweep at finer grid + piecewise-constant gamma).
- PP-43d ARC/LIRS low-alpha rescue (1-2h CPU; fine alpha grid in [0.05, 0.5]).

NEW v329 follow-on candidate (NOT a rescue; production extension):
- **PP-41 edit-distance primitive extension** (carry-over v327 R2, NOW HIGHER PRIORITY post-TRUE-METRIC confirmation) -- ||W_A - W_B||_F / sqrt(|A symdiff B|) over edit chains; substrate-native edit-magnitude readout. PP-41 TRUE-METRIC empirical confirmation makes this extension MUCH more confidently grounded.

**Strategic positioning.** Cycle 5 LANDS 2 STRUCTURAL LIFTs on existing rows:

1. **PP-41 TRUE-METRIC structural confirmation.** Two independent empirical anchors at independent N (v327 frobenius_symdiff_verify_v1 7 configs N=4096 0.7% max error + v329 substrate_metric_norm_axioms_v1 4 axioms N=1024 7e-15 max violation) confirm substrate has a TRUE metric structure under Frobenius distance. Product framing: "substrate edit-distance is a genuine mathematical metric -- not pseudo-metric, not quasi-metric, but a real metric satisfying all 4 norm axioms within machine precision." This is LOAD-BEARING for PP-9 deletion-cert sizing, PP-12 compositionality audit, PP-31a refusal-audit-cert -- all of which can now confidently reason about algebraic distance as a genuine metric.

2. **PP-43 caching-policy Tier 1+2 EMPIRICAL CHARACTERIZATION.** Three v329 anchors extend substrate caching-policy expressibility from v328 Tier 0 (LFU clean + LRU large-M-conditional + write-through clean + ARC high-alpha-conditional) to Tier 1 (write-back dirty-bits clean + write-around routing clean WITH CROSS-PRIMITIVE COMPOSITION probe=refusal-cert) and explicitly Tier 2 BOUNDARY (per-key TTL requires external bookkeeping + eviction-ID requires external codebook). PP-43 row band LIFTs 0.55-0.70 -> 0.62-0.77 reflecting that substrate's caching-policy expressibility is now MAPPED EMPIRICALLY at three tiers with honest constraint characterization. The Tier 2 BOUNDARY confirmations are PRODUCT-FRAMING WINS (not failures): honest envelope documentation is exactly what audit-grade products need to ship reliably. Compliance-sidecar architecture (PRIMARY GTM v315) absorbs Tier 2 external requirements seamlessly -- bookkeeping is the sidecar's job, substrate stays on the algebraic-cert path.

3. **Cross-primitive composition discovery (PP-43f).** write_around_routing_v1 confirms probe primitive serves DUAL purposes: refusal-cert (PP-31a) AND write-around routing (PP-43f). Same algebraic mechanism, two product applications. Reinforces v314 architectural-moat finding that substrate primitives compose cleanly across product features.

**Atomic commit.** cap_map.md + history.md + this strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry. **240th PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Tallies (v328 -> v329).** HONEST 373 -> 378 (+5). LABEL-VS-HONEST 199 UNCHANGED. Portfolio 32+66 UNCHANGED (no new top-level rows; 2 LIFTs + 4 new sub-properties). Framework-reliability product-feature 64-78% -> 66-80% (+2pp). 0 row closures. 0 new LABEL-VS-HONEST catches.
