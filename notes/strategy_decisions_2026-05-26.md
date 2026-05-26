# Strategy decisions log -- 2026-05-26

This file records strategy decisions made on 2026-05-26. Append-only.
Each entry references the cap_map version it pairs with (PROT-009).

---

## v207 -- 2026-05-26 BATCHED 5-VERDICT (Bet B Alt 3 CLOSED; MoE alpha_c v2 marginal miss; Pred-4 v2 TIMEOUT; SHIFT/PARTITION v1 OOM; 4-corpus v3 already-processed at v206)

**Trigger.** Five pending verdicts surfaced by SSH-restore flush after v206 (commit a6bb07b). Exp_dev agent a777bd74dada08bc0 verified pre-block anchors and routed to verdict_handler. Sources:
- `wave14_betB_pac_bayes_kl_predictor_v2` (remote) -> ALT3_LAPLACE_ASSUMPTION_VIOLATED (r2_fisher=0.0; 21/25 cells)
- `wave14_moe_alpha_c_prestep_v2` (remote) -> ALPHA_C_HARD_FAIL (alpha_c=0.390625; band [0.40, 0.70])
- `wave14_betB_4corpus_equalspacing_v1` (local) -> HARD_PASS already-processed at v206
- `wave14_1rsb_hysteresis_v2` (remote) -> TIMEOUT (wall=3600s)
- `wave14_moe_shift_partition_v1` (remote) -> OOM (1.11GiB on 8GiB at M=25600, K=8)

**Decision (1): Bet B Alt 3 PAC-Bayes Laplace CLOSED at production scale; all 3 Bet B predictability rescues now resolved.**
`wave14_betB_pac_bayes_kl_predictor_v2` r2_fisher=0.0 with 21/25 cells flagged ALT3_LAPLACE_ASSUMPTION_VIOLATED -- real instrumentation result, NOT bug. Substrate violates the Laplace approximation R-PRIME-1 PAC-Bayes-KL upper bound rests on. PAC-Bayes posterior-over-W KL framing does NOT predict substrate retention at production scale.

Combined status of Bet B predictability rescue arms:
- Alt 1 (discrete shift-class predictor, 4-class SAME/REPLAY/STAGE4/DIFF taxonomy): GROUP-LEVEL CONFIRMED at v206 (4-corpus equal-spacing HARD_PASS + REPLAY structural axis d=13.3); silhouette=0.584 MIDDLE BAND at within-cell level per v205; Bet B Yellow-PARTIAL row UNCHANGED at within-cell granularity
- Alt 2 (W-internal signature continuous predictor): HARD-FAILed at v202, RECLASSIFIED INCONCLUSIVE v203
- Alt 3 (PAC-Bayes posterior-over-W KL Laplace): **v207 CLOSED**

Net story: continuous predictors do NOT hold; discrete-class IS the substrate's predictability story. The Saad-Solla saddle-cascade 4-plateau confirmation (v206) STRENGTHENS the discrete-class framing -- the 4 plateaus saddle-cascade arithmetic predicts ARE the 4 classes Alt 1 isolated. Discrete-class and saddle-cascade are TWO LENSES ON THE SAME STRUCTURE.

**Decision (2): MoE alpha_c v2 Yellow MARGINAL MISS; defensibility-audit trigger; MoE rebuild tempered but not killed.**
`wave14_moe_alpha_c_prestep_v2` alpha_c=0.390625, below band lower-edge [0.40, 0.70] by 0.009375 (~0.94% of band). Pre-reg label HARD-FAIL stands but margin is technically marginal. NOT a substrate kill. v207 NEW pre-reg: alpha_c band-rationale defensibility audit (Research-capacity-dependent or sub-Strategy). MoE rebuild path TEMPERED but NOT KILLED; SHIFT/PARTITION v2 (in flight) is the live test, dominates over prestep margin.

**Decision (3): SHIFT/PARTITION v1 OOM superseded by v2 in flight; no row-state change.**
`wave14_moe_shift_partition_v1` OOM (1.11GiB on 8GiB at M=25600, K=8). Infrastructure failure, not substrate result. v2 already in flight on remote with patched configuration per v206 OPEN line. v2 outcome dominates. If v2 ALSO OOMs, v3 with reduced M_grid (M <= 16384) -- exp_dev decides v3 design per [[feedback-no-experiment-design-in-prompts]].

**Decision (4): Pred-4 v2 TIMEOUT; v3 design pending (exp_dev decides parameters).**
`wave14_1rsb_hysteresis_v2` TIMEOUT at 3600s; no metrics.json. v1 was INSTRUMENTATION_FAIL TypeError (v195/v197); v2 TIMEOUT. Pred-4 the cleanest 1-RSB-class binary discriminator FAILED TO PRODUCE DATA TWICE. The 1-RSB framing vs Saad-Solla saddle-cascade discriminator (first-order vs continuous transition) REMAINS PENDING -- load-bearing for framework reliability upper-bound (firms to 50-65% if first-order; stays at 40-55% if continuous). v207 NEW pre-reg: Pred-4 v3 design -- exp_dev decides EITHER 2-4h wall OR reduced N per cell OR fewer sweep points.

**Decision (5): 4-corpus equal-spacing V3 verdict ALREADY-PROCESSED at v206; v207 re-confirms v206 row-moves.**
`wave14_betB_4corpus_equalspacing_v1` HARD_PASS (BIC_delta=-121.3; spacing_error=0.0035; all CI pairs non-overlapping). Honest-reread VERIFIED: gap_ratio=0.955 outside pre-reg [0.45, 0.65] on more-equal side; spacing_error overrides per honest-reread protocol; HARD_PASS stands. ALREADY processed at v206 commit a6bb07b -- theoretical-home green-CORROBORATED + framework reliability green 40-55% UNCHANGED at v207. Status_log entry as already-processed confirmation; no new cap_map change FROM V3 verdict at v207.

**Net cap_map effect.** v206 -> v207 BATCHED 5-VERDICT: 1 Closed-Negative closure (Alt 3 PAC-Bayes Laplace); 1 Yellow marginal-miss annotation (MoE alpha_c v2); 2 infrastructure annotations (Pred-4 v2 TIMEOUT, SHIFT/PARTITION v1 OOM); 1 already-processed re-confirmation (4-corpus V3 at v206). 7 capability move rows. 0 row-state advances at v207 (Alt 3 closure adds a CANNOT row; portfolio counts unchanged). 2 v207 NEW pre-reg (Pred-4 v3 design, alpha_c band-rationale audit). 13 demonstrated + 6 evidence-strength rows UNCHANGED. 120th PROT-009 paired commit (cap_map.md v207 + history.md v207 + this strategy_decisions entry).

PROT-004/006/008/009 compliance this commit: 1 new Closed-Negative closure (Alt 3 PAC-Bayes Laplace); 1 axis-closure (predictability rescue arm; not a primary capability -- closure is the appropriate post-mortem per [[feedback-rehabilitation-after-rejection]] since all 3 Alt rescues now resolved); 0 row-state demotions; 0 portfolio-row demotions; 0 new instrumentation debts this cycle (Pred-4 v2 TIMEOUT is wall-budget issue, not instrumentation); pre-existing 29 PROT-004 violations are grandfathered historical entries unchanged; validator passes; history.md v207 block written; strategy_decisions paired; 120th PROT-009 commit.

Honest-reread LOCK (per [[feedback-verdict-msg-honest-reread]]): 72nd-76th observations post-lock. ALT3_LAPLACE_ASSUMPTION_VIOLATED CONFIRMED clean (r2=0.0 + 21/25 cells flagged); ALPHA_C_HARD_FAIL NOMINALLY correct but margin (~1%) documented as marginal not kill; HARD_PASS V3 already documented at v206 with gap_ratio override; TIMEOUT/OOM are infrastructure failures with no per-cell metrics to override (label confirmed by absence of data). 5/5 honest re-reads PROT-009 compliant.

DO NOT trigger queue-refill -- exp_dev separately flushing handoffs same turn; v3 retries (Pred-4 + SHIFT/PARTITION if v2 OOMs) are exp_dev's decisions per [[feedback-no-experiment-design-in-prompts]] item 7. Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
