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
